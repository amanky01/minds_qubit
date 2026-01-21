import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Head from "next/head";
import { useAuth } from "@/contexts/AuthContext";
import ProtectedRoute from "@/components/ProtectedRoute";
import { agentService, Agent } from "@/services/agentService";
import { authService } from "@/services/authService";
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

  useEffect(() => {
    if (id && typeof id === "string") {
      loadAgent(id);
    }
  }, [id]);

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
      const response = await authService.getAccessToken()
        ? await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000/"}api/v1/agents/${agent.id}/execute`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${authService.getAccessToken()}`,
            },
            body: JSON.stringify({
              message: userMessage,
              conversation_id: conversationId,
            }),
          })
        : null;

      if (!response) {
        throw new Error("Not authenticated");
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        if (response.status === 500) {
          throw new Error("Server error. This might be due to database or API issues. Please try again later.");
        }
        throw new Error(errorData.detail || `Error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      
      if (data.response) {
        setMessages((prev) => [...prev, { role: "assistant", content: data.response }]);
        if (data.conversation_id) {
          setConversationId(data.conversation_id);
        }
      }
    } catch (error: any) {
      console.error("Error sending message:", error);
      let errorMessage = "Sorry, I encountered an error. Please try again.";
      
      if (error.message) {
        if (error.message.includes("Network Error") || error.message.includes("Failed to fetch")) {
          errorMessage = "Unable to connect to the server. Please ensure the backend is running.";
        } else {
          errorMessage = error.message;
        }
      }
      
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: errorMessage },
      ]);
    } finally {
      setLoading(false);
    }
  };

  if (!agent) {
    return (
      <ProtectedRoute>
        <div className={styles.container}>
          <div className={styles.loading}>Loading agent...</div>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <>
        <Head>
          <title>{agent.name} - TheMindSqubit</title>
          <meta name="viewport" content="width=device-width, initial-scale=1" />
        </Head>
        <div className={styles.container}>
          <div className={styles.header}>
            <button onClick={() => router.back()} className={styles.backButton}>
              ← Back
            </button>
            <div className={styles.agentInfo}>
              <span className={styles.agentIcon}>{agent.icon}</span>
              <div>
                <h1>{agent.name}</h1>
                <p>{agent.description}</p>
              </div>
            </div>
          </div>

          <div className={styles.chatContainer}>
            <div className={styles.messages}>
              {messages.length === 0 ? (
                <div className={styles.welcomeMessage}>
                  <p>Start a conversation with {agent.name}!</p>
                  <p className={styles.welcomeSubtext}>{agent.description}</p>
                </div>
              ) : (
                messages.map((msg, index) => (
                  <div
                    key={index}
                    className={`${styles.message} ${
                      msg.role === "user" ? styles.userMessage : styles.assistantMessage
                    }`}
                  >
                    <div className={styles.messageContent}>{msg.content}</div>
                  </div>
                ))
              )}
              {loading && (
                <div className={`${styles.message} ${styles.assistantMessage}`}>
                  <div className={styles.messageContent}>Thinking...</div>
                </div>
              )}
            </div>

            <form onSubmit={handleSendMessage} className={styles.inputForm}>
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder={`Message ${agent.name}...`}
                className={styles.messageInput}
                disabled={loading}
              />
              <button type="submit" className={styles.sendButton} disabled={loading || !message.trim()}>
                Send
              </button>
            </form>
          </div>
        </div>
      </>
    </ProtectedRoute>
  );
}
