"""
Forger Backend — FastAPI Server

Main entry point for the Forger AI Content Creator backend.
Provides API endpoints for content generation, library management, and social media posting.
"""

import os
import uuid
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional
from workflows.pipeline import run_content_pipeline, get_pipeline_state



# ============ Models ============

class ContentBrief(BaseModel):
    content_type: str = "blog"
    topic: str = ""
    tone: str = "professional"
    audience: str = "general public"
    keywords: list[str] = []
    additional_instructions: str = ""


class SocialPostRequest(BaseModel):
    content_id: str
    platform: str


# ============ In-Memory Store ============

content_library: list[dict] = []
social_posts: list[dict] = []


# ============ App Setup ============

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: seed demo content
    content_library.extend([
        {
            "id": "demo-1",
            "title": "The Future of AI in Marketing",
            "content": "Explore how generative models are reshaping the landscape of digital marketing...",
            "content_type": "blog",
            "word_count": 1204,
            "created_at": "2026-03-04T10:30:00",
            "snippet": "Explore how generative models are reshaping the landscape of digital..."
        },
        {
            "id": "demo-2",
            "title": "10 Tips for Better Productivity",
            "content": "A thread series designed for Twitter and LinkedIn focusing on high-impact daily habits...",
            "content_type": "twitter",
            "word_count": 450,
            "created_at": "2026-03-03T14:20:00",
            "snippet": "A thread series designed for Twitter and LinkedIn focusing on high-impact daily..."
        },
        {
            "id": "demo-3",
            "title": "Podcast: The Web3 Myth",
            "content": "Intro and outro scripts for a 30-minute podcast episode discussing the realities of Web3...",
            "content_type": "podcast",
            "word_count": 890,
            "created_at": "2026-03-02T09:15:00",
            "snippet": "Intro and outro scripts for a 30-minute podcast episode discussing the realities o..."
        },
        {
            "id": "demo-4",
            "title": "Weekly Tech Roundup #42",
            "content": "A curated summary of the most important tech news from the past week...",
            "content_type": "newsletter",
            "word_count": 1560,
            "created_at": "2026-03-01T16:45:00",
            "snippet": "A curated summary of the most important tech news from the past week, formatted..."
        },
    ])
    
    social_posts.extend([
        {
            "id": "sp-1",
            "platform": "linkedin",
            "title": "The Rise of Generative AI in Creative...",
            "content": "Exploring the impact of generative AI...",
            "posted_at": "2026-03-04T08:00:00",
            "engagement": {"likes": 124, "comments": 38, "shares": 12}
        },
        {
            "id": "sp-2",
            "platform": "x",
            "title": "Why prompt engineering is a core skill...",
            "content": "Thread about prompt engineering...",
            "posted_at": "2026-03-04T05:00:00",
            "engagement": {"likes": 852, "comments": 142, "shares": 56}
        },
        {
            "id": "sp-3",
            "platform": "linkedin",
            "title": "Unlocking the power of RAG systems...",
            "content": "Deep dive into RAG systems...",
            "posted_at": "2026-03-03T12:00:00",
            "engagement": {"likes": 230, "comments": 41, "shares": 5}
        },
    ])
    yield


app = FastAPI(
    title="Forger API",
    description="Multi-Agent AI Content Generation Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all origins (public API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ API Routes ============

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    has_key1 = bool(os.getenv("GOOGLE_API_KEY"))
    has_key2 = bool(os.getenv("GOOGLE_API_KEY_2"))
    return {
        "status": "healthy",
        "service": "Forger API",
        "version": "1.0.0",
        "ai_enabled": has_key1,
        "dual_keys": has_key1 and has_key2,
        "model": os.getenv("DEFAULT_MODEL", "gemini-2.0-flash") if has_key1 else "mock-mode",
    }


@app.post("/api/generate")
async def generate_content(brief: ContentBrief):
    """Start content generation pipeline."""
    if not brief.topic.strip():
        raise HTTPException(status_code=400, detail="Topic is required")
    
    pipeline_id = str(uuid.uuid4())[:8]
    
    run_content_pipeline(
        pipeline_id=pipeline_id,
        content_type=brief.content_type,
        topic=brief.topic,
        tone=brief.tone,
        audience=brief.audience,
        keywords=brief.keywords,
        additional_instructions=brief.additional_instructions,
    )
    
    return {"id": pipeline_id, "status": "generating"}


@app.get("/api/generate/{pipeline_id}/status")
async def get_generation_status(pipeline_id: str):
    """Get the current status of a content generation pipeline."""
    state = get_pipeline_state(pipeline_id)
    if not state:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return state.to_status_dict()


@app.get("/api/generate/{pipeline_id}/result")
async def get_generation_result(pipeline_id: str):
    """Get the final result of a completed generation."""
    state = get_pipeline_state(pipeline_id)
    if not state:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    if state.status != "completed":
        raise HTTPException(status_code=202, detail="Generation still in progress")
    
    # Save to library
    result = state.to_result_dict()
    library_item = {
        "id": result["id"],
        "title": result["title"],
        "content": result["content"],
        "content_type": result["content_type"],
        "word_count": result["word_count"],
        "created_at": result["created_at"],
        "snippet": result["content"][:100] + "...",
    }
    if not any(item["id"] == result["id"] for item in content_library):
        content_library.insert(0, library_item)
    
    return result


@app.get("/api/library")
async def get_library():
    """Get all content in the library."""
    return content_library


@app.post("/api/social/post")
async def publish_to_social(request: SocialPostRequest):
    """Publish content to a social media platform."""
    # Find content
    content_item = next((c for c in content_library if c["id"] == request.content_id), None)
    if not content_item:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Mock publishing
    post = {
        "id": f"sp-{str(uuid.uuid4())[:6]}",
        "platform": request.platform,
        "title": content_item["title"],
        "content": content_item["content"][:280],
        "posted_at": datetime.now().isoformat(),
        "engagement": {"likes": 0, "comments": 0, "shares": 0},
    }
    social_posts.insert(0, post)
    
    return post


@app.get("/api/social/posts")
async def get_social_posts():
    """Get all social media posts."""
    return social_posts


# ============ Run Server ============

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    print(f"\n🔥 Forger API starting at http://{host}:{port}")
    print(f"📖 API Docs: http://{host}:{port}/docs\n")
    uvicorn.run("main:app", host=host, port=port, reload=True)
