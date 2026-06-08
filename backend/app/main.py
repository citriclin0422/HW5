from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .assistant import AskRequest, AskResponse, ask_assistant
from .topics import TOPICS

app = FastAPI(
    title="Top10 Machine Learning Learning API",
    description="Dynamic learning content for the top 10 machine learning algorithms.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/topics")
def list_topics(
    q: str | None = Query(default=None),
    family: str | None = Query(default=None),
    difficulty: str | None = Query(default=None),
) -> list[dict]:
    topics = TOPICS
    if q:
        needle = q.casefold()
        topics = [
            topic
            for topic in topics
            if needle in topic["title"].casefold()
            or needle in topic["english"].casefold()
            or needle in topic["summary"].casefold()
        ]
    if family and family != "all":
        topics = [topic for topic in topics if topic["family"] == family]
    if difficulty and difficulty != "all":
        topics = [topic for topic in topics if topic["difficulty"] == difficulty]
    return topics


@app.get("/api/topics/{slug}")
def get_topic(slug: str) -> dict:
    for topic in TOPICS:
        if topic["slug"] == slug:
            return topic
    raise HTTPException(status_code=404, detail="Topic not found")


@app.get("/api/meta")
def meta() -> dict:
    return {
        "families": sorted({topic["family"] for topic in TOPICS}),
        "difficulties": ["入門", "中階", "進階"],
        "total": len(TOPICS),
    }


@app.post("/api/assistant/ask", response_model=AskResponse)
def ask_ai(request: AskRequest) -> AskResponse:
    return ask_assistant(request)
