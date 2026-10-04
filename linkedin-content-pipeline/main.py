"""
main.py — AutoGen-style LinkedIn Content Microservice
------------------------------------------------------

FastAPI service exposing POST /linkedin. Given a brand configuration and a
content context (topic, key points, CTA), it orchestrates three lightweight
agents:

    Ideation  -> proposes several distinct post angles
    Drafting  -> writes the final post from the best angle + self-rates confidence
    Hashtag   -> proposes relevant hashtags for the finished draft

and returns structured JSON: ideas, draft, confidence, hashtags.

Two run modes:
  * MOCK_MODE (default when no Azure OpenAI key is set) — deterministic,
    offline generator. Lets you test the endpoint shape immediately with
    curl, no API key or cost required.
  * Live mode — uses autogen-agentchat + autogen-ext's
    AzureOpenAIChatCompletionClient, same pattern used in the course's
    AutoGen agent-chain demo, adapted into three sequential async calls
    instead of a GroupChat (a REST endpoint needs one deterministic
    response, not an open-ended multi-turn conversation).

Run:
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload

Test (mock mode, no .env needed):
    curl -X POST http://localhost:8000/linkedin \
      -H "Content-Type: application/json" \
      -d '{
            "brand": {"name": "FinEdge Mumbai", "industry": "Fintech"},
            "context": {"topic": "embedded finance in India", "cta": "Follow us for weekly insights."}
          }'
"""

import os
import re
import json
import logging
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-5-mini")
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21")

# Mock mode kicks in automatically if there's no key, or if forced via env var.
MOCK_MODE = os.environ.get("MOCK_MODE", "").lower() == "true" or not AZURE_OPENAI_API_KEY

LOG_DIR = Path(os.environ.get("LOG_DIR", "logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)
RUN_LOG = LOG_DIR / "runs.jsonl"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("linkedin-microservice")
logger.info("Starting in %s mode", "MOCK" if MOCK_MODE else "LIVE (Azure OpenAI)")


# --------------------------------------------------------------------------
# Request / response models
# --------------------------------------------------------------------------
class BrandConfig(BaseModel):
    name: str = Field(..., description="Company / brand name, e.g. 'FinEdge Mumbai'")
    industry: str = Field(default="Fintech")
    tone: str = Field(default="Professional, authoritative, approachable")
    voice_guidelines: Optional[str] = Field(
        default=None, description="Any additional dos/don'ts for brand voice"
    )
    target_audience: str = Field(default="Fintech decision-makers and finance professionals")


class ContentContext(BaseModel):
    topic: str = Field(..., description="Topic or trend to post about")
    key_points: Optional[List[str]] = Field(default=None)
    cta: Optional[str] = Field(default=None, description="Call to action, if any")
    num_ideas: int = Field(default=3, ge=1, le=6)


class LinkedInRequest(BaseModel):
    brand: BrandConfig
    context: ContentContext


class LinkedInResponse(BaseModel):
    ideas: List[str]
    draft: str
    confidence: float
    hashtags: List[str]
    model: str
    generated_at: str


# --------------------------------------------------------------------------
# Logging helper (same append-a-JSON-line pattern as the class demos)
# --------------------------------------------------------------------------
def log_run(payload: dict) -> None:
    record = {"ts": datetime.now(timezone.utc).isoformat(), **payload}
    with RUN_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# --------------------------------------------------------------------------
# Structured-JSON extraction helper (mirrors extract_code_block from class demos)
# --------------------------------------------------------------------------
JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def extract_json(text: str) -> dict:
    m = JSON_BLOCK_RE.search(text or "")
    raw = m.group(1).strip() if m else (text or "").strip()
    return json.loads(raw)


# --------------------------------------------------------------------------
# Live agent layer (Azure OpenAI via AutoGen) — only imported/used if not mocked
# --------------------------------------------------------------------------
_model_client = None
_ideation_agent = None
_drafting_agent = None
_hashtag_agent = None


def _get_agents():
    """Lazily create the AutoGen agents so mock-mode runs never import autogen."""
    global _model_client, _ideation_agent, _drafting_agent, _hashtag_agent
    if _ideation_agent is not None:
        return _ideation_agent, _drafting_agent, _hashtag_agent

    from autogen_agentchat.agents import AssistantAgent
    from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

    _model_client = AzureOpenAIChatCompletionClient(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        model=AZURE_OPENAI_DEPLOYMENT,
        azure_deployment=AZURE_OPENAI_DEPLOYMENT,
    )

    _ideation_agent = AssistantAgent(
        name="Ideation",
        model_client=_model_client,
        system_message=(
            "You are Ideation, a LinkedIn content strategist for a fintech brand. "
            "Given a brand profile and a topic, propose distinct, non-generic post angles. "
            'Reply with ONLY a fenced JSON code block: {"ideas": ["...", "..."]}'
        ),
    )
    _drafting_agent = AssistantAgent(
        name="Drafting",
        model_client=_model_client,
        system_message=(
            "You are Drafting, a senior LinkedIn copywriter for a fintech brand. "
            "Given a brand profile, a topic, and a chosen idea, write one polished "
            "LinkedIn post (150-220 words) matching the brand's tone and voice "
            "guidelines, ending with the call to action if one is given. "
            "Also self-assess, as a confidence score between 0 and 1, how well the "
            "draft matches the brand voice, is factually cautious (no invented "
            "statistics or claims), and is on-topic. Reserve scores above 0.85 for "
            "drafts you would publish completely unedited. "
            'Reply with ONLY a fenced JSON code block: {"draft": "...", "confidence": 0.0}'
        ),
    )
    _hashtag_agent = AssistantAgent(
        name="Hashtag",
        model_client=_model_client,
        system_message=(
            "You are Hashtag, a LinkedIn hashtag specialist. Given a brand's "
            "industry and a finished post draft, propose 5 to 8 relevant, "
            "non-redundant hashtags (mix of broad and niche, no duplicates). "
            'Reply with ONLY a fenced JSON code block: {"hashtags": ["#..."]}'
        ),
    )
    return _ideation_agent, _drafting_agent, _hashtag_agent


async def _ask(agent, message: str) -> str:
    from autogen_agentchat.messages import TextMessage

    result = await agent.on_messages(
        messages=[TextMessage(content=message, source="user")],
        cancellation_token=None,
    )
    if hasattr(result, "chat_message") and getattr(result.chat_message, "content", None):
        return result.chat_message.content
    if hasattr(result, "messages") and result.messages:
        return getattr(result.messages[-1], "content", "") or ""
    return str(result)


async def generate_live(brand: BrandConfig, context: ContentContext) -> LinkedInResponse:
    ideation, drafting, hashtag = _get_agents()

    brand_brief = (
        f"Brand: {brand.name}\nIndustry: {brand.industry}\nTone: {brand.tone}\n"
        f"Voice guidelines: {brand.voice_guidelines or 'none provided'}\n"
        f"Target audience: {brand.target_audience}"
    )
    context_brief = (
        f"Topic: {context.topic}\n"
        f"Key points: {', '.join(context.key_points) if context.key_points else 'none provided'}\n"
        f"Call to action: {context.cta or 'none provided'}"
    )

    # 1) Ideation
    ideation_reply = await _ask(
        ideation,
        f"{brand_brief}\n\n{context_brief}\n\nPropose {context.num_ideas} distinct post ideas.",
    )
    ideas = extract_json(ideation_reply).get("ideas", [])
    if not ideas:
        raise ValueError("Ideation agent returned no ideas")

    # 2) Drafting — lead with the first idea, informed by the others
    drafting_reply = await _ask(
        drafting,
        f"{brand_brief}\n\n{context_brief}\n\nChosen idea: {ideas[0]}\n"
        f"Other ideas considered: {ideas[1:]}\n\nWrite the post now.",
    )
    draft_json = extract_json(drafting_reply)
    draft = draft_json.get("draft", "").strip()
    confidence = max(0.0, min(1.0, float(draft_json.get("confidence", 0.0))))
    if not draft:
        raise ValueError("Drafting agent returned an empty draft")

    # 3) Hashtags
    hashtag_reply = await _ask(
        hashtag,
        f"Industry: {brand.industry}\n\nFinal draft:\n{draft}\n\nPropose hashtags.",
    )
    hashtags = extract_json(hashtag_reply).get("hashtags", [])

    return LinkedInResponse(
        ideas=ideas,
        draft=draft,
        confidence=confidence,
        hashtags=hashtags,
        model=AZURE_OPENAI_DEPLOYMENT,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )


# --------------------------------------------------------------------------
# Mock generator — deterministic, no external calls, no API key required
# --------------------------------------------------------------------------
def generate_mock(brand: BrandConfig, context: ContentContext) -> LinkedInResponse:
    angles = [
        f"Why {context.topic} matters right now for {brand.industry.lower()} leaders",
        f"3 lessons {brand.name} has learned about {context.topic}",
        f"The overlooked risk in {context.topic} — and how to plan for it",
        f"What {brand.target_audience.split(',')[0]} get wrong about {context.topic}",
        f"A behind-the-scenes look at how {brand.name} approaches {context.topic}",
        f"{context.topic}: a 60-second briefing for busy executives",
    ]
    random.shuffle(angles)
    ideas = angles[: context.num_ideas]

    points = "\n".join(f"- {p}" for p in (context.key_points or [])) or (
        f"- {context.topic} is reshaping how our industry operates"
    )
    cta_line = f"\n\n{context.cta}" if context.cta else "\n\nWhat's your take? Drop a comment below."
    draft = (
        f"{ideas[0]}\n\n"
        f"At {brand.name}, we've been thinking hard about {context.topic}. Here's what stands out:\n\n"
        f"{points}\n\n"
        f"For {brand.target_audience}, the implication is clear: staying ahead of "
        f"{context.topic} is no longer optional — it's a competitive requirement."
        f"{cta_line}"
    )

    # Deterministic heuristic confidence: rewards richer input, never claims certainty
    confidence = 0.55
    if context.key_points:
        confidence += 0.15
    if context.cta:
        confidence += 0.1
    if brand.voice_guidelines:
        confidence += 0.1
    confidence = round(min(confidence, 0.95), 2)

    base_tag = "#" + "".join(w.capitalize() for w in brand.industry.split())
    topic_tag = "#" + "".join(w.capitalize() for w in context.topic.split())[:30]
    hashtags = list(
        dict.fromkeys(
            [base_tag, topic_tag, "#Fintech", "#Leadership", "#Innovation", f"#{brand.name.replace(' ', '')}"]
        )
    )[:6]

    return LinkedInResponse(
        ideas=ideas,
        draft=draft,
        confidence=confidence,
        hashtags=hashtags,
        model="mock-generator",
        generated_at=datetime.now(timezone.utc).isoformat(),
    )


# --------------------------------------------------------------------------
# FastAPI app
# --------------------------------------------------------------------------
app = FastAPI(
    title="LinkedIn Content Automation Microservice",
    description=(
        "AutoGen-style multi-agent service that generates LinkedIn post ideas, "
        "a draft, a confidence score, and hashtags for a given brand and topic."
    ),
    version="1.0.0",
)


@app.get("/health")
async def health():
    return {"status": "ok", "mock_mode": MOCK_MODE}


@app.post("/linkedin", response_model=LinkedInResponse)
async def linkedin_endpoint(req: LinkedInRequest):
    try:
        if MOCK_MODE:
            result = generate_mock(req.brand, req.context)
        else:
            result = await generate_live(req.brand, req.context)
    except Exception as e:
        logger.exception("Content generation failed")
        log_run({"status": "error", "error": str(e), "request": req.model_dump()})
        raise HTTPException(status_code=502, detail=f"Content generation failed: {e}")

    log_run({"status": "ok", "request": req.model_dump(), "response": result.model_dump()})
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=True)
