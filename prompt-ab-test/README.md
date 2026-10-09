# Prompt A/B Test

The same request, worded four ways, sent to the same model. The notebook sends one paragraph to the model with four different summarization prompts, traces every call in LangSmith, and compares the answers side by side. Only the instruction changes between calls, so any difference in the output comes from the wording.

Stack: LangChain, LangSmith, Google Gemini (Azure OpenAI optional), `tabulate`.

## Result (one run per variant, Gemini 3.5 Flash-Lite)

| Variant | Instruction | Words | Latency | Tokens | Cost |
|---|---|---|---|---|---|
| 1 | Summarize the following in one sentence: | 16 | 0.95s | 57 | $0.0000589 |
| 2 | Write a short summary of this paragraph: | 17 | 0.69s | 62 | $0.0000714 |
| 3 | Condense this into a concise statement: | 13 | 0.55s | 56 | $0.0000564 |
| 4 | TL;DR: | 40 | 0.67s | 83 | $0.0001327 |

- With only `TL;DR:` in front of the paragraph, the model read the paragraph as the user's own summary, complimented it and asked what to do next. No summary, and the most expensive call.
- "Write a short summary" added a Markdown `**Summary:**` label.
- "Condense" gave the shortest answer but dropped "from data"; all three working variants dropped "adapt to new inputs".

One input and one run per variant: this shows failure modes, it does not rank the prompts. Word counts come from the notebook; latency, tokens and cost from LangSmith.

## Run
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add your Gemini key (and a LangSmith key if you want tracing).
3. Open `prompt_ab_test.ipynb` in Jupyter or VS Code and run the cells top to bottom.
