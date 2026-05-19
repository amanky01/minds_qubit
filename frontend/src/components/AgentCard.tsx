import { useRouter } from 'next/router';
import { useAuth } from '@/contexts/AuthContext';
import type { Agent } from "@/services/agentService";
import styles from '@/styles/Home.module.css';

interface AgentCardProps {
  agent: Agent;
  onClick: (agent: Agent) => void;
}

export default function AgentCard({ agent, onClick }: AgentCardProps) {
  const router = useRouter();
  const { isAuthenticated } = useAuth();

  const handleTryAgent = (e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (!isAuthenticated) {
      router.push(`/login?redirect=${encodeURIComponent(`/agent/${agent.id}`)}`);
      return;
    }
    
    router.push(`/agent/${agent.id}`);
  };

  return (
    <div 
      className={styles.agentCard}
      onClick={() => onClick(agent)}
    >
      <div className={styles.agentIcon}>{agent.icon}</div>
      <h3>{agent.name}</h3>
      <p>{agent.description}</p>
      <div className={styles.agentCategory}>{agent.category}</div>
      <div className={styles.agentFeatures}>
        {agent.features.slice(0, 2).map((feature, index) => (
          <span key={index} className={styles.featureTag}>
            {feature}
          </span>
        ))}
      </div>
      <button 
        className={styles.agentButton}
        onClick={handleTryAgent}
      >
        Try Agent
      </button>
    </div>
  );
} 