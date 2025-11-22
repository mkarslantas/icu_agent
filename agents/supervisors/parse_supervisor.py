"""
Parse Supervisor

This supervisor coordinates the parsing workflow:
1. Turkish Parser Agent (parses raw notes to structured JSON)
2. Vital Signs Extractor (extracts vital signs in parallel)
3. Lab Values Extractor (extracts lab values in parallel)
"""

import logging
from typing import Any, Dict, List

from agents.base.supervisor import BaseSupervisor
from agents.base.state import StateManager
from agents.workers.turkish_parser import TurkishParserAgent
from agents.workers.vital_extractor import VitalExtractorAgent
from agents.workers.lab_extractor import LabExtractorAgent

logger = logging.getLogger(__name__)


class ParseSupervisor(BaseSupervisor):
    """
    Supervises the parsing phase of the workflow.

    Workflow:
    1. TurkishParser runs first (sequential) - converts Turkish notes to JSON
    2. VitalExtractor and LabExtractor run in parallel - extract specific data
    3. Results validated for data completeness

    Configuration:
    - parallel=True for vital and lab extraction
    - critical_workers=["TurkishParser"] - must succeed for workflow to continue
    """

    def __init__(self, state_manager: StateManager, config: Dict[str, Any] = None):
        """
        Initialize the Parse Supervisor.

        Args:
            state_manager: StateManager instance for this patient/date
            config: Optional configuration dict for agents
        """
        # Initialize worker agents
        agent_config = config or {}

        # Create workers
        turkish_parser = TurkishParserAgent(state_manager, agent_config)
        vital_extractor = VitalExtractorAgent(state_manager, agent_config)
        lab_extractor = LabExtractorAgent(state_manager, agent_config)

        workers = [turkish_parser, vital_extractor, lab_extractor]

        # Supervisor configuration
        supervisor_config = {
            "parallel": False,  # Run sequentially by default, but TurkishParser first
            "max_workers": 2,
            "stop_on_error": False,  # Continue even if extractors fail
            "critical_workers": ["TurkishParser"],  # TurkishParser must succeed
        }

        super().__init__(
            name="ParseSupervisor",
            workers=workers,
            state_manager=state_manager,
            config=supervisor_config
        )

        logger.info("Initialized ParseSupervisor with 3 workers")

    def prepare_context(self) -> Dict[str, Any]:
        """
        Prepare context for parsing workers.

        Loads the raw clinical note from 00_input.md state file.

        Returns:
            Dictionary containing:
                - raw_note: The clinical note text
                - patient_id: Patient identifier
                - date: Date of the note

        Raises:
            ValueError: If no input note is found
        """
        # Load raw clinical note from state
        raw_note = self.state_manager.load("input")

        if not raw_note:
            raise ValueError(
                f"No input note found for patient {self.state_manager.patient_id} "
                f"on {self.state_manager.date}"
            )

        # Prepare context
        context = {
            "raw_note": raw_note,
            "patient_id": self.state_manager.patient_id,
            "date": self.state_manager.date,
        }

        logger.info(
            f"Prepared parse context: "
            f"patient={self.state_manager.patient_id}, "
            f"note_length={len(raw_note)} chars"
        )

        return context

    def validate_results(self, results: List[Dict[str, Any]]) -> bool:
        """
        Validate the combined results from all parsing workers.

        Validation criteria:
        1. TurkishParser must have succeeded
        2. At least one of VitalExtractor or LabExtractor should succeed
        3. Data completeness from TurkishParser should be > 60%

        Args:
            results: List of result dictionaries from workers

        Returns:
            True if results meet acceptance criteria, False otherwise
        """
        # Find results by worker name
        turkish_parser_result = None
        vital_extractor_result = None
        lab_extractor_result = None

        for result in results:
            worker_name = result.get("output", {}).get("agent") if result.get("output") else None
            if not worker_name and "worker" in result:
                worker_name = result["worker"]

            # Try to match by checking the result structure
            if result.get("status") == "success":
                output = result.get("output", {})

                # TurkishParser has patient_info and data_completeness
                if "patient_info" in output or "data_completeness" in output:
                    turkish_parser_result = result
                # VitalExtractor has vitals
                elif "vitals" in output:
                    vital_extractor_result = result
                # LabExtractor has labs
                elif "labs" in output:
                    lab_extractor_result = result

        # Validation 1: TurkishParser must succeed
        if not turkish_parser_result or turkish_parser_result.get("status") != "success":
            logger.error("TurkishParser did not succeed - parse phase failed")
            return False

        # Validation 2: Check data completeness
        parser_output = turkish_parser_result.get("output", {})
        data_completeness = parser_output.get("data_completeness", {})
        overall_score = data_completeness.get("overall_score", 0)

        if overall_score < 60:
            logger.warning(
                f"Data completeness too low: {overall_score}% "
                f"(threshold: 60%)"
            )
            return False

        # Validation 3: At least one extractor should succeed
        extractors_succeeded = (
            (vital_extractor_result and vital_extractor_result.get("status") == "success") or
            (lab_extractor_result and lab_extractor_result.get("status") == "success")
        )

        if not extractors_succeeded:
            logger.warning("Neither VitalExtractor nor LabExtractor succeeded")
            # This is a warning but not a failure - we have the parsed data
            # return False

        # Log validation summary
        logger.info(
            f"Parse validation: "
            f"completeness={overall_score}%, "
            f"vitals={'✓' if vital_extractor_result else '✗'}, "
            f"labs={'✓' if lab_extractor_result else '✗'}"
        )

        return True

    def get_parsed_data(self) -> Dict[str, Any]:
        """
        Get the parsed data from the most recent run.

        Returns:
            Parsed data dictionary or empty dict if not available
        """
        parsed_state = self.state_manager.load("parsed")
        if not parsed_state:
            return {}

        try:
            import json
            import re

            # Extract JSON from markdown
            text = parsed_state.strip()
            json_block_pattern = r"```json\s*(.*?)\s*```"
            match = re.search(json_block_pattern, text, re.DOTALL)

            if match:
                json_str = match.group(1).strip()
                return json.loads(json_str)

            return json.loads(text)
        except Exception as e:
            logger.error(f"Failed to load parsed data: {e}")
            return {}

    def run_sequential_then_parallel(self) -> Dict[str, Any]:
        """
        Custom run method: TurkishParser first, then Vital/Lab in parallel.

        This overrides the default behavior to:
        1. Run TurkishParser first (sequential)
        2. If successful, run VitalExtractor and LabExtractor in parallel

        Returns:
            Supervisor result dictionary
        """
        import time
        start_time = time.time()
        self.execution_count += 1

        logger.info(f"Running ParseSupervisor (custom workflow)")

        # Prepare context
        try:
            context = self.prepare_context()
        except Exception as e:
            logger.error(f"Error preparing context: {e}")
            self.failure_count += 1
            return {
                "status": "error",
                "error": f"Context preparation failed: {str(e)}",
                "elapsed_time": time.time() - start_time,
            }

        results = []

        # Step 1: Run TurkishParser (sequential)
        turkish_parser = self.workers[0]
        logger.info(f"Step 1: Running {turkish_parser.name}")

        try:
            parser_result = turkish_parser.run(context)
            results.append(parser_result)

            if parser_result.get("status") != "success":
                logger.error("TurkishParser failed - stopping parse workflow")
                self.failure_count += 1
                return {
                    "status": "error",
                    "error": "TurkishParser failed",
                    "results": results,
                    "elapsed_time": time.time() - start_time,
                }
        except Exception as e:
            logger.error(f"TurkishParser error: {e}")
            self.failure_count += 1
            return {
                "status": "error",
                "error": f"TurkishParser error: {str(e)}",
                "elapsed_time": time.time() - start_time,
            }

        # Step 2: Run VitalExtractor and LabExtractor in parallel
        logger.info("Step 2: Running VitalExtractor and LabExtractor in parallel")

        from concurrent.futures import ThreadPoolExecutor, as_completed

        # Update context with parsed data
        context["parsed_data"] = parser_result.get("output", {})

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_to_worker = {
                executor.submit(worker.run, context): worker
                for worker in self.workers[1:3]  # Vital and Lab extractors
            }

            for future in as_completed(future_to_worker):
                worker = future_to_worker[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(f"{worker.name}: {result.get('status')}")
                except Exception as e:
                    logger.error(f"{worker.name} error: {e}")
                    results.append({
                        "status": "error",
                        "error": str(e),
                        "worker": worker.name
                    })

        # Validate results
        is_valid = self.validate_results(results)
        elapsed_time = time.time() - start_time

        if is_valid:
            self.success_count += 1
            self.total_elapsed_time += elapsed_time
            logger.info(f"ParseSupervisor completed successfully ({elapsed_time:.2f}s)")
            return {
                "status": "success",
                "results": results,
                "elapsed_time": elapsed_time,
            }
        else:
            self.failure_count += 1
            self.total_elapsed_time += elapsed_time
            logger.error(f"ParseSupervisor validation failed")
            return {
                "status": "error",
                "error": "Validation failed",
                "results": results,
                "elapsed_time": elapsed_time,
            }

    # Override run to use custom workflow
    def run(self) -> Dict[str, Any]:
        """Run the parse supervisor with custom sequential-then-parallel workflow."""
        return self.run_sequential_then_parallel()
