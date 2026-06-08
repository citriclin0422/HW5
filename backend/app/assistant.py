import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import HTTPException
from pydantic import BaseModel, Field

from .topics import TOPICS


class AskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=1000)
    topic_slug: str | None = None


class AskResponse(BaseModel):
    answer: str


def ask_assistant(request: AskRequest) -> AskResponse:
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="AI assistant is not configured. Set OPENAI_API_KEY on the backend.",
        )

    topic = next(
        (item for item in TOPICS if item["slug"] == request.topic_slug),
        None,
    )
    context = _topic_context(topic) if topic else "No lesson is currently selected."

    payload = {
        "model": os.getenv("OPENAI_MODEL", "gpt-5.5"),
        "instructions": (
                "You are a friendly machine learning teaching assistant. "
                "Answer in Traditional Chinese unless the learner asks for another language. "
                "Use clear explanations, short examples, and equations only when useful. "
                "Focus on learning and mention uncertainty when appropriate."
        ),
        "input": f"Current lesson context:\n{context}\n\nLearner question:\n{request.question}",
    }
    api_request = Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(api_request, timeout=60) as response:
            response_body = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        detail = _provider_error(error)
        raise HTTPException(
            status_code=502,
            detail=f"AI provider request failed: {detail}",
        ) from error
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=502, detail="AI provider request failed.") from error

    answer = _output_text(response_body).strip()
    if not answer:
        raise HTTPException(status_code=502, detail="AI provider returned an empty response.")
    return AskResponse(answer=answer)


def _output_text(response_body: dict) -> str:
    texts = []
    for output in response_body.get("output", []):
        for content in output.get("content", []):
            if content.get("type") == "output_text":
                texts.append(content.get("text", ""))
    return "\n".join(texts)


def _provider_error(error: HTTPError) -> str:
    try:
        body = json.loads(error.read().decode("utf-8"))
        return body.get("error", {}).get("message", f"HTTP {error.code}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return f"HTTP {error.code}"


def _topic_context(topic: dict) -> str:
    return "\n".join(
        [
            f"Topic: {topic['title']} ({topic['english']})",
            f"Family: {topic['family']}",
            f"Difficulty: {topic['difficulty']}",
            f"Summary: {topic['summary']}",
            f"Why it matters: {topic['why']}",
            f"Example: {topic['example']}",
            f"Strengths: {', '.join(topic['strengths'])}",
            f"Limitations: {', '.join(topic['limits'])}",
        ]
    )
