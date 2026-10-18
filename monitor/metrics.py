"""
Experiment metrics collector for FENCE.

This module records baseline results without changing
the commit decision.

Metrics are grouped by scenario so that results from
different scenarios remain easy to interpret.
"""

from dataclasses import dataclass, field
from typing import Dict, List

from gateway.commit import CommitResult


@dataclass
class ExperimentMetrics:
    """
    Collect results grouped by scenario.
    """

    results: Dict[str, List[CommitResult]] = field(
        default_factory=dict
    )

    def add(
        self,
        scenario_name: str,
        result: CommitResult,
    ) -> None:
        self.results.setdefault(
            scenario_name,
            [],
        ).append(result)

    def scenario_results(
        self,
        scenario_name: str,
    ) -> List[CommitResult]:
        return self.results.get(
            scenario_name,
            [],
        )

    @property
    def all_results(self) -> List[CommitResult]:
        return [
            result
            for scenario_results in self.results.values()
            for result in scenario_results
        ]

    @property
    def pars_violations(self) -> int:
        return sum(
            result.pars_violation
            for result in self.all_results
        )

    @property
    def commits(self) -> int:
        return sum(
            result.committed
            for result in self.all_results
        )

    @property
    def refusals(self) -> int:
        return sum(
            not result.committed
            for result in self.all_results
        )

    def print_scenario(
        self,
        scenario_name: str,
    ) -> None:
        results = self.scenario_results(
            scenario_name
        )

        print()
        print("=" * 72)
        print(f"SCENARIO: {scenario_name}")
        print("=" * 72)

        for result in results:
            print()
            print(f"Baseline:       {result.baseline}")
            print(f"Artifact:       {result.artifact_id}")
            print(f"Committed:      {result.committed}")
            print(
                f"PARS violation: "
                f"{result.pars_violation}"
            )
            print(f"Reason:         {result.reason}")

            if result.support:
                print(
                    f"Support:        "
                    f"{sorted(result.support)}"
                )

    def print_overall_summary(self) -> None:
        print()
        print("=" * 72)
        print("OVERALL EXPERIMENT SUMMARY")
        print("=" * 72)

        by_baseline: Dict[
            str,
            List[CommitResult],
        ] = {}

        for result in self.all_results:
            by_baseline.setdefault(
                result.baseline,
                [],
            ).append(result)

        print()

        for baseline, results in by_baseline.items():
            total = len(results)
            violations = sum(
                result.pars_violation
                for result in results
            )
            commits = sum(
                result.committed
                for result in results
            )
            refusals = total - commits

            violation_rate = (
                violations / total
                if total > 0
                else 0.0
            )

            print(f"{baseline}")
            print(f"  Evaluations:     {total}")
            print(f"  Commits:         {commits}")
            print(f"  Refusals:        {refusals}")
            print(
                f"  PARS violations: "
                f"{violations}"
            )
            print(
                f"  PARS violation rate: "
                f"{violation_rate:.2%}"
            )
            print()

        print("-" * 72)
        print(
            f"Total evaluations: "
            f"{len(self.all_results)}"
        )
        print(
            f"Total commits:     "
            f"{self.commits}"
        )
        print(
            f"Total refusals:    "
            f"{self.refusals}"
        )
        print(
            f"Total PARS violations: "
            f"{self.pars_violations}"
        )
        print("-" * 72)


def create_metrics() -> ExperimentMetrics:
    return ExperimentMetrics()