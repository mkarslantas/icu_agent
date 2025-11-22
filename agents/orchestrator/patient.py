"""
Patient Orchestrator

This orchestrator manages the complete workflow for a single patient on a specific date.
It executes all three supervisor phases sequentially:
1. Parse Phase (ParseSupervisor)
2. Analysis Phase (AnalysisSupervisor)
3. Report Phase (ReportSupervisor)
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional

from agents.base.state import StateManager
from agents.supervisors.parse_supervisor import ParseSupervisor
from agents.supervisors.analysis_supervisor import AnalysisSupervisor
from agents.supervisors.report_supervisor import ReportSupervisor

logger = logging.getLogger(__name__)


class PatientOrchestrator:
    """
    Orchestrates the complete ICU monitoring workflow for a single patient.

    This orchestrator:
    1. Initializes StateManager for patient/date
    2. Loads raw clinical note
    3. Executes three supervisor phases sequentially:
       - Parse: Converts raw notes to structured data
       - Analysis: Identifies critical values and calculates scores
       - Report: Generates comprehensive Turkish report
    4. Handles errors at each phase
    5. Saves workflow status and returns results

    Attributes:
        patient_id: Unique identifier for the patient
        date: Date string in YYYY-MM-DD format
        config: Configuration dictionary
        state_manager: StateManager instance
        parse_supervisor: ParseSupervisor instance
        analysis_supervisor: AnalysisSupervisor instance
        report_supervisor: ReportSupervisor instance
    """

    def __init__(
        self,
        patient_id: str,
        date: str,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Patient Orchestrator.

        Args:
            patient_id: Unique identifier for the patient (e.g., "HT001")
            date: Date string in YYYY-MM-DD format
            config: Optional configuration dict with keys:
                - model: Claude model to use
                - max_tokens: Maximum tokens per request
                - temperature: Sampling temperature
                - state_dir: Base directory for state files
        """
        self.patient_id = patient_id
        self.date = date
        self.config = config or {}

        # Initialize state manager
        state_dir = self.config.get("state_dir", "state")
        self.state_manager = StateManager(patient_id, date, base_dir=state_dir)

        # Initialize supervisors
        self.parse_supervisor = ParseSupervisor(self.state_manager, self.config)
        self.analysis_supervisor = AnalysisSupervisor(self.state_manager, self.config)
        self.report_supervisor = ReportSupervisor(self.state_manager, self.config)

        logger.info(
            f"Initialized PatientOrchestrator: "
            f"patient={patient_id}, date={date}"
        )

    def load_clinical_note(self, note_path: Optional[str] = None) -> bool:
        """
        Load clinical note and save as 00_input.md.

        Args:
            note_path: Optional path to clinical note file.
                      If not provided, looks for note in standard location:
                      patients/active/{patient_id}/notes/{date}.txt

        Returns:
            True if note loaded successfully, False otherwise
        """
        # Determine note path
        if note_path:
            note_file = Path(note_path)
        else:
            # Standard location
            note_file = Path(f"patients/active/{self.patient_id}/notes/{self.date}.txt")

            # Also check with day suffix (e.g., 2025-11-20-day5.txt)
            if not note_file.exists():
                parent_dir = note_file.parent
                if parent_dir.exists():
                    # Find any file matching the date
                    matching_files = list(parent_dir.glob(f"{self.date}*.txt"))
                    if matching_files:
                        note_file = matching_files[0]
                        logger.info(f"Found note file: {note_file}")

        # Check if file exists
        if not note_file.exists():
            logger.error(f"Clinical note not found: {note_file}")
            return False

        # Load note content
        try:
            with open(note_file, 'r', encoding='utf-8') as f:
                note_content = f.read()

            if not note_content.strip():
                logger.error(f"Clinical note is empty: {note_file}")
                return False

            # Save as 00_input.md
            self.state_manager.save(
                phase="input",
                content=note_content,
                metadata={
                    "source_file": str(note_file),
                    "patient_id": self.patient_id,
                    "date": self.date,
                }
            )

            logger.info(
                f"Loaded clinical note: {note_file} "
                f"({len(note_content)} chars)"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to load clinical note: {e}")
            return False

    def run(
        self,
        note_path: Optional[str] = None,
        skip_phases: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Execute the complete workflow for this patient.

        Phases:
        1. Load raw clinical note → save as 00_input.md
        2. Run ParseSupervisor → generates parsed, vitals, labs
        3. Run AnalysisSupervisor → generates critical, scores
        4. Run ReportSupervisor → generates final report

        Args:
            note_path: Optional path to clinical note file
            skip_phases: Optional list of phases to skip (for debugging)

        Returns:
            Dictionary with keys:
                - status: "success" or "error"
                - patient_id: Patient identifier
                - date: Date of workflow
                - phases: Dict of phase results
                - elapsed_time: Total time in seconds
                - error: Error message if failed
        """
        start_time = time.time()
        skip_phases = skip_phases or []

        logger.info(
            f"Starting workflow for patient {self.patient_id} on {self.date}"
        )

        phases_results = {}

        # Phase 0: Load clinical note
        if "load" not in skip_phases:
            logger.info("Phase 0: Loading clinical note")

            if not self.load_clinical_note(note_path):
                return {
                    "status": "error",
                    "error": "Failed to load clinical note",
                    "patient_id": self.patient_id,
                    "date": self.date,
                    "elapsed_time": time.time() - start_time,
                }

            phases_results["load"] = {"status": "success"}

        # Phase 1: Parse
        if "parse" not in skip_phases:
            logger.info("Phase 1: Parse (Turkish Parser + Extractors)")
            phase_start = time.time()

            try:
                parse_result = self.parse_supervisor.run()
                phases_results["parse"] = parse_result

                if parse_result.get("status") != "success":
                    logger.error("Parse phase failed")
                    return {
                        "status": "error",
                        "error": "Parse phase failed",
                        "patient_id": self.patient_id,
                        "date": self.date,
                        "phases": phases_results,
                        "elapsed_time": time.time() - start_time,
                    }

                logger.info(
                    f"Parse phase completed ({parse_result.get('elapsed_time', 0):.2f}s)"
                )

            except Exception as e:
                logger.error(f"Parse phase error: {e}", exc_info=True)
                return {
                    "status": "error",
                    "error": f"Parse phase error: {str(e)}",
                    "patient_id": self.patient_id,
                    "date": self.date,
                    "phases": phases_results,
                    "elapsed_time": time.time() - start_time,
                }

        # Phase 2: Analysis
        if "analysis" not in skip_phases:
            logger.info("Phase 2: Analysis (Critical Checker + SOFA Calculator)")
            phase_start = time.time()

            try:
                analysis_result = self.analysis_supervisor.run()
                phases_results["analysis"] = analysis_result

                if analysis_result.get("status") != "success":
                    logger.warning("Analysis phase had issues, but continuing")
                    # Don't fail - analysis is important but not critical

                logger.info(
                    f"Analysis phase completed ({analysis_result.get('elapsed_time', 0):.2f}s)"
                )

            except Exception as e:
                logger.error(f"Analysis phase error: {e}", exc_info=True)
                # Continue to report phase even if analysis fails
                phases_results["analysis"] = {
                    "status": "error",
                    "error": str(e)
                }

        # Phase 3: Report
        if "report" not in skip_phases:
            logger.info("Phase 3: Report (Report Generator)")
            phase_start = time.time()

            try:
                report_result = self.report_supervisor.run()
                phases_results["report"] = report_result

                if report_result.get("status") != "success":
                    logger.error("Report phase failed")
                    return {
                        "status": "error",
                        "error": "Report phase failed",
                        "patient_id": self.patient_id,
                        "date": self.date,
                        "phases": phases_results,
                        "elapsed_time": time.time() - start_time,
                    }

                logger.info(
                    f"Report phase completed ({report_result.get('elapsed_time', 0):.2f}s)"
                )

            except Exception as e:
                logger.error(f"Report phase error: {e}", exc_info=True)
                return {
                    "status": "error",
                    "error": f"Report phase error: {str(e)}",
                    "patient_id": self.patient_id,
                    "date": self.date,
                    "phases": phases_results,
                    "elapsed_time": time.time() - start_time,
                }

        # Finalize workflow
        self.state_manager.finalize()

        elapsed_time = time.time() - start_time

        logger.info(
            f"Workflow completed successfully for {self.patient_id} "
            f"(total time: {elapsed_time:.2f}s)"
        )

        return {
            "status": "success",
            "patient_id": self.patient_id,
            "date": self.date,
            "phases": phases_results,
            "elapsed_time": elapsed_time,
        }

    def get_critical_alerts(self) -> list:
        """
        Get critical alerts from the most recent analysis.

        Returns:
            List of critical value dictionaries
        """
        return self.analysis_supervisor.get_critical_values()

    def get_report_path(self) -> str:
        """
        Get the file path to the generated report.

        Returns:
            Path to report file (07_report.md)
        """
        return self.report_supervisor.get_report_path()

    def get_sofa_score(self) -> int:
        """
        Get SOFA score from the most recent analysis.

        Returns:
            SOFA score (0-24) or -1 if not available
        """
        return self.analysis_supervisor.get_sofa_score()

    def requires_immediate_action(self) -> bool:
        """
        Check if any life-threatening values require immediate action.

        Returns:
            True if immediate action is required
        """
        return self.analysis_supervisor.requires_immediate_action()

    def get_workflow_status(self) -> Dict[str, Any]:
        """
        Get the current workflow status.

        Returns:
            Workflow status dictionary
        """
        return self.state_manager.get_status()

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for all supervisors and workers.

        Returns:
            Dictionary containing metrics for all agents
        """
        return {
            "parse_supervisor": self.parse_supervisor.get_metrics(),
            "analysis_supervisor": self.analysis_supervisor.get_metrics(),
            "report_supervisor": self.report_supervisor.get_metrics(),
            "workers": {
                **self.parse_supervisor.get_worker_metrics(),
                **self.analysis_supervisor.get_worker_metrics(),
                **self.report_supervisor.get_worker_metrics(),
            }
        }
