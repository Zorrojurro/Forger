"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navLinks = [
    { href: "/", label: "Dashboard", icon: "dashboard" },
    { href: "/create", label: "Create", icon: "add_circle" },
    { href: "/library", label: "Library", icon: "folder_open" },
    { href: "/social", label: "Social Hub", icon: "share" },
];

export default function Navbar() {
    const pathname = usePathname();

    return (
        <header className="flex items-center justify-between border-b border-primary/10 px-6 py-4 lg:px-12 bg-background/50 backdrop-blur-md sticky top-0 z-50">
            <Link href="/" className="flex items-center gap-3">
                <div className="size-10 bg-gradient-to-br from-primary to-amber-600 rounded-lg flex items-center justify-center text-background">
                    <span className="material-symbols-outlined font-bold">edit_square</span>
                </div>
                <h2 className="text-xl font-black tracking-tight uppercase">
                    <span className="text-primary">Forger</span>
                </h2>
            </Link>

            <nav className="hidden md:flex items-center gap-1">
                {navLinks.map((link) => (
                    <Link
                        key={link.href}
                        href={link.href}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${pathname === link.href
                            ? "text-primary bg-primary/10"
                            : "text-slate-400 hover:text-white hover:bg-surface-light"
                            }`}
                    >
                        <span className="material-symbols-outlined text-lg">{link.icon}</span>
                        {link.label}
                    </Link>
                ))}
            </nav>

            <div className="flex items-center gap-4">
                <Link href="/create" className="btn-primary text-sm flex items-center gap-2">
                    <span className="material-symbols-outlined text-lg">bolt</span>
                    New Content
                </Link>
                <div className="h-10 w-10 rounded-full border-2 border-primary/30 bg-surface flex items-center justify-center">
                    <span className="material-symbols-outlined text-primary">person</span>
                </div>
            </div>
        </header>
    );
}
