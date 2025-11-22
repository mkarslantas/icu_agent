"""
Trend Analysis Agent

This agent analyzes multi-day parameter trends to identify:
- Deterioration patterns (worsening parameters)
- Recovery patterns (improving parameters)
- Stable trends (no significant change)
- Trend velocity (rate of change)
- Clinical significance of trends

The agent loads historical data from StateManager and performs
statistical analysis to detect meaningful patterns.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from agents.base.agent import BaseAgent

logger = logging.getLogger(__name__)


class TrendAnalyzerAgent(BaseAgent):
    """
    Analyzes multi-day trends in clinical parameters.

    This agent:
    - Loads historical vital signs and lab values (up to 7 days)
    - Calculates trend direction and velocity
    - Detects deterioration/recovery patterns
    - Identifies concerning trends requiring intervention
    - Provides clinical interpretation

    Output format (JSON):
    {
        "trend_analysis": {
            "vitals": {
                "heart_rate": {
                    "values": [85, 88, 92, 95],
                    "dates": ["2025-11-17", "2025-11-18", "2025-11-19", "2025-11-20"],
                    "trend": "increasing",
                    "velocity": 3.3,  # units per day
                    "pattern": "deteriorating",
                    "clinical_significance": "moderate"
                },
                ...
            },
            "labs": {
                "lactate": {
                    "values": [2.1, 2.8, 3.2],
                    "dates": ["2025-11-18", "2025-11-19", "2025-11-20"],
                    "trend": "increasing",
                    "velocity": 0.55,
                    "pattern": "deteriorating",
                    "clinical_significance": "high"
                },
                ...
            },
            "sofa_trend": {
                "values": [8, 9, 10],
                "dates": ["2025-11-18", "2025-11-19", "2025-11-20"],
                "trend": "increasing",
                "pattern": "deteriorating",
                "delta": +2
            }
        },
        "concerning_trends": [
            {
                "parameter": "lactate",
                "category": "labs",
                "trend": "increasing",
                "velocity": 0.55,
                "clinical_significance": "high",
                "recommendation": "Lactate yükselme trendi devam ediyor - sepsis protokolü gözden geçirilmeli"
            }
        ],
        "summary": {
            "deteriorating_count": 3,
            "improving_count": 1,
            "stable_count": 5,
            "high_concern_count": 2
        }
    }
    """

    def __init__(self, *args, **kwargs):
        """Initialize Trend Analyzer Agent."""
        super().__init__(
            name="TrendAnalyzer",
            prompt_path="prompts/analysis/10-trend-analysis.md",
            *args,
            **kwargs
        )

        # Trend detection thresholds
        self.thresholds = {
            "minimum_data_points": 2,  # Minimum points to detect trend
            "significant_change": 0.1,  # 10% change is significant
            "high_velocity_threshold": 20,  # 20% change per day
        }

    def prepare_input(self, context: Dict[str, Any]) -> str:
        """
        Prepare input for trend analysis.

        Loads historical data from state files.

        Args:
            context: Execution context (may contain days_back parameter)

        Returns:
            Formatted prompt with historical data
        """
        days_back = context.get("days_back", 7)

        # Load historical data
        history = self.state_manager.get_history(days=days_back)

        if not history:
            logger.warning("No historical data available for trend analysis")
            return self._format_no_data_prompt()

        # Extract parameters from history
        historical_data = self._extract_historical_parameters(history)

        # Format for prompt
        return self._format_historical_data(historical_data)

    def _extract_historical_parameters(
        self, history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Extract parameters from historical state files.

        Args:
            history: List of historical state dictionaries

        Returns:
            Dictionary with parameter timeseries
        """
        vitals_series = {}
        labs_series = {}
        sofa_series = []

        for day_data in history:
            date = day_data.get("date")
            if not date:
                continue

            # Load vitals for this day
            try:
                vitals_state = self._load_state_for_date(date, "vitals")
                if vitals_state:
                    vitals_data = self._extract_json_from_state(vitals_state)
                    if vitals_data:
                        self._append_vitals(vitals_series, date, vitals_data)
            except Exception as e:
                logger.debug(f"Could not load vitals for {date}: {e}")

            # Load labs for this day
            try:
                labs_state = self._load_state_for_date(date, "labs")
                if labs_state:
                    labs_data = self._extract_json_from_state(labs_state)
                    if labs_data:
                        self._append_labs(labs_series, date, labs_data)
            except Exception as e:
                logger.debug(f"Could not load labs for {date}: {e}")

            # Load SOFA for this day
            try:
                scores_state = self._load_state_for_date(date, "scores")
                if scores_state:
                    scores_data = self._extract_json_from_state(scores_state)
                    if scores_data:
                        sofa_score = scores_data.get("scores", {}).get("sofa", {}).get("total_score")
                        if sofa_score is not None:
                            sofa_series.append({"date": date, "value": sofa_score})
            except Exception as e:
                logger.debug(f"Could not load SOFA for {date}: {e}")

        return {
            "vitals": vitals_series,
            "labs": labs_series,
            "sofa": sofa_series,
        }

    def _load_state_for_date(self, date: str, phase: str) -> Optional[str]:
        """
        Load state file for a specific date.

        Args:
            date: Date string
            phase: Phase name

        Returns:
            State content or None
        """
        from agents.base.state import StateManager

        sm = StateManager(self.state_manager.patient_id, date)
        return sm.load(phase)

    def _extract_json_from_state(self, state_content: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from state file content.

        Args:
            state_content: State file content

        Returns:
            Parsed JSON dictionary or None
        """
        try:
            json_match = re.search(r'```json\s*(.*?)\s*```', state_content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
        except Exception as e:
            logger.debug(f"Could not extract JSON: {e}")
        return None

    def _append_vitals(
        self, vitals_series: Dict[str, List], date: str, vitals_data: Dict[str, Any]
    ):
        """Append vital signs to timeseries."""
        vitals = vitals_data.get("vital_signs", {})

        # Extract key vital parameters
        params = {
            "heart_rate": vitals.get("hemodynamics", {}).get("heart_rate"),
            "blood_pressure_systolic": vitals.get("hemodynamics", {}).get("blood_pressure", {}).get("systolic"),
            "blood_pressure_diastolic": vitals.get("hemodynamics", {}).get("blood_pressure", {}).get("diastolic"),
            "mean_arterial_pressure": vitals.get("hemodynamics", {}).get("blood_pressure", {}).get("map"),
            "respiratory_rate": vitals.get("respiratory", {}).get("respiratory_rate"),
            "spo2": vitals.get("respiratory", {}).get("oxygen_saturation"),
            "temperature": vitals.get("temperature", {}).get("current"),
        }

        for param_name, value in params.items():
            if value is not None:
                if param_name not in vitals_series:
                    vitals_series[param_name] = []
                vitals_series[param_name].append({"date": date, "value": value})

    def _append_labs(
        self, labs_series: Dict[str, List], date: str, labs_data: Dict[str, Any]
    ):
        """Append lab values to timeseries."""
        labs = labs_data.get("lab_values", {})

        # Extract key lab parameters
        params = {
            "lactate": labs.get("chemistry", {}).get("lactate", {}).get("value"),
            "creatinine": labs.get("chemistry", {}).get("creatinine", {}).get("value"),
            "bilirubin": labs.get("chemistry", {}).get("bilirubin_total", {}).get("value"),
            "platelets": labs.get("hematology", {}).get("platelets", {}).get("value"),
            "wbc": labs.get("hematology", {}).get("wbc", {}).get("value"),
            "crp": labs.get("inflammatory_markers", {}).get("crp", {}).get("value"),
            "procalcitonin": labs.get("inflammatory_markers", {}).get("procalcitonin", {}).get("value"),
        }

        for param_name, value in params.items():
            if value is not None:
                if param_name not in labs_series:
                    labs_series[param_name] = []
                labs_series[param_name].append({"date": date, "value": value})

    def _format_historical_data(self, historical_data: Dict[str, Any]) -> str:
        """
        Format historical data for prompt.

        Args:
            historical_data: Dictionary with timeseries data

        Returns:
            Formatted prompt string
        """
        lines = ["## HISTORICAL CLINICAL DATA FOR TREND ANALYSIS\n"]

        # Format vitals
        if historical_data["vitals"]:
            lines.append("### Vital Signs Trends\n")
            for param_name, timeseries in historical_data["vitals"].items():
                lines.append(f"**{param_name}**:")
                for point in timeseries:
                    lines.append(f"  - {point['date']}: {point['value']}")
                lines.append("")

        # Format labs
        if historical_data["labs"]:
            lines.append("### Laboratory Values Trends\n")
            for param_name, timeseries in historical_data["labs"].items():
                lines.append(f"**{param_name}**:")
                for point in timeseries:
                    lines.append(f"  - {point['date']}: {point['value']}")
                lines.append("")

        # Format SOFA
        if historical_data["sofa"]:
            lines.append("### SOFA Score Trend\n")
            for point in historical_data["sofa"]:
                lines.append(f"  - {point['date']}: {point['value']}/24")
            lines.append("")

        return "\n".join(lines)

    def _format_no_data_prompt(self) -> str:
        """Format prompt when no historical data is available."""
        return """## HISTORICAL CLINICAL DATA FOR TREND ANALYSIS

**Note:** No historical data available. This is the first day of monitoring for this patient.

Return a JSON response indicating that trend analysis cannot be performed without historical data.
"""

    def validate_output(self, output: str) -> bool:
        """
        Validate trend analysis output.

        Args:
            output: Agent output string

        Returns:
            True if output is valid
        """
        try:
            data = self.parse_output(output)

            # Check required fields
            if "trend_analysis" not in data:
                logger.error("Missing trend_analysis in output")
                return False

            if "summary" not in data:
                logger.error("Missing summary in output")
                return False

            # Validate summary counts
            summary = data["summary"]
            required_counts = ["deteriorating_count", "improving_count", "stable_count"]
            for count_field in required_counts:
                if count_field not in summary:
                    logger.error(f"Missing {count_field} in summary")
                    return False

            return True

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False

    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        Parse trend analysis output.

        Args:
            output: Agent output string

        Returns:
            Parsed dictionary
        """
        # Extract JSON
        json_match = re.search(r'```json\s*(.*?)\s*```', output, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found in output")

        return json.loads(json_match.group(1))

    def get_concerning_trends(self) -> List[Dict[str, Any]]:
        """
        Get list of concerning trends from latest analysis.

        Returns:
            List of concerning trend dictionaries
        """
        try:
            state_content = self.state_manager.load("trends")
            if not state_content:
                return []

            data = self._extract_json_from_state(state_content)
            if not data:
                return []

            return data.get("concerning_trends", [])

        except Exception as e:
            logger.error(f"Could not load concerning trends: {e}")
            return []

    def get_trend_summary(self) -> Dict[str, Any]:
        """
        Get trend analysis summary from latest analysis.

        Returns:
            Summary dictionary
        """
        try:
            state_content = self.state_manager.load("trends")
            if not state_content:
                return {}

            data = self._extract_json_from_state(state_content)
            if not data:
                return {}

            return data.get("summary", {})

        except Exception as e:
            logger.error(f"Could not load trend summary: {e}")
            return {}
