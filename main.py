# import asyncio
# import sys

# from authority.manager import AuthorityManager
# from agent.agent import create_fence_agent


# AGENT_ID = "fence_agent"
# AUTHORITY_ID = "T"


# def create_runtime() -> AuthorityManager:
#     """
#     Create the shared control-plane authority state.
#     """

#     authority_manager = AuthorityManager()

#     authority_manager.grant(
#         authority_id=AUTHORITY_ID,
#         agent_id=AGENT_ID,
#         resource="customer:C001",
#         action="read_risk_profile",
#     )

#     return authority_manager


# async def interactive_mode() -> None:
#     print("=" * 60)
#     print("FENCE - Initial Prototype")
#     print("=" * 60)
#     print()

#     # One shared authority manager.
#     authority_manager = create_runtime()

#     # Agent receives the SAME manager.
#     agent = create_fence_agent(
#         authority_manager
#     )

#     print("Agent initialized successfully.")
#     print("Type 'exit' or 'quit' to stop.")
#     print()

#     while True:
#         try:
#             user_input = input("You > ").strip()

#         except (KeyboardInterrupt, EOFError):
#             print("\nFENCE stopped.")
#             break

#         if not user_input:
#             continue

#         if user_input.lower() in {"exit", "quit"}:
#             print("FENCE stopped.")
#             break

#         try:
#             response = await agent.run(user_input)

#             print()
#             print("FENCE >", response)
#             print()

#         except Exception as exc:
#             print()
#             print("ERROR:", type(exc).__name__)
#             print(exc)
#             print()


# async def experiment_mode() -> None:
#     from scenarios.real_agent_execution import (
#         run_real_agent_execution,
#     )

#     from baselines import naive
#     from baselines import epoch_fencing
#     from baselines import fence

#     from gateway.commit import CommitGateway
#     from monitor.metrics import create_metrics

#     authority_manager = create_runtime()

#     trace = await run_real_agent_execution(
#         authority_manager
#     )

#     print()
#     print("Trace ready for baseline replay.")

#     metrics = create_metrics()

#     for baseline in [
#         naive,
#         epoch_fencing,
#         fence,
#     ]:
#         gateway = CommitGateway()

#         result = baseline.evaluate(
#             trace,
#             gateway,
#         )

#         metrics.add(result)

#     metrics.print_summary()


# async def main() -> None:

#     if len(sys.argv) > 1 and sys.argv[1] == "experiment":
#         await experiment_mode()
#     else:
#         await interactive_mode()


# if __name__ == "__main__":
#     asyncio.run(main())



import asyncio
import sys

from authority.manager import AuthorityManager
from agent.agent import create_fence_agent


AGENT_ID = "fence_agent"
AUTHORITY_ID = "T"


def create_runtime() -> AuthorityManager:
    """
    Create the shared control-plane authority state.
    """

    authority_manager = AuthorityManager()

    authority_manager.grant(
        authority_id=AUTHORITY_ID,
        agent_id=AGENT_ID,
        resource="customer:C001",
        action="read_risk_profile",
    )

    return authority_manager


async def interactive_mode() -> None:
    print("=" * 60)
    print("FENCE - Initial Prototype")
    print("=" * 60)
    print()

    authority_manager = create_runtime()

    agent = create_fence_agent(
        authority_manager
    )

    print("Agent initialized successfully.")
    print("Type 'exit' or 'quit' to stop.")
    print()

    while True:
        try:
            user_input = input("You > ").strip()

        except (KeyboardInterrupt, EOFError):
            print("\nFENCE stopped.")
            break

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit"}:
            print("FENCE stopped.")
            break

        try:
            response = await agent.run(user_input)

            print()
            print("FENCE >", response)
            print()

        except Exception as exc:
            print()
            print("ERROR:", type(exc).__name__)
            print(exc)
            print()


def evaluate_scenario(
    trace,
    scenario_name: str,
    metrics,
) -> None:
    """
    Replay one ExecutionTrace through all baselines.

    No LLM call is made here.
    """

    from baselines import naive
    from baselines import epoch_fencing
    from baselines import fence

    from gateway.commit import CommitGateway
    from monitor.pars import violates_pars

    for baseline in [
        naive,
        epoch_fencing,
        fence,
    ]:
        gateway = CommitGateway()

        # Baseline makes the commit decision.
        result = baseline.evaluate(
            trace,
            gateway,
        )

        # Independent ground-truth PARS evaluation.
        pars_violation = (
            result.committed
            and violates_pars(
                trace,
                result.artifact_id,
            )
        )

        # CommitResult is frozen, so create a new result
        # carrying the independently evaluated PARS value.
        from dataclasses import replace

        result = replace(
            result,
            pars_violation=pars_violation,
        )

        metrics.add(
            scenario_name=scenario_name,
            result=result,
        )

    # Print this scenario once.
    metrics.print_scenario(
        scenario_name
    )


async def experiment_mode() -> None:
    from scenarios.real_agent_execution import (
        run_real_agent_execution,
    )

    from scenarios.stale_handle_trace import (
        make_stale_handle_trace,
    )

    from monitor.metrics import create_metrics

    # ---------------------------------------------------------
    # 1. Create runtime
    # ---------------------------------------------------------

    authority_manager = create_runtime()

    # ---------------------------------------------------------
    # 2. ONE real LLM execution
    # ---------------------------------------------------------
    #
    # The real agent produces the common ExecutionTrace.
    #
    # No baseline calls the LLM.
    #

    trace = await run_real_agent_execution(
        authority_manager
    )

    print()
    print("Trace ready for baseline replay.")

    # ---------------------------------------------------------
    # 3. Collect metrics
    # ---------------------------------------------------------

    metrics = create_metrics()

    # ---------------------------------------------------------
    # 4. Scenario A:
    #    Semantic derivation / handle lost
    # ---------------------------------------------------------

    evaluate_scenario(
        trace=trace,
        scenario_name=(
            "Semantic Derivation / Handle Lost"
        ),
        metrics=metrics,
    )

    # ---------------------------------------------------------
    # 5. Scenario B:
    #    Explicit stale handle
    # ---------------------------------------------------------
    #
    # IMPORTANT:
    # This does NOT call the LLM again.
    #
    # It derives a controlled variant from the same trace.
    #

    stale_handle_trace = make_stale_handle_trace(
        trace
    )

    evaluate_scenario(
        trace=stale_handle_trace,
        scenario_name="Explicit Stale Handle",
        metrics=metrics,
    )

    # ---------------------------------------------------------
    # 6. Overall metrics
    # ---------------------------------------------------------

    metrics.print_overall_summary()


async def main() -> None:

    if (
        len(sys.argv) > 1
        and sys.argv[1] == "experiment"
    ):
        await experiment_mode()

    else:
        await interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())