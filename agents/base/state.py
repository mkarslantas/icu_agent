"""
State Manager for ICU Multi-Agent System

This module handles persistence of agent states and workflow progress.
All agent outputs are saved as structured markdown files for easy review
and historical analysis.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class StateManager:
    """
    Manages state persistence for the ICU monitoring system.

    The StateManager creates a structured directory for each patient and date,
    saving agent outputs as numbered markdown files. This provides:
    - Auditability: Clear record of all processing steps
    - Debuggability: Easy inspection of intermediate results
    - Historical analysis: Trend detection across multiple days

    Directory structure:
        state/
        └── {patient_id}/
            ├── {date}/
            │   ├── 00_input.md
            │   ├── 01_parsed.md
            │   ├── 02_vitals.md
            │   ├── 03_labs.md
            │   ├── 04_trends.md
            │   ├── 05_critical.md
            │   ├── 06_scores.md
            │   ├── 07_report.md
            │   ├── 08_alerts.md
            │   └── workflow_status.json
            └── {previous_date}/
                └── ...

    Attributes:
        patient_id: Unique identifier for the patient
        date: Date string in YYYY-MM-DD format
        base_dir: Base directory for state files
        state_dir: Full path to this patient's state directory
        workflow_status: Dictionary tracking workflow completion
    """

    # Phase name to number mapping
    PHASE_NUMBERS = {
        "input": 0,
        "parsed": 1,
        "vitals": 2,
        "labs": 3,
        "trends": 4,
        "critical": 5,
        "scores": 6,
        "report": 7,
        "alerts": 8,
    }

    def __init__(
        self,
        patient_id: str,
        date: str,
        base_dir: str = "state"
    ):
        """
        Initialize the StateManager.

        Args:
            patient_id: Unique identifier for the patient (e.g., "HT001")
            date: Date string in YYYY-MM-DD format
            base_dir: Base directory for state files (default: "state")
        """
        self.patient_id = patient_id
        self.date = date
        self.base_dir = Path(base_dir)

        # Create state directory structure
        self.state_dir = self.base_dir / patient_id / date
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # Initialize or load workflow status
        self.workflow_status_file = self.state_dir / "workflow_status.json"
        self.workflow_status = self._load_workflow_status()

        logger.info(f"Initialized StateManager for {patient_id} on {date}")

    def _load_workflow_status(self) -> Dict[str, Any]:
        """
        Load or initialize the workflow status.

        Returns:
            Dictionary containing workflow status
        """
        if self.workflow_status_file.exists():
            try:
                with open(self.workflow_status_file, "r", encoding="utf-8") as f:
                    status = json.load(f)
                logger.debug(f"Loaded workflow status from {self.workflow_status_file}")
                return status
            except Exception as e:
                logger.warning(f"Failed to load workflow status: {e}")

        # Initialize new workflow status
        return {
            "patient_id": self.patient_id,
            "date": self.date,
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "phases": {},
            "completed": False,
        }

    def _update_workflow_status(self, phase: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Update the workflow status after saving a phase.

        Args:
            phase: Phase name
            metadata: Optional metadata dictionary
        """
        self.workflow_status["phases"][phase] = {
            "completed_at": datetime.now().isoformat(),
            "metadata": metadata or {},
        }

        # Save updated status
        try:
            with open(self.workflow_status_file, "w", encoding="utf-8") as f:
                json.dump(self.workflow_status, f, indent=2, ensure_ascii=False)
            logger.debug(f"Updated workflow status for phase: {phase}")
        except Exception as e:
            logger.error(f"Failed to update workflow status: {e}")

    def _get_phase_number(self, phase: str) -> int:
        """
        Get the number for a phase name.

        Args:
            phase: Phase name (e.g., "parsed", "vitals", etc.)

        Returns:
            Phase number (0-8)
        """
        # Try exact match first
        if phase in self.PHASE_NUMBERS:
            return self.PHASE_NUMBERS[phase]

        # Try lowercase
        phase_lower = phase.lower()
        if phase_lower in self.PHASE_NUMBERS:
            return self.PHASE_NUMBERS[phase_lower]

        # Try matching by substring (e.g., "TurkishParser" -> "parsed")
        for name, number in self.PHASE_NUMBERS.items():
            if name in phase_lower or phase_lower in name:
                return number

        # Default: use hash to assign a consistent number
        logger.warning(f"Unknown phase name: {phase}, using hash-based number")
        return (hash(phase) % 90) + 10  # 10-99 for custom phases

    def _format_dict_as_markdown(self, data: Any, level: int = 0) -> str:
        """
        Convert a dictionary to readable markdown format.

        Args:
            data: Data to format (dict, list, or primitive)
            level: Current indentation level

        Returns:
            Formatted markdown string
        """
        indent = "  " * level

        if isinstance(data, dict):
            lines = []
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    lines.append(f"{indent}- **{key}**:")
                    lines.append(self._format_dict_as_markdown(value, level + 1))
                else:
                    lines.append(f"{indent}- **{key}**: {value}")
            return "\n".join(lines)

        elif isinstance(data, list):
            lines = []
            for item in data:
                if isinstance(item, (dict, list)):
                    lines.append(self._format_dict_as_markdown(item, level))
                else:
                    lines.append(f"{indent}- {item}")
            return "\n".join(lines)

        else:
            return f"{indent}{data}"

    def save(
        self,
        phase: str,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Save agent output for a phase.

        Args:
            phase: Phase name (e.g., "parsed", "vitals", etc.)
            content: Content to save (dict, string, or JSON-serializable)
            metadata: Optional metadata about this phase

        Returns:
            Path to the saved file

        Example:
            >>> sm = StateManager("HT001", "2025-11-21")
            >>> sm.save("parsed", {"patient_info": {...}, "vitals": {...}})
            Path('state/HT001/2025-11-21/01_parsed.md')
        """
        # Get phase number and filename
        phase_num = self._get_phase_number(phase)
        filename = f"{phase_num:02d}_{phase.lower()}.md"
        filepath = self.state_dir / filename

        # Format content
        if isinstance(content, str):
            formatted_content = content
        elif isinstance(content, dict):
            # Create markdown with metadata header
            lines = [
                f"# {phase.title()} - {self.patient_id}",
                f"",
                f"**Date**: {self.date}",
                f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"",
            ]

            if metadata:
                lines.append("## Metadata")
                lines.append("")
                lines.append(self._format_dict_as_markdown(metadata))
                lines.append("")

            lines.append("## Data")
            lines.append("")

            # Format as JSON code block for structured data
            if all(isinstance(v, (dict, list)) for v in content.values()):
                lines.append("```json")
                lines.append(json.dumps(content, indent=2, ensure_ascii=False))
                lines.append("```")
            else:
                # Format as markdown for mixed content
                lines.append(self._format_dict_as_markdown(content))

            formatted_content = "\n".join(lines)
        else:
            # Try JSON serialization
            try:
                formatted_content = json.dumps(content, indent=2, ensure_ascii=False)
            except:
                formatted_content = str(content)

        # Save file
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(formatted_content)

            logger.info(f"Saved {phase} to {filepath} ({len(formatted_content)} chars)")

            # Update workflow status
            self._update_workflow_status(phase, metadata)

            return filepath

        except Exception as e:
            logger.error(f"Failed to save {phase} to {filepath}: {e}")
            raise

    def load(self, phase: str) -> Optional[str]:
        """
        Load content for a specific phase.

        Args:
            phase: Phase name to load

        Returns:
            Content string if found, None otherwise

        Example:
            >>> sm = StateManager("HT001", "2025-11-21")
            >>> parsed_data = sm.load("parsed")
        """
        # Get phase number and filename
        phase_num = self._get_phase_number(phase)
        filename = f"{phase_num:02d}_{phase.lower()}.md"
        filepath = self.state_dir / filename

        if not filepath.exists():
            logger.warning(f"Phase file not found: {filepath}")
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            logger.debug(f"Loaded {phase} from {filepath} ({len(content)} chars)")
            return content
        except Exception as e:
            logger.error(f"Failed to load {phase} from {filepath}: {e}")
            return None

    def load_multiple(self, phases: List[str]) -> Dict[str, Optional[str]]:
        """
        Load multiple phases at once.

        Args:
            phases: List of phase names to load

        Returns:
            Dictionary mapping phase names to their content

        Example:
            >>> sm = StateManager("HT001", "2025-11-21")
            >>> data = sm.load_multiple(["vitals", "labs", "scores"])
            >>> vitals = data["vitals"]
            >>> labs = data["labs"]
        """
        result = {}
        for phase in phases:
            result[phase] = self.load(phase)
        return result

    def get_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Load historical workflow statuses for this patient.

        Args:
            days: Number of days to look back (default: 7)

        Returns:
            List of historical workflow status dictionaries, sorted by date (newest first)

        Example:
            >>> sm = StateManager("HT001", "2025-11-21")
            >>> history = sm.get_history(days=7)
            >>> for day in history:
            ...     print(f"{day['date']}: SOFA={day.get('sofa_score')}")
        """
        history = []

        # Calculate date range
        current_date = datetime.strptime(self.date, "%Y-%m-%d")

        for i in range(1, days + 1):
            past_date = current_date - timedelta(days=i)
            past_date_str = past_date.strftime("%Y-%m-%d")

            # Check if state directory exists for this date
            past_state_dir = self.base_dir / self.patient_id / past_date_str
            status_file = past_state_dir / "workflow_status.json"

            if status_file.exists():
                try:
                    with open(status_file, "r", encoding="utf-8") as f:
                        status = json.load(f)
                    history.append(status)
                    logger.debug(f"Loaded history for {past_date_str}")
                except Exception as e:
                    logger.warning(f"Failed to load history for {past_date_str}: {e}")

        # Sort by date (newest first)
        history.sort(key=lambda x: x.get("date", ""), reverse=True)

        logger.info(f"Loaded {len(history)} historical records for {self.patient_id}")
        return history

    def finalize(self):
        """
        Mark the workflow as completed.

        Should be called after all phases have successfully completed.
        """
        self.workflow_status["completed"] = True
        self.workflow_status["completed_at"] = datetime.now().isoformat()

        try:
            with open(self.workflow_status_file, "w", encoding="utf-8") as f:
                json.dump(self.workflow_status, f, indent=2, ensure_ascii=False)
            logger.info(f"Workflow finalized for {self.patient_id} on {self.date}")
        except Exception as e:
            logger.error(f"Failed to finalize workflow: {e}")

    def get_status(self) -> Dict[str, Any]:
        """
        Get the current workflow status.

        Returns:
            Workflow status dictionary
        """
        return self.workflow_status.copy()

    def is_completed(self) -> bool:
        """
        Check if the workflow is completed.

        Returns:
            True if workflow is completed, False otherwise
        """
        return self.workflow_status.get("completed", False)

    def list_phases(self) -> List[str]:
        """
        List all phases that have been saved.

        Returns:
            List of phase names
        """
        return list(self.workflow_status.get("phases", {}).keys())
