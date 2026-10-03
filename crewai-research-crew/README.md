# Multi-Agent Research Crew

Two AI agents work as a team: a researcher gathers information on a topic using live web search, and a writer turns those findings into a short, structured brief. Built with CrewAI, which coordinates the agents, their tasks, and the handoff between them.

Stack: CrewAI, Tavily web search, Azure OpenAI.

## Run
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add your Azure OpenAI and Tavily keys (the notebook also sets the Azure endpoint and deployment).
3. Open `research_crew.ipynb` in Jupyter or VS Code and run the cells top to bottom.
