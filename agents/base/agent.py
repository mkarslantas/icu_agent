"""
Base Agent Class for ICU Multi-Agent System

This module provides the abstract base class for all agents in the system.
Each agent is responsible for a specific task in the ICU monitoring workflow.
"""

import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

from anthropic import Anthropic, APIError, RateLimitError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the ICU monitoring system.

    Each agent is responsible for a specific task such as parsing clinical notes,
    extracting vitals, calculating scores, etc. Agents use Claude AI via Anthropic API
    to process clinical data.

    Attributes:
        name: Unique identifier for the agent
        prompt_path: Path to the prompt template file
        state_manager: StateManager instance for persisting agent state
        config: Configuration dictionary with model settings
        client: Anthropic API client
        prompt_template: Loaded prompt template text
        execution_count: Number of times this agent has been run
        success_count: Number of successful executions
        failure_count: Number of failed executions
        total_elapsed_time: Total time spent executing this agent
    """

    def __init__(
        self,
        name: str,
        prompt_path: str,
        state_manager: Any,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the base agent.

        Args:
            name: Unique identifier for the agent
            prompt_path: Path to the prompt template file (relative to project root)
            state_manager: StateManager instance for state persistence
            config: Optional configuration dict with keys:
                - model: Model name (default: claude-sonnet-4-5-20250929)
                - max_tokens: Maximum tokens in response (default: 4096)
                - temperature: Temperature for sampling (default: 0.0)
                - max_retries: Maximum retry attempts (default: 3)
        """
        self.name = name
        self.prompt_path = prompt_path
        self.state_manager = state_manager
        self.config = config or {}

        # Initialize Anthropic client
        self.client = Anthropic()  # Uses ANTHROPIC_API_KEY from environment

        # Load prompt template
        self.prompt_template = self._load_prompt()

        # Initialize metrics
        self.execution_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.total_elapsed_time = 0.0

        logger.info(f"Initialized agent: {self.name}")

    def _load_prompt(self) -> str:
        """
        Load the prompt template from file.

        Returns:
            The prompt template as a string

        Raises:
            FileNotFoundError: If prompt file doesn't exist
        """
        prompt_file = Path(self.prompt_path)

        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {self.prompt_path}")

        with open(prompt_file, "r", encoding="utf-8") as f:
            template = f.read()

        logger.debug(f"Loaded prompt template from {self.prompt_path} ({len(template)} chars)")
        return template

    @abstractmethod
    def prepare_input(self, context: Dict[str, Any]) -> str:
        """
        Prepare input for the agent from the given context.

        This method should format the context data into a string that will be
        appended to the prompt template before calling Claude.

        Args:
            context: Dictionary containing input data for the agent

        Returns:
            Formatted input string to append to prompt
        """
        pass

    @abstractmethod
    def validate_output(self, output: str) -> bool:
        """
        Validate the output from Claude.

        This method should check if the output is in the expected format
        and contains all required fields.

        Args:
            output: Raw output string from Claude

        Returns:
            True if output is valid, False otherwise
        """
        pass

    @abstractmethod
    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        Parse the validated output into a structured format.

        This method should extract the relevant information from Claude's
        output and return it as a dictionary.

        Args:
            output: Validated output string from Claude

        Returns:
            Parsed output as a dictionary
        """
        pass

    def run(
        self,
        context: Dict[str, Any],
        max_retries: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute the agent with the given context.

        This method:
        1. Prepares input from context
        2. Calls Claude API (with retry logic)
        3. Validates output
        4. Parses output
        5. Saves state
        6. Returns result

        Args:
            context: Input data for the agent
            max_retries: Override default max retries from config

        Returns:
            Dictionary with keys:
                - status: "success" or "error"
                - output: Parsed output (if successful)
                - raw_output: Raw Claude response (if successful)
                - error: Error message (if failed)
                - elapsed_time: Time taken in seconds
                - retries: Number of retries attempted
        """
        start_time = time.time()
        self.execution_count += 1

        if max_retries is None:
            max_retries = self.config.get("max_retries", 3)

        retries = 0
        last_error = None

        logger.info(f"Running agent: {self.name}")

        # Prepare input
        try:
            agent_input = self.prepare_input(context)
            logger.debug(f"Prepared input for {self.name} ({len(agent_input)} chars)")
        except Exception as e:
            logger.error(f"Error preparing input for {self.name}: {e}")
            self.failure_count += 1
            return {
                "status": "error",
                "error": f"Input preparation failed: {str(e)}",
                "elapsed_time": time.time() - start_time,
                "retries": 0,
            }

        # Retry loop
        while retries <= max_retries:
            try:
                # Call Claude
                raw_output = self._call_claude(agent_input)
                logger.debug(f"Received output from Claude ({len(raw_output)} chars)")

                # Validate output
                if not self.validate_output(raw_output):
                    raise ValueError("Output validation failed")

                logger.debug(f"Output validated successfully for {self.name}")

                # Parse output
                parsed_output = self.parse_output(raw_output)
                logger.debug(f"Output parsed successfully for {self.name}")

                # Save state
                try:
                    self.state_manager.save(
                        phase=self.name,
                        content=parsed_output,
                        metadata={
                            "agent": self.name,
                            "timestamp": time.time(),
                            "elapsed_time": time.time() - start_time,
                            "retries": retries,
                        }
                    )
                except Exception as e:
                    logger.warning(f"Failed to save state for {self.name}: {e}")

                # Success!
                elapsed_time = time.time() - start_time
                self.success_count += 1
                self.total_elapsed_time += elapsed_time

                logger.info(
                    f"Agent {self.name} completed successfully "
                    f"(took {elapsed_time:.2f}s, {retries} retries)"
                )

                return {
                    "status": "success",
                    "output": parsed_output,
                    "raw_output": raw_output,
                    "elapsed_time": elapsed_time,
                    "retries": retries,
                }

            except RateLimitError as e:
                # Handle rate limits with exponential backoff
                retries += 1
                last_error = e

                if retries <= max_retries:
                    wait_time = 2 ** retries  # Exponential backoff: 2, 4, 8, 16...
                    logger.warning(
                        f"Rate limit hit for {self.name}. "
                        f"Retrying in {wait_time}s (attempt {retries}/{max_retries})"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Max retries exceeded for {self.name} due to rate limits")

            except (APIError, ValueError) as e:
                # Handle other API errors and validation errors
                retries += 1
                last_error = e

                if retries <= max_retries:
                    wait_time = 1.5 ** retries  # Gentler backoff: 1.5, 2.25, 3.375...
                    logger.warning(
                        f"Error in {self.name}: {e}. "
                        f"Retrying in {wait_time:.1f}s (attempt {retries}/{max_retries})"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Max retries exceeded for {self.name}: {e}")

            except Exception as e:
                # Unexpected errors - don't retry
                logger.error(f"Unexpected error in {self.name}: {e}", exc_info=True)
                last_error = e
                break

        # All retries exhausted or unexpected error
        elapsed_time = time.time() - start_time
        self.failure_count += 1
        self.total_elapsed_time += elapsed_time

        return {
            "status": "error",
            "error": str(last_error),
            "elapsed_time": elapsed_time,
            "retries": retries,
        }

    def _call_claude(self, agent_input: str) -> str:
        """
        Call the Anthropic Claude API with the prepared input.

        Args:
            agent_input: The prepared input string

        Returns:
            The response text from Claude

        Raises:
            APIError: If the API call fails
        """
        # Combine prompt template with input
        full_prompt = f"{self.prompt_template}\n\n{agent_input}"

        # Get model configuration
        model = self.config.get("model", "claude-sonnet-4-5-20250929")
        max_tokens = self.config.get("max_tokens", 4096)
        temperature = self.config.get("temperature", 0.0)

        logger.debug(
            f"Calling Claude API for {self.name} "
            f"(model={model}, max_tokens={max_tokens}, temp={temperature})"
        )

        # Call API
        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {
                    "role": "user",
                    "content": full_prompt,
                }
            ]
        )

        # Extract text from response
        return response.content[0].text

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for this agent.

        Returns:
            Dictionary containing:
                - name: Agent name
                - execution_count: Total executions
                - success_count: Successful executions
                - failure_count: Failed executions
                - success_rate: Percentage of successful executions
                - total_elapsed_time: Total time spent (seconds)
                - average_elapsed_time: Average time per execution (seconds)
        """
        success_rate = (
            (self.success_count / self.execution_count * 100)
            if self.execution_count > 0
            else 0.0
        )

        average_time = (
            (self.total_elapsed_time / self.execution_count)
            if self.execution_count > 0
            else 0.0
        )

        return {
            "name": self.name,
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": round(success_rate, 2),
            "total_elapsed_time": round(self.total_elapsed_time, 2),
            "average_elapsed_time": round(average_time, 2),
        }
