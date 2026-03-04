"use client";

import Link from "next/link";
import Navbar from "@/components/Navbar";

const agents = [
  {
    icon: "search",
    name: "Researcher",
    description: "Gathers data and insights on your topic using web scraping and analysis",
    color: "from-blue-500 to-cyan-400",
  },
  {
    icon: "edit_note",
    name: "Writer",
    description: "Crafts compelling content based on research and your brand voice",
    color: "from-primary to-amber-400",
  },
  {
    icon: "spellcheck",
    name: "Editor",
    description: "Reviews tone, grammar, and structure for polished output",
    color: "from-emerald-500 to-green-400",
  },
  {
    icon: "trending_up",
    name: "SEO Optimizer",
    description: "Adds keywords, meta tags, and hashtags for maximum reach",
    color: "from-purple-500 to-pink-400",
  },
];

const contentTypes = [
  { icon: "article", name: "Blog Posts", desc: "SEO-optimized articles" },
  { icon: "work", name: "LinkedIn", desc: "Professional updates" },
  { icon: "tag", name: "X Threads", desc: "Viral-ready threads" },
  { icon: "videocam", name: "Video Scripts", desc: "Hook-driven scripts" },
  { icon: "mail", name: "Newsletters", desc: "Email campaigns" },
  { icon: "mic", name: "Podcasts", desc: "Show notes & outlines" },
];

const stats = [
  { value: "4", label: "AI Agents" },
  { value: "6", label: "Content Types" },
  { value: "< 60s", label: "Generation Time" },
  { value: "100%", label: "Customizable" },
];

export default function HomePage() {
  return (
    <>
      <Navbar />
      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative max-w-6xl mx-auto px-6 pt-20 pb-16 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-8">
            <span className="material-symbols-outlined text-primary text-sm">auto_awesome</span>
            <span className="text-primary text-sm font-semibold">Powered by Multi-Agent AI</span>
          </div>
          <h1 className="text-5xl lg:text-7xl font-black tracking-tight mb-6 leading-tight">
            Create Stunning Content
            <br />
            <span className="text-gradient">with AI Agents</span>
          </h1>
          <p className="text-slate-400 text-lg lg:text-xl max-w-3xl mx-auto mb-10 leading-relaxed">
            Multiple specialized AI agents collaborate — researcher, writer, editor,
            SEO optimizer — to generate personalized content from a simple brief.
          </p>
          <div className="flex items-center justify-center gap-4 mb-16">
            <Link href="/create" className="btn-primary text-lg flex items-center gap-3 px-10 py-5">
              <span className="material-symbols-outlined">bolt</span>
              Start Creating
            </Link>
            <Link href="/library" className="btn-outline text-lg flex items-center gap-3 px-8 py-5">
              <span className="material-symbols-outlined">play_circle</span>
              See Examples
            </Link>
          </div>

          {/* Stats bar */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-3xl mx-auto">
            {stats.map((stat) => (
              <div key={stat.label} className="glass-card p-4 text-center">
                <p className="text-2xl font-black text-primary">{stat.value}</p>
                <p className="text-xs text-slate-400 mt-1">{stat.label}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Agent Pipeline */}
        <section className="max-w-6xl mx-auto px-6 py-16">
          <h2 className="text-3xl font-black text-center mb-4">
            Meet Your <span className="text-gradient">AI Crew</span>
          </h2>
          <p className="text-slate-400 text-center max-w-2xl mx-auto mb-12">
            Four specialized agents work in sequence, each refining the output of the previous one.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {agents.map((agent, i) => (
              <div key={agent.name} className="glass-card p-6 relative group">
                <div className="flex items-center gap-3 mb-4">
                  <div className={`size-12 rounded-xl bg-gradient-to-br ${agent.color} flex items-center justify-center opacity-90`}>
                    <span className="material-symbols-outlined text-white text-2xl">{agent.icon}</span>
                  </div>
                  <span className="text-xs font-bold text-slate-500 uppercase">Agent {i + 1}</span>
                </div>
                <h3 className="text-lg font-bold mb-2">{agent.name}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{agent.description}</p>
                {i < 3 && (
                  <div className="hidden lg:block absolute -right-4 top-1/2 -translate-y-1/2 z-10">
                    <span className="material-symbols-outlined text-primary/40 text-2xl">arrow_forward</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* Content Types */}
        <section className="max-w-6xl mx-auto px-6 py-16">
          <h2 className="text-3xl font-black text-center mb-4">
            Generate <span className="text-gradient">Any Content Type</span>
          </h2>
          <p className="text-slate-400 text-center max-w-2xl mx-auto mb-12">
            Each content type is optimized with platform-specific best practices.
          </p>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {contentTypes.map((type) => (
              <div key={type.name} className="glass-card p-5 text-center group cursor-pointer hover:border-primary/40 transition-all">
                <div className="size-12 rounded-lg bg-primary/10 text-primary flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
                  <span className="material-symbols-outlined text-2xl">{type.icon}</span>
                </div>
                <h4 className="font-bold text-sm mb-1">{type.name}</h4>
                <p className="text-xs text-slate-500">{type.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* CTA Section */}
        <section className="max-w-4xl mx-auto px-6 py-20 text-center">
          <div className="glass-card p-12 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-primary/5 via-transparent to-primary/5" />
            <h2 className="text-3xl font-black mb-4 relative">Ready to <span className="text-gradient">Transform</span> Your Content?</h2>
            <p className="text-slate-400 mb-8 relative">Start generating professional content in under 60 seconds.</p>
            <Link href="/create" className="btn-primary text-lg relative inline-flex items-center gap-3">
              <span className="material-symbols-outlined">rocket_launch</span>
              Get Started Free
            </Link>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-border px-6 py-8">
          <div className="max-w-6xl mx-auto flex items-center justify-between">
            <p className="text-slate-500 text-sm">© 2026 Forger. Powered by CrewAI & LangGraph.</p>
            <div className="flex items-center gap-6 text-slate-500 text-sm">
              <a href="#" className="hover:text-primary transition-colors">Documentation</a>
              <a href="#" className="hover:text-primary transition-colors">API</a>
              <a href="#" className="hover:text-primary transition-colors">GitHub</a>
            </div>
          </div>
        </footer>
      </main>
    </>
  );
}
