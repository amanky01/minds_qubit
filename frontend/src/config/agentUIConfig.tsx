// frontend/src/config/agentUIConfig.ts
//
// ─────────────────────────────────────────────────────────────
//  HOW TO ADD A NEW AGENT'S VISUAL IDENTITY
//  1. Drop an image into  frontend/public/agents/<agentid>.png
//  2. Add one entry below using the agent's id as the key
//  3. That's it — no other file needs to change
// ─────────────────────────────────────────────────────────────

export interface AgentUIConfig {
    /** Path relative to /public  e.g. "/agents/codecraft.png" */
    bannerImage: string;
    /** Primary accent colour for this agent (hex) */
    accentColor: string;
    /** Secondary / glow colour used in gradients */
    accentSecondary: string;
    /** Full CSS gradient string for the banner background */
    bgGradient: string;
    /** One-line tagline shown under the agent name in the banner */
    tagline: string;
    /** Particle / decorative emoji shown floating in the banner */
    decorativeIcon: string;
}

// ── Per-agent configs ──────────────────────────────────────────
export const agentUIConfig: Record<string, AgentUIConfig> = {
    codecraft: {
        bannerImage: "/agents/codecraft.png",
        accentColor: "#00d4ff",
        accentSecondary: "#0099cc",
        bgGradient: "linear-gradient(135deg, #020c14 0%, #041e2e 50%, #062840 100%)",
        tagline: "Write · Debug · Optimise",
        decorativeIcon: "⌨️",
    },

    dataviz: {
        bannerImage: "/agents/dataviz.png",
        accentColor: "#06b6d4",
        accentSecondary: "#0891b2",
        bgGradient: "linear-gradient(135deg, #020e14 0%, #041c24 50%, #062030 100%)",
        tagline: "Analyse · Visualise · Discover",
        decorativeIcon: "📈",
    },

    contentcreator: {
        bannerImage: "/agents/contentcreator.png",
        accentColor: "#ec4899",
        accentSecondary: "#be185d",
        bgGradient: "linear-gradient(135deg, #140210 0%, #240418 50%, #2e0620 100%)",
        tagline: "Create · Inspire · Publish",
        decorativeIcon: "🖊️",
    },

    designmaster: {
        bannerImage: "/agents/designmaster.png",
        accentColor: "#a855f7",
        accentSecondary: "#7c3aed",
        bgGradient: "linear-gradient(135deg, #0e0214 0%, #1a0424 50%, #22062e 100%)",
        tagline: "Design · Brand · Wow",
        decorativeIcon: "🎨",
    },

    researchpro: {
        bannerImage: "/agents/researchpro.png",
        accentColor: "#f59e0b",
        accentSecondary: "#d97706",
        bgGradient: "linear-gradient(135deg, #140e02 0%, #241804 50%, #2e2006 100%)",
        tagline: "Search · Verify · Report",
        decorativeIcon: "🔬",
    },

    languagetutor: {
        bannerImage: "/agents/languagetutor.png",
        accentColor: "#34d399",
        accentSecondary: "#059669",
        bgGradient: "linear-gradient(135deg, #021408 0%, #04240e 50%, #062e12 100%)",
        tagline: "Learn · Practice · Fluency",
        decorativeIcon: "🌐",
    },

    techblog: {
        bannerImage: "/agents/techblog.png",
        accentColor: "#818cf8",
        accentSecondary: "#4f46e5",
        bgGradient: "linear-gradient(135deg, #06020e 0%, #0e0420 50%, #12062a 100%)",
        tagline: "Read · Write · Explore Tech",
        decorativeIcon: "📰",
    },
};

// ── Fallback used when an agent has no entry above ─────────────
export const defaultAgentUIConfig: AgentUIConfig = {
    bannerImage: "",
    accentColor: "#00d4ff",
    accentSecondary: "#7c3aed",
    bgGradient: "linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%)",
    tagline: "Powered by AI",
    decorativeIcon: "🤖",
};