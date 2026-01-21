import Head from "next/head";
import { useState, useEffect } from "react";
import styles from "@/styles/Home.module.css";
import Header from "@/components/Header";
import Hero from "@/components/Hero";
import CategoryFilter from "@/components/CategoryFilter";
import AgentsGrid from "@/components/AgentsGrid";
import About from "@/components/About";
import Footer from "@/components/Footer";
import { Agent } from "@/data/aiAgents";
import { agentService } from "@/services/agentService";

export default function Home() {
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [allAgents, setAllAgents] = useState<Agent[]>([]);
  const [categories, setCategories] = useState<string[]>(["All"]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        setLoading(true);
        setError(null);
        const [agentsData, categoriesData] = await Promise.all([
          agentService.getAllAgents(),
          agentService.getCategories()
        ]);
        setAllAgents(agentsData);
        setCategories(["All", ...categoriesData]);
      } catch (err: any) {
        // Use the error message from the service (already formatted)
        const errorMessage = err?.message || "Failed to load agents. Please ensure the backend server is running.";
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchAgents();
  }, []);

  const filteredAgents = selectedCategory === "All" 
    ? allAgents 
    : allAgents.filter(agent => agent.category === selectedCategory);

  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category);
  };

  const handleAgentClick = (agent: Agent) => {
    setSelectedAgent(agent);
    
    // Navigate to blog page for TechBlog agent
    if (agent.id === "techblog" || agent.name === "TechBlog") {
      window.location.href = "/blog";
      return;
    }
    
    // For other agents, navigate to agent page (will require auth)
    // The AgentCard component handles auth check
  };

  if (loading) {
    return (
      <>
        <Head>
          <title>TheMindSqubit - AI Agents Platform</title>
          <meta name="description" content="Discover powerful AI agents to help you with various tasks" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <link rel="icon" href="/favicon.ico" />
        </Head>
        <div className={styles.container}>
          <Header />
          <div style={{ padding: "2rem", textAlign: "center" }}>
            <p>Loading agents...</p>
          </div>
        </div>
      </>
    );
  }

  if (error) {
    return (
      <>
        <Head>
          <title>TheMindSqubit - AI Agents Platform</title>
          <meta name="description" content="Discover powerful AI agents to help you with various tasks" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <link rel="icon" href="/favicon.ico" />
        </Head>
        <div className={styles.container}>
          <Header />
          <div style={{ 
            padding: "3rem 2rem", 
            textAlign: "center",
            maxWidth: "600px",
            margin: "0 auto"
          }}>
            <div style={{
              background: "#fff3cd",
              border: "1px solid #ffc107",
              borderRadius: "8px",
              padding: "1.5rem",
              marginBottom: "1rem"
            }}>
              <h2 style={{ 
                color: "#856404", 
                marginTop: 0,
                marginBottom: "0.5rem",
                fontSize: "1.25rem"
              }}>
                ⚠️ Connection Issue
              </h2>
              <p style={{ 
                color: "#856404", 
                margin: 0,
                lineHeight: "1.6"
              }}>
                {error}
              </p>
            </div>
            <div style={{ marginTop: "1.5rem" }}>
              <button 
                onClick={() => window.location.reload()} 
                style={{
                  background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  color: "white",
                  border: "none",
                  padding: "0.75rem 2rem",
                  borderRadius: "8px",
                  fontSize: "1rem",
                  fontWeight: 600,
                  cursor: "pointer"
                }}
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Head>
        <title>TheMindSqubit - AI Agents Platform</title>
        <meta name="description" content="Discover powerful AI agents to help you with various tasks" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      
      <div className={styles.container}>
        <Header />
        <Hero aiAgents={allAgents} />
        <CategoryFilter 
          categories={categories}
          selectedCategory={selectedCategory}
          onCategoryChange={handleCategoryChange}
        />
        <AgentsGrid 
          agents={filteredAgents}
          onAgentClick={handleAgentClick}
        />
        <About />
        <Footer />
      </div>
    </>
  );
}
