"""
Forger Agent Definitions — Gemini LLM agents

Each agent has a specialized role in the content creation pipeline:
1. Researcher → Gathers facts, trends, and data
2. Writer → Drafts content based on research
3. Editor → Refines tone, grammar, structure
4. SEO Optimizer → Adds keywords, meta, hashtags
"""

import os
import json
import time
import threading
from typing import Optional
from collections import deque

GEMINI_AVAILABLE = False
_use_new_api = False

# Try new google.genai client first
try:
    from google import genai as genai_new
    _use_new_api = True
    GEMINI_AVAILABLE = True
    print("✅ Using google.genai (new Client API)")
except ImportError:
    pass

# Fallback to legacy google.generativeai
if not GEMINI_AVAILABLE:
    try:
        import google.generativeai as genai_legacy
        GEMINI_AVAILABLE = True
        print("✅ Using google.generativeai (legacy API)")
    except ImportError:
        print("❌ No Gemini library available")


# ============ RATE LIMITER (per-key, 10 req/min) ============

MAX_REQUESTS_PER_MINUTE = 10
MIN_SPACING_SECONDS = 6


class KeyRateLimiter:
    def __init__(self, name: str):
        self.name = name
        self.timestamps: deque = deque()
        self.lock = threading.Lock()
        self.last_call = 0.0
        self.failures = 0

    def wait(self):
        with self.lock:
            now = time.time()
            since_last = now - self.last_call
            if since_last < MIN_SPACING_SECONDS:
                wait = MIN_SPACING_SECONDS - since_last
                print(f"⏳ [{self.name}] spacing {wait:.1f}s")
                time.sleep(wait)
                now = time.time()

            while self.timestamps and self.timestamps[0] < now - 60:
                self.timestamps.popleft()

            if len(self.timestamps) >= MAX_REQUESTS_PER_MINUTE:
                wait_time = 60 - (now - self.timestamps[0]) + 1.0
                if wait_time > 0:
                    print(f"⏳ [{self.name}] rate limit {wait_time:.1f}s")
                    time.sleep(wait_time)
                    now = time.time()
                    while self.timestamps and self.timestamps[0] < now - 60:
                        self.timestamps.popleft()

            self.timestamps.append(time.time())
            self.last_call = time.time()
            print(f"🔑 [{self.name}] call #{len(self.timestamps)}/{MAX_REQUESTS_PER_MINUTE}")


_limiter_1 = KeyRateLimiter("Key1-Research+Write")
_limiter_2 = KeyRateLimiter("Key2-Edit+SEO")
_model_cache: dict[str, object] = {}
_model_lock = threading.Lock()


def _call_gemini(api_key: str, prompt: str) -> str:
    """Direct Gemini call — handles both new and legacy API."""
    model_name = os.getenv("DEFAULT_MODEL", "gemini-2.0-flash")
    
    if _use_new_api:
        client = genai_new.Client(api_key=api_key)
        response = client.models.generate_content(model=model_name, contents=prompt)
        return response.text
    else:
        genai_legacy.configure(api_key=api_key)
        model = genai_legacy.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text


def rate_limited_generate(api_key: str, prompt: str, limiter: KeyRateLimiter, max_retries: int = 2) -> str:
    """Call Gemini with rate limiting + retry."""
    if limiter.failures >= 5:
        raise Exception(f"🔴 [{limiter.name}] circuit breaker OPEN")

    for attempt in range(max_retries):
        limiter.wait()
        try:
            result = _call_gemini(api_key, prompt)
            limiter.failures = 0
            return result
        except Exception as e:
            error_str = str(e).lower()
            print(f"❗ [{limiter.name}] Gemini error (attempt {attempt+1}): {e}")
            if "429" in error_str or "quota" in error_str or "rate" in error_str:
                limiter.failures += 1
                backoff = (attempt + 1) * 8
                print(f"⚠️ [{limiter.name}] quota hit, backoff {backoff}s")
                time.sleep(backoff)
            else:
                raise
    raise Exception(f"[{limiter.name}]: API failed after {max_retries} retries")


def _get_api_key(slot: int) -> str:
    """Get API key for slot 1 or 2."""
    if slot == 2:
        key = os.getenv("GOOGLE_API_KEY_2", "") or os.getenv("GOOGLE_API_KEY", "")
    else:
        key = os.getenv("GOOGLE_API_KEY", "")
    if not key:
        raise Exception(f"No API key for slot {slot}! Set GOOGLE_API_KEY env var.")
    return key


# ============ AGENTS ============

def research_agent(topic: str, content_type: str, keywords: list[str]) -> dict:
    """Agent 1: Researcher — Gathers data and insights."""
    api_key = _get_api_key(1)
    
    prompt = f"""You are a senior content researcher. Research the following topic and provide findings.

Topic: {topic}
Content Type: {content_type}
Target Keywords: {', '.join(keywords) if keywords else 'None specified'}

Return JSON only:
{{
    "key_facts": ["fact1", "fact2", "fact3", "fact4", "fact5"],
    "statistics": ["stat1", "stat2", "stat3"],
    "trends": ["trend1", "trend2"],
    "expert_quotes": ["quote1", "quote2"],
    "suggested_structure": ["section1", "section2", "section3", "section4"],
    "competitor_insights": "Brief analysis"
}}

Return ONLY the JSON, no markdown formatting."""
    
    text = rate_limited_generate(api_key, prompt, _limiter_1).strip()
    print(f"✅ Researcher response: {text[:200]}")
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(text)


def writer_agent(topic: str, content_type: str, tone: str, audience: str, 
                 research: dict, instructions: str = "") -> str:
    """Agent 2: Writer — Crafts content based on research."""
    api_key = _get_api_key(1)
    
    prompt = f"""You are an expert content writer. Using the research below, 
write high-quality {content_type} content.

Topic: {topic}
Tone: {tone}
Target Audience: {audience}
Additional Instructions: {instructions or 'None'}

Research Data:
- Key Facts: {json.dumps(research.get('key_facts', []))}
- Statistics: {json.dumps(research.get('statistics', []))}
- Trends: {json.dumps(research.get('trends', []))}
- Expert Quotes: {json.dumps(research.get('expert_quotes', []))}
- Suggested Structure: {json.dumps(research.get('suggested_structure', []))}

GUIDELINES:
- Write in {tone} tone for {audience}
- Include statistics and quotes from research
- Blog posts: use markdown headers (##), bullet points, bold text
- Social media: concise, hooks, hashtags
- Scripts: speaker directions and timings

Write the complete content now:"""
    
    result = rate_limited_generate(api_key, prompt, _limiter_1).strip()
    print(f"✅ Writer: {len(result)} chars")
    return result


def editor_agent(content: str, tone: str, audience: str) -> str:
    """Agent 3: Editor — Reviews and refines content."""
    api_key = _get_api_key(2)
    
    prompt = f"""You are a senior content editor. Review and improve the following content.

Content to Edit:
{content}

Requirements:
- Ensure {tone} tone throughout
- Optimize for {audience} audience
- Fix grammar and spelling issues
- Improve flow and readability
- Strengthen opening hook
- Make conclusions more impactful
- Keep the same format (markdown headers, lists, etc.)

Return the EDITED content only, no explanations:"""
    
    result = rate_limited_generate(api_key, prompt, _limiter_2).strip()
    print(f"✅ Editor: {len(result)} chars")
    return result


def seo_optimizer_agent(content: str, keywords: list[str], content_type: str) -> dict:
    """Agent 4: SEO Optimizer — Adds meta tags, keywords, optimization."""
    api_key = _get_api_key(2)
    
    prompt = f"""You are an SEO specialist. Optimize this content and generate SEO metadata.

Content:
{content[:2000]}

Target Keywords: {', '.join(keywords) if keywords else 'auto-detect'}
Content Type: {content_type}

Return JSON:
{{
    "optimized_content": "The full content with SEO improvements",
    "seo_title": "SEO-optimized title (60 chars max)",
    "meta_description": "Meta description (155 chars max)",
    "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
    "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3"],
    "readability_score": "Grade level",
    "word_count": 0
}}

Return ONLY valid JSON:"""
    
    text = rate_limited_generate(api_key, prompt, _limiter_2).strip()
    print(f"✅ SEO response: {text[:200]}")
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    result = json.loads(text)
    result["word_count"] = len(content.split())
    return result


def topic_from_content(content: str) -> str:
    """Extract topic/title from content."""
    lines = content.strip().split("\n")
    for line in lines:
        clean = line.strip().lstrip("#").strip()
        if clean and len(clean) > 5:
            return clean
    return "Generated Content"
