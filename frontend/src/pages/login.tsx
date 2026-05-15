import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/router";
import Head from "next/head";
import { useAuth } from "@/contexts/AuthContext";
import config from "@/network/config/config";
import styles from "@/styles/Auth.module.css";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login, isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated) {
      const redirectTo = router.query.redirect as string || "/";
      router.push(redirectTo);
    }
  }, [isAuthenticated, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login(email, password);
      const redirectTo = router.query.redirect as string || "/";
      router.push(redirectTo);
    } catch (err: unknown) {
      // Use the formatted error message from authService and handle auth statuses
      const authErr = err as Error & { status?: number };
      const status = authErr.status;
      if (status === 401) {
        setError(authErr.message || "Invalid credentials. Please try again.");
      } else if (status === 403) {
        setError(authErr.message || "You are not authorized to access this resource.");
      } else if (!(err instanceof Error) || !err.message) {
        setError("Login failed. Please check your credentials and ensure the backend is running.");
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    const redirectTo = (router.query.redirect as string) || "/";
    if (typeof window !== "undefined") {
      localStorage.setItem("redirect_after_login", redirectTo);
    }
    window.location.href = `${config.API_BASE_URL}api/v1/auth/oauth/google`;
  };

  const handleGitHubLogin = () => {
    const redirectTo = (router.query.redirect as string) || "/";
    if (typeof window !== "undefined") {
      localStorage.setItem("redirect_after_login", redirectTo);
    }
    window.location.href = `${config.API_BASE_URL}api/v1/auth/oauth/github`;
  };

  return (
    <>
      <Head>
        <title>Login - TheMindSqubit</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <div className={styles.authContainer}>
        <div className={styles.authCard}>
          <h1 className={styles.authTitle}>Welcome Back</h1>
          <p className={styles.authSubtitle}>Sign in to access AI agents</p>

          {error && <div className={styles.errorMessage}>{error}</div>}

          <form onSubmit={handleSubmit} className={styles.authForm}>
            <div className={styles.formGroup}>
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="your@email.com"
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="••••••••"
              />
            </div>

            <button type="submit" className={styles.primaryButton} disabled={loading}>
              {loading ? "Signing in..." : "Sign In"}
            </button>
          </form>

          <div className={styles.divider}>
            <span>OR</span>
          </div>

          <div className={styles.socialButtons}>
            <button
              type="button"
              onClick={handleGoogleLogin}
              className={styles.socialButton}
            >
              <span>🔵</span> Continue with Google
            </button>
            <button
              type="button"
              onClick={handleGitHubLogin}
              className={styles.socialButton}
            >
              <span>⚫</span> Continue with GitHub
            </button>
          </div>

          <p className={styles.authFooter}>
            Don&apos;t have an account?{" "}
            <Link href="/signup" className={styles.authLink}>
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </>
  );
}
