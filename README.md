# AI Agent Demos

A collection of small, self-contained AI agent and automation demos I built while developing my AI engineering skills. Each folder is one demo with its own README.

Full portfolio, with write-ups, architecture, and results: https://payet-ai-portfolio.netlify.app

> The flagship build, an observable LangGraph support agent, has its own repo: https://github.com/pablopayet3/supportpilot

## Demos

| Folder | What it is | Stack |
|---|---|---|
| `market-research-mcp/` | An MCP server exposing market-research tools (company overview, competitors, pricing, news) to any MCP-compatible AI client. | FastMCP, Tavily |
| `autogen-doc-compliance/` | A multi-agent system (scanner, compliance checker, coordinator) that reviews policy documents and assigns fixes. | Microsoft AutoGen, Claude |
| `format-negotiation/` | A dependency-free demo of two systems negotiating a shared data format, converting or failing safely. | Python stdlib |

More demos are being added to this collection.

## Running a demo

Each folder has its own README and, where needed, a `requirements.txt` and `.env.example`. API keys are read from a local `.env` file and are never committed to the repo.
