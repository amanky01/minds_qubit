import { useRouter } from "next/router";
import styles from "@/styles/Agent.module.css";

interface AgentComingSoonProps {
  agentName: string;
  agentIcon: string;
  accentColor: string;
}

export default function AgentComingSoon({
  agentName,
  agentIcon,
  accentColor,
}: AgentComingSoonProps) {
  const router = useRouter();

  return (
    <div className={styles.comingSoon}>
      <div className={styles.comingSoonIcon} style={{ color: accentColor }}>
        {agentIcon}
      </div>
      <h2 className={styles.comingSoonTitle} style={{ color: accentColor }}>
        Coming soon
      </h2>
      <p className={styles.comingSoonText}>
        {agentName} is not available yet. We&apos;re finishing the integration —
        check back soon or explore agents that are live today.
      </p>
      <button
        type="button"
        className={styles.comingSoonButton}
        style={{
          borderColor: `${accentColor}50`,
          color: accentColor,
        }}
        onClick={() => void router.push({ pathname: "/", hash: "agents" })}
      >
        Browse agents
      </button>
    </div>
  );
}
