[README.md](https://github.com/user-attachments/files/31922950/README.md)
# Alex – AI Customer Support Agent 🤖

Alex is an AI-powered customer support agent that helps customers with **order status, delivery, returns, and refunds**. It's built with LangChain + LangGraph, runs on Groq's fast LLM inference, and uses a local SQLite database to look up real order and refund data.

The project has two agents:

| File | What it does |
|---|---|
| `Customer_Support.py` | The main support agent ("Alex"). Answers order/refund questions and runs a safe, rule-based refund workflow. |
| `chatbot_agent.py` | A simpler general-purpose chat agent with internet search (Tavily) for current-events questions. |

---

## ✨ Key Features

- **Order & refund lookups** – Alex reads directly from a local database, so answers are based on real data, not guesses.
- **Safe refund flow** – Refunds are never processed automatically. Alex calculates the amount, asks the customer to confirm with a clear **YES/NO**, and only then creates the refund request. The actual money transfer is controlled by the application, not the AI.
- **Built-in guardrails** – Alex is designed to:
  - Stay on topic (orders, delivery, refunds, payments) and politely decline unrelated requests.
  - Detect and block prompt-injection attempts (e.g., messages trying to trick it into ignoring its rules, claiming fake admin access, or exposing secrets).
  - Never reveal API keys, system prompts, or another customer's data.
- **Conversation memory** – Each chat has a `thread_id`, so Alex remembers the conversation as it goes.
- **Optional internet search** – The second agent (`chatbot_agent.py`) can search the web for current information using Tavily.

---

## 🧱 Tech Stack

- **Python** 3.14
- **[uv](https://docs.astral.sh/uv/)** – fast Python package/dependency manager
- **[LangChain](https://python.langchain.com/) / [LangGraph](https://langchain-ai.github.io/langgraph/)** – agent framework and memory
- **[Groq](https://groq.com/)** – LLM inference (running `openai/gpt-oss-120b`)
- **[Tavily](https://tavily.com/)** – web search API
- **SQLite** – local database for customers, orders, and refunds

---

## 📁 Project Structure

```
├── Customer_Support.py   # Main support agent (Alex) with refund workflow
├── chatbot_agent.py       # General chat agent with internet search
├── database.py             # Creates the SQLite database and tables
├── seed.py                 # Fills the database with sample data
├── support.db               # SQLite database file
├── pyproject.toml           # Project dependencies
└── uv.lock                  # Locked dependency versions
```

---

## 🚀 How to Run the Project (Step by Step)

You don't need to be an expert to get this running — just follow the steps in order.

### 1. Install `uv`

`uv` is the tool used to manage this project and its dependencies.

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Other ways to install it:
```powershell
winget install --id astral-sh.uv
# or
pip install uv
```

After installing, **close and reopen your terminal**, then check it worked:
```powershell
uv --version
```
You should see a version number like `uv 0.x.x`. If not, add uv to your PATH:
```powershell
$env:Path += ";$env:USERPROFILE\.cargo\bin;$env:USERPROFILE\.local\bin"
```

### 2. Install the project dependencies

From the project folder, run:
```bash
uv sync
```
This reads `pyproject.toml` / `uv.lock` and installs everything you need (LangChain, LangGraph, Groq, Tavily, etc.) into a virtual environment automatically.

### 3. Add your API keys

Create a file named **`.env`** in the project folder and add:
```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```
- Get a free Groq key at [console.groq.com](https://console.groq.com/)
- Get a free Tavily key at [tavily.com](https://tavily.com/)

> ⚠️ Never share your `.env` file or commit it to GitHub — it contains your private keys.

### 4. Set up the database

Create the tables and load some sample customers/orders so Alex has data to work with:
```bash
uv run database.py
uv run seed.py
```
This creates `support.db` with two sample customers (Saqib and Ali) and a few example orders.

### 5. Run the agent

To chat with **Alex**, the customer support agent:
```bash
uv run Customer_Support.py
```

To chat with the **general assistant** (with internet search instead):
```bash
uv run chatbot_agent.py
```

### 6. Chat with it!

Type your message and press Enter. Some things to try with Alex:
- `Where is my order?`
- `I want a refund for order 1`
- `Thanks!`

Type `q` to quit, or `new` (in `chatbot_agent.py`) to start a fresh conversation.

---

## 🔒 A Note on Safety

Alex is intentionally built so it **cannot process refunds on its own** and **cannot be tricked into skipping its rules** — even if a message tries to claim fake admin approval or asks it to ignore instructions. Every refund needs an explicit YES from the customer, and the actual transaction is handled by the application code, not the AI model.

---

## 📌 Notes

- This project uses in-memory conversation storage (`InMemorySaver`), so conversation history resets when you restart the program.
- The database is local (SQLite) and meant for demo/testing purposes — not for production customer data.

---

Built as part of ongoing AI/ML development work. Feel free to explore, adapt, and extend it. 🚀
