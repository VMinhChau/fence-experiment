import os

from dotenv import load_dotenv
from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient

from authority.manager import AuthorityManager
from .tools import create_banking_tools


load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not set.\n"
        "PowerShell:\n"
        '  $env:GROQ_API_KEY="your_api_key"'
    )


MODEL_NAME = "openai/gpt-oss-120b"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"


def create_fence_agent(
    authority_manager: AuthorityManager,
) -> Agent:
    """
    Create a FENCE agent using the shared AuthorityManager.
    """

    client = OpenAIChatCompletionClient(
        model=MODEL_NAME,
        api_key=GROQ_API_KEY,
        base_url=GROQ_BASE_URL,
    )

    banking_tools = create_banking_tools(
        authority_manager
    )

    agent = Agent(
        client=client,
        name="fence_agent",
        description="FENCE banking investigation agent",
        instructions="""
You are the FENCE banking investigation agent.

Your role is to assist with banking and AML investigation tasks.

Rules:

1. Use the available tools when customer information is required.
2. Never invent customer data.
3. Clearly distinguish facts obtained from tools from your reasoning.
4. Only use information necessary to answer the user's task.
5. Avoid unnecessarily exposing sensitive customer information.
6. If required information is unavailable, say so.
7. Do not claim that a customer is suspicious unless the
   available evidence supports that conclusion.

This is the baseline prototype of FENCE.

The banking tools enforce conventional authorization.
Do not assume that semantic revocation tracking is already
implemented by the tools.
""",
        tools=banking_tools,
    )

    return agent