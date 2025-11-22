"""
End-to-End Integration Tests for ICU Agent System

These tests validate the complete workflow from raw clinical notes
to final report generation.
"""

import logging
import pytest
from pathlib import Path

from agents.base.state import StateManager
from agents.orchestrator import PatientOrchestrator, MainOrchestrator, BatchProcessor


# Setup logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestPatientOrchestrator:
    """Test PatientOrchestrator end-to-end workflow."""

    @pytest.fixture
    def test_patient_id(self):
        """Test patient ID."""
        return "HT001"

    @pytest.fixture
    def test_date(self):
        """Test date."""
        return "2025-11-20"

    @pytest.fixture
    def test_note_path(self, test_patient_id, test_date):
        """Path to test clinical note."""
        # Try multiple possible locations
        possible_paths = [
            f"patients/active/{test_patient_id}/notes/{test_date}.txt",
            f"patients/active/{test_patient_id}/notes/{test_date}-day5.txt",
        ]

        for path_str in possible_paths:
            path = Path(path_str)
            if path.exists():
                return str(path)

        # If no file found, return the standard path (test will handle if missing)
        return possible_paths[0]

    @pytest.fixture
    def orchestrator(self, test_patient_id, test_date):
        """Create PatientOrchestrator instance."""
        config = {
            "model": "claude-sonnet-4-5-20250929",
            "max_tokens": 4096,
            "temperature": 0.0,
        }
        return PatientOrchestrator(test_patient_id, test_date, config)

    def test_orchestrator_initialization(self, orchestrator, test_patient_id, test_date):
        """Test that orchestrator initializes correctly."""
        assert orchestrator.patient_id == test_patient_id
        assert orchestrator.date == test_date
        assert orchestrator.state_manager is not None
        assert orchestrator.parse_supervisor is not None
        assert orchestrator.analysis_supervisor is not None
        assert orchestrator.report_supervisor is not None

    def test_clinical_note_loading(self, orchestrator, test_note_path):
        """Test loading clinical note."""
        # Check if note file exists
        if not Path(test_note_path).exists():
            pytest.skip(f"Test note not found: {test_note_path}")

        # Load note
        success = orchestrator.load_clinical_note(test_note_path)
        assert success, "Failed to load clinical note"

        # Verify state was saved
        input_state = orchestrator.state_manager.load("input")
        assert input_state is not None, "Input state not saved"
        assert len(input_state) > 0, "Input state is empty"

    @pytest.mark.skipif(
        not Path("patients/active/HT001/notes/2025-11-20-day5.txt").exists(),
        reason="Test patient note not available"
    )
    def test_complete_workflow(self, orchestrator, test_note_path):
        """
        Test complete workflow from note to report.

        This test validates:
        1. Note loading
        2. Parse phase (Turkish parser + extractors)
        3. Analysis phase (critical checker + SOFA)
        4. Report phase (report generation)
        5. All state files created
        6. Workflow status updated
        """
        # Run complete workflow
        result = orchestrator.run(note_path=test_note_path)

        # Verify workflow succeeded
        assert result["status"] == "success", f"Workflow failed: {result.get('error')}"
        assert result["patient_id"] == orchestrator.patient_id
        assert result["date"] == orchestrator.date

        # Verify all phases completed
        phases = result.get("phases", {})
        assert "load" in phases
        assert "parse" in phases
        assert "analysis" in phases
        assert "report" in phases

        # Verify parse phase
        parse_result = phases["parse"]
        assert parse_result.get("status") == "success", "Parse phase failed"

        # Verify state files were created
        state_files = [
            "00_input.md",
            "01_parsed.md",
            "02_vitals.md",
            "03_labs.md",
            "05_critical.md",
            "06_scores.md",
            "07_report.md",
        ]

        for state_file in state_files:
            file_path = orchestrator.state_manager.state_dir / state_file
            assert file_path.exists(), f"State file not created: {state_file}"

        # Verify workflow status
        workflow_status = orchestrator.get_workflow_status()
        assert workflow_status.get("completed") is True, "Workflow not marked as completed"

        # Verify SOFA score
        sofa_score = orchestrator.get_sofa_score()
        assert sofa_score >= 0, "SOFA score not calculated"
        assert sofa_score <= 24, f"SOFA score out of range: {sofa_score}"

        logger.info(f"Complete workflow test passed - SOFA: {sofa_score}/24")

    @pytest.mark.skipif(
        not Path("patients/active/HT001/notes/2025-11-20-day5.txt").exists(),
        reason="Test patient note not available"
    )
    def test_parsed_data_completeness(self, orchestrator, test_note_path):
        """Test that parsed data has required completeness."""
        # Run workflow
        result = orchestrator.run(note_path=test_note_path)
        assert result["status"] == "success"

        # Load parsed data
        import json
        import re

        parsed_state = orchestrator.state_manager.load("parsed")
        assert parsed_state is not None

        # Extract JSON
        json_match = re.search(r'```json\s*(.*?)\s*```', parsed_state, re.DOTALL)
        assert json_match is not None, "No JSON found in parsed state"

        parsed_data = json.loads(json_match.group(1))

        # Check required fields
        assert "patient_info" in parsed_data
        assert "hemodynamics" in parsed_data
        assert "respiratory" in parsed_data
        assert "data_completeness" in parsed_data

        # Check data completeness
        completeness = parsed_data["data_completeness"]
        overall_score = completeness.get("overall_score", 0)
        assert overall_score >= 60, f"Data completeness too low: {overall_score}%"

        logger.info(f"Data completeness: {overall_score}%")

    @pytest.mark.skipif(
        not Path("patients/active/HT001/notes/2025-11-20-day5.txt").exists(),
        reason="Test patient note not available"
    )
    def test_critical_value_detection(self, orchestrator, test_note_path):
        """Test critical value detection."""
        # Run workflow
        result = orchestrator.run(note_path=test_note_path)
        assert result["status"] == "success"

        # Get critical alerts
        critical_alerts = orchestrator.get_critical_alerts()

        # HT001 is a stable patient, should have few or no critical values
        # Just verify the method works
        assert isinstance(critical_alerts, list)

        logger.info(f"Critical alerts found: {len(critical_alerts)}")

    @pytest.mark.skipif(
        not Path("patients/active/HT001/notes/2025-11-20-day5.txt").exists(),
        reason="Test patient note not available"
    )
    def test_report_generation(self, orchestrator, test_note_path):
        """Test Turkish report generation."""
        # Run workflow
        result = orchestrator.run(note_path=test_note_path)
        assert result["status"] == "success"

        # Get report
        report_text = orchestrator.report_supervisor.get_report_text()
        assert report_text is not None
        assert len(report_text) > 500, "Report too short"

        # Check for Turkish characters
        turkish_chars = ['ş', 'ğ', 'ü', 'ö', 'ç', 'ı']
        has_turkish = any(char in report_text for char in turkish_chars)
        assert has_turkish, "Report does not appear to be in Turkish"

        # Check for required sections
        required_sections = ["GENEL DURUM", "SİSTEM BAZLI", "ÖNERİ"]
        for section in required_sections:
            assert section in report_text, f"Missing section: {section}"

        logger.info(f"Report generated successfully ({len(report_text)} chars)")

    def test_metrics_tracking(self, orchestrator):
        """Test that metrics are tracked correctly."""
        # Get metrics before running
        metrics_before = orchestrator.get_metrics()

        # Verify structure
        assert "parse_supervisor" in metrics_before
        assert "analysis_supervisor" in metrics_before
        assert "report_supervisor" in metrics_before
        assert "workers" in metrics_before


class TestMainOrchestrator:
    """Test MainOrchestrator system-level coordination."""

    @pytest.fixture
    def main_orchestrator(self):
        """Create MainOrchestrator instance."""
        config = {
            "max_concurrent": 3,
            "enable_parallel": True,
        }
        return MainOrchestrator(config)

    def test_main_orchestrator_initialization(self, main_orchestrator):
        """Test MainOrchestrator initialization."""
        assert main_orchestrator.config is not None
        assert main_orchestrator.metrics is not None

        # Verify initial metrics
        assert main_orchestrator.metrics["patients_processed"] == 0
        assert main_orchestrator.metrics["patients_succeeded"] == 0
        assert main_orchestrator.metrics["patients_failed"] == 0

    def test_system_status(self, main_orchestrator):
        """Test system status retrieval."""
        status = main_orchestrator.get_system_status()

        assert "metrics" in status
        assert "health" in status
        assert status["health"] in ["healthy", "degraded", "unhealthy"]

    def test_metrics_reset(self, main_orchestrator):
        """Test metrics reset."""
        # Modify metrics
        main_orchestrator.metrics["patients_processed"] = 10

        # Reset
        main_orchestrator.reset_metrics()

        # Verify reset
        assert main_orchestrator.metrics["patients_processed"] == 0


class TestBatchProcessor:
    """Test BatchProcessor batch operations."""

    @pytest.fixture
    def batch_processor(self):
        """Create BatchProcessor instance."""
        config = {
            "max_concurrent": 3,
        }
        return BatchProcessor(config=config)

    def test_batch_processor_initialization(self, batch_processor):
        """Test BatchProcessor initialization."""
        assert batch_processor.main_orchestrator is not None
        assert batch_processor.patients_dir is not None

    def test_patient_discovery(self, batch_processor):
        """Test patient discovery."""
        # Discover patients for a date
        patients = batch_processor.discover_patients("2025-11-20")

        # Should be a list (may be empty if no patients)
        assert isinstance(patients, list)

        # If patients found, verify structure
        if patients:
            patient = patients[0]
            assert "patient_id" in patient
            assert "date" in patient
            assert "note_path" in patient

        logger.info(f"Discovered {len(patients)} patients for 2025-11-20")

    def test_get_active_patients(self, batch_processor):
        """Test getting active patients list."""
        active_patients = batch_processor.get_active_patients()

        # Should be a list (may be empty)
        assert isinstance(active_patients, list)

        logger.info(f"Active patients: {len(active_patients)}")


class TestStateManagement:
    """Test StateManager functionality."""

    @pytest.fixture
    def state_manager(self, tmp_path):
        """Create StateManager with temporary directory."""
        return StateManager(
            patient_id="TEST001",
            date="2025-11-20",
            base_dir=str(tmp_path / "state")
        )

    def test_state_manager_initialization(self, state_manager):
        """Test StateManager initialization."""
        assert state_manager.patient_id == "TEST001"
        assert state_manager.date == "2025-11-20"
        assert state_manager.state_dir.exists()

    def test_save_and_load(self, state_manager):
        """Test saving and loading state."""
        # Save test data
        test_data = {
            "test_field": "test_value",
            "number": 123
        }

        state_manager.save("test", test_data, metadata={"source": "test"})

        # Load it back
        loaded = state_manager.load("test")
        assert loaded is not None
        assert "test_field" in loaded
        assert "test_value" in loaded

    def test_workflow_status(self, state_manager):
        """Test workflow status tracking."""
        # Save a phase
        state_manager.save("test", {"data": "test"})

        # Get status
        status = state_manager.get_status()
        assert "phases" in status
        assert "test" in status["phases"]

        # Finalize
        state_manager.finalize()
        assert state_manager.is_completed()


# Mark slow tests
pytestmark = pytest.mark.slow


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
