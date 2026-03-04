"use client";

import { useState } from "react";
import Navbar from "@/components/Navbar";

interface ContentItem {
    id: string;
    title: string;
    type: string;
    typeColor: string;
    words: number;
    date: string;
    snippet: string;
}

const MOCK_CONTENT: ContentItem[] = [
    { id: "1", title: "The Future of AI in Marketing", type: "BLOG POST", typeColor: "bg-primary", words: 1204, date: "2h ago", snippet: "Explore how generative models are reshaping the landscape of digital..." },
    { id: "2", title: "10 Tips for Better Productivity", type: "SOCIAL MEDIA", typeColor: "bg-blue-500", words: 450, date: "Oct 24", snippet: "A thread series designed for Twitter and LinkedIn focusing on high-impact daily..." },
    { id: "3", title: "Podcast: The Web3 Myth", type: "SCRIPTS", typeColor: "bg-emerald-500", words: 890, date: "Oct 22", snippet: "Intro and outro scripts for a 30-minute podcast episode discussing the realities o..." },
    { id: "4", title: "Weekly Tech Roundup #42", type: "NEWSLETTER", typeColor: "bg-pink-500", words: 1560, date: "Oct 20", snippet: "A curated summary of the most important tech news from the past week, formatted..." },
    { id: "5", title: "Sustainable Living 101", type: "BLOG POST", typeColor: "bg-primary", words: 2100, date: "Oct 18", snippet: "Beginner-friendly guide to reducing carbon footprint through small, manageable daily..." },
    { id: "6", title: "New Product Launch Teaser", type: "SOCIAL MEDIA", typeColor: "bg-blue-500", words: 210, date: "Oct 15", snippet: "Copywriting for Instagram posts and stories to build anticipation for the upcoming v2..." },
];

const FILTERS = ["All", "Blog Posts", "Social Media", "Scripts", "Newsletters"];
const SIDEBAR_ITEMS = [
    { icon: "folder", label: "My Content", active: true },
    { icon: "group", label: "Shared", active: false },
    { icon: "draft", label: "Drafts", active: false },
    { icon: "star", label: "Favorites", active: false },
];

export default function LibraryPage() {
    const [activeFilter, setActiveFilter] = useState("All");
    const [searchQuery, setSearchQuery] = useState("");

    const filteredContent = MOCK_CONTENT.filter((item) => {
        const matchesFilter = activeFilter === "All" || item.type.toLowerCase().includes(activeFilter.toLowerCase().slice(0, -1));
        const matchesSearch = !searchQuery || item.title.toLowerCase().includes(searchQuery.toLowerCase());
        return matchesFilter && matchesSearch;
    });

    return (
        <>
            <Navbar />
            <main className="flex-1 flex">
                {/* Sidebar */}
                <aside className="hidden lg:flex flex-col w-64 border-r border-border p-6 gap-2">
                    {SIDEBAR_ITEMS.map((item) => (
                        <button
                            key={item.label}
                            className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all ${item.active
                                    ? "bg-primary/10 text-primary border border-primary/20"
                                    : "text-slate-400 hover:text-white hover:bg-surface-light"
                                }`}
                        >
                            <span className="material-symbols-outlined text-lg">{item.icon}</span>
                            {item.label}
                        </button>
                    ))}

                    {/* Usage Stats */}
                    <div className="mt-auto glass-card p-5">
                        <p className="text-xs font-bold text-primary uppercase mb-2">Usage Stats</p>
                        <p className="text-3xl font-black">47</p>
                        <p className="text-xs text-slate-400">pieces generated</p>
                        <div className="mt-3 w-full h-2 bg-surface rounded-full overflow-hidden">
                            <div className="h-full bg-primary rounded-full" style={{ width: "47%" }} />
                        </div>
                        <p className="text-xs text-slate-500 mt-1">Monthly limit: 100 pieces</p>
                    </div>
                </aside>

                {/* Main Content */}
                <div className="flex-1 p-6 lg:p-8">
                    {/* Top bar */}
                    <div className="flex items-center gap-4 mb-6">
                        <div className="flex-1 relative">
                            <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">search</span>
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                placeholder="Search your library..."
                                className="w-full bg-surface border border-border rounded-xl pl-12 pr-4 py-3 text-white focus:border-primary focus:outline-none transition-colors placeholder:text-slate-600"
                            />
                        </div>
                        <button className="btn-primary flex items-center gap-2 whitespace-nowrap" onClick={() => window.location.href = "/create"}>
                            <span className="material-symbols-outlined text-lg">add</span>
                            Create New
                        </button>
                    </div>

                    {/* Filters */}
                    <div className="flex items-center gap-2 mb-8">
                        {FILTERS.map((filter) => (
                            <button
                                key={filter}
                                onClick={() => setActiveFilter(filter)}
                                className={`px-4 py-2 rounded-full text-sm font-semibold transition-all ${activeFilter === filter
                                        ? "bg-primary text-background"
                                        : "bg-surface border border-border text-slate-400 hover:text-white hover:border-primary/40"
                                    }`}
                            >
                                {filter}
                            </button>
                        ))}
                    </div>

                    {/* Content Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {filteredContent.map((item) => (
                            <div key={item.id} className="glass-card p-6 group cursor-pointer hover:border-primary/30 transition-all">
                                <div className="flex items-center justify-between mb-3">
                                    <span className={`px-3 py-1 rounded-full text-xs font-bold text-white ${item.typeColor}`}>{item.type}</span>
                                    <span className="text-xs text-slate-500">{item.date}</span>
                                </div>
                                <h3 className="text-lg font-bold mb-2 group-hover:text-primary transition-colors">{item.title}</h3>
                                <p className="text-slate-400 text-sm mb-4 line-clamp-2">{item.snippet}</p>
                                <div className="flex items-center justify-between">
                                    <span className="text-xs text-slate-500 flex items-center gap-1">
                                        <span className="material-symbols-outlined text-sm">description</span>
                                        {item.words.toLocaleString()} words
                                    </span>
                                    <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button className="p-2 hover:bg-primary/10 rounded-lg transition-colors" title="Edit">
                                            <span className="material-symbols-outlined text-lg text-slate-400 hover:text-primary">edit</span>
                                        </button>
                                        <button className="p-2 hover:bg-primary/10 rounded-lg transition-colors" title="Copy">
                                            <span className="material-symbols-outlined text-lg text-slate-400 hover:text-primary">content_copy</span>
                                        </button>
                                        <button className="p-2 hover:bg-primary/10 rounded-lg transition-colors" title="Share">
                                            <span className="material-symbols-outlined text-lg text-slate-400 hover:text-primary">share</span>
                                        </button>
                                        <button className="p-2 hover:bg-red-500/10 rounded-lg transition-colors" title="Delete">
                                            <span className="material-symbols-outlined text-lg text-slate-400 hover:text-red-400">delete</span>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Load More */}
                    <div className="text-center mt-10">
                        <button className="btn-outline flex items-center gap-2 mx-auto">
                            Load More Content
                            <span className="material-symbols-outlined text-lg">expand_more</span>
                        </button>
                    </div>
                </div>
            </main>
        </>
    );
}
