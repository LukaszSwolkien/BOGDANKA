"""Algo service entrypoint - minimal WS implementation."""

from __future__ import annotations

import argparse
import logging
import signal
import sys
import threading
import time
from pathlib import Path

from algo.algorithm_rc import AlgorithmRC, RCConfig
from algo.algorithm_rn import AlgorithmRN, RNConfig
from algo.algorithm_ws import AlgorithmWS, WSConfig
from algo.display import StatusDisplay
from algo.metrics import AlgoMetrics
from algo.state import AlgoState
from algo.weather_client import WeatherClient
from common.domain import Heater, Line, Scenario
from common.config import load_config
from common.telemetry import TelemetryManager

LOGGER = logging.getLogger("algo-service")


class AlgoService:
    """
    Main algo service implementing heating control algorithms.
    
    Phase 2 MVP: WS algorithm only (scenario selection).
    RC and RN algorithms will be added in subsequent iterations.
    
    Key Design: Uses simulation_time from weather service - NO independent clock!
    """
    
    def __init__(self, config_path: Path, display_output_stream=None, test_profile_description=None):
        # Load configuration
        self.config = load_config(config_path)
        self._configure_logging()
        
        # Initialize telemetry
        self.telemetry = TelemetryManager(self.config.telemetry)
        
        # Initialize global state
        self.state = AlgoState()
        
        # Initialize weather client
        self.weather_client = WeatherClient(
            endpoint_url=self.config.services.algo.weather_endpoint,
            timeout_seconds=self.config.services.algo.otlp_timeout_ms / 1000.0,
        )
        
        # Initialize Algorithm WS
        ws_config = WSConfig(
            temp_monitoring_cycle_s=self.config.services.algo.algorithms.ws.temp_monitoring_cycle_s,
            scenario_stabilization_time_s=self.config.services.algo.algorithms.ws.scenario_stabilization_time_s,
            hysteresis_delta_c=self.config.services.algo.algorithms.ws.hysteresis_delta_c,
        )
        self.algorithm_ws = AlgorithmWS(config=ws_config, state=self.state)
        
        # Initialize Algorithm RC
        rc_config = RCConfig(
            rotation_period_hours=self.config.services.algo.algorithms.rc.rotation_period_hours,
            rotation_duration_s=self.config.services.algo.algorithms.rc.rotation_duration_s,
            algorithm_loop_cycle_s=self.config.services.algo.algorithms.rc.algorithm_loop_cycle_s,
            min_operating_time_s=self.config.services.algo.algorithms.rc.min_operating_time_s,
        )
        self.algorithm_rc = AlgorithmRC(config=rc_config, state=self.state)
        
        # Initialize Algorithm RN
        rn_config = RNConfig(
            rotation_period_hours=self.config.services.algo.algorithms.rn.rotation_period_hours,
            rotation_duration_s=self.config.services.algo.algorithms.rn.rotation_duration_s,
            min_delta_time_s=self.config.services.algo.algorithms.rn.min_delta_time_s,
            algorithm_loop_cycle_s=self.config.services.algo.algorithms.rn.algorithm_loop_cycle_s,
        )
        self.algorithm_rn = AlgorithmRN(config=rn_config, state=self.state)
        
        # Initialize metrics (AFTER algorithm_rn, as it needs reference to it)
        self.metrics = AlgoMetrics(
            telemetry=self.telemetry,
            metrics_prefix=self.config.services.algo.metrics_prefix,
            default_dimensions=dict(self.config.telemetry.default_dimensions),
            state=self.state,
            algorithm_rn=self.algorithm_rn,
        )
        
        # Initialize recent events buffers (for display) - separate for WS, RC, RN
        self._recent_ws_events: list[str] = []
        self._recent_rc_events: list[str] = []
        self._recent_rn_events: list[str] = []
        self._max_recent_events = 8  # Show 8 events (4 rows x 2 columns)
        
        # Initialize status display
        self.display = StatusDisplay(
            state=self.state,
            algorithm_rn=self.algorithm_rn,
            algorithm_ws=self.algorithm_ws,
            algorithm_rc=self.algorithm_rc,
            recent_ws_events=self._recent_ws_events,
            recent_rc_events=self._recent_rc_events,
            recent_rn_events=self._recent_rn_events,
            enabled=self.config.services.algo.display.enabled,
            output_stream=display_output_stream,  # Inject output stream for test runner
            test_profile_description=test_profile_description,  # Inject test profile description for test runner
            acceleration=self.config.simulation.acceleration,  # Pass acceleration factor
            duration_seconds=self.config.simulation.duration_days * 24 * 3600,  # Convert days to seconds
        )
        
        # Control flags
        self._running = False
        self._stop_requested = False
        
        LOGGER.info("Algo service initialized successfully")
        LOGGER.info(f"Weather endpoint: {self.config.services.algo.weather_endpoint}")
        LOGGER.info(f"Acceleration: {self.config.simulation.acceleration}x")
        LOGGER.info(f"Duration: {self.config.simulation.duration_days} days")
        LOGGER.info(f"Display: {'enabled' if self.config.services.algo.display.enabled else 'disabled'}")
    
    def _configure_logging(self) -> None:
        """Configure logging based on config."""
        level = getattr(logging, self.config.telemetry.log_level.upper(), logging.INFO)
        log_format = "%(asctime)s %(levelname)s %(name)s - %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"
        
        # Determine output based on config and display setting
        log_output = self.config.telemetry.log_output
        display_enabled = self.config.services.algo.display.enabled
        
        # If display is enabled, force logs to file only (unless explicitly "both")
        if display_enabled and log_output == "console":
            log_output = "file"
        
        if log_output == "file":
            # Log to file only
            from pathlib import Path
            log_file = Path(self.config.telemetry.log_file)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            logging.basicConfig(
                level=level,
                format=log_format,
                datefmt=date_format,
                filename=str(log_file),
                filemode='a',
            )
        elif log_output == "both":
            # Log to both file and console
            from pathlib import Path
            log_file = Path(self.config.telemetry.log_file)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            logging.basicConfig(
                level=level,
                format=log_format,
                datefmt=date_format,
                handlers=[
                    logging.FileHandler(str(log_file), mode='a'),
                    logging.StreamHandler(),
                ],
            )
        else:
            # Log to console only (default)
            logging.basicConfig(
                level=level,
                format=log_format,
                datefmt=date_format,
            )
    
    def start(self) -> None:
        """Start the algo service main loop."""
        # Wait for weather service to be available
        LOGGER.info("Waiting for weather service to become available...")
        if not self.weather_client.wait_for_service(max_wait_seconds=30.0):
            LOGGER.error("Weather service not available - exiting")
            sys.exit(1)
        
        LOGGER.info("Weather service is ready - starting main loop")
        self._running = True
        
        # Setup signal handlers for graceful shutdown (only if in main thread)
        if threading.current_thread() is threading.main_thread():
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            self._main_loop()
        except KeyboardInterrupt:
            LOGGER.info("Keyboard interrupt received")
        except Exception as exc:
            LOGGER.exception(f"Fatal error in main loop: {exc}")
            raise
        finally:
            self.shutdown()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        LOGGER.info(f"Received signal {signum} - initiating shutdown")
        self._stop_requested = True
    
    def _add_event(self, event_type: str, event_text: str) -> None:
        """
        Add event to recent events buffer (for display).
        
        Args:
            event_type: Type of event ('ws', 'rc', or 'rn')
            event_text: Short event description (e.g., "S3→S4", "C1→C2", "N1→N2")
        """
        # Format: [D5 12:34] event_text (day + HH:MM)
        sim_day = int(self.state.simulation_time // 86400)
        sim_time_h = int((self.state.simulation_time % 86400) // 3600)
        sim_time_m = int((self.state.simulation_time % 3600) // 60)
        timestamp = f"[D{sim_day} {sim_time_h:02d}:{sim_time_m:02d}]"
        
        event_with_timestamp = f"{timestamp} {event_text}"
        
        # Add to appropriate list
        if event_type == 'ws':
            self._recent_ws_events.append(event_with_timestamp)
            while len(self._recent_ws_events) > self._max_recent_events:
                self._recent_ws_events.pop(0)
        elif event_type == 'rc':
            self._recent_rc_events.append(event_with_timestamp)
            while len(self._recent_rc_events) > self._max_recent_events:
                self._recent_rc_events.pop(0)
        elif event_type == 'rn':
            self._recent_rn_events.append(event_with_timestamp)
            while len(self._recent_rn_events) > self._max_recent_events:
                self._recent_rn_events.pop(0)
    
    def _main_loop(self) -> None:
        """
        Main simulation loop.
        
        Critical: Uses simulation_time from weather service responses.
        No independent clock in algo service!
        """
        # Calculate loop timing
        poll_interval_sim = self.config.services.algo.algorithms.ws.temp_monitoring_cycle_s
        acceleration = self.config.simulation.acceleration
        poll_interval_real = poll_interval_sim / acceleration  # Convert to real time
        
        duration_sim = self.config.simulation.duration_seconds
        
        LOGGER.info(
            f"Starting main loop: poll_interval={poll_interval_sim}s sim "
            f"({poll_interval_real:.3f}s real @ {acceleration}x acceleration)"
        )
        LOGGER.info(f"Will run until simulation_time >= {duration_sim}s ({self.config.simulation.duration_days} days)")
        
        loop_count = 0
        rc_check_count = 0
        rn_check_count = 0
        rc_check_interval = self.config.services.algo.algorithms.rc.algorithm_loop_cycle_s
        rn_check_interval = self.config.services.algo.algorithms.rn.algorithm_loop_cycle_s
        
        # Display refresh tracking (in real time)
        display_refresh_interval_real = self.config.services.algo.display.refresh_rate_s
        last_display_refresh_real = 0.0
        
        while self._running and not self._stop_requested:
            loop_start_real = time.time()
            
            # STEP 1: Poll weather service (gets temperature + authoritative simulation_time)
            snapshot = self.weather_client.poll()
            
            if snapshot is None:
                LOGGER.warning("Failed to poll weather service - retrying...")
                time.sleep(poll_interval_real)
                continue
            
            # STEP 2: Update simulation time from weather service (CRITICAL!)
            self.state.update_simulation_time(snapshot.simulation_time)
            
            # Log progress periodically
            if loop_count % 10 == 0:
                LOGGER.info(
                    f"Loop {loop_count}: sim_time={snapshot.simulation_time:.1f}s "
                    f"({snapshot.simulation_day:.2f} days), "
                    f"T_zewn={snapshot.temperature_c:.1f}°C, "
                    f"scenario={self.state.current_scenario.name}"
                )
            
            # STEP 3: Run Algorithm WS (scenario selection)
            old_scenario = self.state.current_scenario
            scenario_changed, message = self.algorithm_ws.process_temperature(snapshot.temperature_c)
            
            if scenario_changed:
                # Record metric
                self.metrics.record_scenario_change(old_scenario, self.state.current_scenario)
                # Add event for display
                self._add_event('ws', f"{old_scenario.name}→{self.state.current_scenario.name}")
            elif loop_count % 60 == 0:  # Every 10 minutes (60 * 10s cycles)
                # Log current state periodically
                LOGGER.debug(
                    f"Status: scenario={self.state.current_scenario.name}, "
                    f"config={self.state.current_config}, "
                    f"temp={snapshot.temperature_c:.1f}°C, "
                    f"sim_day={snapshot.simulation_day:.1f}"
                )
            
            # STEP 4: Run Algorithm RC (configuration rotation)
            # RC runs less frequently than WS (e.g., every 60s vs 10s)
            rc_check_count += 1
            if rc_check_count * poll_interval_sim >= rc_check_interval:
                rc_check_count = 0
                old_config = self.state.current_config
                config_changed, rc_message = self.algorithm_rc.process()
                
                if config_changed:
                    # Record metric
                    self.metrics.record_config_change(old_config, self.state.current_config)
                    # Add event for display
                    old_config_short = "C1" if old_config == "Primary" else "C2"
                    new_config_short = "C1" if self.state.current_config == "Primary" else "C2"
                    self._add_event('rc', f"{old_config_short}→{new_config_short}")
                    
                    # CRITICAL: Immediately run RN to synchronize heater states after RC change
                    # Without this, display shows old heaters until next RN cycle (~60s)
                    LOGGER.debug("RC config changed - triggering immediate RN sync")
                    self.algorithm_rn.process()  # Sync heaters immediately
            
            # STEP 5: Run Algorithm RN (heater rotation)
            # RN runs at same frequency as RC (e.g., every 60s)
            rn_check_count += 1
            if rn_check_count * poll_interval_sim >= rn_check_interval:
                rn_check_count = 0
                rotation_occurred, rn_message = self.algorithm_rn.process()
                
                if rotation_occurred:
                    # Record metric
                    # Parse line and heaters from message (format: "Heater rotated in LINE1: N1 → N2")
                    if "C1" in rn_message:
                        line = "C1"
                    elif "C2" in rn_message:
                        line = "C2"
                    else:
                        line = "UNKNOWN"
                    
                    # Extract heaters from message
                    if ":" in rn_message and "→" in rn_message:
                        parts = rn_message.split(":")[-1].split("→")
                        if len(parts) == 2:
                            heater_off = parts[0].strip()
                            heater_on = parts[1].strip()
                            self.metrics.record_heater_rotation(line, heater_off, heater_on)
                            # Add event for display
                            self._add_event('rn', f"{line}: {heater_off}→{heater_on}")
                elif "blocked" in rn_message.lower() or "cannot" in rn_message.lower():
                    # RN blocked - add as event
                    if "config change" in rn_message.lower():
                        self._add_event("RN: ⊗RC lock")
                    elif "too soon" in rn_message.lower():
                        self._add_event("RN: ⊗wait")
            
            # STEP 6: Update metrics
            self.metrics.update()
            
            # STEP 6.5: Refresh status display (throttled by refresh_rate_s in real time)
            current_real_time = time.time()
            if current_real_time - last_display_refresh_real >= display_refresh_interval_real:
                self.display.render(temperature_c=snapshot.temperature_c)
                last_display_refresh_real = current_real_time
            
            # STEP 7: Check if simulation complete
            if self.state.simulation_time >= duration_sim:
                LOGGER.info(
                    f"Simulation complete: reached {duration_sim}s "
                    f"({self.config.simulation.duration_days} days)"
                )
                break
            
            # STEP 8: Sleep in real time
            loop_duration_real = time.time() - loop_start_real
            sleep_time = max(0, poll_interval_real - loop_duration_real)
            
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                LOGGER.warning(
                    f"Loop took longer than poll interval: {loop_duration_real:.3f}s "
                    f"> {poll_interval_real:.3f}s"
                )
            
            loop_count += 1
        
        LOGGER.info(f"Main loop completed after {loop_count} iterations")
    
    def shutdown(self) -> None:
        """Graceful shutdown."""
        LOGGER.info("Shutting down algo service...")
        self._running = False
        
        # Final update to capture last scenario's time
        self.algorithm_ws._update_scenario_time()
        
        # Final metrics flush
        LOGGER.info("Final metrics state:")
        LOGGER.info(f"  Simulation time: {self.state.simulation_time:.1f}s ({self.state.simulation_time/3600:.1f}h)")
        LOGGER.info(f"  Current scenario: {self.state.current_scenario.name}")
        LOGGER.info(f"  Current config: {self.state.current_config}")
        LOGGER.info(f"  Last temperature: {self.state.last_valid_reading:.1f}°C")
        
        # Scenario distribution
        LOGGER.info("  Scenario distribution:")
        scenario_times = self.algorithm_ws.get_all_scenario_times()
        total_sim_time = self.state.simulation_time
        
        for scenario in Scenario:
            time_s = scenario_times.get(scenario, 0.0)
            time_h = time_s / 3600
            percentage = (time_s / total_sim_time * 100) if total_sim_time > 0 else 0
            LOGGER.info(f"    {scenario.name}: {time_h:.1f}h ({percentage:.1f}%)")
        
        # RC times in hours
        time_primary_h = self.algorithm_rc.get_time_in_primary() / 3600
        time_limited_h = self.algorithm_rc.get_time_in_limited() / 3600
        rc_rotation_count = self.algorithm_rc.get_rotation_count()
        LOGGER.info(f"  Time in Primary: {time_primary_h:.1f}h")
        LOGGER.info(f"  Time in Limited: {time_limited_h:.1f}h")
        if self.algorithm_rc.get_balance_ratio() != float('inf'):
            LOGGER.info(f"  Balance ratio (P/L): {self.algorithm_rc.get_balance_ratio():.2f}")
        LOGGER.info(f"  Configuration changes (RC): {rc_rotation_count}")
        
        # Log heater operating times with percentage distribution
        rn_rotation_count = self.algorithm_rn.get_rotation_count()
        LOGGER.info(f"  Heater rotations (RN): {rn_rotation_count}")
        LOGGER.info("  Heater operating times:")
        sim_time_s = self.state.simulation_time
        for heater in Heater:
            op_time_s = self.algorithm_rn.get_heater_operating_time(heater)
            op_time_h = op_time_s / 3600
            idle_time_s = self.algorithm_rn.get_heater_idle_time(heater)
            idle_time_h = idle_time_s / 3600
            state = self.algorithm_rn.get_heater_state(heater)
            # Percentage = (heater operating time / simulation time) * 100
            percentage = (op_time_s / sim_time_s * 100) if sim_time_s > 0 else 0
            LOGGER.info(
                f"    {heater.name}: {op_time_h:.1f}h operating ({percentage:.1f}%), "
                f"{idle_time_h:.1f}h idle, state={state.value}"
            )
        
        # Shutdown telemetry
        self.telemetry.shutdown()
        LOGGER.info("Algo service shutdown complete")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="BOGDANKA Algo Service - Heating Control Algorithms"
    )
    default_config = Path(__file__).parent / "config.yaml"
    parser.add_argument(
        "--config",
        type=Path,
        default=default_config,
        help="Path to config.yaml",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=None,
        help="Override simulation duration_days from config (useful for testing)",
    )
    
    args = parser.parse_args()
    
    # Load and optionally override config
    if args.days is not None:
        # Create modified config
        import tempfile
        import yaml
        
        config = load_config(args.config)
        config.simulation.duration_days = args.days
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_dict = {
                "simulation": {
                    "acceleration": config.simulation.acceleration,
                    "duration_days": config.simulation.duration_days,
                },
                "telemetry": {
                    "exporter_type": config.telemetry.exporter_type,
                    "endpoints": dict(config.telemetry.endpoints),
                    "headers": dict(config.telemetry.headers),
                    "resource_attributes": dict(config.telemetry.resource_attributes),
                    "default_dimensions": dict(config.telemetry.default_dimensions),
                    "log_level": config.telemetry.log_level,
                },
                "services": {
                    "algo": {
                        "service_name": config.services.algo.service_name,
                        "metrics_prefix": config.services.algo.metrics_prefix,
                        "weather_endpoint": config.services.algo.weather_endpoint,
                        "otlp_timeout_ms": config.services.algo.otlp_timeout_ms,
                        "algorithms": {
                            "ws": {
                                "temp_monitoring_cycle_s": config.services.algo.algorithms.ws.temp_monitoring_cycle_s,
                                "scenario_stabilization_time_s": config.services.algo.algorithms.ws.scenario_stabilization_time_s,
                                "hysteresis_delta_c": config.services.algo.algorithms.ws.hysteresis_delta_c,
                            },
                            "rc": {
                                "rotation_period_hours": config.services.algo.algorithms.rc.rotation_period_hours,
                                "algorithm_loop_cycle_s": config.services.algo.algorithms.rc.algorithm_loop_cycle_s,
                                "min_operating_time_s": config.services.algo.algorithms.rc.min_operating_time_s,
                            },
                            "rn": {
                                "rotation_period_s1_s": config.services.algo.algorithms.rn.rotation_period_s1_s,
                                "rotation_period_s2_s": config.services.algo.algorithms.rn.rotation_period_s2_s,
                                "rotation_period_s3_s": config.services.algo.algorithms.rn.rotation_period_s3_s,
                                "rotation_period_s4_s": config.services.algo.algorithms.rn.rotation_period_s4_s,
                                "rotation_period_s5_s": config.services.algo.algorithms.rn.rotation_period_s5_s,
                                "rotation_period_s6_s": config.services.algo.algorithms.rn.rotation_period_s6_s,
                                "rotation_period_s7_s": config.services.algo.algorithms.rn.rotation_period_s7_s,
                                "rotation_period_s8_s": config.services.algo.algorithms.rn.rotation_period_s8_s,
                                "min_delta_time_s": config.services.algo.algorithms.rn.min_delta_time_s,
                                "algorithm_loop_cycle_s": config.services.algo.algorithms.rn.algorithm_loop_cycle_s,
                            },
                        },
                    },
                    "weather": {},
                },
            }
            yaml.dump(config_dict, f)
            temp_config_path = Path(f.name)
        
        try:
            service = AlgoService(temp_config_path)
            service.start()
        finally:
            # Clean up temp file
            temp_config_path.unlink()
    else:
        # Use config as-is
        service = AlgoService(args.config)
        service.start()


if __name__ == "__main__":
    main()

