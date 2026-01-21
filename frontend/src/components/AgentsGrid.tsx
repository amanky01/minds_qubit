import styles from '@/styles/Home.module.css';
import AgentCard from './AgentCard';

interface Agent {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: string;
  features: string[];
}

interface AgentsGridProps {
  agents: Agent[];
  onAgentClick: (agent: Agent) => void;
}

export default function AgentsGrid({ agents, onAgentClick }: AgentsGridProps) {
  return (
    <section id="agents" className={styles.agents}>
      <div className={styles.agentsContent}>
        <h2>AI Agents</h2>
        <div className={styles.agentsGrid}>
          {agents.map(agent => (
            <AgentCard 
              key={agent.id} 
              agent={agent} 
              onClick={onAgentClick}
            />
          ))}
        </div>
      </div>
    </section>
  );
} 