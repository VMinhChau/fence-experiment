"""
Canonical Figure 1 experiment for FENCE.

Goal
----
Reproduce the semantic separation described in Figure 1:

    Naive Revocation  -> commit succeeds
    Epoch Fencing     -> commit succeeds
    FENCE             -> commit is refused

IMPORTANT
---------
This experiment does NOT set the expected commit result directly.

All three baselines receive the same logical execution:

    T@0
      |
      v
      R
      |
      v
      M
      |
      v
      P
      |
      v
   revoke(T)
      |
      v
   commit(P)

Each baseline independently evaluates whether P can commit.

The only difference is what revocation-relevant information
the baseline preserves:

    Naive:
        checks direct authority use at commit time.

    Epoch Fencing:
        checks epoch-bearing handles/references.

    FENCE:
        checks semantic authorization support propagated
        through derived artifacts.
"""

from dataclasses import dataclass, field
from typing import Set, Tuple

from authority.manager import AuthorityManager
from authority.fence import Artifact, Fence


# ============================================================
# Experiment constants
# ============================================================

AGENT_ID = "fence_agent"
RESOURCE = "customer:C001"
ACTION = "read_risk_profile"
AUTHORITY_ID = "T"


# ============================================================
# Baseline-specific representations
# ============================================================

@dataclass(frozen=True)
class EpochHandle:
    """
    A reference/handle carrying an authorization epoch.

    Classical epoch fencing can reject a stale artifact only
    when such a handle survives until the enforcement point.
    """

    authority_id: str
    epoch: int


@dataclass
class DerivedArtifact:
    """
    Representation used by the baseline simulations.

    This is intentionally different from FENCE's Artifact.

    `direct_authorities` represents authority directly required
    by an operation.

    `epoch_handles` represents classical epoch-bearing references.

    FENCE instead uses its own Artifact.support.
    """

    artifact_id: str
    content: str

    direct_authorities: Set[str] = field(default_factory=set)

    epoch_handles: Set[EpochHandle] = field(default_factory=set)


@dataclass
class CommitOperation:
    """
    Commit operation executed at t4.
    """

    operation_id: str
    artifact: DerivedArtifact


@dataclass
class CanonicalTrace:
    """
    The common logical execution shared by all baselines.

    The trace itself does not contain a baseline result.
    """

    authority_id: str
    initial_epoch: int
    revoked_epoch: int

    response_content: str
    memory_content: str
    patch_content: str


# ============================================================
# Control-plane setup
# ============================================================

def create_authority() -> tuple[AuthorityManager, object]:
    """
    Create the conventional authority used by the experiment.

    T is obtained from AuthorityManager rather than being
    hard-coded as an epoch inside the experiment.
    """

    manager = AuthorityManager()

    authority = manager.grant(
        authority_id=AUTHORITY_ID,
        agent_id=AGENT_ID,
        resource=RESOURCE,
        action=ACTION,
    )

    return manager, authority


# ============================================================
# Canonical execution trace
# ============================================================

def build_canonical_trace() -> CanonicalTrace:
    """
    Execute the common control-plane part of Figure 1.

    t0:
        Obtain T@0.

    t1:
        Produce R and derive M.

    t2:
        Produce P.

    t3:
        Revoke T.

    The actual baseline-specific representations are created
    separately from this logical trace.
    """

    manager, authority = create_authority()

    # --------------------------------------------------------
    # t0: T is active at epoch 0
    # --------------------------------------------------------

    assert manager.check(
        agent_id=AGENT_ID,
        resource=RESOURCE,
        action=ACTION,
    )

    initial_epoch = authority.epoch

    # --------------------------------------------------------
    # Logical execution
    # --------------------------------------------------------

    response_content = (
        "Customer C001 has a high-risk profile."
    )

    memory_content = (
        "C001 is high risk."
    )

    patch_content = (
        "Flag C001 for enhanced review."
    )

    # --------------------------------------------------------
    # t3: revoke T
    # --------------------------------------------------------

    revoked = manager.revoke(
        agent_id=AGENT_ID,
        resource=RESOURCE,
        action=ACTION,
    )

    assert revoked is not None
    assert revoked.status == "REVOKED"

    revoked_epoch = manager.current_epoch(
        AUTHORITY_ID,
    )

    assert revoked_epoch > initial_epoch

    return CanonicalTrace(
        authority_id=AUTHORITY_ID,
        initial_epoch=initial_epoch,
        revoked_epoch=revoked_epoch,
        response_content=response_content,
        memory_content=memory_content,
        patch_content=patch_content,
    )


# ============================================================
# Naive Revocation
# ============================================================

def build_naive_artifacts(
    trace: CanonicalTrace,
) -> CommitOperation:
    """
    Construct the artifacts as visible to naive revocation.

    R -> M -> P is semantic derivation, but naive revocation
    does not maintain provenance/support metadata.

    The final commit operation therefore contains only the
    authorities directly needed by the commit itself.

    In this canonical scenario, merge/commit does not directly
    call T.
    """

    response = DerivedArtifact(
        artifact_id="R",
        content=trace.response_content,
    )

    memory = DerivedArtifact(
        artifact_id="M",
        content=trace.memory_content,
    )

    patch = DerivedArtifact(
        artifact_id="P",
        content=trace.patch_content,
    )

    # These objects deliberately model what the naive system
    # knows. No semantic support is retained.
    #
    # The empty set is not the experimental result.
    # It is the representation of the commit operation:
    # P does not directly invoke T.

    assert response.direct_authorities == set()
    assert memory.direct_authorities == set()
    assert patch.direct_authorities == set()

    operation = CommitOperation(
        operation_id="merge-P",
        artifact=patch,
    )

    return operation


def naive_can_commit(
    operation: CommitOperation,
    manager: AuthorityManager,
) -> bool:
    """
    Naive revocation policy.

    It checks only authorities directly required by the
    current operation.

    It does NOT inspect semantic derivation.
    """

    for authority_id in operation.artifact.direct_authorities:

        # The canonical operation would need a mapping from
        # authority ID to authorization metadata. For this
        # experiment the only relevant authority is T.
        if authority_id != AUTHORITY_ID:
            continue

        authority = manager.get_authority(
            agent_id=AGENT_ID,
            resource=RESOURCE,
            action=ACTION,
        )

        if authority is None:
            return False

        if authority.status != "ACTIVE":
            return False

    return True


def run_naive_revocation(
    trace: CanonicalTrace,
) -> dict:
    """
    Evaluate the canonical operation under naive revocation.
    """

    # Recreate the authority state used for this evaluation.
    manager, _ = create_authority()

    # Revoke it exactly as in the canonical trace.
    revoked = manager.revoke(
        agent_id=AGENT_ID,
        resource=RESOURCE,
        action=ACTION,
    )

    assert revoked is not None
    assert manager.current_epoch(AUTHORITY_ID) == trace.revoked_epoch

    operation = build_naive_artifacts(trace)

    committed = naive_can_commit(
        operation,
        manager,
    )

    return {
        "baseline": "Naive Revocation",
        "authority_id": trace.authority_id,
        "original_epoch": trace.initial_epoch,
        "revoked_epoch": trace.revoked_epoch,
        "artifact": operation.artifact.artifact_id,
        "committed": committed,
        "pars_violation": committed,
    }


# ============================================================
# Classical Epoch Fencing
# ============================================================

def build_epoch_fenced_artifacts(
    trace: CanonicalTrace,
) -> CommitOperation:
    """
    Construct the same semantic derivation under classical
    epoch fencing.

    R initially has an epoch-bearing handle T@0.

    When R is transformed into ordinary semantic content M,
    and M is transformed into P, the handle is not preserved.

    This models the limitation that classical epoch fencing
    protects reference/handle carriers but does not by itself
    track arbitrary semantic derivation.
    """

    response = DerivedArtifact(
        artifact_id="R",
        content=trace.response_content,
        epoch_handles={
            EpochHandle(
                authority_id=trace.authority_id,
                epoch=trace.initial_epoch,
            )
        },
    )

    # Semantic materialization into memory.
    #
    # No epoch handle is carried forward.
    memory = DerivedArtifact(
        artifact_id="M",
        content=trace.memory_content,
    )

    # Semantic materialization into patch.
    #
    # Again, no epoch handle is carried forward.
    patch = DerivedArtifact(
        artifact_id="P",
        content=trace.patch_content,
    )

    # Verify the intended carrier distinction.
    assert len(response.epoch_handles) == 1
    assert memory.epoch_handles == set()
    assert patch.epoch_handles == set()

    return CommitOperation(
        operation_id="merge-P",
        artifact=patch,
    )


def epoch_fencing_can_commit(
    operation: CommitOperation,
    frontier: dict[str, int],
) -> bool:
    """
    Classical epoch-fencing policy.

    Reject only when a stale epoch-bearing handle reaches
    the enforcement point.
    """

    for handle in operation.artifact.epoch_handles:

        current_frontier = frontier.get(
            handle.authority_id,
            0,
        )

        if handle.epoch < current_frontier:
            return False

    return True


def run_epoch_fencing(
    trace: CanonicalTrace,
) -> dict:
    """
    Evaluate the canonical operation under epoch fencing.
    """

    operation = build_epoch_fenced_artifacts(trace)

    frontier = {
        trace.authority_id: trace.revoked_epoch,
    }

    committed = epoch_fencing_can_commit(
        operation,
        frontier,
    )

    return {
        "baseline": "Epoch Fencing",
        "authority_id": trace.authority_id,
        "original_epoch": trace.initial_epoch,
        "revoked_epoch": trace.revoked_epoch,
        "artifact": operation.artifact.artifact_id,
        "committed": committed,
        "pars_violation": committed,
    }


# ============================================================
# FENCE
# ============================================================

def build_fence_artifacts(
    trace: CanonicalTrace,
) -> tuple[Fence, Artifact]:
    """
    Construct R -> M -> P using FENCE support propagation.
    """

    fence = Fence()

    # --------------------------------------------------------
    # t0: R derives from T@0
    # --------------------------------------------------------

    response = Artifact(
        artifact_id="R",
        content=trace.response_content,
        support={
            (
                trace.authority_id,
                trace.initial_epoch,
            )
        },
    )

    # --------------------------------------------------------
    # t1: M derives from R
    # --------------------------------------------------------

    memory = fence.derive(
        "M",
        trace.memory_content,
        response,
    )

    # --------------------------------------------------------
    # t2: P derives from M
    # --------------------------------------------------------

    patch = fence.derive(
        "P",
        trace.patch_content,
        memory,
    )

    # --------------------------------------------------------
    # Verify semantic propagation
    # --------------------------------------------------------

    expected_support = {
        (
            trace.authority_id,
            trace.initial_epoch,
        )
    }

    assert response.support == expected_support
    assert memory.support == expected_support
    assert patch.support == expected_support

    return fence, patch


def run_fence(
    trace: CanonicalTrace,
) -> dict:
    """
    Evaluate the canonical operation under FENCE.
    """

    fence, patch = build_fence_artifacts(trace)

    # --------------------------------------------------------
    # t3: revoke T
    # --------------------------------------------------------

    fence.revoke(
        authority=trace.authority_id,
        new_epoch=trace.revoked_epoch,
    )

    # --------------------------------------------------------
    # t4: commit P
    # --------------------------------------------------------

    committed = fence.validate_commit(
        patch,
    )

    return {
        "baseline": "FENCE",
        "authority_id": trace.authority_id,
        "original_epoch": trace.initial_epoch,
        "revoked_epoch": trace.revoked_epoch,
        "artifact": patch.artifact_id,
        "support": sorted(patch.support),
        "committed": committed,
        "pars_violation": committed,
    }


# ============================================================
# Canonical experiment
# ============================================================

def run_canonical_experiment() -> None:
    """
    Run all three baselines over the same logical execution.
    """

    trace = build_canonical_trace()

    naive = run_naive_revocation(trace)
    epoch = run_epoch_fencing(trace)
    fence = run_fence(trace)

    results = [
        naive,
        epoch,
        fence,
    ]

    print("=" * 72)
    print("FENCE - Canonical Figure 1 Experiment")
    print("=" * 72)

    print()
    print("COMMON EXECUTION")
    print("-" * 72)
    print(f"Authority:       {trace.authority_id}")
    print(f"Initial epoch:   {trace.initial_epoch}")
    print(f"Revoked epoch:   {trace.revoked_epoch}")
    print("Derivation:      R -> M -> P")

    for result in results:
        print()
        print(f"Baseline:        {result['baseline']}")
        print(f"Artifact:        {result['artifact']}")
        print(f"Committed:       {result['committed']}")
        print(f"PARS violation:  {result['pars_violation']}")

        if "support" in result:
            print(f"Support:          {result['support']}")

    # --------------------------------------------------------
    # Structural checks
    # --------------------------------------------------------

    print()
    print("-" * 72)
    print("STRUCTURAL CHECKS")
    print("-" * 72)

    # Same authority and epochs for every baseline.
    assert naive["authority_id"] == trace.authority_id
    assert epoch["authority_id"] == trace.authority_id
    assert fence["authority_id"] == trace.authority_id

    assert naive["original_epoch"] == trace.initial_epoch
    assert epoch["original_epoch"] == trace.initial_epoch
    assert fence["original_epoch"] == trace.initial_epoch

    assert naive["revoked_epoch"] == trace.revoked_epoch
    assert epoch["revoked_epoch"] == trace.revoked_epoch
    assert fence["revoked_epoch"] == trace.revoked_epoch

    # FENCE must actually preserve support.
    expected_support = {
        (
            trace.authority_id,
            trace.initial_epoch,
        )
    }

    assert set(fence["support"]) == expected_support

    print("PASS: common authority/epoch trace")
    print("PASS: FENCE support propagation")

    # --------------------------------------------------------
    # Separation check
    # --------------------------------------------------------

    expected_separation = (
        naive["committed"] is True
        and naive["pars_violation"] is True

        and epoch["committed"] is True
        and epoch["pars_violation"] is True

        and fence["committed"] is False
        and fence["pars_violation"] is False
    )

    print()
    print("-" * 72)

    if expected_separation:
        print("PASS: canonical Figure 1 separation reproduced.")
        print()
        print("Naive Revocation  -> COMMIT -> PARS violation")
        print("Epoch Fencing     -> COMMIT -> PARS violation")
        print("FENCE             -> REFUSE -> PARS preserved")
    else:
        print("FAIL: canonical separation was not reproduced.")
        print()
        print("Observed:")
        print(f"  Naive committed: {naive['committed']}")
        print(f"  Epoch committed: {epoch['committed']}")
        print(f"  FENCE committed: {fence['committed']}")


if __name__ == "__main__":
    run_canonical_experiment()