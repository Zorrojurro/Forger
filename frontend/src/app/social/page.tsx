"use client";

import { useState } from "react";
import Navbar from "@/components/Navbar";

const CONNECTED_ACCOUNTS = [
    { platform: "LinkedIn", user: "Sarah Jenkins", status: "connected", icon: "LinkedIn" },
    { platform: "X (Twitter)", user: "@sarah_dev", status: "connected", icon: "X" },
];

const SCHEDULE: Record<string, { platform: string; time: string; title: string }[]> = {
    Mon: [{ platform: "LinkedIn", time: "09:00 AM", title: "The future of AI agen..." }],
    Tue: [
        { platform: "X", time: "11:30 AM", title: "Just shipped a..." },
        { platform: "LinkedIn", time: "04:00 PM", title: "How we reduced..." },
    ],
    Wed: [],
    Thu: [{ platform: "X", time: "08:15 AM", title: "AI is not coming fo..." }],
    Fri: [{ platform: "X", time: "10:00 AM", title: "The weekend..." }],
    Sat: [],
    Sun: [],
};

const RECENT_POSTS = [
    { platform: "linkedin", title: "The Rise of Generative AI in Creative...", time: "2 hours ago", likes: 124, comments: 38, shares: 12 },
    { platform: "x", title: "Why prompt engineering is a core skill...", time: "5 hours ago", likes: 852, comments: 142, shares: 56 },
    { platform: "linkedin", title: "Unlocking the power of RAG systems...", time: "Yesterday", likes: 230, comments: 41, shares: 5 },
];

export default function SocialPage() {
    const [postContent, setPostContent] = useState("");
    const [shareLinkedIn, setShareLinkedIn] = useState(true);
    const [shareX, setShareX] = useState(false);

    return (
        <>
            <Navbar />
            <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-8">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-black">Social Hub</h1>
                    <p className="text-slate-400 text-sm mt-1">Manage and schedule your AI-generated content across platforms.</p>
                </div>

                {/* Connected Accounts */}
                <section className="mb-10">
                    <h2 className="text-lg font-bold flex items-center gap-2 mb-4">
                        <span className="material-symbols-outlined text-primary">link</span>
                        Connected Accounts
                    </h2>
                    <div className="flex flex-wrap gap-4">
                        {CONNECTED_ACCOUNTS.map((acc) => (
                            <div key={acc.platform} className="glass-card p-5 flex flex-col items-center gap-3 min-w-[180px]">
                                <div className="size-14 rounded-full bg-surface flex items-center justify-center">
                                    <span className="material-symbols-outlined text-2xl text-primary">{acc.platform === "LinkedIn" ? "work" : "tag"}</span>
                                </div>
                                <p className="font-bold text-sm">{acc.user}</p>
                                <span className="text-xs text-emerald-400 flex items-center gap-1">
                                    <span className="size-2 rounded-full bg-emerald-400 inline-block" />
                                    CONNECTED
                                </span>
                                <button className="btn-outline text-xs py-1 px-3">Manage Account</button>
                            </div>
                        ))}
                        <button className="glass-card p-5 flex flex-col items-center justify-center gap-3 min-w-[180px] border-dashed cursor-pointer hover:border-primary/40">
                            <span className="material-symbols-outlined text-3xl text-slate-500">add</span>
                            <p className="text-sm text-slate-400">Connect Platform</p>
                        </button>
                    </div>
                </section>

                {/* Weekly Schedule */}
                <section className="mb-10">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-bold flex items-center gap-2">
                            <span className="material-symbols-outlined text-primary">calendar_month</span>
                            Weekly Schedule
                        </h2>
                        <div className="flex items-center gap-2">
                            <button className="btn-outline text-xs py-1 px-3">Previous</button>
                            <button className="btn-outline text-xs py-1 px-3">Next Week</button>
                        </div>
                    </div>
                    <div className="grid grid-cols-7 gap-3">
                        {Object.entries(SCHEDULE).map(([day, posts]) => (
                            <div key={day} className="glass-card p-3 min-h-[160px]">
                                <p className={`text-xs font-bold uppercase mb-3 ${day === "Fri" ? "text-primary" : "text-slate-400"}`}>
                                    {day} {day === "Fri" && <span className="text-primary">(Today)</span>}
                                </p>
                                <div className="space-y-2">
                                    {posts.map((post, i) => (
                                        <div
                                            key={i}
                                            className={`p-2 rounded-lg text-xs ${post.platform === "LinkedIn" ? "bg-blue-500/10 border border-blue-500/20" : "bg-surface border border-border"
                                                }`}
                                        >
                                            <p className="text-primary font-bold">{post.platform} • {post.time}</p>
                                            <p className="text-slate-300 mt-1 line-clamp-2">{post.title}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

                {/* Bottom Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Recent Posts */}
                    <section>
                        <h2 className="text-lg font-bold flex items-center gap-2 mb-4">
                            <span className="material-symbols-outlined text-primary">history</span>
                            Recent Posts
                        </h2>
                        <div className="space-y-4">
                            {RECENT_POSTS.map((post, i) => (
                                <div key={i} className="glass-card p-5 flex items-center gap-4">
                                    <div className={`size-10 rounded-lg flex items-center justify-center ${post.platform === "linkedin" ? "bg-blue-500/20 text-blue-400" : "bg-surface text-white"
                                        }`}>
                                        <span className="material-symbols-outlined">{post.platform === "linkedin" ? "work" : "tag"}</span>
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <p className="font-bold text-sm truncate">{post.title}</p>
                                        <p className="text-xs text-slate-500">{post.time}</p>
                                    </div>
                                    <div className="flex items-center gap-4 text-xs">
                                        <div className="text-center">
                                            <p className="text-primary font-bold">{post.likes}</p>
                                            <p className="text-slate-500">{post.platform === "x" ? "LIKES" : "LIKES"}</p>
                                        </div>
                                        <div className="text-center">
                                            <p className="text-primary font-bold">{post.comments}</p>
                                            <p className="text-slate-500">{post.platform === "x" ? "RETWEETS" : "COMMENTS"}</p>
                                        </div>
                                        <div className="text-center">
                                            <p className="text-primary font-bold">{post.shares}</p>
                                            <p className="text-slate-500">{post.platform === "x" ? "REPLIES" : "SHARES"}</p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>

                    {/* Quick Post */}
                    <section>
                        <h2 className="text-lg font-bold flex items-center gap-2 mb-4">
                            <span className="material-symbols-outlined text-primary">edit_square</span>
                            Quick Post
                        </h2>
                        <div className="glass-card p-6">
                            <p className="text-xs font-bold text-primary uppercase mb-3">Compose Draft</p>
                            <textarea
                                value={postContent}
                                onChange={(e) => setPostContent(e.target.value)}
                                placeholder="What's happening today? AI can help you generate ideas..."
                                className="w-full bg-surface border border-border rounded-xl p-4 text-white min-h-[120px] resize-y focus:border-primary focus:outline-none transition-colors placeholder:text-slate-600 text-sm"
                            />
                            <p className="text-xs text-slate-500 mt-2 text-right">{postContent.length} / 280 characters</p>

                            {/* Platform Toggles */}
                            <div className="space-y-3 mt-4">
                                <div className="flex items-center justify-between">
                                    <span className="text-sm flex items-center gap-2">
                                        <span className="material-symbols-outlined text-lg">share</span>
                                        Share on LinkedIn
                                    </span>
                                    <button
                                        onClick={() => setShareLinkedIn(!shareLinkedIn)}
                                        className={`w-12 h-6 rounded-full transition-colors relative ${shareLinkedIn ? "bg-primary" : "bg-surface"}`}
                                    >
                                        <div className={`size-5 rounded-full bg-white absolute top-0.5 transition-all ${shareLinkedIn ? "left-6" : "left-0.5"}`} />
                                    </button>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-sm flex items-center gap-2">
                                        <span className="material-symbols-outlined text-lg">close</span>
                                        Share on X (Twitter)
                                    </span>
                                    <button
                                        onClick={() => setShareX(!shareX)}
                                        className={`w-12 h-6 rounded-full transition-colors relative ${shareX ? "bg-primary" : "bg-surface"}`}
                                    >
                                        <div className={`size-5 rounded-full bg-white absolute top-0.5 transition-all ${shareX ? "left-6" : "left-0.5"}`} />
                                    </button>
                                </div>
                            </div>

                            {/* Buttons */}
                            <div className="space-y-3 mt-6">
                                <button className="btn-primary w-full flex items-center justify-center gap-2">
                                    <span className="material-symbols-outlined">send</span>
                                    Post Now
                                </button>
                                <button className="btn-outline w-full flex items-center justify-center gap-2">
                                    <span className="material-symbols-outlined">schedule</span>
                                    Schedule for Later
                                </button>
                            </div>

                            {/* AI Tip */}
                            <div className="mt-6 bg-primary/5 border border-primary/10 rounded-xl p-4">
                                <p className="text-xs font-bold text-primary flex items-center gap-1">
                                    <span className="material-symbols-outlined text-sm">auto_awesome</span>
                                    AI TIP
                                </p>
                                <p className="text-xs text-slate-400 mt-1 italic">
                                    &quot;Post engagement on X is 25% higher on Fridays at 10:00 AM. Consider scheduling your update then.&quot;
                                </p>
                            </div>
                        </div>
                    </section>
                </div>
            </main>
        </>
    );
}
