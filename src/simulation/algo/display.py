"""Console status display for algo service."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from common.domain import Heater, Line, Scenario

if TYPE_CHECKING:
    from .state import AlgoState
    from .algorithm_rn import AlgorithmRN


class StatusDisplay:
    """
    ANSI-based status header for console output.
    
    Displays real-time system state in a fixed header at top of terminal,
    with event logs scrolling below.
    
    Design:
    - Only READS from state (no modifications)
    - Uses ANSI escape codes for positioning
    - Auto-detects terminal support
    - Can be disabled via config
    """
    
    def __init__(
        self,
        state: AlgoState,
        algorithm_rn: AlgorithmRN,
        algorithm_ws,  # Type hint would be circular, so kept as Any
        recent_events: list[str],
        enabled: bool = True,
    ):
        """
        Initialize display.
        
        Args:
            state: Global algorithm state (read-only)
            algorithm_rn: RN algorithm for heater states (read-only)
            algorithm_ws: WS algorithm for scenario time stats (read-only)
            recent_events: List of recent events (last 4, managed externally)
            enabled: Enable/disable display (can disable on Windows CMD)
        """
        self.state = state
        self.algorithm_rn = algorithm_rn
        self.algorithm_ws = algorithm_ws
        self.recent_events = recent_events  # Reference to external list
        
        # Auto-detect terminal support if not explicitly disabled
        if enabled is None:
            # Disable on Windows CMD, enable on Unix/WSL
            self.enabled = sys.stdout.isatty() and sys.platform != 'win32'
        else:
            self.enabled = enabled
        
        # Track if we've rendered at least once (for smooth scrolling)
        self._first_render = True
    
    def render(self, temperature_c: float) -> None:
        """
        Render status header to console.
        
        This is the ONLY output to console (logs go to file).
        Header is redrawn in place on each refresh.
        
        Args:
            temperature_c: Current external temperature
        """
        if not self.enabled:
            return
        
        # Build entire header as string buffer (reduces flicker)
        lines = []
        
        # ANSI codes:
        # \x1b[H = move cursor to home (top-left)
        # \x1b[K = clear line from cursor to end
        # \x1b[2J = clear entire screen (only on first render)
        
        if self._first_render:
            # First render: clear screen
            lines.append("\x1b[2J")
            self._first_render = False
        
        # Always move to top for redraw
        lines.append("\x1b[H")
        
        # ═══════════════════════════════════════════════════════════
        # HEADER: Scenario & Mode
        # ═══════════════════════════════════════════════════════════
        lines.append("┌─ Scenario & Mode ──────────────────────────┐\x1b[K")
        
        # Format scenario (with ANSI colors, so can't use width formatting)
        scenario_str = self._format_scenario(self.state.current_scenario)
        # Pad to align properly (scenario names are 2 chars, add spaces to total ~8)
        scenario_display = f"Scenario: {scenario_str}      "  # Extra spaces for alignment
        
        lines.append(
            f"│ {scenario_display}T_zewn: {temperature_c:6.1f}°C │\x1b[K"
        )
        lines.append(
            f"│ Mode: {self.state.mode:6s}   Locks: {self._format_locks():15s} │\x1b[K"
        )
        
        # ═══════════════════════════════════════════════════════════
        # SECTION: Line Status
        # ═══════════════════════════════════════════════════════════
        lines.append("├─ Line Status ──────────────────────────────┤\x1b[K")
        lines.append(f"│ Active config: {self._format_config():24s} │\x1b[K")
        lines.append(
            f"│ Sim time: {self.state.simulation_time/3600:7.1f}h "
            f"({self.state.simulation_time/86400:5.1f} days)    │\x1b[K"
        )
        
        # ═══════════════════════════════════════════════════════════
        # SECTION: Heaters
        # ═══════════════════════════════════════════════════════════
        lines.append("├─ Heaters ──────────────────────────────────┤\x1b[K")
        lines.append(f"│ C1: {self._format_heaters(Line.C1):37s} │\x1b[K")
        lines.append(f"│ C2: {self._format_heaters(Line.C2):37s} │\x1b[K")
        
        # ═══════════════════════════════════════════════════════════
        # SECTION: Recent Events (last 4, with timestamps)
        # ═══════════════════════════════════════════════════════════
        lines.append("├─ Recent Events ────────────────────────────┤\x1b[K")
        
        # Always show last 4 events (or empty lines if fewer)
        num_events = len(self.recent_events)
        start_idx = max(0, num_events - 4)
        
        for i in range(4):
            event_idx = start_idx + i
            if event_idx < num_events:
                event_text = self.recent_events[event_idx]
            else:
                event_text = ""
            
            # Truncate if too long (max 42 chars to fit in box)
            if len(event_text) > 42:
                event_text = event_text[:39] + "..."
            
            lines.append(f"│ {event_text:42s} │\x1b[K")
        
        # ═══════════════════════════════════════════════════════════
        # SECTION: Scenario Distribution
        # ═══════════════════════════════════════════════════════════
        lines.append("├─ Scenario Distribution ────────────────────┤\x1b[K")
        
        # Get scenario times and format them
        scenario_lines = self._format_scenario_distribution()
        for line in scenario_lines:
            lines.append(f"│ {line:42s} │\x1b[K")
        
        lines.append("└────────────────────────────────────────────┘\x1b[K")
        
        # Clear any remaining lines below (in case terminal is taller)
        for _ in range(5):
            lines.append("\x1b[K")
        
        # Print all at once (reduces flicker)
        print("\n".join(lines), flush=True)
    
    def _format_scenario(self, scenario: Scenario) -> str:
        """Format scenario with color if supported."""
        # Color coding (optional - ANSI color codes)
        # S0: green, S1-S4: yellow, S5-S8: red
        if scenario == Scenario.S0:
            return f"\x1b[32m{scenario.name}\x1b[0m"  # Green
        elif scenario in (Scenario.S1, Scenario.S2, Scenario.S3, Scenario.S4):
            return f"\x1b[33m{scenario.name}\x1b[0m"  # Yellow
        else:  # S5-S8
            return f"\x1b[31m{scenario.name}\x1b[0m"  # Red
    
    def _format_locks(self) -> str:
        """Format lock status."""
        locks = []
        if self.state.config_change_in_progress:
            locks.append("RC")
        if self.state.heater_rotation_in_progress:
            locks.append("RN")
        
        return ", ".join(locks) if locks else "none"
    
    def _format_config(self) -> str:
        """Format current configuration."""
        if self.state.current_config == "Primary":
            return "C1 (Primary)"
        else:
            return "C2 (Limited)"
    
    def _format_heaters(self, line: Line) -> str:
        """
        Format heater status for a line.
        
        Shows heater state with symbols:
        - ✔ (green) = active
        - ✖ (gray) = idle
        - ✗ (red) = faulty
        
        Args:
            line: Which line to format (C1 or C2)
            
        Returns:
            Formatted string like "N1✔ N2✔ N3✖ N4✖"
        """
        # Heater mapping
        if line == Line.C1:
            heaters = [Heater.N1, Heater.N2, Heater.N3, Heater.N4]
        else:  # Line.C2
            heaters = [Heater.N5, Heater.N6, Heater.N7, Heater.N8]
        
        parts = []
        for heater in heaters:
            state = self.algorithm_rn.get_heater_state(heater)
            
            if state.value == "active":
                # Green checkmark
                symbol = f"\x1b[32m✔\x1b[0m"
            elif state.value == "idle":
                # Gray X
                symbol = f"\x1b[90m✖\x1b[0m"
            else:  # faulty
                # Red X
                symbol = f"\x1b[31m✗\x1b[0m"
            
            parts.append(f"{heater.name}{symbol}")
        
        return " ".join(parts)
    
    def _format_scenario_distribution(self) -> list[str]:
        """
        Format scenario time distribution for display.
        
        Shows only scenarios with time > 0, in compact format.
        Max 2 scenarios per line to fit in 42 chars.
        
        Returns:
            List of formatted lines (each max 42 chars)
        """
        # Update scenario times to capture current state
        self.algorithm_ws._update_scenario_time()
        
        # Get all scenario times
        scenario_times = self.algorithm_ws.get_all_scenario_times()
        total_time = self.state.simulation_time
        
        # Filter to only scenarios with time > 0, and format them
        entries = []
        for scenario in Scenario:
            time_s = scenario_times.get(scenario, 0.0)
            if time_s > 0.1:  # Skip negligible times
                time_h = time_s / 3600
                percentage = (time_s / total_time * 100) if total_time > 0 else 0
                # Format: "S3: 45.6h (55%)"
                entry = f"{scenario.name}: {time_h:4.1f}h ({percentage:2.0f}%)"
                entries.append(entry)
        
        # If no scenarios yet, show placeholder
        if not entries:
            return ["No scenario time yet"]
        
        # Pack entries into lines (2 per line, separated by spacing)
        lines = []
        for i in range(0, len(entries), 2):
            if i + 1 < len(entries):
                # Two entries per line, left-aligned with spacing
                left = entries[i]
                right = entries[i + 1]
                # Each entry is ~18 chars, total 42 with spacing
                line = f"{left:20s} {right}"
            else:
                # Single entry (odd number of entries)
                line = entries[i]
            
            lines.append(line)
        
        return lines

