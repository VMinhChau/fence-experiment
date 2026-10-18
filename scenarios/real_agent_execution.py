# """
# Real-agent canonical experiment for FENCE.

# This experiment replaces the hard-coded semantic contents
# of the canonical Figure 1 experiment with output generated
# by the real gpt-oss-120b agent.

# The revocation/control plane remains outside the agent.
# """

# import asyncio

# from agent.agent import create_fence_agent
# from agent.tools import create_banking_tools

# from authority.manager import AuthorityManager
# from authority.fence import Artifact, Fence
# from scenarios.trace import ExecutionTrace, TraceArtifact


# AGENT_ID = "fence_agent"
# RESOURCE = "customer:C001"
# ACTION = "read_risk_profile"
# AUTHORITY_ID = "T"


# async def run_real_agent_execution(
#     authority_manager: AuthorityManager,
# ) -> ExecutionTrace:

#     print("=" * 72)
#     print("FENCE - Real Agent Canonical Experiment")
#     print("=" * 72)

#     # ========================================================
#     # 1. Control plane
#     # ========================================================

#     authority = authority_manager.grant(
#         authority_id=AUTHORITY_ID,
#         agent_id=AGENT_ID,
#         resource=RESOURCE,
#         action=ACTION,
#     )

#     print()
#     print("AUTHORITY")
#     print("-" * 72)
#     print(f"Authority: {authority.authority_id}")
#     print(f"Epoch:     {authority.epoch}")
#     print(f"Status:    {authority.status}")

#     assert authority.epoch == 0
#     assert authority.status == "ACTIVE"

#     # ========================================================
#     # 2. Create real agent
#     # ========================================================

#     agent = create_fence_agent(authority_manager)

#     print()
#     print("REAL AGENT")
#     print("-" * 72)
#     print("Model: openai/gpt-oss-120b")
#     print("Provider: Groq")
#     print("Agent initialized.")

#     # ========================================================
#     # 3. Agent A obtains R
#     # ========================================================

#     print()
#     print("t0 - AGENT A READS AUTHORIZED DATA")
#     print("-" * 72)

#     assert authority_manager.check(
#         agent_id=AGENT_ID,
#         resource=RESOURCE,
#         action=ACTION,
#     )

#     # The actual tool call.
#     get_customer_risk_profile = create_banking_tools(
#         authority_manager
#     )[0]
#     raw_response = get_customer_risk_profile("C001")

#     print("Tool response:")
#     print(raw_response)

#     assert raw_response.get("status") != "DENIED"

#     response_content = str(raw_response)

#     # The response is semantically derived from T@0.
#     response_artifact = Artifact(
#         artifact_id="R",
#         content=response_content,
#         support={
#             (AUTHORITY_ID, authority.epoch)
#         },
#     )

#     print()
#     print("R support:")
#     print(response_artifact.support)

#     # ========================================================
#     # 4. Real LLM derives M
#     # ========================================================

#     print()
#     print("t1 - REAL AGENT DERIVES MEMORY M")
#     print("-" * 72)

#     memory_prompt = f"""
# You are Agent A in a banking investigation system.

# Below is information retrieved from an authorized banking
# system.

# Retrieved information:
# {response_content}

# Create one short investigation memory note that captures
# the important risk information.

# Do not invent facts.
# Do not call any tools.
# Return only the memory note.
# """

#     memory_response = await agent.run(memory_prompt)

#     memory_content = str(memory_response)

#     print("Generated M:")
#     print(memory_content)

#     # FENCE records semantic derivation.
#     fence = Fence()

#     memory_artifact = fence.derive(
#         "M",
#         memory_content,
#         response_artifact,
#     )

#     print()
#     print("M support:")
#     print(memory_artifact.support)

#     assert memory_artifact.support == {
#         (AUTHORITY_ID, authority.epoch)
#     }

#     # ========================================================
#     # 5. Real LLM derives P from M
#     # ========================================================

#     print()
#     print("t2 - REAL AGENT DERIVES PATCH P")
#     print("-" * 72)

#     patch_prompt = f"""
# You are Agent B performing a banking investigation task.

# The following investigation memory was produced by
# another agent:

# {memory_content}

# Create one short proposed maintenance/action patch based
# ONLY on this memory.

# Do not call any tools.
# Do not retrieve additional customer information.
# Return only the proposed patch.
# """

#     patch_response = await agent.run(patch_prompt)

#     patch_content = str(patch_response)

#     print("Generated P:")
#     print(patch_content)

#     patch_artifact = fence.derive(
#         "P",
#         patch_content,
#         memory_artifact,
#     )

#     print()
#     print("P support:")
#     print(patch_artifact.support)

#     assert patch_artifact.support == {
#         (AUTHORITY_ID, authority.epoch)
#     }

#     # ========================================================
#     # 6. Revoke T
#     # ========================================================

#     print()
#     print("t3 - REVOKE T")
#     print("-" * 72)

#     revoked = authority_manager.revoke(
#         agent_id=AGENT_ID,
#         resource=RESOURCE,
#         action=ACTION,
#     )

#     assert revoked is not None

#     revoked_epoch = authority_manager.current_epoch(
#         AUTHORITY_ID
#     )

#     print(f"Old epoch: {authority.epoch}")
#     print(f"New epoch: {revoked_epoch}")
#     print(f"Status:    {revoked.status}")

#     assert revoked_epoch == 1
#     assert revoked.status == "REVOKED"

#     print()
#     print("t3a - ATTEMPT NEW ACCESS AFTER REVOCATION")
#     print("-" * 72)

#     post_revocation_response = get_customer_risk_profile("C001")

#     print("Post-revocation tool response:")
#     print(post_revocation_response)

#     assert post_revocation_response.get("status") == "DENIED"

#     # FENCE receives the same revocation.
#     fence.revoke(
#         authority=AUTHORITY_ID,
#         new_epoch=revoked_epoch,
#     )

#     # ========================================================
#     # 7. Commit-time validation
#     # ========================================================

#     print()
#     print("t4 - COMMIT P")
#     print("-" * 72)

#     committed = fence.validate_commit(
#         patch_artifact,
#     )

#     print(f"P support:       {patch_artifact.support}")
#     print(f"Current frontier:{AUTHORITY_ID}={revoked_epoch}")
#     print(f"Committed:       {committed}")

#     # P contains support (T,0), while current frontier is 1.
#     assert committed is False

#     print()
#     print("=" * 72)
#     print("PASS: real-agent FENCE experiment")
#     print("=" * 72)
#     print()
#     print("Real gpt-oss-120b generated:")
#     print("  R -> M -> P")
#     print()
#     print("FENCE propagated:")
#     print(f"  {patch_artifact.support}")
#     print()
#     print("After revocation:")
#     print(f"  frontier[{AUTHORITY_ID}] = {revoked_epoch}")
#     print()
#     print("Commit:")
#     print("  REFUSED")
#     print()
#     print("PARS preserved.")

#     return ExecutionTrace(
#         authority_id=AUTHORITY_ID,
#         agent_id=AGENT_ID,
#         initial_epoch=authority.epoch,
#         revoked_epoch=revoked_epoch,
#         response=TraceArtifact(
#             artifact_id=response_artifact.artifact_id,
#             content=response_artifact.content,
#             direct_authorities={AUTHORITY_ID},
#             epoch_handles={(AUTHORITY_ID, authority.epoch)},
#         ),
#         memory=TraceArtifact(
#             artifact_id=memory_artifact.artifact_id,
#             content=memory_artifact.content,
#             derived_from=(response_artifact.artifact_id,),
#         ),
#         patch=TraceArtifact(
#             artifact_id=patch_artifact.artifact_id,
#             content=patch_artifact.content,
#             derived_from=(memory_artifact.artifact_id,),
#         ),
#         events=[
#             "Agent read R using T@0",
#             "Agent derived M from R",
#             "Agent derived P from M",
#             "Authority T revoked",
#             "Post-revocation customer read denied",
#         ],
#     )


# if __name__ == "__main__":
#     asyncio.run(run_real_agent_execution())



"""
Real-agent canonical execution for FENCE.

The real gpt-oss-120b agent is executed once.

The resulting execution is converted into an ExecutionTrace.
All baselines replay the same trace; they must not call the
LLM again.

Canonical execution:

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
    revoke T -> epoch 1
      |
      v
    commit P
"""

from agent.agent import create_fence_agent
from agent.tools import create_banking_tools

from authority.manager import AuthorityManager
from scenarios.trace import (
    ExecutionTrace,
    TraceArtifact,
    TraceEvent,
)


AGENT_ID = "fence_agent"
AUTHORITY_ID = "T"

RESOURCE = "customer:C001"
ACTION = "read_risk_profile"


async def run_real_agent_execution(
    authority_manager: AuthorityManager,
) -> ExecutionTrace:

    print("=" * 72)
    print("FENCE - Real Agent Canonical Execution")
    print("=" * 72)

    # ------------------------------------------------------------
    # 1. Retrieve the actual authority object
    # ------------------------------------------------------------

    authority = authority_manager.get_authority(
        agent_id=AGENT_ID,
        resource=RESOURCE,
        action=ACTION,
    )

    if authority is None:
        raise RuntimeError(
            "Expected authority was not found. "
            "Call create_runtime() before running the experiment."
        )

    if authority.authority_id != AUTHORITY_ID:
        raise RuntimeError(
            f"Unexpected authority ID: {authority.authority_id}"
        )

    if authority.epoch != 0:
        raise RuntimeError(
            f"Canonical experiment expected epoch 0, "
            f"got {authority.epoch}."
        )

    if authority.status != "ACTIVE":
        raise RuntimeError(
            "Canonical experiment requires an active authority."
        )

    initial_epoch = authority.epoch

    print()
    print("AUTHORITY")
    print("-" * 72)
    print(f"Authority: {authority.authority_id}")
    print(f"Epoch:     {authority.epoch}")
    print(f"Status:    {authority.status}")

    # ------------------------------------------------------------
    # 2. Create the real agent
    # ------------------------------------------------------------

    agent = create_fence_agent(authority_manager)

    # ------------------------------------------------------------
    # 3. Agent A obtains R
    # ------------------------------------------------------------

    allowed = authority_manager.check(
        agent_id=AGENT_ID,
        resource=RESOURCE,
        action=ACTION,
    )

    if not allowed:
        raise RuntimeError(
            "Agent does not have the expected authority."
        )

    banking_tools = create_banking_tools(authority_manager)

    # The first banking tool is get_customer_risk_profile.
    get_customer_risk_profile = banking_tools[0]

    raw_response = get_customer_risk_profile("C001")

    if raw_response.get("status") == "DENIED":
        raise RuntimeError(
            "Canonical tool call was denied unexpectedly."
        )

    response_content = str(raw_response)

    response_artifact = TraceArtifact(
        artifact_id="R",
        content=response_content,
        epoch_handles=frozenset({
            (AUTHORITY_ID, initial_epoch),
        }),
        derived_from=(),
    )

    print()
    print("ARTIFACT R")
    print("-" * 72)
    print("Tool: get_customer_risk_profile")
    print(f"Support handle: {(AUTHORITY_ID, initial_epoch)}")
    print(f"Content: {response_content}")

    # ------------------------------------------------------------
    # 4. Agent derives memory M using the real LLM
    # ------------------------------------------------------------

    memory_prompt = f"""
You are investigating a banking customer.

Below is information obtained from an authorized banking tool:

{response_content}

Create a short internal investigation memory summarizing
the relevant facts for a later investigation.

Do not invent facts.
Do not add information that is not present above.
"""

    memory_result = await agent.run(memory_prompt)

    memory_content = str(memory_result)

    memory_artifact = TraceArtifact(
        artifact_id="M",
        content=memory_content,

        # Important:
        #
        # The semantic memory does NOT retain the original epoch
        # handle. This models materialized semantic content.
        epoch_handles=frozenset(),

        derived_from=("R",),
    )

    print()
    print("ARTIFACT M")
    print("-" * 72)
    print("Derived from: R")
    print("Epoch handle retained: False")
    print(f"Content: {memory_content}")

    # ------------------------------------------------------------
    # 5. Agent derives patch P from memory M
    # ------------------------------------------------------------

    patch_prompt = f"""
You are preparing a small maintenance patch for an internal
banking investigation workflow.

Use the following internal investigation memory:

{memory_content}

Produce a concise proposed patch/change that preserves the
relevant investigation fact for the workflow.

Do not invent facts.
Do not introduce information that is not present in the memory.
"""

    patch_result = await agent.run(patch_prompt)

    patch_content = str(patch_result)

    patch_artifact = TraceArtifact(
        artifact_id="P",
        content=patch_content,

        # Again, P is semantic content and does not retain
        # the original epoch handle.
        epoch_handles=frozenset(),

        derived_from=("M",),
    )

    print()
    print("ARTIFACT P")
    print("-" * 72)
    print("Derived from: M")
    print("Epoch handle retained: False")
    print(f"Content: {patch_content}")

    # ------------------------------------------------------------
    # 6. Revoke T
    # ------------------------------------------------------------

    revoked_authority = authority_manager.revoke(
        agent_id=AGENT_ID,
        resource=RESOURCE,
        action=ACTION,
    )

    if revoked_authority is None:
        raise RuntimeError(
            "Authority revocation failed."
        )

    revoked_epoch = authority_manager.current_epoch(
        AUTHORITY_ID
    )

    print()
    print("REVOCATION")
    print("-" * 72)
    print(f"Authority: {AUTHORITY_ID}")
    print(f"Initial epoch: {initial_epoch}")
    print(f"Revoked epoch: {revoked_epoch}")

    if revoked_epoch != initial_epoch + 1:
        raise RuntimeError(
            "Unexpected revocation epoch."
        )

    # ------------------------------------------------------------
    # 7. Build the common execution trace
    # ------------------------------------------------------------

    events = (
        TraceEvent(
            event_type="AUTHORITY_GRANTED",
            authority_id=AUTHORITY_ID,
            epoch=initial_epoch,
            description="Authority T granted at epoch 0.",
        ),
        TraceEvent(
            event_type="TOOL_RESULT",
            artifact_id="R",
            authority_id=AUTHORITY_ID,
            epoch=initial_epoch,
            description=(
                "Agent obtained R using authority T at epoch 0."
            ),
        ),
        TraceEvent(
            event_type="DERIVATION",
            artifact_id="M",
            description="M was derived from R.",
        ),
        TraceEvent(
            event_type="DERIVATION",
            artifact_id="P",
            description="P was derived from M.",
        ),
        TraceEvent(
            event_type="AUTHORITY_REVOKED",
            authority_id=AUTHORITY_ID,
            epoch=revoked_epoch,
            description=(
                "Authority T was revoked and frontier advanced."
            ),
        ),
    )

    trace = ExecutionTrace(
        authority_id=AUTHORITY_ID,
        agent_id=AGENT_ID,
        initial_epoch=initial_epoch,
        revoked_epoch=revoked_epoch,
        response=response_artifact,
        memory=memory_artifact,
        patch=patch_artifact,
        events=events,
    )

    # ------------------------------------------------------------
    # 8. Validate trace invariants
    # ------------------------------------------------------------

    trace.validate()

    print()
    print("EXECUTION TRACE")
    print("-" * 72)
    print("R -> M -> P")
    print(
        f"Initial epoch: {trace.initial_epoch}"
    )
    print(
        f"Revoked epoch: {trace.revoked_epoch}"
    )
    print(
        f"R handles:     {trace.response.epoch_handles}"
    )
    print(
        f"M handles:     {trace.memory.epoch_handles}"
    )
    print(
        f"P handles:     {trace.patch.epoch_handles}"
    )
    print(
        f"M derived from: {trace.memory.derived_from}"
    )
    print(
        f"P derived from: {trace.patch.derived_from}"
    )

    print()
    print("PASS: real-agent execution converted to ExecutionTrace.")

    return trace