# RAG over PDFs, with citations

Ask a question about a stack of PDFs and get an answer with the exact page it came from, so you can trust it. The documents are chunked, embedded, and stored in a FAISS vector index; at query time the most relevant chunks are retrieved and passed to Gemini, which answers and cites the source page.

Stack: LangChain, FAISS, Google Gemini, PyPDF.

## Run
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add your Google (Gemini) key.
3. Open `rag_pipeline.ipynb` in Jupyter or VS Code and run the cells top to bottom.
