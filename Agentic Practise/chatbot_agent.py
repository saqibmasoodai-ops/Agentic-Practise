import os 
import logging 
from uuid import uuid4
import asyncio

from dotenv import load_dotenv
from tavily_agent_toolkit import search_and_format

from langchain.agents import create_agent
from langchain.agents.middleware import(
    ModelCallLimitMiddleware,
    ToolCallLimitMiddleware,
    ModelRetryMiddleware,
    ToolRetryMiddleware,
    SummarizationMiddleware,
)
from langchain.tools import tool
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is missing from your .env file."
    )

if not TAVILY_API_KEY:
    raise RuntimeError(
        "TAVILY_API_KEY is missing from your .env file."
    )


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("alex-agent")

model = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    max_retries=2,
)


@tool
def say_hello() -> str:
    """Say hello before answering the user message.
    """
    logger.info("say_hello tool executed")
    return "Hello! The greeting tool executed successfully."


@tool
def internet_search_tool(query: str) -> str:
    """
    Search the internet for current, recent,
    or time-sensitive information.
    """

    logger.info("Tavily search started: %s", query)

    try:
        result = asyncio.run(
            search_and_format(
                queries=[query],
                api_key=TAVILY_API_KEY,
                search_depth="advanced",
                max_results=5,
                time_range="month",
            )
        )

        logger.info("Tavily search completed")

        return str(result)

    except Exception as e:
        logger.exception("Tavily search failed")

        return (
            f"Tavily search failed: {type(e).__name__}: {e}"
        )
    
checkpointer = InMemorySaver()

middleware = [

    # --------------------------------------------------------
    # Prevent too many model calls
    # --------------------------------------------------------

    ModelCallLimitMiddleware(
        thread_limit=20,
        run_limit=10,
    ),

    # --------------------------------------------------------
    # Prevent excessive Tavily calls
    # --------------------------------------------------------

    ToolCallLimitMiddleware(
        tool_name="internet_search_tool",
        thread_limit=10,
        run_limit=5,
    ),

    # --------------------------------------------------------
    # Retry temporary model failures
    # --------------------------------------------------------

    ModelRetryMiddleware(
        max_retries=2,
    ),

    # --------------------------------------------------------
    # Retry temporary tool failures
    # --------------------------------------------------------

    ToolRetryMiddleware(
        max_retries=2,
    ),

    # --------------------------------------------------------
    # Summarize long conversations
    # --------------------------------------------------------

    SummarizationMiddleware(
        model=model,
        trigger=("tokens", 8000),
        keep=("messages", 20),
    ),
]

SYSTEM_PROMPT = """
You are Alex, a reliable AI assistant.

Your job is to answer users clearly, accurately,
and efficiently.

AVAILABLE TOOLS
===============

1. say_hello

Use this tool before answering every user message.

2. internet_search_tool

Use this tool when:

- The user asks for latest information.
- The user asks for current information.
- The user asks about recent events.
- The user asks about changing information.
- The user explicitly asks you to search the internet.
- You need external information to answer accurately.

Do not use internet search unnecessarily.

SEARCH RULES
============

When using internet_search_tool:

1. Create a focused search query.
2. Review the search results.
3. Use the results to formulate your answer.
4. Do not invent information.
5. Do not claim you searched the internet if you
   did not actually use the search tool.

GENERAL RULES
=============

- Be helpful.
- Be accurate.
- Be concise but informative.
- Admit uncertainty when appropriate.
- Never expose API keys or secrets.
- Never reveal environment variables.
- If a tool fails, handle the failure gracefully.
"""

agent = create_agent(
    model=model,
    tools=[
        say_hello,
        internet_search_tool,
    ],
    system_prompt=SYSTEM_PROMPT,
    middleware=middleware,
    checkpointer=checkpointer
)

def get_response(
        query: str,
        thread_id: str,
):
    if not query.strip():
        raise ValueError(
            "Query cannot be empty."
        )

    logger.info(
        "Processing request | thread=%s",
        thread_id,
    )

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": query,
                }
            ]
        },

        config={
            "configurable": {
                "thread_id": thread_id,
            }
        },
    )

    return result

# ============================================================
# 11. MAIN CHAT APPLICATION
# ============================================================

def main():

    # Create a unique conversation
    thread_id = str(uuid4())

    print()
    print("=" * 65)
    print("                 ALEX AI AGENT")
    print("=" * 65)
    print("Model      : OpenAI GPT-OSS 120B")
    print("Provider   : Groq")
    print("Search     : Tavily")
    print("Framework  : LangChain + LangGraph")
    print("Memory     : InMemorySaver")
    print()
    print(f"Thread ID  : {thread_id}")
    print()
    print("Commands:")
    print("  q       -> quit")
    print("  new     -> new conversation")
    print("=" * 65)

    while True:

        try:

            query = input("\nYou: ").strip()

            # ------------------------------------------------
            # Empty input
            # ------------------------------------------------

            if not query:
                continue

            # ------------------------------------------------
            # Quit
            # ------------------------------------------------

            if query.lower() == "q":
                print("\nGoodbye!")
                break

            # ------------------------------------------------
            # New conversation
            # ------------------------------------------------

            if query.lower() == "new":

                thread_id = str(uuid4())

                print(
                    "\nNew conversation started."
                )

                print(
                    f"Thread ID: {thread_id}"
                )

                continue

            # ------------------------------------------------
            # Agent
            # ------------------------------------------------

            result = get_response(
                query=query,
                thread_id=thread_id,
            )

            # ------------------------------------------------
            # Final message
            # ------------------------------------------------

            final_message = result["messages"][-1]

            print("\nAlex:")
            print(final_message.content)

        except KeyboardInterrupt:

            print("\n\nGoodbye!")
            break

        except Exception as e:

            logger.exception(
                "Unexpected agent error"
            )

            print(
                "\nAlex encountered an error."
            )

            print(
                f"Error type: {type(e).__name__}"
            )

            print(
                "Please try again."
            )


# ============================================================
# 12. START
# ============================================================

if __name__ == "__main__":
    main()