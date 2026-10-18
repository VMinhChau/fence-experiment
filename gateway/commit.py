# """
# Common commit gateway.

# The gateway represents the commit boundary where a baseline
# must make its final safety decision.

# The gateway itself does not implement a particular baseline's
# revocation semantics.
# """

# from dataclasses import dataclass, field
# from typing import Set, Tuple


# AuthorityEpoch = Tuple[str, int]


# @dataclass(frozen=True)
# class CommitRequest:
#     """
#     Information available at the commit boundary.
#     """

#     operation_id: str
#     artifact_id: str

#     # Authority directly required by this operation.
#     direct_authorities: Set[str] = field(
#         default_factory=set
#     )

#     # Classical epoch-bearing references.
#     epoch_handles: Set[AuthorityEpoch] = field(
#         default_factory=set
#     )

#     # FENCE semantic authorization support.
#     support: Set[AuthorityEpoch] = field(
#         default_factory=set
#     )


# @dataclass(frozen=True)
# class CommitResult:
#     baseline: str
#     operation_id: str
#     artifact_id: str

#     committed: bool
#     pars_violation: bool

#     authority_id: str
#     revoked_epoch: int

#     reason: str

#     support: Set[AuthorityEpoch] = field(
#         default_factory=set
#     )


# class CommitGateway:
#     """
#     Common commit gateway.

#     The gateway validates only the metadata supplied by the
#     selected baseline.

#     This allows all baselines to use the same commit boundary.
#     """

#     def __init__(self) -> None:
#         self.committed_operations: list[CommitResult] = []

#     def commit(
#         self,
#         request: CommitRequest,
#         baseline: str,
#         authority_id: str,
#         revoked_epoch: int,
#     ) -> CommitResult:
#         """
#         Perform the final commit decision.

#         The baseline-specific metadata determines what can
#         be checked here.
#         """

#         # ----------------------------------------------------
#         # FENCE semantic support
#         # ----------------------------------------------------

#         if request.support:

#             for authority, epoch in request.support:

#                 if (
#                     authority == authority_id
#                     and epoch < revoked_epoch
#                 ):
#                     result = CommitResult(
#                         baseline=baseline,
#                         operation_id=request.operation_id,
#                         artifact_id=request.artifact_id,
#                         committed=False,
#                         pars_violation=False,
#                         authority_id=authority_id,
#                         revoked_epoch=revoked_epoch,
#                         reason=(
#                             "Commit refused: artifact carries "
#                             f"stale support ({authority}, {epoch}) "
#                             f"below frontier {revoked_epoch}."
#                         ),
#                         support=set(request.support),
#                     )

#                     self.committed_operations.append(result)
#                     return result

#         # ----------------------------------------------------
#         # Classical epoch handles
#         # ----------------------------------------------------

#         for authority, epoch in request.epoch_handles:

#             if (
#                 authority == authority_id
#                 and epoch < revoked_epoch
#             ):
#                 result = CommitResult(
#                     baseline=baseline,
#                     operation_id=request.operation_id,
#                     artifact_id=request.artifact_id,
#                     committed=False,
#                     pars_violation=False,
#                     authority_id=authority_id,
#                     revoked_epoch=revoked_epoch,
#                     reason=(
#                         "Commit refused: stale epoch handle."
#                     ),
#                     support=set(request.support),
#                 )

#                 self.committed_operations.append(result)
#                 return result

#         # ----------------------------------------------------
#         # No revocation-relevant dependency visible here.
#         # ----------------------------------------------------

#         result = CommitResult(
#             baseline=baseline,
#             operation_id=request.operation_id,
#             artifact_id=request.artifact_id,
#             committed=True,
#             pars_violation=True,
#             authority_id=authority_id,
#             revoked_epoch=revoked_epoch,
#             reason=(
#                 "Commit accepted: no stale revocation-relevant "
#                 "dependency was visible at the commit boundary."
#             ),
#             support=set(request.support),
#         )

#         self.committed_operations.append(result)

#         return result



"""
Common commit gateway.

The gateway represents the commit boundary where a baseline
must make its final safety decision.

The gateway itself does NOT implement any baseline-specific
revocation semantics.

Each baseline must decide whether the operation is allowed
before calling this gateway.

PARS is evaluated independently by monitor/pars.py.
"""

from dataclasses import dataclass, field
from typing import Set, Tuple


AuthorityEpoch = Tuple[str, int]


@dataclass(frozen=True)
class CommitRequest:
    """
    Information supplied by a baseline at the commit boundary.
    """

    operation_id: str
    artifact_id: str

    # Final decision made by the baseline.
    allow_commit: bool

    # Explanation produced by the baseline.
    reason: str

    # Metadata carried by the artifact / execution trace.
    #
    # The gateway records these fields but does not interpret them.
    direct_authorities: Set[str] = field(
        default_factory=set
    )

    epoch_handles: Set[AuthorityEpoch] = field(
        default_factory=set
    )

    support: Set[AuthorityEpoch] = field(
        default_factory=set
    )


@dataclass(frozen=True)
class CommitResult:
    baseline: str
    operation_id: str
    artifact_id: str

    committed: bool

    # IMPORTANT:
    # This is NOT decided by the gateway.
    #
    # It is filled later by the independent PARS evaluator.
    pars_violation: bool

    authority_id: str
    revoked_epoch: int

    reason: str

    support: Set[AuthorityEpoch] = field(
        default_factory=set
    )


class CommitGateway:
    """
    Common commit boundary.

    The gateway only records whether the selected baseline
    allowed the operation.

    It does not inspect:
        - support
        - epoch handles
        - derived_from
        - revocation semantics
        - PARS

    This keeps the gateway baseline-neutral.
    """

    def __init__(self) -> None:
        self.committed_operations: list[CommitResult] = []

    def commit(
        self,
        request: CommitRequest,
        baseline: str,
        authority_id: str,
        revoked_epoch: int,
    ) -> CommitResult:
        """
        Record the baseline's final commit decision.

        PARS is evaluated separately after this call.
        """

        result = CommitResult(
            baseline=baseline,
            operation_id=request.operation_id,
            artifact_id=request.artifact_id,
            committed=request.allow_commit,

            # Filled by the independent PARS evaluator later.
            pars_violation=False,

            authority_id=authority_id,
            revoked_epoch=revoked_epoch,

            reason=request.reason,

            support=set(request.support),
        )

        self.committed_operations.append(result)

        return result    