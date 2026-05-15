import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/router";
import Head from "next/head";
import { useAuth } from "@/contexts/AuthContext";
import styles from "@/styles/Auth.module.css";

export default function Signup() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { register, isAuthenticated } = useAuth();
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

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters long");
      return;
    }

    setLoading(true);

    try {
      await register(email, password, fullName || undefined);
      const redirectTo = router.query.redirect as string || "/";
      router.push(redirectTo);
    } catch (err: unknown) {
      // Use the formatted error message from authService
      const message = err instanceof Error ? err.message : "Registration failed. Please check your input and ensure the backend is running.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    window.location.href = `${process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000/"}api/v1/auth/oauth/google`;
  };

  const handleGitHubLogin = () => {
    window.location.href = `${process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000/"}api/v1/auth/oauth/github`;
  };

  return (
    <>
      <Head>
        <title>Sign Up - TheMindSqubit</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <div className={styles.authContainer}>
        <div className={styles.authCard}>
          <h1 className={styles.authTitle}>Create Account</h1>
          <p className={styles.authSubtitle}>Join us to access AI agents</p>

          {error && <div className={styles.errorMessage}>{error}</div>}

          <form onSubmit={handleSubmit} className={styles.authForm}>
            <div className={styles.formGroup}>
              <label htmlFor="fullName">Full Name (Optional)</label>
              <input
                id="fullName"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="John Doe"
              />
            </div>

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
                minLength={8}
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="confirmPassword">Confirm Password</label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                placeholder="••••••••"
                minLength={8}
              />
            </div>

            <button type="submit" className={styles.primaryButton} disabled={loading}>
              {loading ? "Creating account..." : "Sign Up"}
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
            Already have an account?{" "}
            <Link href="/login" className={styles.authLink}>
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </>
  );
}
