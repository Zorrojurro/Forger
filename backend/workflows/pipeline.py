"""
Forger Content Pipeline — Sequential multi-agent workflow

Pipeline: Brief → Researcher → Writer → Editor → SEO Optimizer → Final Output

This implements a sequential pipeline that runs each agent in order,
passing the output of each to the next as input.
"""

import time
import threading
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime

from agents.crew import (
    research_agent,
    writer_agent,
    editor_agent,
    seo_optimizer_agent,
    topic_from_content,
)


@dataclass
class AgentLog:
    agent: str
    status: str  # "completed", "in_progress", "pending"
    message: str
    timestamp: str = ""

    def to_dict(self):
        return {
            "agent": self.agent,
            "status": self.status,
            "message": self.message,
            "timestamp": self.timestamp or datetime.now().isoformat(),
        }


@dataclass
class PipelineState:
    id: str
    content_type: str
    topic: str
    tone: str
    audience: str
    keywords: list[str]
    additional_instructions: str
    
    # Pipeline state
    progress: int = 0
    status: str = "generating"  # "generating", "completed", "error"
    agents: list[AgentLog] = field(default_factory=list)
    
    # Outputs
    research: Optional[dict] = None
    draft_content: Optional[str] = None
    edited_content: Optional[str] = None
    final_content: Optional[str] = None
    seo_data: Optional[dict] = None
    title: Optional[str] = None
    word_count: int = 0
    created_at: str = ""

    def to_status_dict(self):
        return {
            "progress": self.progress,
            "status": self.status,
            "agents": [a.to_dict() for a in self.agents],
        }

    def to_result_dict(self):
        return {
            "id": self.id,
            "title": self.title or topic_from_content(self.final_content or ""),
            "content": self.final_content or "",
            "content_type": self.content_type,
            "word_count": self.word_count,
            "seo_meta": {
                "title": self.seo_data.get("seo_title", "") if self.seo_data else "",
                "description": self.seo_data.get("meta_description", "") if self.seo_data else "",
                "keywords": self.seo_data.get("keywords", []) if self.seo_data else [],
            },
            "created_at": self.created_at,
            "agent_log": [a.to_dict() for a in self.agents],
        }


# In-memory store for active generations
_pipeline_store: dict[str, PipelineState] = {}


def get_pipeline_state(pipeline_id: str) -> Optional[PipelineState]:
    return _pipeline_store.get(pipeline_id)


def run_content_pipeline(
    pipeline_id: str,
    content_type: str,
    topic: str,
    tone: str,
    audience: str,
    keywords: list[str],
    additional_instructions: str = "",
) -> PipelineState:
    """Run the multi-agent content pipeline in a background thread."""
    
    state = PipelineState(
        id=pipeline_id,
        content_type=content_type,
        topic=topic,
        tone=tone,
        audience=audience,
        keywords=keywords,
        additional_instructions=additional_instructions,
        created_at=datetime.now().isoformat(),
        agents=[
            AgentLog("Researcher", "pending", "Waiting to start..."),
            AgentLog("Writer", "pending", "Waiting to start..."),
            AgentLog("Editor", "pending", "Waiting to start..."),
            AgentLog("SEO Optimizer", "pending", "Waiting to start..."),
        ],
    )
    _pipeline_store[pipeline_id] = state

    # Run pipeline in background thread
    thread = threading.Thread(target=_execute_pipeline, args=(state,))
    thread.daemon = True
    thread.start()

    return state


def _execute_pipeline(state: PipelineState):
    """Execute the 4-agent pipeline sequentially."""
    try:
        # === Agent 1: Researcher ===
        state.agents[0] = AgentLog("Researcher", "in_progress", "Analyzing topic trends & citations...")
        state.progress = 10
        time.sleep(1)  # Small delay for UI feedback
        
        state.research = research_agent(state.topic, state.content_type, state.keywords)
        state.agents[0] = AgentLog("Researcher", "completed", "Research complete — gathered key facts, statistics, and trends.")
        state.progress = 25

        # === Agent 2: Writer ===
        state.agents[1] = AgentLog("Writer", "in_progress", "Drafting content based on research...")
        time.sleep(1)

        state.draft_content = writer_agent(
            state.topic, state.content_type, state.tone, state.audience,
            state.research, state.additional_instructions
        )
        state.agents[1] = AgentLog("Writer", "completed", "Draft complete — content structured and written.")
        state.progress = 50

        # === Agent 3: Editor ===
        state.agents[2] = AgentLog("Editor", "in_progress", "Reviewing tone, grammar, and structure...")
        time.sleep(1)

        state.edited_content = editor_agent(state.draft_content, state.tone, state.audience)
        state.agents[2] = AgentLog("Editor", "completed", "Editing complete — content polished and refined.")
        state.progress = 75

        # === Agent 4: SEO Optimizer ===
        state.agents[3] = AgentLog("SEO Optimizer", "in_progress", "Adding keywords, meta tags, and optimization...")
        time.sleep(1)

        state.seo_data = seo_optimizer_agent(state.edited_content, state.keywords, state.content_type)
        state.final_content = state.seo_data.get("optimized_content", state.edited_content)
        state.word_count = state.seo_data.get("word_count", len(state.final_content.split()))
        state.title = state.seo_data.get("seo_title", topic_from_content(state.final_content))
        # Add Forger watermark
        watermark = "\n\n---\n\n*🔥 Generated by Forger — AI Multi-Agent Content Platform*"
        if state.final_content and "Generated by Forger" not in state.final_content:
            state.final_content += watermark

        state.agents[3] = AgentLog("SEO Optimizer", "completed", "SEO optimization complete — content ready to publish!")
        state.progress = 100
        state.status = "completed"

    except Exception as e:
        print(f"Pipeline error: {e}")
        # Complete with whatever we have so frontend doesn't hang
        for agent in state.agents:
            if agent.status == "in_progress":
                agent.status = "completed"
                agent.message = f"Completed with fallback — {str(e)[:50]}"
            elif agent.status == "pending":
                agent.status = "completed"
                agent.message = "Skipped due to earlier error"
        
        # Use best available content
        state.final_content = state.edited_content or state.draft_content or f"# {state.topic}\n\nContent generation encountered an issue. Please try again."
        state.word_count = len(state.final_content.split())
        state.progress = 100
        state.status = "completed"
