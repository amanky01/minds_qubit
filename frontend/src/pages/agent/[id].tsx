import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/router";
import Head from "next/head";
import { useAuth } from "@/contexts/AuthContext";
import ProtectedRoute from "@/components/ProtectedRoute";
import { agentService, Agent } from "@/services/agentService";
import { authService } from "@/services/authService";
import { agentUIConfig, defaultAgentUIConfig } from "@/config/agentUIConfig";
import styles from "@/styles/Agent.module.css";

export default function AgentPage() {
  const router = useRouter();
  const { id } = router.query;
  const { isAuthenticated } = useAuth();
  const [agent, setAgent] = useState<Agent | null>(null);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (id && typeof id === "string") loadAgent(id);
  }, [id]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const loadAgent = async (agentId: string) => {
    try {
      const agentData = await agentService.getAgentById(agentId);
      setAgent(agentData);
    } catch (error) {
      console.error("Error loading agent:", error);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || !agent || !isAuthenticated) return;

    const userMessage = message.trim();
    setMessage("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    try {
      const token = authService.getAccessToken();
      if (!token) throw new Error("Not authenticated");

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000/"}api/v1/agents/${agent.id}/execute`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ message: userMessage, conversation_id: conversationId }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        if (response.status === 500) throw new Error("Server error. Please try again later.");
        throw new Error(errorData.detail || `Error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      if (data.response) {
        setMessages((prev) => [...prev, { role: "assistant", content: data.response }]);
        if (data.conversation_id) setConversationId(data.conversation_id);
      }
    } catch (error: unknown) {
      let errorMessage = "Sorry, I encountered an error. Please try again.";
      const msg = error instanceof Error ? error.message : "";
      if (msg.includes("Failed to fetch") || msg.includes("Network Error")) {
        errorMessage = "Unable to connect to the server. Please ensure the backend is running.";
      } else if (msg) {
        errorMessage = msg;
      }
      setMessages((prev) => [...prev, { role: "assistant", content: errorMessage }]);
    } finally {
      setLoading(false);
    }
  };

  if (!agent) {
    return (
      <ProtectedRoute>
        <div className={styles.container}>
          <div className={styles.loadingScreen}>
            <div className={styles.loadingDots}><span /><span /><span /></div>
            <p>Loading agent...</p>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  const ui = agentUIConfig[agent.id] || defaultAgentUIConfig;

  return (
    <ProtectedRoute>
      <>
        <Head>
          <title>{agent.name} — TheMindSqubit</title>
          <meta name="viewport" content="width=device-width, initial-scale=1" />
        </Head>

        <div className={styles.container}>

          {/* ══ BANNER ══════════════════════════════════════════ */}
          <div className={styles.banner} style={{ background: ui.bgGradient }}>

            {/* Floating decorative icons */}
            <span className={`${styles.floatIcon} ${styles.fi1}`}>{ui.decorativeIcon}</span>
            <span className={`${styles.floatIcon} ${styles.fi2}`}>{agent.icon}</span>
            <span className={`${styles.floatIcon} ${styles.fi3}`}>{ui.decorativeIcon}</span>

            {/* Back button */}
            <button
              onClick={() => router.back()}
              className={styles.backButton}
              style={{ borderColor: `${ui.accentColor}50`, color: ui.accentColor }}
            >
              ← Back
            </button>

            {/* Agent identity row */}
            <div className={styles.agentIdentity}>

              {/* Banner image – hidden gracefully if file missing */}
              <div
                className={styles.bannerImageWrap}
                style={{ boxShadow: `0 0 40px ${ui.accentColor}40` }}
              >
                {ui.bannerImage ? (
                  <img
                    src={ui.bannerImage}
                    alt={agent.name}
                    className={styles.bannerImg}
                    onError={(e) => {
                      const wrap = (e.target as HTMLImageElement).parentElement;
                      if (wrap) wrap.style.display = "none";
                    }}
                  />
                ) : (
                  <span className={styles.bannerEmoji}>{agent.icon}</span>
                )}
              </div>

              {/* Text info */}
              <div className={styles.agentMeta}>
                <span className={styles.categoryBadge}>{agent.category}</span>
                <h1 className={styles.agentName} style={{ color: ui.accentColor }}>
                  {agent.name}
                </h1>
                <p className={styles.agentTagline}>{ui.tagline}</p>
                <p className={styles.agentDescription}>{agent.description}</p>

                {/* Feature pills */}
                <div className={styles.featurePills}>
                  {agent.features.map((f, i) => (
                    <span
                      key={i}
                      className={styles.featurePill}
                      style={{
                        borderColor: `${ui.accentColor}50`,
                        color: ui.accentColor,
                        background: `${ui.accentColor}15`,
                      }}
                    >
                      {f}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Bottom glow line */}
            <div
              className={styles.bannerGlow}
              style={{
                background: `linear-gradient(90deg, transparent, ${ui.accentColor}80, transparent)`,
              }}
            />
          </div>

          {/* ══ CHAT ════════════════════════════════════════════ */}
          <div className={styles.chatContainer}>
            <div className={styles.messages}>

              {messages.length === 0 ? (
                <div className={styles.welcomeMessage}>
                  <div className={styles.welcomeIcon} style={{ color: ui.accentColor }}>
                    {agent.icon}
                  </div>
                  <p className={styles.welcomeTitle} style={{ color: ui.accentColor }}>
                    Start a conversation with {agent.name}!
                  </p>
                  <p className={styles.welcomeSubtext}>{agent.description}</p>
                </div>
              ) : (
                messages.map((msg, index) => (
                  <div
                    key={index}
                    className={`${styles.message} ${msg.role === "user" ? styles.userMessage : styles.assistantMessage
                      }`}
                  >
                    <div
                      className={styles.messageContent}
                      style={
                        msg.role === "user"
                          ? {
                            background: `linear-gradient(135deg, ${ui.accentColor}, ${ui.accentSecondary})`,
                          }
                          : {}
                      }
                    >
                      {msg.content}
                    </div>
                  </div>
                ))
              )}

              {/* Typing indicator */}
              {loading && (
                <div className={`${styles.message} ${styles.assistantMessage}`}>
                  <div className={styles.messageContent}>
                    <div className={styles.typingDots}>
                      <span style={{ background: ui.accentColor }} />
                      <span style={{ background: ui.accentColor }} />
                      <span style={{ background: ui.accentColor }} />
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <form
              onSubmit={handleSendMessage}
              className={styles.inputForm}
              style={{ borderColor: `${ui.accentColor}30` }}
            >
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder={`Message ${agent.name}...`}
                className={styles.messageInput}
                disabled={loading}
              />
              <button
                type="submit"
                className={styles.sendButton}
                disabled={loading || !message.trim()}
                style={{
                  background: `linear-gradient(135deg, ${ui.accentColor}, ${ui.accentSecondary})`,
                }}
              >
                {loading ? "···" : "Send ➤"}
              </button>
            </form>
          </div>
        </div>
      </>
    </ProtectedRoute>
  );
}
