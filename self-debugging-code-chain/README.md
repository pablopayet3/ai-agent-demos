# Self-Debugging Code Chain

The model writes a small program, writes its own unit tests, runs them, reads the failures, and keeps fixing its own code until every test passes. A closed loop of generate, test, and repair, so the final output is code that actually runs.

Stack: Google Gemini, Python `unittest`, `subprocess`.

## Run
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add your Gemini key.
3. Open `code_chain.ipynb` in Jupyter or VS Code and run the cells top to bottom.
