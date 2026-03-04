// API client for Forger backend
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ContentBrief {
    content_type: string;
    topic: string;
    tone: string;
    audience: string;
    keywords: string[];
    additional_instructions: string;
}

export interface AgentStatus {
    agent: string;
    status: "completed" | "in_progress" | "pending";
    message: string;
    timestamp: string;
}

export interface GenerationResult {
    id: string;
    title: string;
    content: string;
    content_type: string;
    word_count: number;
    seo_meta?: {
        title: string;
        description: string;
        keywords: string[];
    };
    created_at: string;
    agent_log: AgentStatus[];
}

export interface ContentItem {
    id: string;
    title: string;
    content: string;
    content_type: string;
    word_count: number;
    created_at: string;
    snippet: string;
}

export interface SocialPost {
    id: string;
    platform: string;
    title: string;
    content: string;
    scheduled_at?: string;
    posted_at?: string;
    engagement: {
        likes: number;
        comments: number;
        shares: number;
    };
}

export async function generateContent(brief: ContentBrief): Promise<{ id: string }> {
    const res = await fetch(`${API_BASE}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(brief),
    });
    if (!res.ok) throw new Error("Generation failed");
    return res.json();
}

export async function getGenerationStatus(id: string): Promise<{
    progress: number;
    agents: AgentStatus[];
    status: "generating" | "completed" | "error";
}> {
    const res = await fetch(`${API_BASE}/api/generate/${id}/status`);
    if (!res.ok) throw new Error("Failed to get status");
    return res.json();
}

export async function getGenerationResult(id: string): Promise<GenerationResult> {
    const res = await fetch(`${API_BASE}/api/generate/${id}/result`);
    if (!res.ok) throw new Error("Failed to get result");
    return res.json();
}

export async function getContentLibrary(): Promise<ContentItem[]> {
    const res = await fetch(`${API_BASE}/api/library`);
    if (!res.ok) throw new Error("Failed to fetch library");
    return res.json();
}

export async function publishToSocial(contentId: string, platform: string): Promise<SocialPost> {
    const res = await fetch(`${API_BASE}/api/social/post`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content_id: contentId, platform }),
    });
    if (!res.ok) throw new Error("Failed to publish");
    return res.json();
}

export async function getSocialPosts(): Promise<SocialPost[]> {
    const res = await fetch(`${API_BASE}/api/social/posts`);
    if (!res.ok) throw new Error("Failed to get posts");
    return res.json();
}

export async function healthCheck(): Promise<{ status: string }> {
    const res = await fetch(`${API_BASE}/api/health`);
    return res.json();
}
