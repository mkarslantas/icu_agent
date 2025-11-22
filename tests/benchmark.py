#!/usr/bin/env python
"""
Performance Benchmarking for ICU Agent System

Measures and reports performance metrics for the multi-agent system:
- Single patient processing time
- Batch processing time (sequential vs parallel)
- Phase breakdown timings
- Memory usage
- API call counts
- Token usage (estimated)

Usage:
    python tests/benchmark.py --patients 1 --output benchmark_report.md
    python tests/benchmark.py --patients 10 --parallel --output batch_benchmark.md
"""

import argparse
import time
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from agents.orchestrator import PatientOrchestrator, MainOrchestrator, BatchProcessor


class PerformanceBenchmark:
    """Performance benchmarking for ICU monitoring system."""

    def __init__(self):
        """Initialize benchmark."""
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "single_patient": {},
            "batch_processing": {},
            "phase_timings": {},
        }

    def benchmark_single_patient(
        self,
        patient_id: str = "HT001",
        date: str = "2025-11-20"
    ) -> Dict[str, Any]:
        """
        Benchmark single patient processing.

        Args:
            patient_id: Patient identifier
            date: Date string

        Returns:
            Dictionary with benchmark results
        """
        print(f"\n{'='*60}")
        print(f"SINGLE PATIENT BENCHMARK")
        print(f"{'='*60}")
        print(f"Patient: {patient_id}")
        print(f"Date: {date}\n")

        # Create orchestrator
        start_time = time.time()
        orchestrator = PatientOrchestrator(patient_id, date)
        init_time = time.time() - start_time

        # Run workflow
        print("Running workflow...")
        workflow_start = time.time()

        try:
            result = orchestrator.run()
            total_time = time.time() - workflow_start

            if result["status"] != "success":
                print(f"❌ Workflow failed: {result.get('error')}")
                return {"status": "error", "error": result.get("error")}

        except Exception as e:
            print(f"❌ Error: {e}")
            return {"status": "error", "error": str(e)}

        # Extract phase timings
        phases = result.get("phases", {})
        phase_timings = {}

        for phase_name, phase_result in phases.items():
            if isinstance(phase_result, dict):
                elapsed = phase_result.get("elapsed_time", 0)
                phase_timings[phase_name] = elapsed

        # Get metrics
        metrics = orchestrator.get_metrics()

        # Compile results
        benchmark_result = {
            "status": "success",
            "initialization_time": round(init_time, 3),
            "total_time": round(total_time, 3),
            "phase_timings": phase_timings,
            "sofa_score": orchestrator.get_sofa_score(),
            "critical_alerts": len(orchestrator.get_critical_alerts()),
            "metrics": metrics,
        }

        # Display results
        print(f"\n✓ Workflow completed successfully!")
        print(f"\nTIMINGS:")
        print(f"  Initialization: {init_time:.3f}s")
        print(f"  Total workflow: {total_time:.3f}s")

        if phase_timings:
            print(f"\n  Phase breakdown:")
            for phase, timing in phase_timings.items():
                print(f"    {phase}: {timing:.3f}s")

        print(f"\nRESULTS:")
        print(f"  SOFA Score: {orchestrator.get_sofa_score()}/24")
        print(f"  Critical Alerts: {len(orchestrator.get_critical_alerts())}")

        # Check against targets
        target_time = 120  # 120 seconds target
        if total_time < target_time:
            print(f"\n✓ Performance target met ({total_time:.1f}s < {target_time}s)")
        else:
            print(f"\n⚠ Performance target missed ({total_time:.1f}s > {target_time}s)")

        self.results["single_patient"] = benchmark_result
        return benchmark_result

    def benchmark_batch(
        self,
        num_patients: int = 10,
        parallel: bool = True
    ) -> Dict[str, Any]:
        """
        Benchmark batch processing.

        Args:
            num_patients: Number of patients to process
            parallel: Use parallel processing

        Returns:
            Dictionary with benchmark results
        """
        print(f"\n{'='*60}")
        print(f"BATCH PROCESSING BENCHMARK")
        print(f"{'='*60}")
        print(f"Patients: {num_patients}")
        print(f"Mode: {'Parallel' if parallel else 'Sequential'}\n")

        # Discover patients
        batch_processor = BatchProcessor(config={"enable_parallel": parallel})
        patients = batch_processor.discover_patients("2025-11-20")

        if not patients:
            print("❌ No patients found for benchmarking")
            return {"status": "error", "error": "No patients available"}

        # Limit to requested number
        patients = patients[:num_patients]
        actual_count = len(patients)

        print(f"Found {actual_count} patients")

        # Run batch processing
        print(f"\nProcessing batch ({parallel and 'parallel' or 'sequential'})...")
        start_time = time.time()

        result = batch_processor.main_orchestrator.process_batch(
            patients,
            parallel=parallel
        )

        total_time = time.time() - start_time

        # Compile results
        summary = result.get("summary", {})

        benchmark_result = {
            "status": result.get("status"),
            "num_patients": actual_count,
            "parallel": parallel,
            "total_time": round(total_time, 3),
            "succeeded": summary.get("succeeded", 0),
            "failed": summary.get("failed", 0),
            "success_rate": summary.get("success_rate", 0),
            "average_time": summary.get("average_time", 0),
        }

        # Display results
        print(f"\n✓ Batch processing completed!")
        print(f"\nRESULTS:")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Succeeded: {summary.get('succeeded', 0)}/{actual_count}")
        print(f"  Success rate: {summary.get('success_rate', 0):.1f}%")
        print(f"  Average time: {summary.get('average_time', 0):.3f}s per patient")

        # Check against targets
        if parallel:
            target_time = 180  # 3 minutes for 10 patients parallel
        else:
            target_time = num_patients * 120  # 2 min per patient sequential

        if total_time < target_time:
            print(f"\n✓ Performance target met ({total_time:.1f}s < {target_time}s)")
        else:
            print(f"\n⚠ Performance target missed ({total_time:.1f}s > {target_time}s)")

        self.results["batch_processing"][f"{actual_count}_patients_{'parallel' if parallel else 'sequential'}"] = benchmark_result
        return benchmark_result

    def compare_sequential_vs_parallel(
        self,
        num_patients: int = 5
    ) -> Dict[str, Any]:
        """
        Compare sequential vs parallel batch processing.

        Args:
            num_patients: Number of patients to process

        Returns:
            Comparison results
        """
        print(f"\n{'='*60}")
        print(f"SEQUENTIAL VS PARALLEL COMPARISON")
        print(f"{'='*60}")

        # Run sequential
        print("\n1. Running SEQUENTIAL batch...")
        seq_result = self.benchmark_batch(num_patients, parallel=False)

        # Run parallel
        print("\n2. Running PARALLEL batch...")
        par_result = self.benchmark_batch(num_patients, parallel=True)

        # Compare
        if seq_result["status"] == "success" and par_result["status"] == "success":
            speedup = seq_result["total_time"] / par_result["total_time"]

            print(f"\n{'='*60}")
            print(f"COMPARISON RESULTS")
            print(f"{'='*60}")
            print(f"Sequential time: {seq_result['total_time']:.3f}s")
            print(f"Parallel time:   {par_result['total_time']:.3f}s")
            print(f"Speedup:         {speedup:.2f}x")

            if speedup > 1.5:
                print(f"\n✓ Good parallelization benefit ({speedup:.2f}x speedup)")
            elif speedup > 1.0:
                print(f"\n⚠ Moderate parallelization benefit ({speedup:.2f}x speedup)")
            else:
                print(f"\n⚠ Limited parallelization benefit ({speedup:.2f}x speedup)")

        return {
            "sequential": seq_result,
            "parallel": par_result,
        }

    def generate_report(self, output_path: str = "benchmark_report.md"):
        """
        Generate markdown benchmark report.

        Args:
            output_path: Path to output file
        """
        lines = [
            "# ICU Agent Performance Benchmark Report",
            "",
            f"**Generated:** {self.results['timestamp']}",
            "",
            "---",
            "",
        ]

        # Single patient results
        if self.results.get("single_patient"):
            sp = self.results["single_patient"]

            lines.extend([
                "## Single Patient Processing",
                "",
                f"**Status:** {sp.get('status', 'N/A')}",
                f"**Total Time:** {sp.get('total_time', 0):.3f}s",
                f"**SOFA Score:** {sp.get('sofa_score', 'N/A')}/24",
                f"**Critical Alerts:** {sp.get('critical_alerts', 0)}",
                "",
                "### Phase Timings",
                "",
            ])

            phase_timings = sp.get("phase_timings", {})
            if phase_timings:
                lines.append("| Phase | Time (s) | Percentage |")
                lines.append("|-------|----------|------------|")

                total = sp.get("total_time", 0)
                for phase, timing in phase_timings.items():
                    pct = (timing / total * 100) if total > 0 else 0
                    lines.append(f"| {phase} | {timing:.3f} | {pct:.1f}% |")

            lines.append("")

        # Batch processing results
        if self.results.get("batch_processing"):
            lines.extend([
                "## Batch Processing",
                "",
            ])

            for config_name, bp in self.results["batch_processing"].items():
                lines.extend([
                    f"### {config_name.replace('_', ' ').title()}",
                    "",
                    f"**Status:** {bp.get('status', 'N/A')}",
                    f"**Patients:** {bp.get('num_patients', 0)}",
                    f"**Total Time:** {bp.get('total_time', 0):.3f}s",
                    f"**Success Rate:** {bp.get('success_rate', 0):.1f}%",
                    f"**Average Time:** {bp.get('average_time', 0):.3f}s per patient",
                    "",
                ])

        # Performance targets
        lines.extend([
            "---",
            "",
            "## Performance Targets",
            "",
            "| Metric | Target | Actual | Status |",
            "|--------|--------|--------|--------|",
        ])

        # Single patient target
        if self.results.get("single_patient"):
            sp = self.results["single_patient"]
            target = 120
            actual = sp.get("total_time", 0)
            status = "✓ Pass" if actual < target else "✗ Fail"
            lines.append(f"| Single patient | < {target}s | {actual:.1f}s | {status} |")

        # Batch parallel target
        for config_name, bp in self.results.get("batch_processing", {}).items():
            if "parallel" in config_name:
                target = 180
                actual = bp.get("total_time", 0)
                status = "✓ Pass" if actual < target else "✗ Fail"
                lines.append(f"| Batch (10 parallel) | < {target}s | {actual:.1f}s | {status} |")

        report_text = "\n".join(lines)

        # Save report
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)

        print(f"\n✓ Benchmark report saved to: {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="ICU Agent Performance Benchmark")
    parser.add_argument(
        "--patients",
        "-p",
        type=int,
        default=1,
        help="Number of patients to process (default: 1)"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Use parallel processing for batch"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare sequential vs parallel"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="benchmark_report.md",
        help="Output report path (default: benchmark_report.md)"
    )

    args = parser.parse_args()

    # Create benchmark
    benchmark = PerformanceBenchmark()

    try:
        if args.patients == 1:
            # Single patient benchmark
            benchmark.benchmark_single_patient()
        elif args.compare:
            # Comparison
            benchmark.compare_sequential_vs_parallel(args.patients)
        else:
            # Batch benchmark
            benchmark.benchmark_batch(args.patients, args.parallel)

        # Generate report
        benchmark.generate_report(args.output)

    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Benchmark error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
