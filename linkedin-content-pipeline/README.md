# LinkedIn Content Pipeline

A FastAPI microservice that writes a brand's LinkedIn posts with three AutoGen agents run in sequence, returning structured JSON an automation can act on.

- **Ideation** proposes several distinct post angles for the brand and topic.
- **Drafting** writes the post from the best angle and self-rates a confidence score (0 to 1) for brand voice, factual caution, and topic fit.
- **Hashtag** proposes 5 to 8 relevant hashtags for the finished draft.

In the full build, an n8n workflow calls this service on a schedule: it assembles the brand brief, calls `POST /linkedin`, composes the post, and sends it through an approval gate. Drafts that clear the gate go to the LinkedIn publish branch; the rest are sent to Slack for human review, and every run is logged. This folder contains the service; the n8n workflow is described on the portfolio page.

## Endpoints

- `POST /linkedin` takes a brand config and a content context, and returns `ideas`, `draft`, `confidence`, `hashtags`, `model`, and `generated_at`.
- `GET /health` reports whether the service is in mock or live mode.

Every request is appended to `logs/runs.jsonl`.

## Mock or live

With no Azure OpenAI key set, the service runs in **mock mode**: a deterministic, offline generator, so you can test the endpoint immediately with no key and no cost. Set the key in `.env` and it switches to **live mode** with Azure OpenAI (gpt-5-mini). The three agents run as sequential calls rather than an open-ended group chat, because a REST endpoint needs one predictable response.

## Run

1. `pip install -r requirements.txt`
2. Optional, for live mode: copy `.env.example` to `.env` and add your Azure OpenAI details.
3. `uvicorn main:app --port 8000 --reload`

```bash
curl -X POST http://localhost:8000/linkedin \
  -H "Content-Type: application/json" \
  -d '{"brand": {"name": "FinEdge Mumbai", "industry": "Fintech"},
       "context": {"topic": "embedded finance in India", "cta": "Follow us for weekly insights."}}'
```

## Sample output (live run, trimmed)

```json
{
  "ideas": [
    "Compliance sprint: a one-page roadmap for launching embedded finance in India ...",
    "Underwriting reimagined: how platforms can use embedded finance + alternative data ...",
    "Balance-sheet orchestration: choosing the partner and revenue model that scales ..."
  ],
  "draft": "Regulators and licences are the gating factor, treat them as a checklist, not a blocker. ...",
  "confidence": 0.9,
  "hashtags": ["#Fintech", "#EmbeddedFinance", "#RegulatoryCompliance", "#UPI", "#NBFC", "#KYC", "#DataLocalisation"],
  "model": "gpt-5-mini"
}
```

FinEdge Mumbai is a sample brand used for the demo.
