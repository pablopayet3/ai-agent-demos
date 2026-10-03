# Market-Research MCP Server

An MCP (Model Context Protocol) server that gives an AI assistant a set of market-research tools, so it can assemble a sourced brief on any company on demand: company overview, competitor list, product-portfolio map, pricing snapshot, and a recent-news pulse. Built with FastMCP and Tavily web search.

## Tools exposed
- `company_overview` — founding, HQ, products, business model, recent news
- `list_competitors` — direct competitors and upstart challengers
- `product_portfolio` — product list, suites, tiers, with content extraction
- `pricing_snapshot` — list price, tiers, billing cycles, discounts
- `recent_news_pulse` — funding, acquisitions, launches, leadership

## Run
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add your Tavily key.
3. `python server.py`

The server starts on SSE transport; point any MCP-compatible client at it.
