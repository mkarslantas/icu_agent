"""
Base Supervisor Class for ICU Multi-Agent System

Supervisors coordinate multiple worker agents to complete complex tasks.
They can execute workers sequentially or in parallel based on configuration.
"""

import logging
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

from agents.base.agent import BaseAgent
from agents.base.state import StateManager

logger = logging.getLogger(__name__)


class BaseSupervisor(ABC):
    """
    Abstract base class for supervisors that coordinate multiple worker agents.

    Supervisors are responsible for:
    1. Preparing context for worker agents
    2. Executing workers (sequential or parallel)
    3. Validating combined results
    4. Handling worker failures gracefully

    Attributes:
        name: Unique identifier for the supervisor
        workers: List of BaseAgent instances to coordinate
        state_manager: StateManager instance for persistence
        config: Configuration dictionary
        parallel_enabled: Whether to run workers in parallel
        max_workers: Maximum number of parallel workers
        execution_count: Number of times this supervisor has been run
        success_count: Number of successful executions
    """

    def __init__(
        self,
        name: str,
        workers: List[BaseAgent],
        state_manager: StateManager,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the supervisor.

        Args:
            name: Unique identifier for the supervisor
            workers: List of worker agents to coordinate
            state_manager: StateManager instance for state persistence
            config: Optional configuration dict with keys:
                - parallel: Enable parallel execution (default: False)
                - max_workers: Max parallel workers (default: 5)
                - stop_on_error: Stop if any worker fails (default: True)
                - critical_workers: List of worker names that must succeed
        """
        self.name = name
        self.workers = workers
        self.state_manager = state_manager
        self.config = config or {}

        # Parallel execution settings
        self.parallel_enabled = self.config.get("parallel", False)
        self.max_workers = self.config.get("max_workers", 5)
        self.stop_on_error = self.config.get("stop_on_error", True)
        self.critical_workers = set(self.config.get("critical_workers", []))

        # Metrics
        self.execution_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.total_elapsed_time = 0.0

        logger.info(
            f"Initialized supervisor: {self.name} "
            f"(workers={len(workers)}, parallel={self.parallel_enabled})"
        )

    @abstractmethod
    def prepare_context(self) -> Dict[str, Any]:
        """
        Prepare the context for worker agents.

        This method should gather all necessary data (e.g., from previous
        workflow phases) and return it as a dictionary that will be passed
        to each worker agent.

        Returns:
            Dictionary containing context data for workers
        """
        pass

    @abstractmethod
    def validate_results(self, results: List[Dict[str, Any]]) -> bool:
        """
        Validate the combined results from all workers.

        This method should check if the results meet the supervisor's
        requirements (e.g., all critical workers succeeded, data quality
        is acceptable).

        Args:
            results: List of result dictionaries from workers

        Returns:
            True if results are valid, False otherwise
        """
        pass

    def run(self) -> Dict[str, Any]:
        """
        Execute the supervisor's workflow.

        This method:
        1. Prepares context for workers
        2. Executes workers (parallel or sequential)
        3. Validates combined results
        4. Returns supervisor result

        Returns:
            Dictionary with keys:
                - status: "success" or "error"
                - results: List of worker results (if successful)
                - error: Error message (if failed)
                - elapsed_time: Time taken in seconds
                - workers_completed: Number of workers that completed
                - workers_failed: Number of workers that failed
        """
        start_time = time.time()
        self.execution_count += 1

        logger.info(f"Running supervisor: {self.name}")

        # Prepare context
        try:
            context = self.prepare_context()
            logger.debug(f"Prepared context for {self.name}")
        except Exception as e:
            logger.error(f"Error preparing context for {self.name}: {e}")
            self.failure_count += 1
            return {
                "status": "error",
                "error": f"Context preparation failed: {str(e)}",
                "elapsed_time": time.time() - start_time,
            }

        # Execute workers
        try:
            if self.parallel_enabled:
                results = self._run_parallel(context)
            else:
                results = self._run_sequential(context)

            logger.debug(f"All workers completed for {self.name}")
        except Exception as e:
            logger.error(f"Error executing workers for {self.name}: {e}")
            self.failure_count += 1
            return {
                "status": "error",
                "error": f"Worker execution failed: {str(e)}",
                "elapsed_time": time.time() - start_time,
            }

        # Count successes and failures
        workers_completed = sum(1 for r in results if r.get("status") == "success")
        workers_failed = sum(1 for r in results if r.get("status") == "error")

        # Validate results
        try:
            is_valid = self.validate_results(results)
            logger.debug(f"Results validation for {self.name}: {is_valid}")
        except Exception as e:
            logger.error(f"Error validating results for {self.name}: {e}")
            is_valid = False

        # Determine overall status
        elapsed_time = time.time() - start_time

        if is_valid:
            self.success_count += 1
            self.total_elapsed_time += elapsed_time

            logger.info(
                f"Supervisor {self.name} completed successfully "
                f"({workers_completed}/{len(self.workers)} workers, {elapsed_time:.2f}s)"
            )

            return {
                "status": "success",
                "results": results,
                "elapsed_time": elapsed_time,
                "workers_completed": workers_completed,
                "workers_failed": workers_failed,
            }
        else:
            self.failure_count += 1
            self.total_elapsed_time += elapsed_time

            logger.error(
                f"Supervisor {self.name} failed validation "
                f"({workers_completed}/{len(self.workers)} workers completed)"
            )

            return {
                "status": "error",
                "error": "Results validation failed",
                "results": results,
                "elapsed_time": elapsed_time,
                "workers_completed": workers_completed,
                "workers_failed": workers_failed,
            }

    def _run_sequential(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute workers sequentially (one after another).

        Args:
            context: Context dictionary to pass to each worker

        Returns:
            List of result dictionaries from each worker
        """
        results = []

        logger.info(f"Running {len(self.workers)} workers sequentially")

        for i, worker in enumerate(self.workers, 1):
            logger.info(f"Running worker {i}/{len(self.workers)}: {worker.name}")

            try:
                result = worker.run(context)
                results.append(result)

                # Log result
                status = result.get("status")
                elapsed = result.get("elapsed_time", 0)
                logger.info(
                    f"Worker {worker.name} {status} ({elapsed:.2f}s)"
                )

                # Check if critical worker failed
                if status == "error" and worker.name in self.critical_workers:
                    logger.error(f"Critical worker {worker.name} failed")
                    if self.stop_on_error:
                        logger.warning("Stopping execution due to critical worker failure")
                        break

            except Exception as e:
                logger.error(f"Unexpected error in worker {worker.name}: {e}", exc_info=True)
                results.append({
                    "status": "error",
                    "error": str(e),
                    "worker": worker.name,
                })

                if self.stop_on_error:
                    logger.warning("Stopping execution due to worker error")
                    break

        return results

    def _run_parallel(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute workers in parallel using ThreadPoolExecutor.

        Args:
            context: Context dictionary to pass to each worker

        Returns:
            List of result dictionaries from each worker
        """
        results = []
        max_parallel = min(self.max_workers, len(self.workers))

        logger.info(f"Running {len(self.workers)} workers in parallel (max={max_parallel})")

        with ThreadPoolExecutor(max_workers=max_parallel) as executor:
            # Submit all workers
            future_to_worker = {
                executor.submit(worker.run, context): worker
                for worker in self.workers
            }

            # Collect results as they complete
            for future in as_completed(future_to_worker):
                worker = future_to_worker[future]

                try:
                    result = future.result()
                    results.append(result)

                    # Log result
                    status = result.get("status")
                    elapsed = result.get("elapsed_time", 0)
                    logger.info(
                        f"Worker {worker.name} {status} ({elapsed:.2f}s)"
                    )

                    # Check if critical worker failed
                    if status == "error" and worker.name in self.critical_workers:
                        logger.error(f"Critical worker {worker.name} failed")
                        if self.stop_on_error:
                            logger.warning("Critical worker failed (will wait for others to finish)")

                except Exception as e:
                    logger.error(f"Unexpected error in worker {worker.name}: {e}", exc_info=True)
                    results.append({
                        "status": "error",
                        "error": str(e),
                        "worker": worker.name,
                    })

        # Sort results by worker order (to maintain consistency)
        worker_names = [w.name for w in self.workers]
        results.sort(key=lambda r: worker_names.index(r.get("output", {}).get("agent", r.get("worker", ""))) if r.get("output", {}).get("agent", r.get("worker", "")) in worker_names else 999)

        return results

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for this supervisor.

        Returns:
            Dictionary containing:
                - name: Supervisor name
                - execution_count: Total executions
                - success_count: Successful executions
                - failure_count: Failed executions
                - success_rate: Percentage of successful executions
                - total_elapsed_time: Total time spent (seconds)
                - average_elapsed_time: Average time per execution (seconds)
                - workers: List of worker names
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
            "workers": [w.name for w in self.workers],
            "parallel_enabled": self.parallel_enabled,
        }

    def get_worker_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metrics for all worker agents.

        Returns:
            Dictionary mapping worker names to their metrics
        """
        return {
            worker.name: worker.get_metrics()
            for worker in self.workers
        }
