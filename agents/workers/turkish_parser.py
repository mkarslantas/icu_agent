"""
Turkish Parser Agent

This agent parses Turkish clinical notes into structured JSON format.
It handles Turkish number conversions, medical terminology, and extracts
all clinical parameters including vitals, labs, and treatment plans.
"""

import json
import logging
import re
from typing import Any, Dict

from agents.base.agent import BaseAgent

logger = logging.getLogger(__name__)


class TurkishParserAgent(BaseAgent):
    """
    Parses Turkish clinical notes into structured JSON.

    This agent:
    - Converts Turkish numbers to numerals (e.g., "nokta on beş" -> 0.15)
    - Extracts patient information, vitals, labs, and plans
    - Validates data completeness and accuracy
    - Returns structured JSON for downstream processing

    Uses prompt: prompts/core/01-parse-note.md
    Saves to: 01_parsed.md
    """

    def __init__(self, state_manager, config=None):
        """
        Initialize the Turkish Parser Agent.

        Args:
            state_manager: StateManager instance
            config: Optional configuration dict
        """
        super().__init__(
            name="TurkishParser",
            prompt_path="prompts/core/01-parse-note.md",
            state_manager=state_manager,
            config=config,
        )

    def prepare_input(self, context: Dict[str, Any]) -> str:
        """
        Prepare the clinical note for parsing.

        Args:
            context: Dictionary containing either:
                - "raw_note": The clinical note text directly
                - OR will load from 00_input.md in state

        Returns:
            Formatted input string with the clinical note
        """
        # Try to get raw note from context first
        if "raw_note" in context:
            note = context["raw_note"]
            logger.debug("Using raw_note from context")
        else:
            # Load from state (00_input.md)
            note = self.state_manager.load("input")
            if not note:
                raise ValueError("No clinical note found in context or state")
            logger.debug("Loaded note from state (00_input.md)")

        # Format the input
        input_text = f"""## TURKISH CLINICAL NOTE TO PARSE

```
{note.strip()}
```

Parse this Turkish clinical note and return ONLY valid JSON (no markdown, no explanations).
Convert all Turkish numbers to numerals and extract all clinical parameters.
"""

        logger.info(f"Prepared input for Turkish parser ({len(note)} chars)")
        return input_text

    def validate_output(self, output: str) -> bool:
        """
        Validate that the output is valid JSON with required fields.

        Args:
            output: Raw output from Claude

        Returns:
            True if valid, False otherwise
        """
        try:
            # Try to extract JSON from markdown code blocks if present
            cleaned_output = self._extract_json(output)

            # Parse JSON
            data = json.loads(cleaned_output)

            # Check required top-level fields
            required_fields = [
                "patient_info",
                "hemodynamics",
                "respiratory",
                "fluids_electrolytes",
                "data_completeness"
            ]

            for field in required_fields:
                if field not in data:
                    logger.warning(f"Missing required field: {field}")
                    return False

            # Check data completeness
            completeness = data.get("data_completeness", {})
            overall_score = completeness.get("overall_score", 0)

            if overall_score < 60:
                logger.warning(f"Data completeness too low: {overall_score}%")
                return False

            logger.info(f"Output validation passed (completeness: {overall_score}%)")
            return True

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return False
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False

    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        Parse the validated JSON output.

        Args:
            output: Validated output string

        Returns:
            Dictionary containing all parsed clinical data
        """
        # Extract JSON from markdown if needed
        cleaned_output = self._extract_json(output)

        # Parse JSON
        data = json.loads(cleaned_output)

        # Log parsing summary
        completeness = data.get("data_completeness", {})
        logger.info(
            f"Parsed clinical note: "
            f"completeness={completeness.get('overall_score', 0)}%, "
            f"confidence={completeness.get('parsing_confidence', 'unknown')}"
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
        # Remove markdown code blocks (```json ... ``` or ``` ... ```)
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

        # No markdown found, return as-is
        return text

    def get_parsed_vitals(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract vitals from parsed data.

        Args:
            parsed_data: Parsed clinical data

        Returns:
            Dictionary containing vital signs
        """
        return {
            "hemodynamics": parsed_data.get("hemodynamics", {}),
            "respiratory": parsed_data.get("respiratory", {}),
        }

    def get_parsed_labs(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract labs from parsed data.

        Args:
            parsed_data: Parsed clinical data

        Returns:
            Dictionary containing laboratory values
        """
        return {
            "fluids_electrolytes": parsed_data.get("fluids_electrolytes", {}),
            "hematology": parsed_data.get("hematology", {}),
            "inflammatory_markers": parsed_data.get("inflammatory_markers", {}),
            "blood_gas": parsed_data.get("blood_gas", {}),
            "coagulation": parsed_data.get("coagulation", {}),
        }
