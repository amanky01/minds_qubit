import { useRouter } from 'next/router';
import { useAuth } from '@/contexts/AuthContext';
import styles from '@/styles/Home.module.css';

interface HeroProps {
  aiAgents: Array<{
    id: string;
    icon: string;
  }>;
}

export default function Hero({ aiAgents }: HeroProps) {
  const router = useRouter();
  const { isAuthenticated } = useAuth();

  const handleGetStarted = () => {
    if (isAuthenticated) {
      // Scroll to agents section
      const agentsSection = document.getElementById('agents');
      if (agentsSection) {
        agentsSection.scrollIntoView({ behavior: 'smooth' });
      }
    } else {
      // Redirect to login with current path as redirect
      router.push(`/login?redirect=${encodeURIComponent(router.asPath)}`);
    }
  };

  return (
    <section className={styles.hero}>
      <div className={styles.heroContent}>
        <h1 className={styles.heroTitle}>
          Unleash the Power of
          <span className={styles.highlight}> AI Agents</span>
        </h1>
        <p className={styles.heroSubtitle}>
          Discover specialized AI agents designed to help you accomplish any task. 
          From coding to content creation, we&apos;ve got you covered.
        </p>
        <div className={styles.heroButtons}>
          <button className={styles.primaryButton} onClick={handleGetStarted}>
            Get Started
          </button>
          <button className={styles.secondaryButton}>Learn More</button>
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