"""
Analysis Supervisor

This supervisor coordinates the analysis workflow:
1. Trend Analyzer (if history exists) - analyzes trends over time
2. Critical Value Checker - identifies critical values requiring intervention
3. SOFA Calculator - calculates severity scores

All run in parallel for efficiency.
"""

import logging
from typing import Any, Dict, List

from agents.base.supervisor import BaseSupervisor
from agents.base.state import StateManager
from agents.workers.critical_checker import CriticalCheckerAgent
from agents.workers.sofa_calculator import SofaCalculatorAgent

logger = logging.getLogger(__name__)


class AnalysisSupervisor(BaseSupervisor):
    """
    Supervises the analysis phase of the workflow.

    Workflow:
    1. All agents run in parallel for efficiency:
       - CriticalChecker: Identifies critical values
       - SofaCalculator: Calculates SOFA score and mortality risk
       - (Future: TrendAnalyzer for multi-day trend analysis)

    Configuration:
    - parallel=True for maximum efficiency
    - All workers are important but not critical (workflow continues if one fails)
    """

    def __init__(self, state_manager: StateManager, config: Dict[str, Any] = None):
        """
        Initialize the Analysis Supervisor.

        Args:
            state_manager: StateManager instance for this patient/date
            config: Optional configuration dict for agents
        """
        # Initialize worker agents
        agent_config = config or {}

        # Create workers
        critical_checker = CriticalCheckerAgent(state_manager, agent_config)
        sofa_calculator = SofaCalculatorAgent(state_manager, agent_config)

        workers = [critical_checker, sofa_calculator]

        # Supervisor configuration
        supervisor_config = {
            "parallel": True,  # Run all in parallel
            "max_workers": 3,
            "stop_on_error": False,  # Continue even if one fails
            "critical_workers": [],  # None are strictly critical
        }

        super().__init__(
            name="AnalysisSupervisor",
            workers=workers,
            state_manager=state_manager,
            config=supervisor_config
        )

        logger.info("Initialized AnalysisSupervisor with 2 workers")

    def prepare_context(self) -> Dict[str, Any]:
        """
        Prepare context for analysis workers.

        Loads vitals, labs, and parsed data from previous phases.
        Also loads historical data for trend analysis.

        Returns:
            Dictionary containing:
                - vitals_data: Vital signs data
                - labs_data: Laboratory values data
                - parsed_data: Parsed clinical note
                - history: Historical workflow statuses (7 days)
                - patient_id: Patient identifier
                - date: Date of analysis

        Raises:
            ValueError: If required data is missing
        """
        # Load vitals and labs from parse phase
        vitals_data = self._load_phase_json("vitals")
        labs_data = self._load_phase_json("labs")
        parsed_data = self._load_phase_json("parsed")

        if not vitals_data and not labs_data and not parsed_data:
            raise ValueError(
                f"No clinical data found for analysis: "
                f"patient={self.state_manager.patient_id}, "
                f"date={self.state_manager.date}"
            )

        # Load historical data for trend analysis
        history = self.state_manager.get_history(days=7)

        # Prepare context
        context = {
            "vitals_data": vitals_data,
            "labs_data": labs_data,
            "parsed_data": parsed_data,
            "history": history,
            "patient_id": self.state_manager.patient_id,
            "date": self.state_manager.date,
        }

        logger.info(
            f"Prepared analysis context: "
            f"vitals={'✓' if vitals_data else '✗'}, "
            f"labs={'✓' if labs_data else '✗'}, "
            f"history={len(history)} days"
        )

        return context

    def validate_results(self, results: List[Dict[str, Any]]) -> bool:
        """
        Validate the combined results from all analysis workers.

        Validation criteria:
        1. At least one worker should succeed (preferably SOFA calculator)
        2. If critical checker succeeded, verify structure is valid
        3. If SOFA calculator succeeded, verify score is in valid range (0-24)

        Args:
            results: List of result dictionaries from workers

        Returns:
            True if results meet acceptance criteria, False otherwise
        """
        # Count successes
        successes = sum(1 for r in results if r.get("status") == "success")

        if successes == 0:
            logger.error("All analysis workers failed")
            return False

        # Find specific results
        critical_checker_result = None
        sofa_calculator_result = None

        for result in results:
            if result.get("status") != "success":
                continue

            output = result.get("output", {})

            # CriticalChecker has critical_analysis
            if "critical_analysis" in output:
                critical_checker_result = result
            # SofaCalculator has scores
            elif "scores" in output:
                sofa_calculator_result = result

        # Validate SOFA score if present
        if sofa_calculator_result:
            scores = sofa_calculator_result.get("output", {}).get("scores", {})
            sofa = scores.get("sofa", {})
            total_score = sofa.get("total_score")

            if total_score is not None:
                if not (0 <= total_score <= 24):
                    logger.error(f"Invalid SOFA score: {total_score} (must be 0-24)")
                    return False

                logger.info(f"SOFA score validated: {total_score}/24")

        # Validate critical analysis if present
        if critical_checker_result:
            analysis = critical_checker_result.get("output", {}).get("critical_analysis", {})
            summary = analysis.get("summary", {})
            total_critical = summary.get("total_critical_values", 0)

            logger.info(f"Critical analysis validated: {total_critical} critical values")

        # Log validation summary
        logger.info(
            f"Analysis validation: "
            f"successes={successes}/{len(results)}, "
            f"sofa={'✓' if sofa_calculator_result else '✗'}, "
            f"critical={'✓' if critical_checker_result else '✗'}"
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

    def get_critical_values(self) -> List[Dict[str, Any]]:
        """
        Get critical values from the most recent analysis.

        Returns:
            List of critical value dictionaries or empty list
        """
        critical_state = self.state_manager.load("critical")
        if not critical_state:
            return []

        try:
            data = self._load_phase_json("critical")
            if not data:
                return []

            analysis = data.get("critical_analysis", {})
            life_threatening = analysis.get("life_threatening", [])
            critical = analysis.get("critical", [])

            return life_threatening + critical
        except Exception as e:
            logger.error(f"Failed to load critical values: {e}")
            return []

    def get_sofa_score(self) -> int:
        """
        Get SOFA score from the most recent analysis.

        Returns:
            SOFA score (0-24) or -1 if not available
        """
        scores_state = self.state_manager.load("scores")
        if not scores_state:
            return -1

        try:
            data = self._load_phase_json("scores")
            if not data:
                return -1

            scores = data.get("scores", {})
            sofa = scores.get("sofa", {})
            return sofa.get("total_score", -1)
        except Exception as e:
            logger.error(f"Failed to load SOFA score: {e}")
            return -1

    def requires_immediate_action(self) -> bool:
        """
        Check if any life-threatening values require immediate action.

        Returns:
            True if immediate action is required
        """
        critical_values = self.get_critical_values()

        # Check for life-threatening severity
        for value in critical_values:
            if value.get("severity") == "life-threatening":
                return True

        return False
