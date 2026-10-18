"""
Naive revocation baseline.

The baseline checks only direct authority requirements
of the commit operation.

It does not track semantic derivation.
"""

from scenarios.trace import ExecutionTrace
from gateway.commit import CommitGateway, CommitRequest, CommitResult


def evaluate(
    trace: ExecutionTrace,
    gateway: CommitGateway,
) -> CommitResult:
    """
    Evaluate the shared execution trace using naive revocation.

    The patch was derived from previously authorized data,
    but the final commit itself does not directly call T.

    Therefore the naive baseline sees no active authority
    requirement at commit time.
    """

    patch = trace.patch

    request = CommitRequest(
        operation_id="merge-P",
        artifact_id=patch.artifact_id,

        allow_commit=True,
        reason=(
            "Commit accepted: naive revocation does not track "
            "derived artifacts."
        ),
        # Naive baseline only knows direct authority use.
        direct_authorities=set(),

        # It deliberately does not provide semantic support.
        epoch_handles=set(),
        support=set(),
    )

    return gateway.commit(
        request=request,
        baseline="Naive Revocation",
        authority_id=trace.authority_id,
        revoked_epoch=trace.revoked_epoch,
    )