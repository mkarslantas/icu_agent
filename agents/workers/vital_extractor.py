"""
Vital Signs Extractor Agent

This agent extracts vital signs from clinical notes or parsed data.
It validates vital sign values and flags critical abnormalities.
"""

import json
import logging
import re
from typing import Any, Dict

from agents.base.agent import BaseAgent

logger = logging.getLogger(__name__)


class VitalExtractorAgent(BaseAgent):
    """
    Extracts vital signs from clinical data.

    This agent:
    - Extracts heart rate, blood pressure, respiratory rate, SpO2, temperature
    - Validates numeric ranges
    - Flags critical values (MAP<65, HR<40/>180, SpO2<90, etc.)
    - Works with both raw notes and parsed JSON

    Uses prompt: prompts/core/02-extract-vitals.md
    Saves to: 02_vitals.md
    """

    # Critical thresholds
    CRITICAL_THRESHOLDS = {
        "heart_rate": {"min": 40, "max": 180},
        "map": {"min": 65},
        "respiratory_rate": {"min": 8, "max": 40},
        "spo2": {"min": 90},
        "temperature": {"min": 35.0, "max": 40.0},
    }

    def __init__(self, state_manager, config=None):
        """
        Initialize the Vital Extractor Agent.

        Args:
            state_manager: StateManager instance
            config: Optional configuration dict
        """
        super().__init__(
            name="VitalExtractor",
            prompt_path="prompts/core/02-extract-vitals.md",
            state_manager=state_manager,
            config=config,
        )

    def prepare_input(self, context: Dict[str, Any]) -> str:
        """
        Prepare input for vital signs extraction.

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

Extract ONLY vital signs from this data and return as JSON.
Include critical flags for any abnormal values.
"""
        else:
            input_text = f"""## CLINICAL NOTE

```
{data}
```

Extract vital signs from this Turkish clinical note and return as JSON.
Convert Turkish numbers and include critical flags.
"""

        logger.info("Prepared input for vital signs extraction")
        return input_text

    def validate_output(self, output: str) -> bool:
        """
        Validate that the output contains valid vital signs.

        Args:
            output: Raw output from Claude

        Returns:
            True if valid, False otherwise
        """
        try:
            # Extract JSON
            cleaned_output = self._extract_json(output)
            data = json.loads(cleaned_output)

            # Check for vitals field
            if "vitals" not in data:
                logger.warning("Missing 'vitals' field in output")
                return False

            vitals = data["vitals"]

            # Check for at least some required vital signs
            required_any = ["heart_rate", "blood_pressure", "respiratory_rate", "spo2"]
            has_any = any(field in vitals for field in required_any)

            if not has_any:
                logger.warning("No vital signs found in output")
                return False

            # Validate numeric ranges if present
            if "heart_rate" in vitals:
                hr = vitals["heart_rate"].get("value")
                if hr and not (20 <= hr <= 250):
                    logger.warning(f"Heart rate out of physiological range: {hr}")
                    return False

            if "blood_pressure" in vitals:
                bp = vitals["blood_pressure"]
                map_val = bp.get("map")
                if map_val and not (30 <= map_val <= 200):
                    logger.warning(f"MAP out of physiological range: {map_val}")
                    return False

            logger.info("Vital signs validation passed")
            return True

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return False
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False

    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        Parse the validated vital signs output.

        Args:
            output: Validated output string

        Returns:
            Dictionary containing vital signs data
        """
        # Extract and parse JSON
        cleaned_output = self._extract_json(output)
        data = json.loads(cleaned_output)

        # Log summary
        vitals = data.get("vitals", {})
        critical_flags = vitals.get("critical_flags", [])

        logger.info(
            f"Extracted vital signs: "
            f"HR={vitals.get('heart_rate', {}).get('value', 'N/A')}, "
            f"MAP={vitals.get('blood_pressure', {}).get('map', 'N/A')}, "
            f"critical_flags={len(critical_flags)}"
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

    def get_critical_values(self, vitals_data: Dict[str, Any]) -> list:
        """
        Get list of critical vital signs.

        Args:
            vitals_data: Vitals data dictionary

        Returns:
            List of critical value dictionaries
        """
        vitals = vitals_data.get("vitals", {})
        return vitals.get("critical_flags", [])
