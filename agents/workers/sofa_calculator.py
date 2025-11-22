"""
SOFA Calculator Agent

This agent calculates SOFA (Sequential Organ Failure Assessment) score
and other ICU severity scores from patient clinical data.
"""

import json
import logging
import re
import yaml
from pathlib import Path
from typing import Any, Dict, Optional

from agents.base.agent import BaseAgent

logger = logging.getLogger(__name__)


class SofaCalculatorAgent(BaseAgent):
    """
    Calculates SOFA and other severity scores.

    This agent:
    - Calculates SOFA score (6 components, total 0-24)
    - Determines mortality risk based on SOFA total
    - Calculates delta SOFA (change from previous)
    - Optionally calculates APACHE-II and qSOFA
    - Loads scoring criteria from config/scoring-criteria.yaml

    Uses prompt: prompts/analysis/13-calculate-scores.md
    Saves to: 06_scores.md
    """

    def __init__(self, state_manager, config=None):
        """
        Initialize the SOFA Calculator Agent.

        Args:
            state_manager: StateManager instance
            config: Optional configuration dict
        """
        super().__init__(
            name="SofaCalculator",
            prompt_path="prompts/analysis/13-calculate-scores.md",
            state_manager=state_manager,
            config=config,
        )

        # Load scoring criteria
        self.scoring_criteria = self._load_scoring_criteria()

    def _load_scoring_criteria(self) -> Dict[str, Any]:
        """
        Load scoring criteria from configuration file.

        Returns:
            Dictionary containing scoring criteria
        """
        config_path = Path("config/scoring-criteria.yaml")

        if not config_path.exists():
            logger.warning(f"Scoring criteria file not found: {config_path}")
            return {}

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                criteria = yaml.safe_load(f)
            logger.debug(f"Loaded scoring criteria from {config_path}")
            return criteria
        except Exception as e:
            logger.error(f"Failed to load scoring criteria: {e}")
            return {}

    def prepare_input(self, context: Dict[str, Any]) -> str:
        """
        Prepare input for SOFA calculation.

        Args:
            context: Dictionary containing clinical data or will load from state

        Returns:
            Formatted input string with all required parameters
        """
        # Load all necessary data
        vitals_data = context.get("vitals_data") or self._load_state_json("vitals")
        labs_data = context.get("labs_data") or self._load_state_json("labs")
        parsed_data = context.get("parsed_data") or self._load_state_json("parsed")

        if not any([vitals_data, labs_data, parsed_data]):
            raise ValueError("No clinical data found for SOFA calculation")

        # Load historical SOFA scores for delta calculation
        history = self.state_manager.get_history(days=3)
        previous_sofa = self._extract_previous_sofa(history)

        # Extract required SOFA components
        sofa_components = self._extract_sofa_components(vitals_data, labs_data, parsed_data)

        # Format input
        input_text = f"""## CLINICAL DATA FOR SOFA CALCULATION

### Vital Signs
```json
{json.dumps(vitals_data.get('vitals', {}), indent=2, ensure_ascii=False)}
```

### Laboratory Values
```json
{json.dumps(labs_data.get('labs', {}), indent=2, ensure_ascii=False)}
```

### Additional Patient Data
```json
{json.dumps(parsed_data, indent=2, ensure_ascii=False) if parsed_data else "{}"}
```

### Previous SOFA Score
```json
{json.dumps(previous_sofa, indent=2) if previous_sofa else "null"}
```

### Scoring Criteria
```json
{json.dumps(self.scoring_criteria.get('sofa', {}), indent=2)}
```

Calculate SOFA score with all 6 components.
Include rationale for each component.
Calculate delta SOFA if previous score available.
Determine mortality risk from total score.
Return ONLY JSON.
"""

        logger.info("Prepared input for SOFA calculation")
        return input_text

    def validate_output(self, output: str) -> bool:
        """
        Validate that the output contains valid SOFA score.

        Args:
            output: Raw output from Claude

        Returns:
            True if valid, False otherwise
        """
        try:
            # Extract JSON
            cleaned_output = self._extract_json(output)
            data = json.loads(cleaned_output)

            # Check for scores field
            if "scores" not in data:
                logger.warning("Missing 'scores' field in output")
                return False

            scores = data["scores"]

            # Check for SOFA
            if "sofa" not in scores:
                logger.warning("Missing 'sofa' in scores")
                return False

            sofa = scores["sofa"]

            # Check for components
            if "components" not in sofa:
                logger.warning("Missing SOFA components")
                return False

            components = sofa["components"]

            # Check all 6 SOFA components
            required_components = [
                "respiratory",
                "coagulation",
                "hepatic",
                "cardiovascular",
                "neurological",
                "renal"
            ]

            for comp in required_components:
                if comp not in components:
                    logger.warning(f"Missing SOFA component: {comp}")
                    return False

                # Check score is valid (0-4)
                score = components[comp].get("score")
                if not isinstance(score, int) or not (0 <= score <= 4):
                    logger.warning(f"Invalid score for {comp}: {score}")
                    return False

            # Check total score
            total = sofa.get("total_score")
            if not isinstance(total, int) or not (0 <= total <= 24):
                logger.warning(f"Invalid total SOFA score: {total}")
                return False

            # Verify total equals sum of components
            component_sum = sum(components[comp]["score"] for comp in required_components)
            if total != component_sum:
                logger.warning(f"Total ({total}) != sum of components ({component_sum})")
                return False

            logger.info("SOFA calculation validation passed")
            return True

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return False
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False

    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        Parse the validated SOFA calculation output.

        Args:
            output: Validated output string

        Returns:
            Dictionary containing SOFA and other scores
        """
        # Extract and parse JSON
        cleaned_output = self._extract_json(output)
        data = json.loads(cleaned_output)

        # Log summary
        scores = data.get("scores", {})
        sofa = scores.get("sofa", {})

        total_score = sofa.get("total_score", 0)
        mortality_risk = sofa.get("mortality_risk", "unknown")
        severity = sofa.get("severity", "unknown")

        # Delta SOFA
        delta_sofa = scores.get("delta_sofa", {})
        change = delta_sofa.get("change")
        interpretation = delta_sofa.get("interpretation", "N/A")

        logger.info(
            f"SOFA calculation complete: "
            f"total={total_score}, "
            f"severity={severity}, "
            f"mortality_risk={mortality_risk}, "
            f"delta={change} ({interpretation})"
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

    def _load_state_json(self, phase: str) -> Optional[Dict[str, Any]]:
        """Load JSON data from a state phase."""
        state = self.state_manager.load(phase)
        if not state:
            return None

        try:
            json_str = self._extract_json(state)
            return json.loads(json_str)
        except Exception as e:
            logger.warning(f"Failed to load JSON from {phase}: {e}")
            return None

    def _extract_previous_sofa(self, history: list) -> Optional[Dict[str, Any]]:
        """
        Extract previous SOFA score from history.

        Args:
            history: List of historical workflow statuses

        Returns:
            Previous SOFA data or None
        """
        if not history:
            return None

        # Look for most recent SOFA score
        for day in history:
            phases = day.get("phases", {})
            if "SofaCalculator" in phases or "scores" in phases:
                # Try to load that day's SOFA score
                try:
                    date = day.get("date")
                    patient_id = day.get("patient_id")

                    if date and patient_id:
                        # Create temporary state manager for that date
                        from agents.base.state import StateManager
                        temp_sm = StateManager(patient_id, date)
                        scores_state = temp_sm.load("scores")

                        if scores_state:
                            scores_json = self._extract_json(scores_state)
                            scores_data = json.loads(scores_json)
                            sofa = scores_data.get("scores", {}).get("sofa", {})

                            return {
                                "date": date,
                                "total_score": sofa.get("total_score"),
                                "components": sofa.get("components", {})
                            }
                except Exception as e:
                    logger.debug(f"Could not extract previous SOFA: {e}")
                    continue

        return None

    def _extract_sofa_components(
        self,
        vitals_data: Optional[Dict],
        labs_data: Optional[Dict],
        parsed_data: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        Extract required components for SOFA calculation.

        Args:
            vitals_data: Vitals data
            labs_data: Labs data
            parsed_data: Parsed clinical data

        Returns:
            Dictionary with SOFA components
        """
        components = {}

        # Extract respiratory (P/F ratio)
        if labs_data:
            blood_gas = labs_data.get("labs", {}).get("blood_gas", {})
            po2 = blood_gas.get("po2", {}).get("value") if isinstance(blood_gas.get("po2"), dict) else blood_gas.get("po2")
            components["po2"] = po2

        if parsed_data:
            resp = parsed_data.get("respiratory", {})
            fio2 = resp.get("fio2", {}).get("value") if isinstance(resp.get("fio2"), dict) else resp.get("fio2")
            components["fio2"] = fio2
            components["mechanical_ventilation"] = resp.get("mechanical_ventilation", False)

        # Extract coagulation (Platelets)
        if labs_data:
            heme = labs_data.get("labs", {}).get("hematology", {})
            plt = heme.get("platelet", {}).get("value") if isinstance(heme.get("platelet"), dict) else heme.get("platelet")
            components["platelet"] = plt

        # Extract hepatic (Bilirubin)
        # Extract cardiovascular (MAP, vasopressors)
        if vitals_data:
            bp = vitals_data.get("vitals", {}).get("blood_pressure", {})
            components["map"] = bp.get("map")

        if parsed_data:
            hemodynamics = parsed_data.get("hemodynamics", {})
            components["vasopressor"] = hemodynamics.get("vasopressor_support")

        # Extract neurological (GCS)
        if parsed_data:
            neuro = parsed_data.get("neurological", {})
            components["gcs"] = neuro.get("gcs", {}).get("total") if isinstance(neuro.get("gcs"), dict) else neuro.get("gcs")

        # Extract renal (Creatinine, UO)
        if labs_data:
            chem = labs_data.get("labs", {}).get("chemistry", {})
            cr = chem.get("creatinine", {}).get("value") if isinstance(chem.get("creatinine"), dict) else chem.get("creatinine")
            components["creatinine"] = cr

        return components

    def get_sofa_score(self, scores_data: Dict[str, Any]) -> int:
        """
        Get the total SOFA score.

        Args:
            scores_data: Scores data dictionary

        Returns:
            Total SOFA score
        """
        scores = scores_data.get("scores", {})
        sofa = scores.get("sofa", {})
        return sofa.get("total_score", 0)

    def get_mortality_risk(self, scores_data: Dict[str, Any]) -> str:
        """
        Get the mortality risk assessment.

        Args:
            scores_data: Scores data dictionary

        Returns:
            Mortality risk string
        """
        scores = scores_data.get("scores", {})
        sofa = scores.get("sofa", {})
        return sofa.get("mortality_risk", "unknown")
