import styles from '@/styles/Home.module.css';

export default function About() {
  return (
    <section id="about" className={styles.about}>
      <div className={styles.aboutContent}>
        <h2>About TheMindSqubit</h2>
        <p>
          TheMindSqubit is a cutting-edge platform that brings together specialized AI agents 
          to help you accomplish any task. Our agents are designed with specific expertise 
          and can work together to solve complex problems.
        </p>
        <div className={styles.stats}>
          <div className={styles.stat}>
            <h3>6+</h3>
            <p>AI Agents</p>
          </div>
          <div className={styles.stat}>
            <h3>24/7</h3>
            <p>Availability</p>
          </div>
          <div className={styles.stat}>
            <h3>100%</h3>
            <p>AI Powered</p>
          </div>
        </div>
      </div>
    </section>
  );
} 