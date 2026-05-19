import Link from "next/link";
import { useRouter } from "next/router";
import { useAuth } from "@/contexts/AuthContext";
import styles from "@/styles/Home.module.css";

interface HeroLoggedInProps {
  aiAgents: Array<{
    id: string;
    icon: string;
  }>;
}

export default function HeroLoggedIn({ aiAgents }: HeroLoggedInProps) {
  const router = useRouter();
  const { user } = useAuth();

  const displayName =
    user?.full_name || user?.email?.split("@")[0] || "there";

  const scrollToAgents = () => {
    const section = document.getElementById("agents");
    if (section) {
      section.scrollIntoView({ behavior: "smooth" });
    } else {
      void router.push({ pathname: "/", hash: "agents" });
    }
  };

  return (
    <section className={styles.hero}>
      <div className={styles.heroContent}>
        <h1 className={styles.heroTitle}>
          Welcome back,
          <span className={styles.highlight}> {displayName}</span>
        </h1>
        <p className={styles.heroSubtitle}>
          Pick up where you left off — open your dashboard for plan and usage,
          or jump straight into any agent below.
        </p>
        <div className={styles.heroButtons}>
          <Link href="/dashboard" className={styles.primaryButton}>
            Open dashboard
          </Link>
          <button
            type="button"
            className={styles.secondaryButton}
            onClick={scrollToAgents}
          >
            Browse agents
          </button>
        </div>
      </div>
      <div className={styles.heroVisual}>
        <div className={styles.floatingIcons}>
          {aiAgents.slice(0, 4).map((agent, index) => (
            <div
              key={agent.id}
              className={styles.floatingIcon}
              style={{ animationDelay: `${index * 0.5}s` }}
            >
              {agent.icon}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
