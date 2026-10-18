from dataclasses import replace

from scenarios.trace import ExecutionTrace


def make_stale_handle_trace(
    trace: ExecutionTrace,
) -> ExecutionTrace:
    """
    Create a control scenario where P retains the original
    authorization epoch handle.

    No new LLM execution is performed.
    """

    patch = replace(
        trace.patch,
        epoch_handles=frozenset({
            (trace.authority_id, trace.initial_epoch),
        }),
    )

    return replace(
        trace,
        patch=patch,
    )