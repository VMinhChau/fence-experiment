"""
Independent PARS evaluator.

This module evaluates whether a committed operation actually violates
Post-Acknowledgment Revocation Safety.

It is NOT a baseline. It acts as an oracle over the execution trace.
"""

from scenarios.trace import ExecutionTrace


def semantic_support(
    trace: ExecutionTrace,
    artifact_id: str,
) -> set[tuple[str, int]]:
    """
    Reconstruct the semantic authorization support of an artifact.

    This is ground-truth evaluation logic, independent of any baseline.
    """

    artifact = trace.artifact(artifact_id)

    # Direct authorization evidence.
    support = set(artifact.epoch_handles)

    # Semantic provenance.
    for parent_id in artifact.derived_from:
        support.update(
            semantic_support(trace, parent_id)
        )

    return support


def violates_pars(
    trace: ExecutionTrace,
    artifact_id: str,
) -> bool:
    """
    Return True iff the artifact is semantically dependent on a
    revoked authorization epoch.
    """

    support = semantic_support(trace, artifact_id)

    for authority, epoch in support:
        if (
            authority == trace.authority_id
            and epoch < trace.revoked_epoch
        ):
            return True

    return False