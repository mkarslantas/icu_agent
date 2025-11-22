#!/usr/bin/env python
"""
ICU Agent Live Monitor

Real-time monitoring dashboard for the ICU monitoring system.
Displays system status, processing queue, and recent activity.
"""

import time
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

from agents.orchestrator import MainOrchestrator, BatchProcessor
from agents.base.state import StateManager


console = Console()


class ICUMonitor:
    """
    Real-time ICU monitoring dashboard.

    Features:
    - System health status
    - Active patients list
    - Processing queue
    - Recent activity log
    - Critical alerts
    - Auto-refresh
    """

    def __init__(self):
        """Initialize the monitor."""
        self.main_orch = MainOrchestrator()
        self.batch_processor = BatchProcessor()
        self.activity_log = []
        self.max_log_entries = 10

    def generate_layout(self) -> Layout:
        """
        Generate the dashboard layout.

        Returns:
            Rich Layout object with all panels
        """
        layout = Layout()

        # Create layout structure
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )

        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )

        layout["left"].split_column(
            Layout(name="status", size=12),
            Layout(name="patients")
        )

        layout["right"].split_column(
            Layout(name="activity", size=15),
            Layout(name="alerts")
        )

        # Populate panels
        layout["header"].update(self._create_header())
        layout["status"].update(self._create_status_panel())
        layout["patients"].update(self._create_patients_panel())
        layout["activity"].update(self._create_activity_panel())
        layout["alerts"].update(self._create_alerts_panel())
        layout["footer"].update(self._create_footer())

        return layout

    def _create_header(self) -> Panel:
        """Create header panel."""
        title = Text("🏥 ICU MONITORING SYSTEM - LIVE DASHBOARD", style="bold cyan", justify="center")
        return Panel(title, border_style="cyan")

    def _create_status_panel(self) -> Panel:
        """Create system status panel."""
        status = self.main_orch.get_system_status()
        metrics = status.get("metrics", {})
        health = status.get("health", "unknown")

        # Health indicator
        if health == "healthy":
            health_display = "[green]✓ HEALTHY[/green]"
        elif health == "degraded":
            health_display = "[yellow]⚠ DEGRADED[/yellow]"
        else:
            health_display = "[red]✗ UNHEALTHY[/red]"

        # Create status table
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="bold white")

        table.add_row("System Health:", health_display)
        table.add_row("Patients Processed:", str(metrics.get("patients_processed", 0)))
        table.add_row("Success Rate:", f"{metrics.get('success_rate', 0):.1f}%")
        table.add_row("Avg Processing Time:", f"{metrics.get('average_processing_time', 0):.2f}s")
        table.add_row("Critical Alerts:", f"[red]{metrics.get('critical_alerts_total', 0)}[/red]")

        return Panel(table, title="System Status", border_style="green")

    def _create_patients_panel(self) -> Panel:
        """Create active patients panel."""
        # Get patients
        active_patients = self.batch_processor.get_active_patients()
        patients_with_notes = self.batch_processor.get_patients_with_notes_today()

        # Create table
        table = Table(show_header=True, box=None)
        table.add_column("Patient ID", style="cyan")
        table.add_column("Status", style="bold")

        # Add patients
        for patient_id in active_patients[:10]:  # Limit to 10
            if patient_id in patients_with_notes:
                status = "[green]● Ready[/green]"
            else:
                status = "[dim]○ No note today[/dim]"

            table.add_row(patient_id, status)

        if len(active_patients) > 10:
            table.add_row("[dim]...[/dim]", f"[dim]+{len(active_patients) - 10} more[/dim]")

        summary_text = f"Active: {len(active_patients)} | Ready: {len(patients_with_notes)}"

        return Panel(table, title=f"Patients ({summary_text})", border_style="blue")

    def _create_activity_panel(self) -> Panel:
        """Create recent activity panel."""
        # Create activity log
        if not self.activity_log:
            content = Text("No recent activity", style="dim")
        else:
            lines = []
            for entry in self.activity_log[-10:]:  # Last 10 entries
                timestamp = entry.get("timestamp", "")
                message = entry.get("message", "")
                status = entry.get("status", "info")

                if status == "success":
                    icon = "[green]✓[/green]"
                elif status == "error":
                    icon = "[red]✗[/red]"
                elif status == "warning":
                    icon = "[yellow]⚠[/yellow]"
                else:
                    icon = "[cyan]•[/cyan]"

                lines.append(f"{icon} {timestamp} {message}")

            content = "\n".join(lines)

        return Panel(content, title="Recent Activity", border_style="yellow")

    def _create_alerts_panel(self) -> Panel:
        """Create critical alerts panel."""
        # Try to find recent critical alerts from state files
        alerts_found = []

        try:
            # Scan recent state files for critical alerts
            state_base = Path("state")
            if state_base.exists():
                for patient_dir in state_base.iterdir():
                    if not patient_dir.is_dir():
                        continue

                    # Check most recent date
                    date_dirs = sorted(patient_dir.iterdir(), reverse=True)
                    if date_dirs:
                        recent_dir = date_dirs[0]
                        critical_file = recent_dir / "05_critical.md"

                        if critical_file.exists():
                            # Load and check for life-threatening values
                            import json
                            import re

                            with open(critical_file, 'r', encoding='utf-8') as f:
                                content = f.read()

                            # Try to extract JSON
                            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                            if json_match:
                                data = json.loads(json_match.group(1))
                                analysis = data.get("critical_analysis", {})
                                life_threatening = analysis.get("life_threatening", [])

                                if life_threatening:
                                    alerts_found.extend([
                                        {
                                            "patient_id": patient_dir.name,
                                            "date": recent_dir.name,
                                            "values": life_threatening
                                        }
                                    ])
        except Exception:
            pass

        # Display alerts
        if not alerts_found:
            content = Text("No critical alerts", style="green")
        else:
            lines = []
            for alert in alerts_found[:5]:  # Max 5 alerts
                patient = alert["patient_id"]
                date = alert["date"]
                count = len(alert["values"])

                lines.append(f"[red bold]🚨 {patient}[/red bold] ({date})")
                for value in alert["values"][:2]:  # Max 2 values per patient
                    param = value.get("parameter", "Unknown")
                    val = value.get("value", "?")
                    lines.append(f"   • {param}: {val}")

            content = "\n".join(lines)

        return Panel(content, title="Critical Alerts", border_style="red")

    def _create_footer(self) -> Panel:
        """Create footer panel."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        footer_text = Text(
            f"Last Updated: {current_time} | Press Ctrl+C to exit",
            style="dim",
            justify="center"
        )
        return Panel(footer_text, border_style="cyan")

    def add_activity(self, message: str, status: str = "info"):
        """
        Add an entry to the activity log.

        Args:
            message: Activity message
            status: Status type (success, error, warning, info)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.activity_log.append({
            "timestamp": timestamp,
            "message": message,
            "status": status
        })

        # Keep only recent entries
        if len(self.activity_log) > self.max_log_entries:
            self.activity_log = self.activity_log[-self.max_log_entries:]

    def run(self, refresh_interval: int = 5):
        """
        Run the live monitoring dashboard.

        Args:
            refresh_interval: Refresh interval in seconds
        """
        console.print("[cyan]Starting ICU Monitor...[/cyan]")
        self.add_activity("Monitor started", "success")

        try:
            with Live(
                self.generate_layout(),
                console=console,
                screen=True,
                refresh_per_second=1
            ) as live:
                while True:
                    time.sleep(refresh_interval)

                    # Update layout
                    live.update(self.generate_layout())

        except KeyboardInterrupt:
            console.print("\n[cyan]Monitor stopped[/cyan]")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="ICU Agent Live Monitor")
    parser.add_argument(
        "--interval",
        "-i",
        type=int,
        default=5,
        help="Refresh interval in seconds (default: 5)"
    )

    args = parser.parse_args()

    # Create and run monitor
    monitor = ICUMonitor()
    monitor.run(refresh_interval=args.interval)


if __name__ == "__main__":
    main()
