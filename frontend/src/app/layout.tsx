import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Forger — AI Content Creator",
  description: "Multiple specialized AI agents collaborate to generate personalized content from a simple brief. Powered by CrewAI & LangGraph.",
  keywords: ["AI", "content creator", "multi-agent", "CrewAI", "LangGraph", "blog generator", "social media"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap"
          rel="stylesheet"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-background font-display text-slate-100 min-h-screen antialiased">
        <div className="relative flex flex-col w-full min-h-screen overflow-x-hidden bg-mesh">
          {children}
        </div>
      </body>
    </html>
  );
}
