#!/usr/bin/env python
"""
ICU Agent CLI

Main command-line interface for the ICU monitoring system.
Provides commands for processing patients, viewing reports, and monitoring.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.syntax import Syntax
from rich.markdown import Markdown

from agents.orchestrator import PatientOrchestrator, MainOrchestrator, BatchProcessor

# Setup console
console = Console()

# Setup logging
def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/icu-agent.log'),
            logging.StreamHandler() if verbose else logging.NullHandler()
        ]
    )


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.version_option(version='1.0.0')
def cli(verbose):
    """
    ICU Agent - Multi-Agent System for ICU Patient Monitoring

    Process Turkish clinical notes, analyze patient data, and generate
    comprehensive daily reports with AI-powered analysis.
    """
    # Ensure logs directory exists
    Path('logs').mkdir(exist_ok=True)
    setup_logging(verbose)


@cli.command()
@click.option('--patient-id', '-p', required=True, help='Patient ID (e.g., HT001)')
@click.option('--date', '-d', help='Date in YYYY-MM-DD format (default: today)')
@click.option('--note-path', '-n', help='Path to clinical note file')
@click.option('--show-report', '-r', is_flag=True, help='Display report after processing')
def process_patient(patient_id, date, note_path, show_report):
    """
    Process a single patient's clinical data.

    Examples:

      icu-agent process-patient -p HT001

      icu-agent process-patient -p HT001 -d 2025-11-20

      icu-agent process-patient -p HT001 -n /path/to/note.txt -r
    """
    # Use today's date if not specified
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    console.print(f"\n[bold cyan]Processing Patient: {patient_id}[/bold cyan]")
    console.print(f"Date: {date}\n")

    try:
        # Create orchestrator
        config = {}
        orchestrator = PatientOrchestrator(patient_id, date, config)

        # Run with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Processing workflow...", total=4)

            # Custom run with progress updates
            result = _run_with_progress(orchestrator, note_path, progress, task)

        # Display results
        if result["status"] == "success":
            console.print("\n[bold green]✓ Processing completed successfully![/bold green]\n")

            # Display summary
            _display_patient_summary(orchestrator, result)

            # Show report if requested
            if show_report:
                console.print("\n")
                _display_report(orchestrator)
        else:
            console.print(f"\n[bold red]✗ Processing failed: {result.get('error')}[/bold red]\n")
            sys.exit(1)

    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]\n")
        if logging.getLogger().level == logging.DEBUG:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.option('--all', 'process_all', is_flag=True, help='Process all patients with today\'s notes')
@click.option('--patients', '-p', help='Comma-separated list of patient IDs')
@click.option('--date', '-d', help='Date in YYYY-MM-DD format (default: today)')
@click.option('--priority', is_flag=True, help='Process critical patients first')
@click.option('--sequential', is_flag=True, help='Process sequentially (no parallel)')
def process_batch(process_all, patients, date, priority, sequential):
    """
    Process multiple patients in batch.

    Examples:

      icu-agent process-batch --all

      icu-agent process-batch --all --priority

      icu-agent process-batch -p HT001,HT002,HT003
    """
    # Use today's date if not specified
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    console.print(f"\n[bold cyan]Batch Processing[/bold cyan]")
    console.print(f"Date: {date}\n")

    try:
        # Create batch processor
        config = {
            'enable_parallel': not sequential,
        }
        batch_processor = BatchProcessor(config=config)

        # Determine which patients to process
        if process_all:
            console.print("Discovering patients with notes for today...")
            result = batch_processor.process_morning_round(date, priority=priority)
        elif patients:
            patient_list = [p.strip() for p in patients.split(',')]
            console.print(f"Processing {len(patient_list)} specified patients...")
            result = batch_processor.process_specific_patients(patient_list, date)
        else:
            console.print("[yellow]Please specify --all or --patients[/yellow]")
            sys.exit(1)

        # Display results
        _display_batch_results(result)

    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]\n")
        if logging.getLogger().level == logging.DEBUG:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.option('--patient-id', '-p', required=True, help='Patient ID')
@click.option('--date', '-d', help='Date in YYYY-MM-DD format (default: today)')
@click.option('--format', '-f', type=click.Choice(['markdown', 'plain']), default='markdown', help='Output format')
def report(patient_id, date, format):
    """
    Display a patient's report.

    Examples:

      icu-agent report -p HT001

      icu-agent report -p HT001 -d 2025-11-20
    """
    # Use today's date if not specified
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    try:
        # Create state manager to load report
        from agents.base.state import StateManager
        sm = StateManager(patient_id, date)

        # Load report
        report_state = sm.load("report")

        if not report_state:
            console.print(f"[yellow]No report found for {patient_id} on {date}[/yellow]")
            console.print("Run 'process-patient' first to generate the report.")
            sys.exit(1)

        # Extract report content (skip metadata header)
        lines = report_state.split('\n')
        report_start = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('# 🏥'):
                report_start = i
                break

        report_text = '\n'.join(lines[report_start:]) if report_start > 0 else report_state

        # Display based on format
        if format == 'markdown':
            md = Markdown(report_text)
            console.print(md)
        else:
            console.print(report_text)

    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]\n")
        sys.exit(1)


@cli.command()
@click.option('--reset', is_flag=True, help='Reset system metrics')
def stats(reset):
    """
    Show system statistics and health.

    Examples:

      icu-agent stats

      icu-agent stats --reset
    """
    try:
        # Create main orchestrator
        main_orch = MainOrchestrator()

        if reset:
            main_orch.reset_metrics()
            console.print("[green]✓ System metrics reset[/green]\n")
            return

        # Get system status
        status = main_orch.get_system_status()

        # Display status
        _display_system_status(status)

    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]\n")
        sys.exit(1)


@cli.command()
@click.option('--live', is_flag=True, help='Enable live monitoring (refreshes every 5s)')
def monitor(live):
    """
    Monitor system status and active patients.

    Examples:

      icu-agent monitor

      icu-agent monitor --live
    """
    if live:
        console.print("[yellow]Live monitoring not yet implemented[/yellow]")
        console.print("Use 'icu-agent stats' for current status")
    else:
        # Show current status
        try:
            batch_processor = BatchProcessor()

            # Get active patients
            active_patients = batch_processor.get_active_patients()
            patients_with_notes = batch_processor.get_patients_with_notes_today()

            console.print(f"\n[bold cyan]System Monitor[/bold cyan]\n")
            console.print(f"Active Patients: {len(active_patients)}")
            console.print(f"Patients with Today's Notes: {len(patients_with_notes)}\n")

            if patients_with_notes:
                console.print("[bold]Patients ready for processing:[/bold]")
                for pid in patients_with_notes:
                    console.print(f"  • {pid}")
            else:
                console.print("[yellow]No patients with notes for today[/yellow]")

        except Exception as e:
            console.print(f"\n[bold red]Error: {str(e)}[/bold red]\n")
            sys.exit(1)


# Helper functions

def _run_with_progress(orchestrator, note_path, progress, task):
    """Run orchestrator with progress updates."""
    progress.update(task, description="[cyan]Loading clinical note...")
    if not orchestrator.load_clinical_note(note_path):
        raise ValueError("Failed to load clinical note")
    progress.advance(task)

    progress.update(task, description="[cyan]Parsing Turkish clinical note...")
    parse_result = orchestrator.parse_supervisor.run()
    if parse_result.get("status") != "success":
        raise ValueError("Parse phase failed")
    progress.advance(task)

    progress.update(task, description="[cyan]Analyzing clinical data...")
    analysis_result = orchestrator.analysis_supervisor.run()
    progress.advance(task)

    progress.update(task, description="[cyan]Generating Turkish report...")
    report_result = orchestrator.report_supervisor.run()
    if report_result.get("status") != "success":
        raise ValueError("Report phase failed")
    progress.advance(task)

    orchestrator.state_manager.finalize()

    return {
        "status": "success",
        "patient_id": orchestrator.patient_id,
        "date": orchestrator.date,
    }


def _display_patient_summary(orchestrator, result):
    """Display patient processing summary."""
    # Get metrics
    sofa_score = orchestrator.get_sofa_score()
    critical_alerts = orchestrator.get_critical_alerts()
    requires_action = orchestrator.requires_immediate_action()
    report_path = orchestrator.get_report_path()

    # Create summary table
    table = Table(title="Processing Summary", show_header=False, box=None)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold")

    table.add_row("Patient ID", orchestrator.patient_id)
    table.add_row("Date", orchestrator.date)

    if sofa_score >= 0:
        sofa_color = "red" if sofa_score > 15 else "yellow" if sofa_score > 10 else "green"
        table.add_row("SOFA Score", f"[{sofa_color}]{sofa_score}/24[/{sofa_color}]")

    if critical_alerts:
        alert_text = f"[red]{len(critical_alerts)} critical value(s)[/red]"
        table.add_row("Critical Alerts", alert_text)
    else:
        table.add_row("Critical Alerts", "[green]None[/green]")

    if requires_action:
        table.add_row("Status", "[red bold]⚠️  IMMEDIATE ACTION REQUIRED[/red bold]")
    else:
        table.add_row("Status", "[green]✓ Stable[/green]")

    table.add_row("Report Path", report_path)

    console.print(table)


def _display_report(orchestrator):
    """Display patient report."""
    report_text = orchestrator.report_supervisor.get_report_text()

    if report_text:
        md = Markdown(report_text)
        console.print(Panel(md, title="📋 Patient Report", border_style="cyan"))
    else:
        console.print("[yellow]Report not available[/yellow]")


def _display_batch_results(result):
    """Display batch processing results."""
    summary = result.get("summary", {})

    # Summary panel
    summary_text = f"""
    [bold]Total Patients:[/bold] {summary.get('total', 0)}
    [bold green]Succeeded:[/bold green] {summary.get('succeeded', 0)} ✓
    [bold red]Failed:[/bold red] {summary.get('failed', 0)} ✗
    [bold]Success Rate:[/bold] {summary.get('success_rate', 0):.1f}%
    [bold]Average Time:[/bold] {summary.get('average_time', 0):.2f}s per patient
    """

    console.print(Panel(summary_text, title="Batch Summary", border_style="cyan"))

    # Individual results table
    if result.get("results"):
        table = Table(title="Individual Results")
        table.add_column("Patient ID", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Time", justify="right")

        for patient_result in result["results"]:
            patient_id = patient_result.get("patient_id", "Unknown")
            status = patient_result.get("status", "unknown")
            elapsed = patient_result.get("elapsed_time", 0)

            status_display = "[green]✓ Success[/green]" if status == "success" else "[red]✗ Failed[/red]"

            table.add_row(
                patient_id,
                status_display,
                f"{elapsed:.2f}s"
            )

        console.print("\n")
        console.print(table)

    # Summary file path
    if "summary_path" in summary:
        console.print(f"\n[dim]Summary saved to: {summary['summary_path']}[/dim]")


def _display_system_status(status):
    """Display system health status."""
    metrics = status.get("metrics", {})
    health = status.get("health", "unknown")

    # Health indicator
    health_color = "green" if health == "healthy" else "yellow" if health == "degraded" else "red"
    health_icon = "✓" if health == "healthy" else "⚠" if health == "degraded" else "✗"

    # Create status table
    table = Table(title="System Status", show_header=False, box=None)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold")

    table.add_row("Health", f"[{health_color}]{health_icon} {health.upper()}[/{health_color}]")
    table.add_row("Patients Processed", str(metrics.get("patients_processed", 0)))
    table.add_row("Success Rate", f"{metrics.get('success_rate', 0):.1f}%")
    table.add_row("Average Time", f"{metrics.get('average_processing_time', 0):.2f}s")
    table.add_row("Critical Alerts", str(metrics.get("critical_alerts_total", 0)))

    console.print("\n")
    console.print(table)
    console.print()


if __name__ == '__main__':
    cli()
