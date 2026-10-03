# Agentic RAG Router

Figures out where each question should be answered from before it answers: your documents (vector retrieval), a live web search, or the model's own knowledge. A routing step classifies the query and sends it down the right path, so simple questions don't trigger an expensive search and document questions aren't answered from memory.

Stack: CrewAI, Google Gemini, FAISS, Tavily web search.

## Run
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add your Google (Gemini) and Tavily keys.
3. Open `agentic_rag_router.ipynb` in Jupyter or VS Code and run the cells top to bottom.
