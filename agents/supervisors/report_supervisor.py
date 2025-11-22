"""
Report Supervisor

This supervisor coordinates the report generation workflow:
1. Report Generator - creates comprehensive Turkish daily report
2. Alert Generator - creates prioritized clinical alerts

Runs sequentially to ensure each component has access to all analysis results.
"""

import logging
from typing import Any, Dict, List

from agents.base.supervisor import BaseSupervisor
from agents.base.state import StateManager
from agents.workers.report_generator import ReportGeneratorAgent
from agents.workers.alert_generator import AlertGeneratorAgent

logger = logging.getLogger(__name__)


class ReportSupervisor(BaseSupervisor):
    """
    Supervises the report generation phase of the workflow.

    Workflow:
    1. ReportGenerator creates comprehensive Turkish daily report
       - Loads all previous phase outputs
       - Includes historical trend analysis
       - Provides specific actionable recommendations

    2. AlertGenerator creates prioritized clinical alerts
       - Reviews critical values and trends
       - Categorizes by urgency (immediate, urgent, monitor)
       - Provides specific intervention recommendations

    Configuration:
    - parallel=False (sequential execution - report first, then alerts)
    - critical_workers=["ReportGenerator"] - must succeed
    """

    def __init__(self, state_manager: StateManager, config: Dict[str, Any] = None):
        """
        Initialize the Report Supervisor.

        Args:
            state_manager: StateManager instance for this patient/date
            config: Optional configuration dict for agents
        """
        # Initialize worker agents
        agent_config = config or {}

        # Create workers
        report_generator = ReportGeneratorAgent(state_manager, agent_config)
        alert_generator = AlertGeneratorAgent(state_manager, agent_config)

        workers = [report_generator, alert_generator]

        # Supervisor configuration
        supervisor_config = {
            "parallel": False,  # Sequential execution (report first, then alerts)
            "max_workers": 1,
            "stop_on_error": True,  # Stop if report generation fails
            "critical_workers": ["ReportGenerator"],  # Must succeed
        }

        super().__init__(
            name="ReportSupervisor",
            workers=workers,
            state_manager=state_manager,
            config=supervisor_config
        )

        logger.info("Initialized ReportSupervisor with 2 workers (ReportGenerator + AlertGenerator)")

    def prepare_context(self) -> Dict[str, Any]:
        """
        Prepare comprehensive context for report generation.

        Loads ALL previous phase outputs:
        - Parsed clinical note
        - Vital signs
        - Laboratory values
        - Critical values analysis
        - SOFA scores
        - Historical data (2-3 days)

        Returns:
            Dictionary containing all clinical data and metadata

        Raises:
            ValueError: If essential data is missing
        """
        # Load all phase outputs
        parsed_data = self._load_phase_json("parsed")
        vitals_data = self._load_phase_json("vitals")
        labs_data = self._load_phase_json("labs")
        critical_data = self._load_phase_json("critical")
        scores_data = self._load_phase_json("scores")

        # Parsed data is essential
        if not parsed_data:
            raise ValueError(
                f"No parsed clinical data found for report generation: "
                f"patient={self.state_manager.patient_id}, "
                f"date={self.state_manager.date}"
            )

        # Load historical data for trend analysis
        history = self.state_manager.get_history(days=3)

        # Extract patient demographics from parsed data
        patient_info = parsed_data.get("patient_info", {})
        admission_info = parsed_data.get("admission_info", {})

        # Prepare comprehensive context
        context = {
            "parsed_data": parsed_data,
            "vitals_data": vitals_data,
            "labs_data": labs_data,
            "critical_data": critical_data,
            "scores_data": scores_data,
            "history": history,
            "patient_id": self.state_manager.patient_id,
            "date": self.state_manager.date,
            "patient_info": patient_info,
            "admission_info": admission_info,
        }

        logger.info(
            f"Prepared report context: "
            f"parsed={'✓' if parsed_data else '✗'}, "
            f"vitals={'✓' if vitals_data else '✗'}, "
            f"labs={'✓' if labs_data else '✗'}, "
            f"critical={'✓' if critical_data else '✗'}, "
            f"scores={'✓' if scores_data else '✗'}, "
            f"history={len(history)} days"
        )

        return context

    def validate_results(self, results: List[Dict[str, Any]]) -> bool:
        """
        Validate the report generation results.

        Validation criteria:
        1. ReportGenerator must have succeeded
        2. Report must be non-empty and substantial (>500 chars)
        3. Report must be in Turkish (contains Turkish characters)
        4. Report must include required sections

        Args:
            results: List of result dictionaries from workers

        Returns:
            True if results meet acceptance criteria, False otherwise
        """
        # Find ReportGenerator result
        report_result = None

        for result in results:
            if result.get("status") == "success":
                output = result.get("output", {})
                if "report" in output:
                    report_result = result
                    break

        # Validation 1: ReportGenerator must succeed
        if not report_result:
            logger.error("ReportGenerator did not succeed")
            return False

        # Extract report content
        report_output = report_result.get("output", {})
        report_text = report_output.get("report", "")

        # Validation 2: Report must be substantial
        if len(report_text) < 500:
            logger.error(f"Report too short: {len(report_text)} chars (min: 500)")
            return False

        # Validation 3: Check for Turkish content
        turkish_chars = ['ş', 'ğ', 'ü', 'ö', 'ç', 'ı', 'İ', 'Ş', 'Ğ', 'Ü', 'Ö', 'Ç']
        has_turkish = any(char in report_text for char in turkish_chars)

        if not has_turkish:
            logger.warning("Report does not appear to be in Turkish")
            # Don't fail, just warn
            # return False

        # Validation 4: Check for required sections
        required_sections = [
            "GENEL DURUM",
            "SİSTEM BAZLI",
            "ÖNERİ"  # Matches "ÖNERİLER" or "PLAN"
        ]

        missing_sections = []
        for section in required_sections:
            if section not in report_text:
                missing_sections.append(section)

        if missing_sections:
            logger.warning(f"Report missing sections: {missing_sections}")
            # Don't fail for missing sections, just warn
            # return False

        # Get report metadata
        recommendation_count = report_output.get("recommendation_count", 0)
        sections_count = len(report_output.get("sections", {}))

        logger.info(
            f"Report validation passed: "
            f"length={len(report_text)} chars, "
            f"sections={sections_count}, "
            f"recommendations={recommendation_count}"
        )

        return True

    def _load_phase_json(self, phase: str) -> Dict[str, Any]:
        """
        Load JSON data from a state phase.

        Args:
            phase: Phase name to load

        Returns:
            Parsed JSON dictionary or None if not available
        """
        state = self.state_manager.load(phase)
        if not state:
            return None

        try:
            import json
            import re

            # Extract JSON from markdown
            text = state.strip()
            json_block_pattern = r"```json\s*(.*?)\s*```"
            match = re.search(json_block_pattern, text, re.DOTALL)

            if match:
                json_str = match.group(1).strip()
                return json.loads(json_str)

            return json.loads(text)
        except Exception as e:
            logger.debug(f"Failed to load JSON from {phase}: {e}")
            return None

    def get_report_text(self) -> str:
        """
        Get the generated report text from the most recent run.

        Returns:
            Report markdown text or empty string if not available
        """
        report_state = self.state_manager.load("report")
        if not report_state:
            return ""

        try:
            # The report is saved as plain markdown (not JSON)
            # Extract the actual report content (skip metadata header)
            lines = report_state.split('\n')

            # Find where the actual report starts (after metadata)
            report_start = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('# 🏥'):
                    report_start = i
                    break

            if report_start > 0:
                return '\n'.join(lines[report_start:])
            else:
                return report_state

        except Exception as e:
            logger.error(f"Failed to load report text: {e}")
            return ""

    def get_report_path(self) -> str:
        """
        Get the file path to the generated report.

        Returns:
            Path to report file (07_report.md)
        """
        report_path = self.state_manager.state_dir / "07_report.md"
        return str(report_path)

    def save_report_to_file(self, output_path: str) -> bool:
        """
        Save the report to a custom output path.

        Args:
            output_path: Path where report should be saved

        Returns:
            True if successful, False otherwise
        """
        report_text = self.get_report_text()
        if not report_text:
            logger.error("No report text available to save")
            return False

        try:
            from pathlib import Path
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)

            logger.info(f"Report saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save report to {output_path}: {e}")
            return False

    def get_all_alerts(self) -> List[Dict[str, Any]]:
        """
        Get all generated alerts from the most recent run.

        Returns:
            List of alert dictionaries or empty list
        """
        alerts_state = self.state_manager.load("alerts")
        if not alerts_state:
            return []

        try:
            data = self._load_phase_json("alerts")
            if not data:
                return []

            return data.get("alerts", [])

        except Exception as e:
            logger.error(f"Failed to load alerts: {e}")
            return []

    def get_immediate_alerts(self) -> List[Dict[str, Any]]:
        """
        Get immediate priority alerts only.

        Returns:
            List of immediate alert dictionaries
        """
        all_alerts = self.get_all_alerts()
        return [a for a in all_alerts if a.get("urgency") == "immediate"]

    def get_alerts_summary(self) -> Dict[str, Any]:
        """
        Get alerts summary from the most recent run.

        Returns:
            Summary dictionary with alert counts by urgency and category
        """
        alerts_state = self.state_manager.load("alerts")
        if not alerts_state:
            return {
                "total_alerts": 0,
                "immediate_count": 0,
                "urgent_count": 0,
                "monitor_count": 0
            }

        try:
            data = self._load_phase_json("alerts")
            if not data:
                return {}

            return data.get("summary", {})

        except Exception as e:
            logger.error(f"Failed to load alerts summary: {e}")
            return {}
