# """
# FENCE baseline.

# FENCE tracks semantic authorization support across
# derived artifacts and validates the final artifact
# against the revocation frontier.
# """

# from authority.fence import Artifact, Fence

# from scenarios.trace import ExecutionTrace
# from gateway.commit import CommitGateway, CommitRequest, CommitResult


# def evaluate(
#     trace: ExecutionTrace,
#     gateway: CommitGateway,
# ) -> CommitResult:
#     """
#     Evaluate the shared real-agent execution under FENCE.

#     The LLM produced the actual contents.

#     FENCE, outside the LLM, reconstructs semantic support:

#         R <- T@0
#         M <- R
#         P <- M

#     Therefore:

#         support(P) = {(T, 0)}
#     """

#     fence = Fence()

#     # --------------------------------------------------------
#     # R: obtained using T@0
#     # --------------------------------------------------------

#     response = Artifact(
#         artifact_id=trace.response.artifact_id,
#         content=trace.response.content,
#         support={
#             (
#                 trace.authority_id,
#                 trace.initial_epoch,
#             )
#         },
#     )

#     # --------------------------------------------------------
#     # M: derived from R
#     # --------------------------------------------------------

#     memory = fence.derive(
#         trace.memory.artifact_id,
#         trace.memory.content,
#         response,
#     )

#     # --------------------------------------------------------
#     # P: derived from M
#     # --------------------------------------------------------

#     patch = fence.derive(
#         trace.patch.artifact_id,
#         trace.patch.content,
#         memory,
#     )

#     # --------------------------------------------------------
#     # Revoke T
#     # --------------------------------------------------------

#     fence.revoke(
#         authority=trace.authority_id,
#         new_epoch=trace.revoked_epoch,
#     )

#     # --------------------------------------------------------
#     # Commit request
#     # --------------------------------------------------------

#     request = CommitRequest(
#         operation_id="merge-P",
#         artifact_id=patch.artifact_id,

#         direct_authorities=set(),
#         epoch_handles=set(),

#         # This is the FENCE-specific information.
#         support=patch.support,
#     )

#     return gateway.commit(
#         request=request,
#         baseline="FENCE",
#         authority_id=trace.authority_id,
#         revoked_epoch=trace.revoked_epoch,
#     )


from authority.fence import Artifact, Fence
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

    fence = Fence()

    response = Artifact(
        artifact_id=trace.response.artifact_id,
        content=trace.response.content,
        support=set(trace.response.epoch_handles),
    )

    memory = fence.derive(
        trace.memory.artifact_id,
        trace.memory.content,
        response,
    )

    patch = fence.derive(
        trace.patch.artifact_id,
        trace.patch.content,
        memory,
    )

    fence.revoke(
        authority=trace.authority_id,
        new_epoch=trace.revoked_epoch,
    )

    live = fence.validate_commit(patch)

    if live:
        allow_commit = True
        reason = "Commit accepted: FENCE support is live."
    else:
        allow_commit = False
        reason = (
            "Commit refused: artifact carries stale semantic support."
        )

    request = CommitRequest(
        operation_id="merge-P",
        artifact_id=patch.artifact_id,
        allow_commit=allow_commit,
        reason=reason,
        direct_authorities=set(),
        epoch_handles=set(),
        support=set(patch.support),
    )

    return gateway.commit(
        request=request,
        baseline="FENCE",
        authority_id=trace.authority_id,
        revoked_epoch=trace.revoked_epoch,
    )