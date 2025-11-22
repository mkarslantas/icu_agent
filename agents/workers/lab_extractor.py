"""
Laboratory Values Extractor Agent

This agent extracts laboratory values from clinical notes or parsed data.
It validates lab values, tracks trends, and flags critical abnormalities.
"""

import json
import logging
import re
from typing import Any, Dict, List

from agents.base.agent import BaseAgent

logger = logging.getLogger(__name__)


class LabExtractorAgent(BaseAgent):
    """
    Extracts laboratory values from clinical data.

    This agent:
    - Extracts hematology, chemistry, inflammatory markers, blood gas, coagulation
    - Validates value ranges
    - Tracks trends (improvement/worsening)
    - Flags critical values (K+<2.5/>6.5, Lactate>4, etc.)
    - Works with both raw notes and parsed JSON

    Uses prompt: prompts/core/03-extract-labs.md
    Saves to: 03_labs.md
    """

    # Critical thresholds
    CRITICAL_THRESHOLDS = {
        "potassium": {"min": 2.5, "max": 6.5},
        "glucose": {"min": 40, "max": 400},
        "lactate": {"max": 4.0},
        "hemoglobin": {"min": 7.0},
        "platelet": {"min": 20},
        "ph": {"min": 7.2, "max": 7.6},
    }

    def __init__(self, state_manager, config=None):
        """
        Initialize the Lab Extractor Agent.

        Args:
            state_manager: StateManager instance
            config: Optional configuration dict
        """
        super().__init__(
            name="LabExtractor",
            prompt_path="prompts/core/03-extract-labs.md",
            state_manager=state_manager,
            config=config,
        )

    def prepare_input(self, context: Dict[str, Any]) -> str:
        """
        Prepare input for laboratory values extraction.

        Args:
            context: Dictionary containing either:
                - "parsed_data": Already parsed JSON
                - "raw_note": Raw clinical note
                - OR will load from 01_parsed.md or 00_input.md

        Returns:
            Formatted input string
        """
        # Try to get parsed data first
        if "parsed_data" in context:
            data = context["parsed_data"]
            logger.debug("Using parsed_data from context")
        else:
            # Try to load from state (01_parsed.md)
            parsed_state = self.state_manager.load("parsed")
            if parsed_state:
                # Extract JSON from markdown
                data = self._extract_json_from_markdown(parsed_state)
                logger.debug("Loaded parsed data from state (01_parsed.md)")
            else:
                # Fall back to raw note
                raw_note = context.get("raw_note") or self.state_manager.load("input")
                if not raw_note:
                    raise ValueError("No clinical data found in context or state")

                data = raw_note
                logger.debug("Using raw note as fallback")

        # Format the input
        if isinstance(data, dict):
            input_text = f"""## CLINICAL DATA

```json
{json.dumps(data, indent=2, ensure_ascii=False)}
```

Extract ALL laboratory values from this data and return as JSON.
Include trend analysis if previous values are mentioned.
Flag any critical values.
"""
        else:
            input_text = f"""## CLINICAL NOTE

```
{data}
```

Extract all laboratory values from this Turkish clinical note and return as JSON.
Convert Turkish numbers, identify trends, and flag critical values.
"""

        logger.info("Prepared input for lab values extraction")
        return input_text

    def validate_output(self, output: str) -> bool:
        """
        Validate that the output contains valid laboratory values.

        Args:
            output: Raw output from Claude

        Returns:
            True if valid, False otherwise
        """
        try:
            # Extract JSON
            cleaned_output = self._extract_json(output)
            data = json.loads(cleaned_output)

            # Check for labs field
            if "labs" not in data:
                logger.warning("Missing 'labs' field in output")
                return False

            labs = data["labs"]

            # Check for at least one lab category
            lab_categories = ["hematology", "chemistry", "inflammatory_markers", "blood_gas", "coagulation"]
            has_any = any(category in labs for category in lab_categories)

            if not has_any:
                logger.warning("No laboratory categories found in output")
                return False

            # Validate specific values if present
            if "chemistry" in labs:
                chem = labs["chemistry"]

                # Check potassium range
                if "potassium" in chem:
                    k_val = chem["potassium"].get("value")
                    if k_val and not (1.0 <= k_val <= 10.0):
                        logger.warning(f"Potassium out of physiological range: {k_val}")
                        return False

                # Check creatinine range
                if "creatinine" in chem:
                    cr_val = chem["creatinine"].get("value")
                    if cr_val and not (0.1 <= cr_val <= 20.0):
                        logger.warning(f"Creatinine out of physiological range: {cr_val}")
                        return False

            # Validate blood gas if present
            if "blood_gas" in labs:
                bg = labs["blood_gas"]

                if "ph" in bg:
                    ph_val = bg.get("ph") if isinstance(bg.get("ph"), (int, float)) else bg.get("ph", {}).get("value")
                    if ph_val and not (6.8 <= ph_val <= 8.0):
                        logger.warning(f"pH out of physiological range: {ph_val}")
                        return False

            logger.info("Laboratory values validation passed")
            return True

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return False
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False

    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        Parse the validated laboratory values output.

        Args:
            output: Validated output string

        Returns:
            Dictionary containing laboratory data
        """
        # Extract and parse JSON
        cleaned_output = self._extract_json(output)
        data = json.loads(cleaned_output)

        # Log summary
        labs = data.get("labs", {})
        critical_values = labs.get("critical_values", [])

        # Count total lab values
        total_values = 0
        for category in ["hematology", "chemistry", "inflammatory_markers", "blood_gas", "coagulation"]:
            if category in labs:
                total_values += len(labs[category])

        logger.info(
            f"Extracted laboratory values: "
            f"total_values={total_values}, "
            f"critical_values={len(critical_values)}"
        )

        return data

    def _extract_json(self, text: str) -> str:
        """
        Extract JSON from markdown code blocks if present.

        Args:
            text: Raw text that may contain markdown

        Returns:
            Cleaned JSON string
        """
        text = text.strip()

        # Pattern 1: ```json ... ```
        json_block_pattern = r"```json\s*(.*?)\s*```"
        match = re.search(json_block_pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Pattern 2: ``` ... ```
        code_block_pattern = r"```\s*(.*?)\s*```"
        match = re.search(code_block_pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()

        return text

    def _extract_json_from_markdown(self, markdown: str) -> Dict[str, Any]:
        """
        Extract JSON data from a markdown state file.

        Args:
            markdown: Markdown content with JSON code block

        Returns:
            Parsed JSON dictionary
        """
        json_str = self._extract_json(markdown)
        return json.loads(json_str)

    def get_critical_values(self, labs_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get list of critical laboratory values.

        Args:
            labs_data: Labs data dictionary

        Returns:
            List of critical value dictionaries
        """
        labs = labs_data.get("labs", {})
        return labs.get("critical_values", [])

    def get_trends(self, labs_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract trends from lab data.

        Args:
            labs_data: Labs data dictionary

        Returns:
            Dictionary mapping parameter names to trend directions
        """
        trends = {}
        labs = labs_data.get("labs", {})

        # Look for trend information in each category
        for category_name, category_data in labs.items():
            if isinstance(category_data, dict):
                for param_name, param_data in category_data.items():
                    if isinstance(param_data, dict) and "trend" in param_data:
                        trends[param_name] = param_data["trend"]

        return trends
