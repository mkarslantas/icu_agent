"""
Critical Value Checker Agent

This agent identifies critical clinical values that require immediate attention.
It categorizes abnormalities by severity and provides actionable recommendations.
"""

import json
import logging
import re
import yaml
from pathlib import Path
from typing import Any, Dict, List

from agents.base.agent import BaseAgent

logger = logging.getLogger(__name__)


class CriticalCheckerAgent(BaseAgent):
    """
    Checks for critical values across all clinical parameters.

    This agent:
    - Loads reference ranges from config/reference-ranges.yaml
    - Compares vital signs and labs against critical thresholds
    - Categorizes by severity (life-threatening, critical, urgent)
    - Provides specific action recommendations
    - Generates alerts for notification system

    Uses prompt: prompts/analysis/critical-checker.md
    Saves to: 05_critical.md
    """

    def __init__(self, state_manager, config=None):
        """
        Initialize the Critical Checker Agent.

        Args:
            state_manager: StateManager instance
            config: Optional configuration dict
        """
        super().__init__(
            name="CriticalChecker",
            prompt_path="prompts/analysis/critical-checker.md",
            state_manager=state_manager,
            config=config,
        )

        # Load reference ranges
        self.reference_ranges = self._load_reference_ranges()

    def _load_reference_ranges(self) -> Dict[str, Any]:
        """
        Load reference ranges from configuration file.

        Returns:
            Dictionary containing reference ranges
        """
        config_path = Path("config/reference-ranges.yaml")

        if not config_path.exists():
            logger.warning(f"Reference ranges file not found: {config_path}")
            return {}

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                ranges = yaml.safe_load(f)
            logger.debug(f"Loaded reference ranges from {config_path}")
            return ranges
        except Exception as e:
            logger.error(f"Failed to load reference ranges: {e}")
            return {}

    def prepare_input(self, context: Dict[str, Any]) -> str:
        """
        Prepare input for critical value checking.

        Args:
            context: Dictionary containing:
                - Optionally "vitals_data" and "labs_data"
                - OR will load from 02_vitals.md and 03_labs.md

        Returns:
            Formatted input string with all values and thresholds
        """
        # Load vitals
        if "vitals_data" in context:
            vitals_data = context["vitals_data"]
        else:
            vitals_state = self.state_manager.load("vitals")
            if vitals_state:
                vitals_data = self._extract_json_from_markdown(vitals_state)
            else:
                vitals_data = {}

        # Load labs
        if "labs_data" in context:
            labs_data = context["labs_data"]
        else:
            labs_state = self.state_manager.load("labs")
            if labs_state:
                labs_data = self._extract_json_from_markdown(labs_state)
            else:
                labs_data = {}

        if not vitals_data and not labs_data:
            raise ValueError("No clinical data found for critical value checking")

        # Extract critical thresholds from reference ranges
        critical_thresholds = self._extract_critical_thresholds()

        # Format input
        input_text = f"""## CLINICAL DATA

### Vital Signs
```json
{json.dumps(vitals_data.get('vitals', {}), indent=2, ensure_ascii=False)}
```

### Laboratory Values
```json
{json.dumps(labs_data.get('labs', {}), indent=2, ensure_ascii=False)}
```

### Critical Thresholds
```json
{json.dumps(critical_thresholds, indent=2, ensure_ascii=False)}
```

Analyze all parameters and identify critical values.
Categorize by severity and provide specific action recommendations.
Return ONLY JSON.
"""

        logger.info("Prepared input for critical value checking")
        return input_text

    def validate_output(self, output: str) -> bool:
        """
        Validate that the output contains proper critical analysis.

        Args:
            output: Raw output from Claude

        Returns:
            True if valid, False otherwise
        """
        try:
            # Extract JSON
            cleaned_output = self._extract_json(output)
            data = json.loads(cleaned_output)

            # Check for critical_analysis field
            if "critical_analysis" not in data:
                logger.warning("Missing 'critical_analysis' field in output")
                return False

            analysis = data["critical_analysis"]

            # Check for severity categories
            required_categories = ["life_threatening", "critical", "urgent"]
            for category in required_categories:
                if category not in analysis:
                    logger.warning(f"Missing severity category: {category}")
                    return False

            # Check for summary
            if "summary" not in analysis:
                logger.warning("Missing summary in critical analysis")
                return False

            # Validate structure of critical values
            for category in required_categories:
                values = analysis[category]
                if not isinstance(values, list):
                    logger.warning(f"Category {category} should be a list")
                    return False

                # Check structure of each critical value
                for value in values:
                    if not all(key in value for key in ["parameter", "value", "severity"]):
                        logger.warning(f"Critical value missing required fields: {value}")
                        return False

            logger.info("Critical analysis validation passed")
            return True

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return False
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False

    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        Parse the validated critical analysis output.

        Args:
            output: Validated output string

        Returns:
            Dictionary containing critical analysis
        """
        # Extract and parse JSON
        cleaned_output = self._extract_json(output)
        data = json.loads(cleaned_output)

        # Log summary
        analysis = data.get("critical_analysis", {})
        summary = analysis.get("summary", {})

        total_critical = summary.get("total_critical_values", 0)
        highest_severity = summary.get("highest_severity", "none")

        logger.info(
            f"Critical analysis complete: "
            f"total={total_critical}, "
            f"severity={highest_severity}"
        )

        return data

    def _extract_json(self, text: str) -> str:
        """Extract JSON from markdown code blocks if present."""
        text = text.strip()

        json_block_pattern = r"```json\s*(.*?)\s*```"
        match = re.search(json_block_pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()

        code_block_pattern = r"```\s*(.*?)\s*```"
        match = re.search(code_block_pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()

        return text

    def _extract_json_from_markdown(self, markdown: str) -> Dict[str, Any]:
        """Extract JSON data from a markdown state file."""
        json_str = self._extract_json(markdown)
        return json.loads(json_str)

    def _extract_critical_thresholds(self) -> Dict[str, Any]:
        """
        Extract critical thresholds from reference ranges.

        Returns:
            Dictionary of critical thresholds organized by severity
        """
        if not self.reference_ranges:
            return {}

        thresholds = {
            "life_threatening": {},
            "critical": {},
            "urgent": {}
        }

        # Extract from critical_thresholds section if it exists
        if "critical_thresholds" in self.reference_ranges:
            for item in self.reference_ranges["critical_thresholds"].get("immediate_intervention", []):
                param = item.get("parameter")
                if param:
                    thresholds["life_threatening"][param] = {
                        "condition": item.get("condition"),
                        "severity": item.get("severity")
                    }

        # Add specific thresholds from individual sections
        # Vitals
        vitals = self.reference_ranges.get("vitals", {})
        if "blood_pressure" in vitals:
            map_data = vitals["blood_pressure"].get("map", {})
            if "critical_low" in map_data:
                thresholds["life_threatening"]["MAP"] = {
                    "condition": f"< {map_data['critical_low']} mmHg",
                    "threshold": map_data["critical_low"]
                }

        # Blood gas lactate
        bg = self.reference_ranges.get("blood_gas", {})
        if "lactate" in bg:
            lactate_data = bg["lactate"]
            if "critical_high" in lactate_data:
                thresholds["critical"]["Lactate"] = {
                    "condition": f"> {lactate_data['critical_high']} mmol/L",
                    "threshold": lactate_data["critical_high"]
                }

        # Chemistry - Potassium
        chem = self.reference_ranges.get("chemistry", {})
        if "potassium" in chem:
            k_data = chem["potassium"]
            if "critical_low" in k_data and "critical_high" in k_data:
                thresholds["life_threatening"]["Potassium"] = {
                    "condition": f"< {k_data['critical_low']} or > {k_data['critical_high']} mEq/L",
                    "min": k_data["critical_low"],
                    "max": k_data["critical_high"]
                }

        return thresholds

    def get_life_threatening_values(self, critical_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get list of life-threatening values.

        Args:
            critical_data: Critical analysis data

        Returns:
            List of life-threatening value dictionaries
        """
        analysis = critical_data.get("critical_analysis", {})
        return analysis.get("life_threatening", [])

    def requires_immediate_action(self, critical_data: Dict[str, Any]) -> bool:
        """
        Check if immediate action is required.

        Args:
            critical_data: Critical analysis data

        Returns:
            True if immediate action is required
        """
        analysis = critical_data.get("critical_analysis", {})
        summary = analysis.get("summary", {})
        return summary.get("requires_immediate_action", False)
