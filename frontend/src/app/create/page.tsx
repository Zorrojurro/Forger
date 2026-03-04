"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Navbar from "@/components/Navbar";

const contentTypes = [
    { id: "blog", icon: "article", name: "Blog Post", desc: "SEO-optimized long-form articles designed to rank and engage readers." },
    { id: "linkedin", icon: "work", name: "LinkedIn Post", desc: "Professional updates, networking hooks, and thought leadership content." },
    { id: "twitter", icon: "format_list_numbered", name: "X/Twitter Thread", desc: "Punchy, viral-ready threads formatted for maximum reach and clarity." },
    { id: "video", icon: "videocam", name: "Video Script", desc: "Compelling hook-driven scripts for YouTube, Reels, or TikTok shorts." },
    { id: "newsletter", icon: "mail", name: "Email Newsletter", desc: "Curated updates and direct-to-inbox messaging that drives conversions." },
    { id: "podcast", icon: "mic", name: "Podcast Script", desc: "Structured outlines and show notes for audio-first storytelling." },
];

const tones = ["Professional", "Casual", "Storytelling", "Technical", "Persuasive", "Educational"];
const audiences = ["General Public", "Tech Professionals", "Business Leaders", "Students", "Developers", "Marketing Teams"];

export default function CreatePage() {
    const router = useRouter();
    const [step, setStep] = useState(1);
    const [selectedType, setSelectedType] = useState("blog");
    const [topic, setTopic] = useState("");
    const [tone, setTone] = useState("Professional");
    const [audience, setAudience] = useState("General Public");
    const [keywords, setKeywords] = useState("");
    const [instructions, setInstructions] = useState("");
    const [isGenerating, setIsGenerating] = useState(false);

    const steps = [
        { num: 1, label: "Content Type", icon: "category" },
        { num: 2, label: "Brief", icon: "description" },
        { num: 3, label: "Configure", icon: "settings" },
        { num: 4, label: "Generate", icon: "auto_awesome" },
    ];

    const handleGenerate = async () => {
        setIsGenerating(true);
        try {
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/generate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    content_type: selectedType,
                    topic,
                    tone: tone.toLowerCase(),
                    audience: audience.toLowerCase(),
                    keywords: keywords.split(",").map((k) => k.trim()).filter(Boolean),
                    additional_instructions: instructions,
                }),
            });
            const data = await res.json();
            router.push(`/studio?id=${data.id}&topic=${encodeURIComponent(topic)}`);
        } catch {
            // If backend is down, demo mode — redirect with mock ID
            router.push(`/studio?id=demo-${Date.now()}&topic=${encodeURIComponent(topic)}`);
        }
    };

    return (
        <>
            <Navbar />
            <main className="flex-1 max-w-5xl mx-auto w-full px-6 py-12">
                {/* Stepper */}
                <div className="mb-16">
                    <div className="flex items-start justify-between gap-4 relative">
                        <div className="absolute top-5 left-0 w-full h-0.5 bg-border -z-10 hidden lg:block" />
                        {steps.map((s) => (
                            <div key={s.num} className={`flex flex-col items-center gap-3 flex-1 min-w-[100px] ${s.num > step ? "opacity-40" : ""}`}>
                                <div className={`size-10 rounded-full flex items-center justify-center ${s.num === step
                                    ? "bg-primary text-background glow-amber"
                                    : s.num < step
                                        ? "bg-emerald-500 text-white"
                                        : "bg-surface border border-border text-slate-400"
                                    }`}>
                                    {s.num < step ? (
                                        <span className="material-symbols-outlined text-base">check</span>
                                    ) : (
                                        <span className="material-symbols-outlined text-base">{s.icon}</span>
                                    )}
                                </div>
                                <div className="text-center">
                                    <p className={`text-xs font-bold uppercase tracking-wider ${s.num === step ? "text-primary" : ""}`}>Step {s.num}</p>
                                    <p className="font-semibold text-sm">{s.label}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Step 1: Content Type */}
                {step === 1 && (
                    <div>
                        <h1 className="text-4xl lg:text-5xl font-black mb-4 tracking-tight">
                            What are we <span className="text-gradient">creating today?</span>
                        </h1>
                        <p className="text-slate-400 text-lg max-w-2xl mb-10">
                            Select the format of your content. Our AI models are optimized specifically for each channel&apos;s best practices.
                        </p>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
                            {contentTypes.map((type) => (
                                <button
                                    key={type.id}
                                    onClick={() => setSelectedType(type.id)}
                                    className={`glass-card p-6 text-left transition-all group relative ${selectedType === type.id ? "!border-primary bg-primary/5" : ""
                                        }`}
                                >
                                    <div className="size-12 rounded-lg bg-primary/20 text-primary flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                                        <span className="material-symbols-outlined text-3xl">{type.icon}</span>
                                    </div>
                                    <h3 className="text-xl font-bold mb-2">{type.name}</h3>
                                    <p className="text-slate-400 text-sm leading-relaxed">{type.desc}</p>
                                    {selectedType === type.id && (
                                        <span className="material-symbols-outlined text-primary absolute top-4 right-4">check_circle</span>
                                    )}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* Step 2: Brief */}
                {step === 2 && (
                    <div>
                        <h1 className="text-4xl font-black mb-4 tracking-tight">
                            Tell us about your <span className="text-gradient">content</span>
                        </h1>
                        <p className="text-slate-400 text-lg mb-10">
                            Provide a topic or brief. The more detail you give, the better the output.
                        </p>
                        <div className="glass-card p-8 mb-8">
                            <label className="block text-sm font-bold text-primary mb-3">Topic / Brief *</label>
                            <textarea
                                value={topic}
                                onChange={(e) => setTopic(e.target.value)}
                                placeholder="e.g., Write about the future of AI in content marketing, how it's changing the industry, and what marketers should prepare for..."
                                className="w-full bg-surface border border-border rounded-xl p-4 text-white min-h-[160px] resize-y focus:border-primary focus:outline-none transition-colors placeholder:text-slate-600"
                            />
                            <p className="text-xs text-slate-500 mt-2">{topic.length} characters</p>
                        </div>
                        <div className="glass-card p-8">
                            <label className="block text-sm font-bold text-primary mb-3">SEO Keywords (comma separated)</label>
                            <input
                                type="text"
                                value={keywords}
                                onChange={(e) => setKeywords(e.target.value)}
                                placeholder="e.g., AI marketing, content strategy, automation"
                                className="w-full bg-surface border border-border rounded-xl p-4 text-white focus:border-primary focus:outline-none transition-colors placeholder:text-slate-600"
                            />
                        </div>
                    </div>
                )}

                {/* Step 3: Configure */}
                {step === 3 && (
                    <div>
                        <h1 className="text-4xl font-black mb-4 tracking-tight">
                            Fine-tune your <span className="text-gradient">preferences</span>
                        </h1>
                        <p className="text-slate-400 text-lg mb-10">Configure tone, audience, and any special instructions.</p>
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                            <div className="glass-card p-8">
                                <label className="block text-sm font-bold text-primary mb-4">Tone of Voice</label>
                                <div className="grid grid-cols-2 gap-3">
                                    {tones.map((t) => (
                                        <button
                                            key={t}
                                            onClick={() => setTone(t)}
                                            className={`px-4 py-3 rounded-lg text-sm font-semibold transition-all ${tone === t
                                                ? "bg-primary text-background"
                                                : "bg-surface border border-border text-slate-300 hover:border-primary/50"
                                                }`}
                                        >
                                            {t}
                                        </button>
                                    ))}
                                </div>
                            </div>
                            <div className="glass-card p-8">
                                <label className="block text-sm font-bold text-primary mb-4">Target Audience</label>
                                <div className="grid grid-cols-2 gap-3">
                                    {audiences.map((a) => (
                                        <button
                                            key={a}
                                            onClick={() => setAudience(a)}
                                            className={`px-4 py-3 rounded-lg text-sm font-semibold transition-all ${audience === a
                                                ? "bg-primary text-background"
                                                : "bg-surface border border-border text-slate-300 hover:border-primary/50"
                                                }`}
                                        >
                                            {a}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                        <div className="glass-card p-8">
                            <label className="block text-sm font-bold text-primary mb-3">Additional Instructions</label>
                            <textarea
                                value={instructions}
                                onChange={(e) => setInstructions(e.target.value)}
                                placeholder="Any special requirements, references, or constraints..."
                                className="w-full bg-surface border border-border rounded-xl p-4 text-white min-h-[100px] resize-y focus:border-primary focus:outline-none transition-colors placeholder:text-slate-600"
                            />
                        </div>
                    </div>
                )}

                {/* Step 4: Review & Generate */}
                {step === 4 && (
                    <div>
                        <h1 className="text-4xl font-black mb-4 tracking-tight">
                            Review & <span className="text-gradient">Generate</span>
                        </h1>
                        <p className="text-slate-400 text-lg mb-10">Everything looks good? Hit generate and our AI crew will get to work.</p>
                        <div className="glass-card p-8 mb-8">
                            <h3 className="text-lg font-bold text-primary mb-4">Summary</h3>
                            <div className="grid grid-cols-2 gap-4 text-sm">
                                <div><span className="text-slate-400">Content Type:</span> <span className="font-semibold ml-2">{contentTypes.find((c) => c.id === selectedType)?.name}</span></div>
                                <div><span className="text-slate-400">Tone:</span> <span className="font-semibold ml-2">{tone}</span></div>
                                <div><span className="text-slate-400">Audience:</span> <span className="font-semibold ml-2">{audience}</span></div>
                                <div><span className="text-slate-400">Keywords:</span> <span className="font-semibold ml-2">{keywords || "None"}</span></div>
                            </div>
                            <div className="mt-4 pt-4 border-t border-border">
                                <span className="text-slate-400 text-sm">Topic:</span>
                                <p className="mt-1 font-medium">{topic || "No topic provided"}</p>
                            </div>
                        </div>
                        <div className="glass-card p-8 text-center">
                            <div className="size-20 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-6">
                                <span className="material-symbols-outlined text-primary text-4xl">rocket_launch</span>
                            </div>
                            <h3 className="text-xl font-bold mb-2">Ready to Generate?</h3>
                            <p className="text-slate-400 text-sm mb-6">4 AI agents will collaborate to create your content in under 60 seconds.</p>
                            <button
                                onClick={handleGenerate}
                                disabled={isGenerating}
                                className="btn-primary text-lg inline-flex items-center gap-3 disabled:opacity-50"
                            >
                                {isGenerating ? (
                                    <>
                                        <span className="material-symbols-outlined animate-spin">progress_activity</span>
                                        Launching Agents...
                                    </>
                                ) : (
                                    <>
                                        <span className="material-symbols-outlined">auto_awesome</span>
                                        Generate Content
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                )}

                {/* Navigation */}
                <div className="flex items-center justify-between pt-10 border-t border-border mt-12">
                    {step > 1 ? (
                        <button onClick={() => setStep(step - 1)} className="flex items-center gap-2 px-6 py-3 text-sm font-bold text-slate-400 hover:text-white transition-colors">
                            <span className="material-symbols-outlined">arrow_back</span>
                            Previous
                        </button>
                    ) : (
                        <div />
                    )}
                    {step < 4 && (
                        <button
                            onClick={() => setStep(step + 1)}
                            disabled={step === 2 && !topic.trim()}
                            className="btn-primary flex items-center gap-3 disabled:opacity-40"
                        >
                            Next Step
                            <span className="material-symbols-outlined">arrow_forward</span>
                        </button>
                    )}
                </div>
            </main>
        </>
    );
}
