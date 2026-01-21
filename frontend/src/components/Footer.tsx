import styles from '@/styles/Home.module.css';

export default function Footer() {
  return (
    <footer id="contact" className={styles.footer}>
      <div className={styles.footerContent}>
        <div className={styles.footerSection}>
          <h3>TheMindSqubit</h3>
          <p>Empowering you with AI agents for every task.</p>
        </div>
        <div className={styles.footerSection}>
          <h4>Quick Links</h4>
          <a href="#agents">Agents</a>
          <a href="#about">About</a>
          <a href="#contact">Contact</a>
        </div>
        <div className={styles.footerSection}>
          <h4>Contact</h4>
          <p>hello@themindsqubit.com</p>
          <p>+1 (555) 123-4567</p>
        </div>
      </div>
      <div className={styles.footerBottom}>
        <p>&copy; 2024 TheMindSqubit. All rights reserved.</p>
      </div>
    </footer>
  );
} 