import { useEffect } from "react";
import { useRouter } from "next/router";
import { useAuth } from "@/contexts/AuthContext";

export default function AuthCallback() {
  const router = useRouter();
  const { checkAuth } = useAuth();

  useEffect(() => {
    const handleCallback = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const accessToken = urlParams.get("access_token");
      const refreshToken = urlParams.get("refresh_token");

      if (accessToken && refreshToken) {
        // Store tokens
        localStorage.setItem("access_token", accessToken);
        localStorage.setItem("refresh_token", refreshToken);

        // Refresh auth state
        await checkAuth();

        // Redirect to home or desired page
        const redirectTo = localStorage.getItem("redirect_after_login") || "/";
        localStorage.removeItem("redirect_after_login");
        router.push(redirectTo);
      } else {
        // No tokens, redirect to login
        router.push("/login");
      }
    };

    handleCallback();
  }, [router, checkAuth]);

  return (
    <div style={{ padding: "2rem", textAlign: "center" }}>
      <p>Completing authentication...</p>
    </div>
  );
}
