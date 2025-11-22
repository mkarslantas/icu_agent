"""
Alert Generator Agent

This agent generates actionable clinical alerts based on:
- Critical laboratory and vital sign values
- Concerning parameter trends
- SOFA score changes
- Multi-organ dysfunction patterns

The agent categorizes alerts by urgency and provides specific
recommendations for clinical intervention.
"""

import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from agents.base.agent import BaseAgent

logger = logging.getLogger(__name__)


class AlertGeneratorAgent(BaseAgent):
    """
    Generates prioritized clinical alerts for ICU patients.

    This agent:
    - Reviews critical values, trends, and SOFA scores
    - Generates alerts with urgency levels (immediate, urgent, monitor)
    - Provides specific clinical recommendations
    - Tracks alert history to avoid alert fatigue
    - Outputs alerts in Turkish for clinical staff

    Alert urgency levels:
    - **Immediate** (ACİL): Life-threatening, requires instant intervention
    - **Urgent** (ÖNEMLİ): Significant abnormality, needs attention within 1-2 hours
    - **Monitor** (TAKİP): Concerning trend, requires close monitoring

    Output format (JSON):
    {
        "alerts": [
            {
                "alert_id": "ALERT-2025-11-20-001",
                "timestamp": "2025-11-20T14:30:00",
                "urgency": "immediate",
                "category": "hemodynamic",
                "title": "Kritik Hipotansiyon",
                "description": "MAP 55 mmHg - hedef değerin altında",
                "values": {
                    "parameter": "mean_arterial_pressure",
                    "current_value": 55,
                    "normal_range": "65-110 mmHg",
                    "severity": "life-threatening"
                },
                "recommendation": "Norepinefrin dozu derhal artırılmalı (mevcut doz + 0.05 mcg/kg/dk), volüm durumu değerlendirilmeli",
                "auto_generated": true
            }
        ],
        "summary": {
            "total_alerts": 5,
            "immediate_count": 1,
            "urgent_count": 2,
            "monitor_count": 2,
            "categories": {
                "hemodynamic": 1,
                "respiratory": 1,
                "metabolic": 2,
                "renal": 1
            }
        }
    }
    """

    def __init__(self, *args, **kwargs):
        """Initialize Alert Generator Agent."""
        super().__init__(
            name="AlertGenerator",
            prompt_path="prompts/alerts/20-alert-generation.md",
            *args,
            **kwargs
        )

        # Alert generation configuration
        self.config_alerts = {
            "max_alerts_per_run": 20,
            "alert_id_prefix": "ALERT",
        }

    def prepare_input(self, context: Dict[str, Any]) -> str:
        """
        Prepare input for alert generation.

        Loads critical values, trends, and SOFA scores.

        Args:
            context: Execution context

        Returns:
            Formatted prompt with analysis data
        """
        # Load critical analysis
        critical_data = self._load_json_phase("critical")

        # Load trend analysis
        trends_data = self._load_json_phase("trends")

        # Load SOFA scores
        scores_data = self._load_json_phase("scores")

        # Format for prompt
        return self._format_analysis_data(critical_data, trends_data, scores_data)

    def _load_json_phase(self, phase: str) -> Optional[Dict[str, Any]]:
        """
        Load JSON data from a state phase.

        Args:
            phase: Phase name

        Returns:
            Parsed JSON dictionary or None
        """
        state_content = self.state_manager.load(phase)
        if not state_content:
            return None

        try:
            json_match = re.search(r'```json\s*(.*?)\s*```', state_content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
        except Exception as e:
            logger.debug(f"Could not load JSON from {phase}: {e}")

        return None

    def _format_analysis_data(
        self,
        critical_data: Optional[Dict[str, Any]],
        trends_data: Optional[Dict[str, Any]],
        scores_data: Optional[Dict[str, Any]]
    ) -> str:
        """
        Format analysis data for prompt.

        Args:
            critical_data: Critical value analysis
            trends_data: Trend analysis
            scores_data: SOFA scores

        Returns:
            Formatted prompt string
        """
        lines = ["## CLINICAL DATA FOR ALERT GENERATION\n"]

        # Critical values section
        if critical_data:
            lines.append("### Critical Values\n")

            critical_analysis = critical_data.get("critical_analysis", {})

            # Life-threatening
            life_threatening = critical_analysis.get("life_threatening", [])
            if life_threatening:
                lines.append("**Life-Threatening:**")
                for item in life_threatening:
                    param = item.get("parameter", "Unknown")
                    value = item.get("value", "N/A")
                    ref = item.get("reference_range", "N/A")
                    lines.append(f"  - {param}: {value} (Normal: {ref})")
                lines.append("")

            # Critical
            critical = critical_analysis.get("critical", [])
            if critical:
                lines.append("**Critical:**")
                for item in critical:
                    param = item.get("parameter", "Unknown")
                    value = item.get("value", "N/A")
                    ref = item.get("reference_range", "N/A")
                    lines.append(f"  - {param}: {value} (Normal: {ref})")
                lines.append("")

            # Urgent
            urgent = critical_analysis.get("urgent", [])
            if urgent:
                lines.append("**Urgent:**")
                for item in urgent:
                    param = item.get("parameter", "Unknown")
                    value = item.get("value", "N/A")
                    ref = item.get("reference_range", "N/A")
                    lines.append(f"  - {param}: {value} (Normal: {ref})")
                lines.append("")

        # Trends section
        if trends_data:
            lines.append("### Concerning Trends\n")

            concerning_trends = trends_data.get("concerning_trends", [])
            if concerning_trends:
                for trend in concerning_trends:
                    param = trend.get("parameter", "Unknown")
                    trend_dir = trend.get("trend", "N/A")
                    velocity = trend.get("velocity", 0)
                    significance = trend.get("clinical_significance", "unknown")
                    lines.append(f"  - **{param}**: {trend_dir} (velocity: {velocity}, significance: {significance})")
                lines.append("")
            else:
                lines.append("  No concerning trends identified\n")

        # SOFA scores section
        if scores_data:
            lines.append("### SOFA Score\n")

            scores = scores_data.get("scores", {})
            sofa = scores.get("sofa", {})

            total_score = sofa.get("total_score", "N/A")
            delta_sofa = sofa.get("delta_sofa")

            lines.append(f"  - **Total SOFA**: {total_score}/24")
            if delta_sofa is not None:
                lines.append(f"  - **Delta SOFA**: {delta_sofa:+d} points")
            lines.append("")

        if not critical_data and not trends_data and not scores_data:
            lines.append("**Note:** No analysis data available for alert generation.\n")

        return "\n".join(lines)

    def validate_output(self, output: str) -> bool:
        """
        Validate alert generation output.

        Args:
            output: Agent output string

        Returns:
            True if output is valid
        """
        try:
            data = self.parse_output(output)

            # Check required fields
            if "alerts" not in data:
                logger.error("Missing alerts in output")
                return False

            if "summary" not in data:
                logger.error("Missing summary in output")
                return False

            # Validate alerts structure
            alerts = data["alerts"]
            if not isinstance(alerts, list):
                logger.error("Alerts must be a list")
                return False

            # Validate each alert
            for alert in alerts:
                required_fields = ["urgency", "category", "title", "description", "recommendation"]
                for field in required_fields:
                    if field not in alert:
                        logger.error(f"Alert missing required field: {field}")
                        return False

                # Validate urgency level
                if alert["urgency"] not in ["immediate", "urgent", "monitor"]:
                    logger.error(f"Invalid urgency level: {alert['urgency']}")
                    return False

            # Validate summary
            summary = data["summary"]
            required_counts = ["total_alerts", "immediate_count", "urgent_count", "monitor_count"]
            for count_field in required_counts:
                if count_field not in summary:
                    logger.error(f"Summary missing {count_field}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False

    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        Parse alert generation output.

        Args:
            output: Agent output string

        Returns:
            Parsed dictionary
        """
        # Extract JSON
        json_match = re.search(r'```json\s*(.*?)\s*```', output, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found in output")

        data = json.loads(json_match.group(1))

        # Add timestamps if missing
        if "alerts" in data:
            current_time = datetime.now().isoformat()
            for i, alert in enumerate(data["alerts"]):
                if "timestamp" not in alert:
                    alert["timestamp"] = current_time
                if "alert_id" not in alert:
                    alert["alert_id"] = self._generate_alert_id(i)

        return data

    def _generate_alert_id(self, index: int) -> str:
        """
        Generate unique alert ID.

        Args:
            index: Alert index

        Returns:
            Alert ID string
        """
        date_str = self.state_manager.date
        return f"{self.config_alerts['alert_id_prefix']}-{date_str}-{index+1:03d}"

    def get_immediate_alerts(self) -> List[Dict[str, Any]]:
        """
        Get immediate priority alerts from latest generation.

        Returns:
            List of immediate alert dictionaries
        """
        try:
            state_content = self.state_manager.load("alerts")
            if not state_content:
                return []

            data = self._load_json_phase("alerts")
            if not data:
                return []

            alerts = data.get("alerts", [])
            return [a for a in alerts if a.get("urgency") == "immediate"]

        except Exception as e:
            logger.error(f"Could not load immediate alerts: {e}")
            return []

    def get_all_alerts(self) -> List[Dict[str, Any]]:
        """
        Get all alerts from latest generation.

        Returns:
            List of all alert dictionaries
        """
        try:
            state_content = self.state_manager.load("alerts")
            if not state_content:
                return []

            data = self._load_json_phase("alerts")
            if not data:
                return []

            return data.get("alerts", [])

        except Exception as e:
            logger.error(f"Could not load alerts: {e}")
            return []

    def get_alerts_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get alerts filtered by category.

        Args:
            category: Alert category (hemodynamic, respiratory, metabolic, etc.)

        Returns:
            List of alert dictionaries for the category
        """
        try:
            all_alerts = self.get_all_alerts()
            return [a for a in all_alerts if a.get("category") == category]

        except Exception as e:
            logger.error(f"Could not filter alerts by category: {e}")
            return []
