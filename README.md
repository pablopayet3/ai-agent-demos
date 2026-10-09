# AI Agent Demos

A collection of small, self-contained AI agent and automation demos I built while developing my AI engineering skills. Each folder is one demo with its own README.

Full portfolio, with write-ups, architecture, and results: https://payet-ai-portfolio.netlify.app

> The flagship build, an observable LangGraph support agent, has its own repo: https://github.com/pablopayet3/supportpilot

## Demos

| Folder | What it is | Stack |
|---|---|---|
| `rag-pdf-qa/` | Ask a question about a stack of PDFs and get an answer with the exact page it came from. | LangChain, FAISS, Gemini |
| `agentic-rag-router/` | Decides where each question should be answered from (your documents, a live web search, or the model itself) before answering. | CrewAI, Gemini, FAISS, Tavily |
| `crewai-research-crew/` | Two agents work as a team: one researches a topic on the live web, the other writes it up as a brief. | CrewAI, Tavily, Azure OpenAI |
| `crewai-serial-parallel/` | Two ways to make agents work together: in sequence when one needs the other's output, or in parallel when they don't. | CrewAI, Tavily, Azure OpenAI |
| `self-debugging-code-chain/` | The model writes a small program, writes its own tests, runs them, and fixes its own bugs until they pass. | Google Gemini, unittest |
| `market-research-mcp/` | An MCP server exposing market-research tools (company overview, competitors, pricing, news) to any MCP client. | FastMCP, Tavily |
| `autogen-doc-compliance/` | A multi-agent system (scanner, compliance checker, coordinator) that reviews policy documents and assigns fixes. | Microsoft AutoGen, Claude |
| `linkedin-content-pipeline/` | A FastAPI service where three AutoGen agents write a brand's LinkedIn post (ideas, draft with a confidence score, hashtags) for an n8n workflow with a human approval gate. | AutoGen, FastAPI, Azure OpenAI |
| `prompt-ab-test/` | The same request worded four ways and sent to the same model, every call traced in LangSmith; one wording made the model skip the task. | LangChain, LangSmith, Gemini |
| `format-negotiation/` | A dependency-free demo of two systems negotiating a shared data format, converting or failing safely. | Python stdlib |

## Running a demo

Each folder has its own README and, where needed, a `requirements.txt` and `.env.example`. The notebook demos open in Jupyter or VS Code. API keys are read from a local `.env` file and are never committed to the repo.
