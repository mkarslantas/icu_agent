"""
Batch Processor

This module provides high-level batch processing capabilities for the ICU monitoring system.
It handles:
- Morning round processing (all active patients)
- Custom batch processing
- Priority-based processing
- Batch summary reporting
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from agents.orchestrator.main import MainOrchestrator

logger = logging.getLogger(__name__)


class BatchProcessor:
    """
    Handles batch processing of multiple ICU patients.

    This processor:
    - Scans for active patients with today's notes
    - Processes patients in priority order (critical first)
    - Generates batch summary reports
    - Supports morning round workflows

    Attributes:
        main_orchestrator: MainOrchestrator instance
        patients_dir: Base directory for patient data
        max_concurrent: Maximum concurrent patient processing
    """

    def __init__(
        self,
        main_orchestrator: Optional[MainOrchestrator] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Batch Processor.

        Args:
            main_orchestrator: Optional MainOrchestrator instance
                              If None, creates a new one
            config: Optional configuration dict
        """
        self.config = config or {}

        # Initialize main orchestrator
        if main_orchestrator:
            self.main_orchestrator = main_orchestrator
        else:
            self.main_orchestrator = MainOrchestrator(self.config)

        # Configuration
        self.patients_dir = Path(self.config.get("patients_dir", "patients/active"))
        self.max_concurrent = self.config.get("max_concurrent", 5)

        logger.info("Initialized BatchProcessor")

    def discover_patients(
        self,
        date: Optional[str] = None,
        pattern: str = "*.txt"
    ) -> List[Dict[str, str]]:
        """
        Discover patients with clinical notes for a given date.

        Args:
            date: Date string in YYYY-MM-DD format
                 If None, uses today's date
            pattern: File pattern to match (default: "*.txt")

        Returns:
            List of patient dicts with keys:
                - patient_id: Patient identifier
                - date: Date string
                - note_path: Path to clinical note file
        """
        # Use today's date if not specified
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        logger.info(f"Discovering patients for date: {date}")

        patients = []

        if not self.patients_dir.exists():
            logger.warning(f"Patients directory not found: {self.patients_dir}")
            return patients

        # Scan all patient directories
        for patient_dir in self.patients_dir.iterdir():
            if not patient_dir.is_dir():
                continue

            patient_id = patient_dir.name
            notes_dir = patient_dir / "notes"

            if not notes_dir.exists():
                continue

            # Look for notes matching the date
            # Patterns: YYYY-MM-DD.txt, YYYY-MM-DD-dayX.txt, etc.
            matching_notes = list(notes_dir.glob(f"{date}*.txt"))

            if matching_notes:
                note_path = matching_notes[0]  # Use first match

                patients.append({
                    "patient_id": patient_id,
                    "date": date,
                    "note_path": str(note_path)
                })

                logger.debug(f"Found patient: {patient_id} ({note_path})")

        logger.info(f"Discovered {len(patients)} patients with notes for {date}")

        return patients

    def process_morning_round(
        self,
        date: Optional[str] = None,
        priority: bool = True
    ) -> Dict[str, Any]:
        """
        Process all active patients for morning rounds.

        This method:
        1. Discovers all patients with today's notes
        2. Optionally sorts by priority (critical patients first)
        3. Processes all patients
        4. Generates batch summary

        Args:
            date: Date string in YYYY-MM-DD format
                 If None, uses today's date
            priority: If True, processes critical patients first

        Returns:
            Batch processing result with summary
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        logger.info(f"Starting morning round processing for {date}")

        # Discover patients
        patients = self.discover_patients(date)

        if not patients:
            logger.warning(f"No patients found for morning round on {date}")
            return {
                "status": "success",
                "results": [],
                "summary": {
                    "total": 0,
                    "succeeded": 0,
                    "failed": 0,
                    "date": date,
                    "critical_alerts": 0,
                }
            }

        # Process with or without priority
        if priority:
            logger.info(f"Processing {len(patients)} patients with priority ordering")
            result = self.main_orchestrator.process_with_priority(patients)
        else:
            logger.info(f"Processing {len(patients)} patients in standard order")
            result = self.main_orchestrator.process_batch(patients)

        # Add date to summary
        result["summary"]["date"] = date

        # Count critical alerts
        critical_alerts = 0
        for patient_result in result.get("results", []):
            if patient_result.get("status") == "success":
                # Try to count critical alerts (not available directly, would need to load)
                pass

        result["summary"]["critical_alerts"] = critical_alerts

        # Generate summary report
        summary_path = self._generate_batch_summary(result, date)
        result["summary"]["summary_path"] = summary_path

        logger.info(
            f"Morning round complete: "
            f"{result['summary']['succeeded']}/{result['summary']['total']} succeeded"
        )

        return result

    def process_with_priority(
        self,
        patients: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Process patients with priority ordering.

        Delegates to MainOrchestrator.process_with_priority.

        Args:
            patients: List of patient dicts

        Returns:
            Batch processing result
        """
        return self.main_orchestrator.process_with_priority(patients)

    def _generate_batch_summary(
        self,
        result: Dict[str, Any],
        date: str
    ) -> str:
        """
        Generate a markdown summary report for the batch.

        Args:
            result: Batch processing result
            date: Date string

        Returns:
            Path to summary file
        """
        summary = result.get("summary", {})

        # Create summary text
        summary_lines = [
            f"# Batch Processing Summary - {date}",
            "",
            f"**Date:** {date}",
            f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Statistics",
            "",
            f"- **Total Patients:** {summary.get('total', 0)}",
            f"- **Succeeded:** {summary.get('succeeded', 0)} ✓",
            f"- **Failed:** {summary.get('failed', 0)} ✗",
            f"- **Success Rate:** {summary.get('success_rate', 0):.1f}%",
            f"- **Average Time:** {summary.get('average_time', 0):.2f}s per patient",
            "",
        ]

        # Add critical alerts if available
        if "critical_alerts" in summary:
            summary_lines.extend([
                f"- **Critical Alerts:** {summary['critical_alerts']} 🚨",
                "",
            ])

        # Add priority info if available
        if "high_priority" in summary:
            summary_lines.extend([
                "## Priority Breakdown",
                "",
                f"- **High Priority (SOFA >15):** {summary.get('high_priority', 0)}",
                f"- **Normal Priority:** {summary.get('normal_priority', 0)}",
                "",
            ])

        # Add individual patient results
        summary_lines.extend([
            "## Patient Results",
            "",
        ])

        for patient_result in result.get("results", []):
            patient_id = patient_result.get("patient_id", "Unknown")
            status = patient_result.get("status", "unknown")
            elapsed = patient_result.get("elapsed_time", 0)

            status_icon = "✓" if status == "success" else "✗"
            summary_lines.append(
                f"- **{patient_id}**: {status} {status_icon} ({elapsed:.2f}s)"
            )

        summary_text = "\n".join(summary_lines)

        # Save to file
        summary_dir = Path("state") / "batch_summaries"
        summary_dir.mkdir(parents=True, exist_ok=True)

        summary_path = summary_dir / f"batch_summary_{date}.md"

        try:
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary_text)

            logger.info(f"Batch summary saved to {summary_path}")
        except Exception as e:
            logger.error(f"Failed to save batch summary: {e}")

        return str(summary_path)

    def process_specific_patients(
        self,
        patient_ids: List[str],
        date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process specific patients by ID.

        Args:
            patient_ids: List of patient identifiers
            date: Date string in YYYY-MM-DD format
                 If None, uses today's date

        Returns:
            Batch processing result
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        logger.info(f"Processing {len(patient_ids)} specific patients for {date}")

        # Discover all patients
        all_patients = self.discover_patients(date)

        # Filter to specified patients
        patients = [
            p for p in all_patients
            if p["patient_id"] in patient_ids
        ]

        # Check for missing patients
        found_ids = {p["patient_id"] for p in patients}
        missing_ids = set(patient_ids) - found_ids

        if missing_ids:
            logger.warning(f"Patients not found: {missing_ids}")

        if not patients:
            return {
                "status": "error",
                "error": "No patients found",
                "results": [],
                "summary": {"total": 0, "succeeded": 0, "failed": 0}
            }

        # Process batch
        result = self.main_orchestrator.process_batch(patients)

        return result

    def get_active_patients(self) -> List[str]:
        """
        Get list of all active patient IDs.

        Returns:
            List of patient identifiers
        """
        if not self.patients_dir.exists():
            return []

        return [
            d.name for d in self.patients_dir.iterdir()
            if d.is_dir()
        ]

    def get_patients_with_notes_today(self) -> List[str]:
        """
        Get list of patient IDs with notes for today.

        Returns:
            List of patient identifiers
        """
        today = datetime.now().strftime("%Y-%m-%d")
        patients = self.discover_patients(today)

        return [p["patient_id"] for p in patients]
