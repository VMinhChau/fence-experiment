# """
# Shared execution trace for FENCE experiments.

# A real agent execution is performed once and represented here.
# All baselines replay/evaluate the same trace.
# """

# from dataclasses import dataclass, field
# from typing import List, Tuple


# AuthorityEpoch = Tuple[str, int]


# @dataclass(frozen=True)
# class TraceArtifact:
#     """
#     Artifact produced during the real agent execution.

#     The content comes from the real LLM/tool execution.

#     The provenance fields describe the execution history
#     independently from any particular baseline.
#     """

#     artifact_id: str
#     content: str

#     # Direct authority used to obtain the artifact.
#     direct_authorities: set[str] = field(default_factory=set)

#     # Classical epoch-bearing references, if any.
#     epoch_handles: set[AuthorityEpoch] = field(default_factory=set)

#     # Semantic derivation relation in the common execution.
#     derived_from: Tuple[str, ...] = ()


# @dataclass(frozen=True)
# class ExecutionTrace:
#     """
#     One immutable execution trace shared by all baselines.

#     The trace corresponds to:

#         T@0 -> R -> M -> P -> revoke(T) -> commit(P)

#     No baseline result is stored here.
#     """

#     authority_id: str
#     agent_id: str

#     initial_epoch: int
#     revoked_epoch: int

#     response: TraceArtifact
#     memory: TraceArtifact
#     patch: TraceArtifact

#     # Ordered events make the execution explicit and replayable.
#     events: List[str] = field(default_factory=list)

#     def artifact(self, artifact_id: str) -> TraceArtifact:
#         artifacts = {
#             self.response.artifact_id: self.response,
#             self.memory.artifact_id: self.memory,
#             self.patch.artifact_id: self.patch,
#         }

#         return artifacts[artifact_id]


"""
Shared execution trace for FENCE experiments.

The real agent is executed once. The resulting execution is
represented as an ExecutionTrace and replayed by all baselines.

The trace records what happened during the common execution;
it does not encode any baseline-specific decision.
"""

from dataclasses import dataclass, field
from typing import FrozenSet, Tuple


AuthorityEpoch = Tuple[str, int]


@dataclass(frozen=True)
class TraceArtifact:
    """
    An artifact produced during the common agent execution.

    `epoch_handles` represents explicit authorization handles that
    remain attached to the artifact.

    `derived_from` represents semantic provenance at the execution
    level. Baselines may interpret this provenance differently.
    """

    artifact_id: str
    content: str

    # Explicit authorization handles still carried by the artifact.
    epoch_handles: FrozenSet[AuthorityEpoch] = frozenset()

    # IDs of artifacts from which this artifact was derived.
    derived_from: Tuple[str, ...] = ()


@dataclass(frozen=True)
class TraceEvent:
    """
    One event in the common execution trace.
    """

    event_type: str
    artifact_id: str | None = None
    authority_id: str | None = None
    epoch: int | None = None
    description: str = ""


@dataclass(frozen=True)
class ExecutionTrace:
    """
    Baseline-neutral representation of one real-agent execution.

    All baselines must consume the same ExecutionTrace.
    """

    authority_id: str
    agent_id: str

    initial_epoch: int
    revoked_epoch: int

    response: TraceArtifact
    memory: TraceArtifact
    patch: TraceArtifact

    events: Tuple[TraceEvent, ...] = ()

    def artifact(self, artifact_id: str) -> TraceArtifact:
        artifacts = {
            self.response.artifact_id: self.response,
            self.memory.artifact_id: self.memory,
            self.patch.artifact_id: self.patch,
        }

        try:
            return artifacts[artifact_id]
        except KeyError as exc:
            raise KeyError(
                f"Unknown artifact_id: {artifact_id}"
            ) from exc

    def validate(self) -> None:
        """
        Validate structural invariants of the common execution.
        """

        if self.initial_epoch >= self.revoked_epoch:
            raise ValueError(
                "revoked_epoch must be greater than initial_epoch."
            )

        # The canonical execution is:
        # response -> memory -> patch
        if self.memory.derived_from != (
            self.response.artifact_id,
        ):
            raise ValueError(
                "Memory must be derived from the response."
            )

        if self.patch.derived_from != (
            self.memory.artifact_id,
        ):
            raise ValueError(
                "Patch must be derived from memory."
            )

        # The semantic patch intentionally does NOT carry the
        # original epoch handle in the canonical semantic case.
        #
        # This is what allows us to distinguish:
        #
        #   classical epoch fencing
        #       from
        #   semantic support tracking.
        #
        # We do not force this invariant globally because other
        # scenarios may intentionally preserve a handle.