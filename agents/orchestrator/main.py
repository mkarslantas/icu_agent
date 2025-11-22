"""
Main Orchestrator

This orchestrator provides system-level coordination for the ICU monitoring system.
It manages:
- Single patient processing
- Batch patient processing
- Priority management
- System health monitoring
- Performance metrics
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

from agents.orchestrator.patient import PatientOrchestrator

logger = logging.getLogger(__name__)


class MainOrchestrator:
    """
    Main system orchestrator for ICU monitoring.

    This orchestrator:
    - Processes single or multiple patients
    - Manages parallel vs sequential batch processing
    - Handles priority patients (critical first)
    - Tracks system-wide metrics
    - Provides system health status

    Attributes:
        config: Configuration dictionary
        metrics: System-wide metrics tracking
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Main Orchestrator.

        Args:
            config: Optional configuration dict with keys:
                - model: Claude model to use
                - max_tokens: Maximum tokens per request
                - temperature: Sampling temperature
                - max_concurrent: Maximum concurrent patient processing
                - state_dir: Base directory for state files
                - enable_parallel: Enable parallel batch processing
        """
        self.config = config or {}

        # Initialize metrics
        self.metrics = {
            "patients_processed": 0,
            "patients_succeeded": 0,
            "patients_failed": 0,
            "total_elapsed_time": 0.0,
            "critical_alerts_total": 0,
            "last_run_time": None,
        }

        logger.info("Initialized MainOrchestrator")

    def process_patient(
        self,
        patient_id: str,
        date: str,
        note_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a single patient.

        Args:
            patient_id: Patient identifier
            date: Date string in YYYY-MM-DD format
            note_path: Optional path to clinical note file

        Returns:
            Result dictionary from PatientOrchestrator
        """
        logger.info(f"Processing patient: {patient_id} on {date}")

        start_time = time.time()

        try:
            # Create patient orchestrator
            patient_orch = PatientOrchestrator(patient_id, date, self.config)

            # Run workflow
            result = patient_orch.run(note_path=note_path)

            # Update metrics
            self.metrics["patients_processed"] += 1
            if result.get("status") == "success":
                self.metrics["patients_succeeded"] += 1

                # Count critical alerts
                try:
                    critical_alerts = patient_orch.get_critical_alerts()
                    self.metrics["critical_alerts_total"] += len(critical_alerts)
                except:
                    pass
            else:
                self.metrics["patients_failed"] += 1

            elapsed = time.time() - start_time
            self.metrics["total_elapsed_time"] += elapsed
            self.metrics["last_run_time"] = time.time()

            logger.info(
                f"Patient {patient_id} processing {result.get('status')} "
                f"({elapsed:.2f}s)"
            )

            return result

        except Exception as e:
            logger.error(f"Error processing patient {patient_id}: {e}", exc_info=True)
            self.metrics["patients_processed"] += 1
            self.metrics["patients_failed"] += 1

            return {
                "status": "error",
                "error": str(e),
                "patient_id": patient_id,
                "date": date,
                "elapsed_time": time.time() - start_time,
            }

    def process_batch(
        self,
        patients: List[Dict[str, str]],
        parallel: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Process multiple patients.

        Args:
            patients: List of patient dicts with keys:
                - patient_id: Patient identifier
                - date: Date string
                - note_path: Optional path to note file
            parallel: Optional override for parallel processing.
                     If None, uses config or decides based on batch size.

        Returns:
            Dictionary with keys:
                - status: "success" or "partial" or "error"
                - results: List of individual patient results
                - summary: Summary statistics
                - elapsed_time: Total batch processing time
        """
        logger.info(f"Processing batch of {len(patients)} patients")

        start_time = time.time()

        # Decide parallel vs sequential
        if parallel is None:
            # Use config or auto-decide based on batch size
            parallel = self.config.get("enable_parallel", True)
            if len(patients) <= 3:
                parallel = False  # Sequential for small batches

        # Get max concurrent from config
        max_concurrent = self.config.get("max_concurrent", 5)

        results = []

        if parallel and len(patients) > 1:
            logger.info(f"Processing {len(patients)} patients in parallel (max={max_concurrent})")
            results = self._process_parallel(patients, max_concurrent)
        else:
            logger.info(f"Processing {len(patients)} patients sequentially")
            results = self._process_sequential(patients)

        # Calculate summary
        elapsed_time = time.time() - start_time
        succeeded = sum(1 for r in results if r.get("status") == "success")
        failed = sum(1 for r in results if r.get("status") == "error")

        # Determine overall status
        if succeeded == len(patients):
            status = "success"
        elif succeeded > 0:
            status = "partial"
        else:
            status = "error"

        summary = {
            "total": len(patients),
            "succeeded": succeeded,
            "failed": failed,
            "success_rate": (succeeded / len(patients) * 100) if patients else 0,
            "average_time": (elapsed_time / len(patients)) if patients else 0,
        }

        logger.info(
            f"Batch processing complete: "
            f"{succeeded}/{len(patients)} succeeded "
            f"({elapsed_time:.2f}s total)"
        )

        return {
            "status": status,
            "results": results,
            "summary": summary,
            "elapsed_time": elapsed_time,
        }

    def _process_sequential(
        self,
        patients: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Process patients sequentially.

        Args:
            patients: List of patient dicts

        Returns:
            List of result dictionaries
        """
        results = []

        for i, patient in enumerate(patients, 1):
            logger.info(f"Processing patient {i}/{len(patients)}: {patient['patient_id']}")

            result = self.process_patient(
                patient_id=patient["patient_id"],
                date=patient["date"],
                note_path=patient.get("note_path")
            )

            results.append(result)

        return results

    def _process_parallel(
        self,
        patients: List[Dict[str, str]],
        max_workers: int
    ) -> List[Dict[str, Any]]:
        """
        Process patients in parallel using ThreadPoolExecutor.

        Args:
            patients: List of patient dicts
            max_workers: Maximum number of parallel workers

        Returns:
            List of result dictionaries
        """
        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all patients
            future_to_patient = {
                executor.submit(
                    self.process_patient,
                    patient["patient_id"],
                    patient["date"],
                    patient.get("note_path")
                ): patient
                for patient in patients
            }

            # Collect results as they complete
            for future in as_completed(future_to_patient):
                patient = future_to_patient[future]

                try:
                    result = future.result()
                    results.append(result)

                    logger.info(
                        f"Patient {patient['patient_id']}: "
                        f"{result.get('status')} "
                        f"({result.get('elapsed_time', 0):.2f}s)"
                    )

                except Exception as e:
                    logger.error(f"Patient {patient['patient_id']} error: {e}")
                    results.append({
                        "status": "error",
                        "error": str(e),
                        "patient_id": patient["patient_id"],
                        "date": patient["date"],
                    })

        return results

    def process_with_priority(
        self,
        patients: List[Dict[str, str]],
        priority_fn: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Process patients with priority ordering.

        Critical patients (high SOFA, critical values) are processed first.

        Args:
            patients: List of patient dicts
            priority_fn: Optional function to determine priority
                        Should return a number (lower = higher priority)
                        Default: uses previous SOFA scores if available

        Returns:
            Batch processing result dictionary
        """
        logger.info(f"Processing {len(patients)} patients with priority ordering")

        # Sort by priority
        if priority_fn:
            sorted_patients = sorted(patients, key=priority_fn)
        else:
            sorted_patients = self._sort_by_sofa_priority(patients)

        # Process high priority patients first (sequential)
        # Then process normal priority in parallel

        high_priority = []
        normal_priority = []

        for patient in sorted_patients:
            priority_score = patient.get("priority_score", 0)
            if priority_score > 15:  # SOFA > 15 is very high risk
                high_priority.append(patient)
            else:
                normal_priority.append(patient)

        results = []

        # Process high priority sequentially
        if high_priority:
            logger.info(f"Processing {len(high_priority)} high-priority patients sequentially")
            high_priority_results = self._process_sequential(high_priority)
            results.extend(high_priority_results)

        # Process normal priority in parallel
        if normal_priority:
            logger.info(f"Processing {len(normal_priority)} normal-priority patients in parallel")
            normal_priority_results = self._process_parallel(
                normal_priority,
                self.config.get("max_concurrent", 5)
            )
            results.extend(normal_priority_results)

        # Create summary (same as process_batch)
        succeeded = sum(1 for r in results if r.get("status") == "success")
        failed = len(results) - succeeded

        return {
            "status": "success" if succeeded == len(patients) else "partial",
            "results": results,
            "summary": {
                "total": len(patients),
                "succeeded": succeeded,
                "failed": failed,
                "high_priority": len(high_priority),
                "normal_priority": len(normal_priority),
            }
        }

    def _sort_by_sofa_priority(
        self,
        patients: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Sort patients by SOFA score priority (higher SOFA = higher priority).

        Loads previous SOFA scores from state files.

        Args:
            patients: List of patient dicts

        Returns:
            Sorted list of patient dicts (highest priority first)
        """
        from agents.base.state import StateManager
        import json
        import re

        # Add priority scores
        for patient in patients:
            try:
                # Load previous SOFA score
                sm = StateManager(patient["patient_id"], patient["date"])
                history = sm.get_history(days=1)

                if history:
                    # Try to extract SOFA from most recent day
                    last_day = history[0]
                    date = last_day.get("date")

                    if date:
                        temp_sm = StateManager(patient["patient_id"], date)
                        scores_state = temp_sm.load("scores")

                        if scores_state:
                            # Extract JSON
                            text = scores_state.strip()
                            json_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
                            if json_match:
                                json_str = json_match.group(1).strip()
                                scores_data = json.loads(json_str)
                                sofa = scores_data.get("scores", {}).get("sofa", {})
                                patient["priority_score"] = sofa.get("total_score", 0)
                            else:
                                patient["priority_score"] = 0
                        else:
                            patient["priority_score"] = 0
                    else:
                        patient["priority_score"] = 0
                else:
                    patient["priority_score"] = 0

            except Exception as e:
                logger.debug(f"Could not load SOFA for {patient['patient_id']}: {e}")
                patient["priority_score"] = 0

        # Sort by priority score (descending)
        return sorted(patients, key=lambda p: p.get("priority_score", 0), reverse=True)

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get system health and status.

        Returns:
            Dictionary containing:
                - metrics: System-wide metrics
                - health: "healthy", "degraded", or "unhealthy"
                - uptime: Time since last run
        """
        success_rate = (
            (self.metrics["patients_succeeded"] / self.metrics["patients_processed"] * 100)
            if self.metrics["patients_processed"] > 0
            else 0
        )

        # Determine health
        if success_rate >= 90:
            health = "healthy"
        elif success_rate >= 70:
            health = "degraded"
        else:
            health = "unhealthy"

        avg_time = (
            self.metrics["total_elapsed_time"] / self.metrics["patients_processed"]
            if self.metrics["patients_processed"] > 0
            else 0
        )

        return {
            "metrics": {
                "patients_processed": self.metrics["patients_processed"],
                "patients_succeeded": self.metrics["patients_succeeded"],
                "patients_failed": self.metrics["patients_failed"],
                "success_rate": round(success_rate, 2),
                "average_processing_time": round(avg_time, 2),
                "critical_alerts_total": self.metrics["critical_alerts_total"],
            },
            "health": health,
            "last_run_time": self.metrics["last_run_time"],
        }

    def reset_metrics(self):
        """Reset system metrics."""
        self.metrics = {
            "patients_processed": 0,
            "patients_succeeded": 0,
            "patients_failed": 0,
            "total_elapsed_time": 0.0,
            "critical_alerts_total": 0,
            "last_run_time": None,
        }
        logger.info("System metrics reset")
