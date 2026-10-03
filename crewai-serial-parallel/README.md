# Serial & Parallel Agent Workflows

Shows two ways to make AI agents work together: in sequence, when one agent needs the previous one's output, and in parallel, when their tasks are independent and can run at the same time. A side-by-side look at how orchestration choices affect speed and dependencies.

Stack: CrewAI, Tavily web search, Azure OpenAI.

## Run
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add your Azure OpenAI and Tavily keys (the notebook also sets the Azure endpoint and deployment).
3. Open `serial_parallel_workflows.ipynb` in Jupyter or VS Code and run the cells top to bottom.
