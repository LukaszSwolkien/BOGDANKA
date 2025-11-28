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

    # Display box dimensions
    CONTENT_WIDTH = 59  # Width of content area (excluding padding and borders)
    PADDING = 2  # Padding on each side
    # Total box width = 1 (│) + PADDING + CONTENT_WIDTH + PADDING + 1 (│)
    TOTAL_WIDTH = 1 + PADDING + CONTENT_WIDTH + PADDING + 1  # = 61 chars

    def __init__(
        self,
        state: AlgoState,
        algorithm_rn: AlgorithmRN,
        algorithm_ws,  # Type hint would be circular, so kept as Any
        algorithm_rc,  # Type hint would be circular, so kept as Any
        recent_ws_events: list[str],
        recent_rc_events: list[str],
        recent_rn_events: list[str],
        enabled: bool = True,
        output_stream=None,  # Allow injecting output stream (for test runner compatibility)
        acceleration: float = 1.0,  # Simulation acceleration factor
        duration_seconds: float = 0.0,  # Total simulation duration in seconds
        test_profile_description: str | None = None,  # Test profile description (if running from test runner)
    ):
        """
        Initialize display.

        Args:
            state: Global algorithm state (read-only)
            algorithm_rn: RN algorithm for heater states (read-only)
            algorithm_ws: WS algorithm for scenario time stats (read-only)
            algorithm_rc: RC algorithm for config rotation stats (read-only)
            recent_ws_events: List of recent WS events (last 4, managed externally)
            recent_rc_events: List of recent RC events (last 4, managed externally)
            recent_rn_events: List of recent RN events (last 4, managed externally)
            enabled: Enable/disable display (can disable on Windows CMD)
            output_stream: Stream to write to (default: sys.stdout, can inject original stdout)
            acceleration: Simulation acceleration factor (e.g., 1000x)
            duration_seconds: Total simulation duration in seconds
            test_profile_description: Description of test profile (if running from test runner)
        """
        self.state = state
        self.algorithm_rn = algorithm_rn
        self.algorithm_ws = algorithm_ws
        self.algorithm_rc = algorithm_rc
        self.recent_ws_events = recent_ws_events  # Reference to external list
        self.recent_rc_events = recent_rc_events  # Reference to external list
        self.recent_rn_events = recent_rn_events  # Reference to external list

        # Output stream (allow injection for test runner)
        self.output_stream = output_stream if output_stream is not None else sys.stdout

        # Simulation parameters
        self.acceleration = acceleration
        self.duration_seconds = duration_seconds
        self.test_profile_description = test_profile_description

        # Auto-detect terminal support if not explicitly disabled
        if enabled is None:
            # Disable on Windows CMD, enable on Unix/WSL
            self.enabled = sys.stdout.isatty() and sys.platform != "win32"
        else:
            self.enabled = enabled

        # Track if we've rendered at least once (for smooth scrolling)
        self._first_render = True

    def _make_header(self, title: str, top: bool = False, bottom: bool = False) -> str:
        """
        Create a box header line with title.
        
        Args:
            title: Section title (e.g., "Scenariusz & Tryb")
            top: True for top border (┌), False for middle (├)
            bottom: True for bottom border (└)
            
        Returns:
            Formatted header line of exactly TOTAL_WIDTH characters
        """
        if bottom:
            # Bottom border: "└─────────────┘"
            left = "└"
            right = "┘"
            dashes_needed = self.TOTAL_WIDTH - len(left) - len(right)
            return f"{left}{'─' * dashes_needed}{right}\x1b[K"
        
        # Calculate how many '─' characters we need
        # Format: "├─ TITLE ─...─┤"
        # Left side: "├─ " = 3 chars
        # Title: len(title)
        # Right side: " ─...─┤" = need to fill to TOTAL_WIDTH
        
        if top:
            left = "┌─ "
            right = "┐"
        else:
            left = "├─ "
            right = "┤"
        
        # Calculate padding needed
        # total_width - left - title - space - right = dashes needed
        dashes_needed = self.TOTAL_WIDTH - len(left) - len(title) - 1 - len(right)
        
        return f"{left}{title} {'─' * dashes_needed}{right}\x1b[K"

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
        # HEADER: Scenariusz & Tryb
        # ═══════════════════════════════════════════════════════════
        lines.append(self._make_header("Symulacja", top=True))

        # Test profile description (if running from test runner)
        if self.test_profile_description:
            content = f"{self.test_profile_description}"
            # Truncate if too long
            if len(content) > self.CONTENT_WIDTH:
                content = content[:self.CONTENT_WIDTH - 3] + "..."
            lines.append(f"│  {content:{self.CONTENT_WIDTH}s}  │\x1b[K")

        # Scenario has ANSI color codes, so we need special handling
        import re
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        
        scenario_str = self._format_scenario(self.state.current_scenario)
        content = f"Scenariusz: {scenario_str}     T_zewn: {temperature_c:6.1f}°C"
        visible_content = ansi_escape.sub('', content)
        padding_needed = self.CONTENT_WIDTH - len(visible_content)
        lines.append(f"│  {content}{' ' * padding_needed}  │\x1b[K")
        
        # Tryb line (no ANSI codes)
        content = f"Tryb: {self.state.mode:6s}"
        lines.append(f"│  {content:{self.CONTENT_WIDTH}s}  │\x1b[K")
        
        # RC rotation period (in hours)
        rc_period_h = self.algorithm_rc.config.rotation_period_hours
        content = f"Rotacja RC (ciągi): {rc_period_h}h"
        lines.append(f"│  {content:{self.CONTENT_WIDTH}s}  │\x1b[K")
        
        # RN rotation period (in hours, same for all scenarios)
        rn_period_h = self.algorithm_rn.config.rotation_period_hours
        content = f"Rotacja RN (nagrzewnice): {rn_period_h}h"
        lines.append(f"│  {content:{self.CONTENT_WIDTH}s}  │\x1b[K")

        # Simulation time (moved from Line Status)
        sim_hours = self.state.simulation_time / 3600
        sim_days = self.state.simulation_time / 86400
        
        # Format with total duration if available
        if self.duration_seconds > 0:
            total_days = self.duration_seconds / 86400
            content = f"Czas sym: {sim_hours:7.1f}h ({sim_days:5.1f}/{total_days:.0f} dni)"
            lines.append(f"│  {content:{self.CONTENT_WIDTH}s}  │\x1b[K")
        else:
            content = f"Czas sym: {sim_hours:7.1f}h ({sim_days:5.1f} dni)"
            lines.append(f"│  {content:{self.CONTENT_WIDTH}s}  │\x1b[K")

        # Acceleration with real-time duration for 1h, 24h, and total simulation
        real_time_for_1h = 3600 / self.acceleration  # seconds in real time
        real_time_for_24h = 86400 / self.acceleration  # seconds in real time for 1 day
        
        def format_duration(seconds: float) -> str:
            """Format duration in seconds to human-readable string."""
            if seconds < 60:
                return f"{seconds:.1f}s"
            elif seconds < 3600:
                return f"{seconds/60:.1f}m"
            else:
                return f"{seconds/3600:.1f}h"
        
        time_1h_str = format_duration(real_time_for_1h)
        time_24h_str = format_duration(real_time_for_24h)
        
        # If total duration is known, show total real time
        if self.duration_seconds > 0:
            sim_days = self.duration_seconds / 86400
            real_time_total_s = self.duration_seconds / self.acceleration
            total_time_str = format_duration(real_time_total_s)
            content = f"Akceleracja: {self.acceleration:.0f}x  (1h={time_1h_str}, 24h={time_24h_str}, {sim_days:.0f}d={total_time_str})"
        else:
            content = f"Akceleracja: {self.acceleration:.0f}x  (1h={time_1h_str}, 24h={time_24h_str})"
        
        lines.append(f"│  {content:{self.CONTENT_WIDTH}s}  │\x1b[K")

        # ETA (if duration is known)
        if self.duration_seconds > 0:
            remaining_sim_s = self.duration_seconds - self.state.simulation_time
            if remaining_sim_s > 0:
                remaining_real_s = remaining_sim_s / self.acceleration
                if remaining_real_s < 60:
                    eta_str = f"{remaining_real_s:.0f}s"
                elif remaining_real_s < 3600:
                    eta_str = f"{remaining_real_s/60:.1f}m"
                else:
                    eta_str = f"{remaining_real_s/3600:.1f}h"
                progress_pct = (
                    self.state.simulation_time / self.duration_seconds
                ) * 100
                
                # Calculate completion time (current time + remaining real seconds)
                import datetime
                completion_time = datetime.datetime.now() + datetime.timedelta(seconds=remaining_real_s)
                completion_str = completion_time.strftime("%H:%M")
                
                content = f"ETA: {eta_str:>8s}  Postęp: {progress_pct:5.1f}%  Koniec: ~{completion_str}"
                lines.append(f"│  {content:{self.CONTENT_WIDTH}s}  │\x1b[K")
            else:
                content = "ETA: Zakończono"
                lines.append(f"│  {content:{self.CONTENT_WIDTH}s}  │\x1b[K")

        # Scenario distribution (moved from separate section)
        scenario_lines = self._format_scenario_distribution()
        for line in scenario_lines:
            lines.append(f"│  {line:{self.CONTENT_WIDTH}s}  │\x1b[K")
        
        # Empty line at end of section
        lines.append(f"│  {'':{self.CONTENT_WIDTH}s}  │\x1b[K")

        # ═══════════════════════════════════════════════════════════
        # SECTION: Status Ciągów
        # ═══════════════════════════════════════════════════════════
        lines.append(self._make_header("Status Ciągów"))
        
        # Check if lines are operating using algorithm's logic
        c1_operating = self.algorithm_rn.is_line_operating(Line.C1)
        c2_operating = self.algorithm_rn.is_line_operating(Line.C2)
        
        # Format status strings
        c1_status = "C1 (Podstawowy)"
        c2_status = "C2 (Ograniczony)" if self.state.current_config == "Limited" else "C2 (Podstawowy)"
        
        # Add active markers
        if c1_operating:
            c1_status = f"{c1_status}  ← aktywny"
        if c2_operating:
            c2_status = f"{c2_status}  ← aktywny"
        
        lines.append(f"│  {c1_status:{self.CONTENT_WIDTH}s}  │\x1b[K")
        lines.append(f"│  {c2_status:{self.CONTENT_WIDTH}s}  │\x1b[K")
        
        # Empty line at end of section
        lines.append(f"│  {'':{self.CONTENT_WIDTH}s}  │\x1b[K")

        # ═══════════════════════════════════════════════════════════
        # SECTION: Nagrzewnice
        # ═══════════════════════════════════════════════════════════
        lines.append(self._make_header("Nagrzewnice"))
        
        # Heaters have ANSI color codes, so we need special handling
        heaters_c1 = self._format_heaters(Line.C1)
        content = f"C1: {heaters_c1}"
        # Calculate visible length (ANSI codes don't count)
        visible_len = len(content.encode().decode('unicode-escape'))
        # Actually, simpler: count only printable chars
        import re
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        visible_content = ansi_escape.sub('', content)
        padding_needed = self.CONTENT_WIDTH - len(visible_content)
        lines.append(f"│  {content}{' ' * padding_needed}  │\x1b[K")
        
        heaters_c2 = self._format_heaters(Line.C2)
        content = f"C2: {heaters_c2}"
        visible_content = ansi_escape.sub('', content)
        padding_needed = self.CONTENT_WIDTH - len(visible_content)
        lines.append(f"│  {content}{' ' * padding_needed}  │\x1b[K")
        
        # Empty line at end of section
        lines.append(f"│  {'':{self.CONTENT_WIDTH}s}  │\x1b[K")

        # ═══════════════════════════════════════════════════════════
        # SECTION: Statystyki Nagrzewnic (moved here, right after Heaters)
        # ═══════════════════════════════════════════════════════════
        lines.append(self._make_header("Statystyki Nagrzewnic"))

        # Get heater stats and format them
        heater_lines = self._format_heater_statistics()
        for line in heater_lines:
            lines.append(f"│  {line:{self.CONTENT_WIDTH}s}  │\x1b[K")
        
        # Empty line at end of section
        lines.append(f"│  {'':{self.CONTENT_WIDTH}s}  │\x1b[K")

        # ═══════════════════════════════════════════════════════════
        # SECTION: Ostatnie Zdarzenia WS (scenario changes)
        # ═══════════════════════════════════════════════════════════
        lines.append(self._make_header("Ostatnie Zdarzenia WS"))

        # Always show last 4 WS events (or empty lines if fewer)
        num_ws_events = len(self.recent_ws_events)
        start_idx_ws = max(0, num_ws_events - 4)

        for i in range(4):
            event_idx = start_idx_ws + i
            if event_idx < num_ws_events:
                event_text = self.recent_ws_events[event_idx]
            else:
                event_text = ""

            # Truncate if too long (max CONTENT_WIDTH chars to fit in box)
            if len(event_text) > self.CONTENT_WIDTH:
                event_text = event_text[:self.CONTENT_WIDTH - 3] + "..."

            lines.append(f"│  {event_text:{self.CONTENT_WIDTH}s}  │\x1b[K")
        
        # Empty line at end of section
        lines.append(f"│  {'':{self.CONTENT_WIDTH}s}  │\x1b[K")

        # ═══════════════════════════════════════════════════════════
        # SECTION: Ostatnie Zdarzenia RC (configuration changes)
        # ═══════════════════════════════════════════════════════════
        lines.append(self._make_header("Ostatnie Zdarzenia RC"))

        # Show last 8 RC events in 2 columns (4 rows × 2 columns)
        num_rc_events = len(self.recent_rc_events)
        start_idx_rc = max(0, num_rc_events - 8)
        
        # Column width: (59 - 1 separator) / 2 = 29 chars per column
        col_width = 29

        for row in range(4):
            # Left column: events 0-3 (oldest to newer)
            left_idx = start_idx_rc + row
            if left_idx < num_rc_events:
                left_text = self.recent_rc_events[left_idx]
                # Truncate if too long
                if len(left_text) > col_width:
                    left_text = left_text[:col_width - 3] + "..."
            else:
                left_text = ""
            
            # Right column: events 4-7 (newer to newest)
            right_idx = start_idx_rc + row + 4
            if right_idx < num_rc_events:
                right_text = self.recent_rc_events[right_idx]
                # Truncate if too long
                if len(right_text) > col_width:
                    right_text = right_text[:col_width - 3] + "..."
            else:
                right_text = ""
            
            # Format: "LEFT_TEXT | RIGHT_TEXT" with proper padding
            line_content = f"{left_text:<{col_width}s} {right_text:<{col_width}s}"
            lines.append(f"│  {line_content}  │\x1b[K")
        
        # Empty line at end of section
        lines.append(f"│  {'':{self.CONTENT_WIDTH}s}  │\x1b[K")

        # ═══════════════════════════════════════════════════════════
        # SECTION: Ostatnie Zdarzenia RN (heater rotations)
        # ═══════════════════════════════════════════════════════════
        lines.append(self._make_header("Ostatnie Zdarzenia RN"))

        # Show last 8 RN events in 2 columns (4 rows × 2 columns)
        num_rn_events = len(self.recent_rn_events)
        start_idx_rn = max(0, num_rn_events - 8)
        
        # Column width: (59 - 1 separator) / 2 = 29 chars per column
        col_width = 29

        for row in range(4):
            # Left column: events 0-3 (oldest to newer)
            left_idx = start_idx_rn + row
            if left_idx < num_rn_events:
                left_text = self.recent_rn_events[left_idx]
                # Truncate if too long
                if len(left_text) > col_width:
                    left_text = left_text[:col_width - 3] + "..."
            else:
                left_text = ""
            
            # Right column: events 4-7 (newer to newest)
            right_idx = start_idx_rn + row + 4
            if right_idx < num_rn_events:
                right_text = self.recent_rn_events[right_idx]
                # Truncate if too long
                if len(right_text) > col_width:
                    right_text = right_text[:col_width - 3] + "..."
            else:
                right_text = ""
            
            # Format: "LEFT_TEXT | RIGHT_TEXT" with proper padding
            line_content = f"{left_text:<{col_width}s} {right_text:<{col_width}s}"
            lines.append(f"│  {line_content}  │\x1b[K")
        
        # Empty line at end of section
        lines.append(f"│  {'':{self.CONTENT_WIDTH}s}  │\x1b[K")

        # ═══════════════════════════════════════════════════════════
        # SECTION: Następne rotacje i blokady
        # ═══════════════════════════════════════════════════════════
        lines.append(self._make_header("Następne rotacje i blokady"))

        # Get lock stats and format them
        lock_lines = self._format_lock_statistics()
        for line in lock_lines:
            lines.append(f"│  {line:{self.CONTENT_WIDTH}s}  │\x1b[K")
        
        # Empty line at end of section
        lines.append(f"│  {'':{self.CONTENT_WIDTH}s}  │\x1b[K")

        lines.append(self._make_header("", bottom=True))

        # Clear any remaining lines below (in case terminal is taller)
        for _ in range(5):
            lines.append("\x1b[K")

        # Print all at once (reduces flicker) - use injected output stream
        print("\n".join(lines), flush=True, file=self.output_stream)

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

        return ", ".join(locks) if locks else "brak"

    def _format_config(self) -> str:
        """Format current configuration."""
        if self.state.current_config == "Primary":
            return "C1 (Podstawowy)"
        else:
            return "C2 (Ograniczony)"

    def _format_heaters(self, line: Line) -> str:
        """
        Format heater status for a line.

        Shows heater state with symbols:
        - ✔ (green) = aktywna
        - ✖ (gray) = bezczynna
        - ✗ (red) = awaria

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
        Max 2 scenarios per line to fit in CONTENT_WIDTH chars.

        Returns:
            List of formatted lines (each max CONTENT_WIDTH chars)
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
            return ["Brak danych o scenariuszach"]

        # Pack entries into lines (2 per line, separated by spacing)
        lines = []
        for i in range(0, len(entries), 2):
            if i + 1 < len(entries):
                # Two entries per line, left-aligned with spacing
                left = entries[i]
                right = entries[i + 1]
                # Each entry is ~18 chars, add spacing for 53 total
                line = f"{left:23s} {right}"
            else:
                # Single entry (odd number of entries)
                line = entries[i]

            lines.append(line)

        return lines

    def _format_heater_statistics(self) -> list[str]:
        """
        Format heater operating time statistics for display.

        Shows:
        - Total RC rotations (line changes)
        - Total RN rotations (heater rotations)
        - Each heater's operating time (hours) and percentage, grouped by line (C1/C2)

        Format: heaters per line (C1: ..., C2: ...)

        Returns:
            List of formatted lines (each max CONTENT_WIDTH chars)
        """
        from common.domain import Heater

        # Get rotation counts
        rc_rotation_count = self.algorithm_rc.get_rotation_count()
        rn_rotation_count = self.algorithm_rn.get_rotation_count()

        # Calculate total operating time across all heaters
        total_op_time = sum(
            self.algorithm_rn.get_heater_operating_time(h) for h in Heater
        )

        # First line: rotation counts (both RC and RN)
        lines = [f"Rotacje RC: {rc_rotation_count}  RN: {rn_rotation_count}"]

        # C1 heaters (N1-N4)
        c1_heaters = [Heater.N1, Heater.N2, Heater.N3, Heater.N4]
        c1_entries = []
        for heater in c1_heaters:
            op_time_s = self.algorithm_rn.get_heater_operating_time(heater)
            op_time_h = op_time_s / 3600
            percentage = (op_time_s / total_op_time * 100) if total_op_time > 0 else 0
            # Format: "N1:12.3h(25%)" - compact, ~13 chars
            entry = f"{heater.name}:{op_time_h:4.1f}h({percentage:2.0f}%)"
            c1_entries.append(entry)
        
        # Format C1 line
        c1_line = " ".join(c1_entries)
        lines.append(c1_line)

        # C2 heaters (N5-N8)
        c2_heaters = [Heater.N5, Heater.N6, Heater.N7, Heater.N8]
        c2_entries = []
        for heater in c2_heaters:
            op_time_s = self.algorithm_rn.get_heater_operating_time(heater)
            op_time_h = op_time_s / 3600
            percentage = (op_time_s / total_op_time * 100) if total_op_time > 0 else 0
            # Format: "N5:12.3h(25%)" - compact, ~13 chars
            entry = f"{heater.name}:{op_time_h:4.1f}h({percentage:2.0f}%)"
            c2_entries.append(entry)
        
        # Format C2 line
        c2_line = " ".join(c2_entries)
        lines.append(c2_line)

        return lines

    def _format_lock_statistics(self) -> list[str]:
        """
        Format rotation lock statistics and timers for display.

        Shows:
        - Active locks (RC/RN in progress)
        - Time to next RC rotation
        - Time to next RN rotation (for C1 and C2)

        Returns:
            List of formatted lines (each max CONTENT_WIDTH chars)
        """
        from common.domain import Line

        # Get active locks status
        active_locks_str = self._format_locks()

        # Get time to next rotations
        rc_time_remaining = self.algorithm_rc.get_time_to_next_rotation()
        rn_time_remaining = self.algorithm_rn.get_time_to_next_rotation()

        # Format times (convert to hours and minutes)
        def format_time(seconds: float) -> str:
            """Format seconds as 'Xh Ym', 'gotowe', or 'N/A'."""
            if seconds < 0:
                return "N/A"  # Not applicable in current scenario
            if seconds == 0:
                return "gotowe"
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"

        rc_timer = format_time(rc_time_remaining)
        rn_c1_timer = format_time(rn_time_remaining[Line.C1])
        rn_c2_timer = format_time(rn_time_remaining[Line.C2])

        # Get collision statistics (only inter-algorithm blocking)
        rc_blocked_by_reason = self.algorithm_rc.get_blocked_by_reason()
        rn_blocked_by_reason = self.algorithm_rn.get_blocked_by_reason()
        
        # Collisions: Direct mutual blocking during rotation
        rc_collisions = rc_blocked_by_reason.get("rn_rotation_in_progress", 0)  # RC blocked by RN
        rn_collisions = rn_blocked_by_reason.get("rc_rotation_in_progress", 0)  # RN blocked by RC
        total_collisions = rc_collisions + rn_collisions
        
        # Coordination blocks: Post-rotation waiting period
        rn_too_soon = rn_blocked_by_reason.get("too_soon_after_rc", 0)  # RN waiting after RC
        
        # Other blocks (not inter-algorithm)
        rc_other_blocks = self.algorithm_rc.get_blocked_count() - rc_collisions
        rn_other_blocks = self.algorithm_rn.get_blocked_count() - rn_collisions - rn_too_soon

        lines = [
            f"Następna rotacja ciągów (RC): {rc_timer}",
            f"Następna rotacja nagrzewnic (RN):",
            f"  C1:{rn_c1_timer:12s}",
            f"  C2:{rn_c2_timer:12s}",
            f"Wszystkie kolizje RC↔RN: {total_collisions}",
            f"RN czekal 1h po RC: {rn_too_soon}",
        ]

        return lines


