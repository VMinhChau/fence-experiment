from scenarios.trace import ExecutionTrace
from gateway.commit import (
    CommitGateway,
    CommitRequest,
    CommitResult,
)


def evaluate(
    trace: ExecutionTrace,
    gateway: CommitGateway,
) -> CommitResult:

    patch = trace.patch

    stale_handle = any(
        authority == trace.authority_id
        and epoch < trace.revoked_epoch
        for authority, epoch in patch.epoch_handles
    )

    if stale_handle:
        allow_commit = False
        reason = (
            "Commit refused: patch carries a stale epoch handle."
        )
    else:
        allow_commit = True
        reason = (
            "Commit accepted: no stale explicit epoch handle "
            "was present."
        )

    request = CommitRequest(
        operation_id="merge-P",
        artifact_id=patch.artifact_id,
        allow_commit=allow_commit,
        reason=reason,
        direct_authorities=set(),
        epoch_handles=set(patch.epoch_handles),
        support=set(),
    )

    return gateway.commit(
        request=request,
        baseline="Epoch Fencing",
        authority_id=trace.authority_id,
        revoked_epoch=trace.revoked_epoch,
    )