"""
Forger Agent Definitions — CrewAI-style agents with Gemini LLM

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
import traceback
from typing import Optional
from collections import deque

GEMINI_AVAILABLE = False
_use_new_api = False

# Try new google.genai client first (recommended)
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


# ============ STRICT RATE LIMITER (per-key, 10 requests/minute each) ============

MAX_REQUESTS_PER_MINUTE = 10
MIN_SPACING_SECONDS = 6

class KeyRateLimiter:
    """Independent rate limiter per API key."""
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


# Two independent rate limiters
_limiter_1 = KeyRateLimiter("Key1-Research+Write")
_limiter_2 = KeyRateLimiter("Key2-Edit+SEO")

# Model cache per key
_model_cache: dict[str, object] = {}
_model_lock = threading.Lock()


def rate_limited_generate(model, prompt: str, limiter: KeyRateLimiter, api_key: str = "", max_retries: int = 2) -> str:
    """Call Gemini with per-key rate limiting + retry. Circuit breaker on repeated failures."""
    if limiter.failures >= 3:
        print(f"🔴 [{limiter.name}] circuit breaker OPEN — using mock data")
        raise Exception(f"Circuit breaker: {limiter.name} disabled")

    for attempt in range(max_retries):
        limiter.wait()
        try:
            if _use_new_api:
                # New google.genai Client API — use client directly
                client = genai_new.Client(api_key=api_key)
                model_name = os.getenv("DEFAULT_MODEL", "gemini-2.0-flash")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                limiter.failures = 0
                return response.text
            else:
                # Legacy google.generativeai API
                response = model.generate_content(prompt)
                limiter.failures = 0
                return response.text
        except Exception as e:
            error_str = str(e).lower()
            print(f"❗ [{limiter.name}] Gemini error (attempt {attempt+1}): {e}")
            if "429" in error_str or "quota" in error_str or "rate" in error_str:
                limiter.failures += 1
                backoff = (attempt + 1) * 5
                print(f"⚠️ [{limiter.name}] quota hit, backoff {backoff}s")
                time.sleep(backoff)
            else:
                limiter.failures += 1
                raise
    limiter.failures += 1
    raise Exception(f"{limiter.name}: rate limit exceeded after retries")


def get_model(slot: int = 1):
    """Get Gemini model for the given slot (1 or 2).
    Slot 1: Researcher + Writer (uses GOOGLE_API_KEY)
    Slot 2: Editor + SEO (uses GOOGLE_API_KEY_2, falls back to GOOGLE_API_KEY)
    Returns (model_or_marker, api_key) tuple.
    """
    if not GEMINI_AVAILABLE:
        print(f"⚠️ get_model(slot={slot}): GEMINI_AVAILABLE=False")
        return None

    if slot == 2:
        api_key = os.getenv("GOOGLE_API_KEY_2", "") or os.getenv("GOOGLE_API_KEY", "")
    else:
        api_key = os.getenv("GOOGLE_API_KEY", "")

    if not api_key:
        print(f"⚠️ get_model(slot={slot}): No API key found!")
        return None

    if _use_new_api:
        # For new API, we create the client in rate_limited_generate
        # Return a marker object that carries the api_key
        print(f"✅ Slot {slot} ready (new API, key: {api_key[:8]}...)")
        return {"_api_key": api_key, "_slot": slot}
    else:
        # Legacy API: configure and create model
        with _model_lock:
            cache_key = f"{api_key[:8]}_{slot}"
            if cache_key not in _model_cache:
                genai_legacy.configure(api_key=api_key)
                model_name = os.getenv("DEFAULT_MODEL", "gemini-2.0-flash")
                _model_cache[cache_key] = genai_legacy.GenerativeModel(model_name)
                print(f"✅ Created legacy model for slot {slot} (key: {api_key[:8]}..., model: {model_name})")
            return _model_cache[cache_key]


def research_agent(topic: str, content_type: str, keywords: list[str]) -> dict:
    """Agent 1: Researcher — Gathers data and insights on the topic."""
    model = get_model(slot=1)  # Researcher uses Key 1
    
    if model:
        prompt = f"""You are a senior content researcher. Your job is to research the following topic 
and provide comprehensive findings that a writer can use to create high-quality content.

Topic: {topic}
Content Type: {content_type}
Target Keywords: {', '.join(keywords) if keywords else 'None specified'}

Provide your research in the following JSON format:
{{
    "key_facts": ["fact1", "fact2", "fact3", "fact4", "fact5"],
    "statistics": ["stat1", "stat2", "stat3"],
    "trends": ["trend1", "trend2"],
    "expert_quotes": ["quote1", "quote2"],
    "suggested_structure": ["section1", "section2", "section3", "section4"],
    "competitor_insights": "Brief analysis of what competitors are doing"
}}

Return ONLY the JSON, no markdown formatting."""
        
        try:
            api_key = model.get("_api_key", "") if isinstance(model, dict) else ""
            text = rate_limited_generate(model, prompt, _limiter_1, api_key=api_key).strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            return json.loads(text)
        except Exception as e:
            print(f"Researcher agent error: {e}")
    
    # Fallback mock research
    return {
        "key_facts": [
            f"The {topic} industry is growing at 25% annually",
            "AI-powered tools are transforming content creation",
            "78% of marketers plan to increase AI adoption by 2027",
            "Multi-agent systems outperform single-model approaches by 2.3x",
            "Content personalization drives 40% higher engagement"
        ],
        "statistics": [
            "4.4 million blog posts published daily globally",
            "Content marketing generates 3x more leads than traditional marketing",
            "72% of consumers prefer personalized messaging"
        ],
        "trends": [
            "Shift towards AI-augmented content workflows",
            "Rise of multi-channel content syndication"
        ],
        "expert_quotes": [
            "\"AI won't replace content creators — it will make them superhuman.\" — Industry Expert",
            "\"The future of marketing is personalized at scale.\" — Marketing Leader"
        ],
        "suggested_structure": [
            "Introduction & Hook",
            "Current Landscape",
            "Key Trends & Analysis",
            "Practical Implications",
            "Conclusion & Call to Action"
        ],
        "competitor_insights": "Top competitors are focusing on AI integration while maintaining human editorial oversight."
    }


def writer_agent(topic: str, content_type: str, tone: str, audience: str, 
                 research: dict, instructions: str = "") -> str:
    """Agent 2: Writer — Crafts compelling content based on research."""
    model = get_model(slot=1)  # Writer uses Key 1
    
    if model:
        prompt = f"""You are an expert content writer. Using the research provided below, 
write high-quality {content_type} content.

Topic: {topic}
Content Type: {content_type}
Tone: {tone}
Target Audience: {audience}
Additional Instructions: {instructions or 'None'}

Research Data:
- Key Facts: {json.dumps(research.get('key_facts', []))}
- Statistics: {json.dumps(research.get('statistics', []))}
- Trends: {json.dumps(research.get('trends', []))}
- Expert Quotes: {json.dumps(research.get('expert_quotes', []))}
- Suggested Structure: {json.dumps(research.get('suggested_structure', []))}

IMPORTANT GUIDELINES:
- Write in {tone} tone appropriate for {audience}
- Include relevant statistics and quotes from the research
- For blog posts: use markdown headers (##), bullet points, and bold text
- For social media: keep it concise, use hooks, and include hashtags
- For scripts: include speaker directions and timings
- For newsletters: use sections with clear value propositions

Write the complete content now:"""
        
        try:
            api_key = model.get("_api_key", "") if isinstance(model, dict) else ""
            return rate_limited_generate(model, prompt, _limiter_1, api_key=api_key).strip()
        except Exception as e:
            print(f"Writer agent error: {e}")
    
    # Fallback mock content based on type
    if content_type == "blog":
        return _mock_blog_content(topic)
    elif content_type in ("linkedin", "twitter"):
        return _mock_social_content(topic, content_type)
    elif content_type == "video":
        return _mock_video_script(topic)
    elif content_type == "newsletter":
        return _mock_newsletter(topic)
    elif content_type == "podcast":
        return _mock_podcast_script(topic)
    return _mock_blog_content(topic)


def editor_agent(content: str, tone: str, audience: str) -> str:
    """Agent 3: Editor — Reviews and refines content."""
    model = get_model(slot=2)  # Editor uses Key 2
    
    if model:
        prompt = f"""You are a senior content editor. Review and improve the following content.

Content to Edit:
{content}

Requirements:
- Ensure {tone} tone throughout
- Optimize for {audience} audience
- Fix any grammar or spelling issues
- Improve flow and readability
- Strengthen the opening hook
- Make conclusions more impactful
- Keep the same format (markdown headers, lists, etc.)

Return the EDITED content only, no explanations:"""
        
        try:
            api_key = model.get("_api_key", "") if isinstance(model, dict) else ""
            return rate_limited_generate(model, prompt, _limiter_2, api_key=api_key).strip()
        except Exception as e:
            print(f"Editor agent error: {e}")
    
    # If no model, return content as-is (mock editing)
    return content


def seo_optimizer_agent(content: str, keywords: list[str], content_type: str) -> dict:
    """Agent 4: SEO Optimizer — Adds meta tags, keywords, and platform optimization."""
    model = get_model(slot=2)  # SEO uses Key 2
    
    if model:
        prompt = f"""You are an SEO and content optimization specialist. 
Optimize the following content and generate SEO metadata.

Content:
{content[:2000]}

Target Keywords: {', '.join(keywords) if keywords else 'auto-detect relevant keywords'}
Content Type: {content_type}

Return a JSON object with:
{{
    "optimized_content": "The full content with SEO improvements (add keywords naturally, improve headers)",
    "seo_title": "SEO-optimized title (60 chars max)",
    "meta_description": "Compelling meta description (155 chars max)",
    "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
    "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3"],
    "readability_score": "Grade level (e.g., Grade 8)",
    "word_count": 0
}}

Return ONLY valid JSON:"""
        
        try:
            api_key = model.get("_api_key", "") if isinstance(model, dict) else ""
            text = rate_limited_generate(model, prompt, _limiter_2, api_key=api_key).strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            result = json.loads(text)
            result["word_count"] = len(content.split())
            return result
        except Exception as e:
            print(f"SEO Optimizer agent error: {e}")
    
    # Fallback mock SEO
    word_count = len(content.split())
    title_words = topic_from_content(content)
    return {
        "optimized_content": content,
        "seo_title": title_words[:60] if title_words else "AI-Generated Content",
        "meta_description": f"Discover insights about {title_words[:50]}. Expert analysis and actionable takeaways.",
        "keywords": keywords if keywords else ["AI", "content marketing", "automation", "productivity", "strategy"],
        "hashtags": ["#AI", "#ContentMarketing", "#Innovation", "#TechTrends", "#Growth"],
        "readability_score": "Grade 8",
        "word_count": word_count
    }


def topic_from_content(content: str) -> str:
    """Extract a likely topic/title from content."""
    lines = content.strip().split("\n")
    for line in lines:
        clean = line.strip().lstrip("#").strip()
        if clean and len(clean) > 5:
            return clean
    return "Generated Content"


# ============ Mock Content Templates ============

def _mock_blog_content(topic: str) -> str:
    return f"""# {topic}

As we stand at the precipice of a new technological era, the convergence of artificial intelligence and modern innovation is reshaping industries across the globe. This comprehensive analysis explores what this means for professionals and organizations.

## The Current Landscape

The landscape has undergone a seismic shift in recent years. With rapid advancements in AI and automation, the demand for smart, data-driven approaches has never been greater.

**Key statistics paint a compelling picture:**
- The global market is projected to reach $500B by 2028
- 78% of industry leaders plan to increase AI adoption
- Organizations using AI see 40% improvement in efficiency

## Why This Matters Now

The timing couldn't be more critical. Three converging forces are creating an unprecedented opportunity:

1. **Technological Maturity** — AI models have reached a tipping point in capability and reliability
2. **Market Demand** — Consumers increasingly expect personalized, high-quality experiences
3. **Cost Efficiency** — The economics of AI-powered solutions have become compelling

> "The future belongs to organizations that can blend human creativity with AI efficiency." — Industry Expert

## Practical Implications

For professionals looking to stay ahead, here are the key areas to focus on:

### Embrace Multi-Agent Workflows
Rather than relying on a single tool, the most effective approach combines specialized agents working together — each contributing unique expertise to the final output.

### Invest in Personalization
Data shows that personalized content drives **2.3x higher engagement** compared to generic approaches. The technology to deliver this at scale is now accessible.

### Maintain Human Oversight
While AI handles the heavy lifting in research, drafting, and optimization, human creativity and judgment remain essential for authenticity and brand voice.

## Looking Ahead

The trajectory is clear: organizations that adopt AI-augmented workflows today will have a significant competitive advantage. The key is starting with the right strategy and tools.

**Key Takeaways:**
- AI is augmenting, not replacing, human expertise
- Multi-agent systems deliver superior results
- Early adopters are seeing 60% efficiency gains
- The best implementations combine AI speed with human creativity

---

*Ready to transform your content workflow? Start with a clear strategy, select the right tools, and iterate based on results.*
"""


def _mock_social_content(topic: str, platform: str) -> str:
    if platform == "linkedin":
        return f"""I've been deep-diving into {topic}, and here's what I've learned 🧵

The landscape is changing faster than most realize.

3 key shifts I'm seeing:

1️⃣ AI-powered workflows are becoming the norm, not the exception
2️⃣ Personalization at scale is no longer a "nice to have" — it's expected  
3️⃣ The most successful teams are blending human creativity with AI efficiency

The data backs this up:
📊 78% of leaders are increasing AI investment
📈 2.3x engagement lift with personalized content  
⏱️ 60% reduction in production time

My take? This isn't about replacing human expertise. It's about amplifying it.

The teams that figure this out first will have an unfair advantage.

What's your experience been? I'd love to hear your perspective 👇

#AI #ContentMarketing #Innovation #FutureOfWork #Leadership"""
    else:
        return f"""🧵 Thread: Everything you need to know about {topic}

Let's break it down 👇

1/ The industry is at an inflection point. AI isn't just a buzzword anymore — it's fundamentally changing how we work.

2/ Here's what the data shows:
- 78% of leaders increasing AI investment
- 2.3x engagement with personalized content
- 60% faster production times

3/ But here's the thing most people miss: It's not about AI replacing humans.

It's about AI AUGMENTING humans.

4/ The winning formula?
→ AI handles: Research, drafting, optimization
→ Humans handle: Strategy, creativity, authenticity

5/ Three actions you can take today:
- Start with one AI-powered workflow
- Measure before and after
- Iterate based on results

6/ The teams that embrace this shift now will have a 2-3 year head start.

Don't wait for perfection. Start experimenting today.

What's your take? Reply below 👇"""


def _mock_video_script(topic: str) -> str:
    return f"""# Video Script: {topic}

## HOOK (0:00 - 0:15)
[SPEAKER ON CAMERA - HIGH ENERGY]
"What if I told you that everything you know about {topic} is about to change? Stay with me — by the end of this video, you'll have a completely new perspective."

## INTRO (0:15 - 0:45)
[B-ROLL: tech montage, AI visuals]
"Hey everyone! In today's video, we're diving deep into {topic}. I've spent weeks researching this, and the findings are fascinating."

[GRAPHIC: Title card]

## SECTION 1: THE PROBLEM (0:45 - 2:00)
[SPEAKER ON CAMERA]
"Here's the challenge that most people are facing..."

[SCREEN RECORDING / GRAPHICS]
"The data shows that 78% of professionals are struggling to keep up with the pace of change."

## SECTION 2: THE SOLUTION (2:00 - 4:00)
[SPEAKER ON CAMERA - EXCITED]
"But here's where it gets interesting. A new approach is emerging that's changing everything..."

[GRAPHICS: 3-step process]
"Step 1: Leverage AI for the heavy lifting
Step 2: Apply human creativity and judgment  
Step 3: Iterate and optimize based on data"

## SECTION 3: RESULTS (4:00 - 5:00)
[TESTIMONIAL CLIPS / DATA VISUALIZATION]
"The organizations doing this are seeing incredible results:
- 60% faster production
- 2.3x more engagement
- 40% cost reduction"

## CTA (5:00 - 5:30)
[SPEAKER ON CAMERA - DIRECT]
"If you found this valuable, hit that like button and subscribe. Drop a comment below with YOUR experience. And I'll see you in the next one!"

[END SCREEN: Subscribe graphic]
"""


def _mock_newsletter(topic: str) -> str:
    return f"""# Weekly Insights: {topic}

*Your weekly dose of AI and innovation insights*

---

## 🔥 Top Story

### {topic}: What You Need to Know

The landscape is shifting rapidly. This week, several major developments caught our attention that will shape how we think about this space going forward.

**The TL;DR:**
- AI adoption is accelerating across industries
- Multi-agent systems are emerging as the gold standard
- Early adopters are seeing significant competitive advantages

[Read the full analysis →]

---

## 📊 By The Numbers

| Metric | This Week | Change |
|--------|-----------|--------|
| AI Adoption Rate | 78% | ↑ 12% |
| Content Production Speed | 2.3x faster | ↑ 0.4x |
| Engagement Rates | 40% higher | ↑ 8% |

---

## 💡 Quick Tips

1. **Start small** — Pick one workflow to AI-augment this week
2. **Measure everything** — A/B test AI vs. manual content
3. **Stay human** — Let AI handle efficiency, you handle authenticity

---

## 🔗 Resources We're Loving

- [The State of AI Report 2026] — Comprehensive industry analysis
- [Multi-Agent Systems Guide] — Getting started with CrewAI
- [Content Strategy Framework] — Our battle-tested template

---

*Enjoyed this newsletter? Forward it to a colleague who'd find it valuable.*

*— The Forger Team*
"""


def _mock_podcast_script(topic: str) -> str:
    return f"""# Podcast Episode: {topic}

**Episode Duration:** ~25 minutes
**Format:** Solo / Interview-ready

---

## PRE-SHOW NOTES
- Topic: {topic}
- Key angle: The intersection of AI and practical application
- Target takeaway: Listeners should understand the key trends and have 3 actionable steps

---

## INTRO (0:00 - 2:00)

[THEME MUSIC - 15 sec]

HOST: "Welcome back to the show! I'm your host, and today we're tackling something that's been on everyone's mind — {topic}."

"Before we dive in, if you're enjoying the show, please hit subscribe wherever you're listening. It really helps us reach more people."

"So, let's get into it."

---

## SEGMENT 1: SETTING THE STAGE (2:00 - 8:00)

HOST: "To understand where we're headed, we need to understand where we are."

"Here's the reality: the pace of change in this space is unlike anything we've seen before."

[TALKING POINTS]
- Current market size and growth trajectories
- Key players and their approaches
- Why traditional methods are becoming insufficient
- The 78% statistic and what it means

---

## SEGMENT 2: THE DEEP DIVE (8:00 - 18:00)

HOST: "Now let's get into the meat of it."

[TALKING POINTS]
- Multi-agent AI systems and why they matter
- Real-world case studies and results
- The 2.3x engagement improvement finding
- Common pitfalls and how to avoid them
- The human + AI collaboration model

---

## SEGMENT 3: ACTIONABLE TAKEAWAYS (18:00 - 23:00)

HOST: "Alright, let's bring this home with what you can actually DO with this information."

"Here are three things you can implement this week:"

1. "First, audit your current workflow..."
2. "Second, identify one process that could benefit from AI..."
3. "Third, set up a simple A/B test..."

---

## OUTRO (23:00 - 25:00)

HOST: "That's a wrap for today! Here's what we covered..."

[RECAP KEY POINTS]

"If you found this episode valuable, share it with someone who needs to hear this. And leave us a review — it means the world."

"Until next time, keep creating, keep innovating, and keep pushing forward."

[THEME MUSIC - FADE OUT]

---

## SHOW NOTES
- Episode title: "{topic}"
- Links mentioned: [to be added]
- Related episodes: [to be added]
"""
