import { useRouter } from 'next/router';
import { useAuth } from '@/contexts/AuthContext';
import styles from '@/styles/Home.module.css';

export default function Header() {
  const router = useRouter();
  const { isAuthenticated, user, logout } = useAuth();

  const handleAuthClick = () => {
    if (isAuthenticated) {
      logout();
    } else {
      router.push(`/login?redirect=${encodeURIComponent(router.asPath)}`);
    }
  };

  return (
    <header className={styles.header}>
      <div className={styles.headerContent}>
        <div className={styles.logo}>
          <a href="/">
            <h1>TheMindsQubit</h1>
          </a>
        </div>
        <nav className={styles.nav}>
          <a href="/#agents">Agents</a>
          <a href="/clients">Clients</a>
          <a href="/blog">Tech Blog</a>
          <a href="/#about">About</a>
          <a href="/#contact">Contact</a>
          <button 
            onClick={handleAuthClick}
            className={styles.authButton}
          >
            {isAuthenticated ? (
              <>
                {user?.full_name || user?.email?.split('@')[0] || 'User'}
                <span style={{ marginLeft: '0.5rem' }}>| Logout</span>
              </>
            ) : (
              'Login'
            )}
          </button>
        </nav>
      </div>
    </header>
  );
} 