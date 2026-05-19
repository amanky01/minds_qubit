import Head from "next/head";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import Header from "@/components/Header";
import ProtectedRoute from "@/components/ProtectedRoute";
import { useAuth } from "@/contexts/AuthContext";
import { agentService, Agent } from "@/services/agentService";
import { quotaService, QuotaMeResponse } from "@/services/quotaService";
import styles from "@/styles/Dashboard.module.css";

function UsageBar({
  label,
  used,
  limit,
}: {
  label: string;
  used: number;
  limit: number;
}) {
  const pct = limit > 0 ? Math.min(100, (used / limit) * 100) : 0;
  return (
    <div className={styles.limitBlock}>
      <h3>{label}</h3>
      <div className={styles.barTrack}>
        <div className={styles.barFill} style={{ width: `${pct}%` }} />
      </div>
      <p className={styles.barLabel}>
        {used} / {limit} used
      </p>
    </div>
  );
}

function DashboardContent() {
  const { user } = useAuth();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [quota, setQuota] = useState<QuotaMeResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        const [agentsData, quotaData] = await Promise.all([
          agentService.getAllAgents(),
          quotaService.getMyQuota(),
        ]);
        setAgents(agentsData);
        setQuota(quotaData);
      } catch (err: unknown) {
        const message =
          err instanceof Error ? err.message : "Failed to load dashboard data.";
        setError(message);
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, []);

  const { dailyUsed, monthlyUsed } = useMemo(() => {
    if (!quota) return { dailyUsed: 0, monthlyUsed: 0 };
    const values = Object.values(quota.by_agent);
    return {
      dailyUsed: values.reduce((sum, a) => sum + a.daily_used, 0),
      monthlyUsed: values.reduce((sum, a) => sum + a.monthly_used, 0),
    };
  }, [quota]);

  const displayName =
    user?.full_name || user?.email?.split("@")[0] || "there";

  if (loading) {
    return (
      <div className={styles.page}>
        <Header />
        <div className={styles.loading}>Loading your dashboard…</div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <Header />
      <main className={styles.main}>
        <h1 className={styles.title}>Dashboard</h1>
        <p className={styles.subtitle}>Welcome back, {displayName}</p>

        {error && <div className={styles.errorBox}>{error}</div>}

        {quota && (
          <section className={styles.planCard}>
            <div className={styles.planHeader}>
              <h2 className={styles.planName}>{quota.plan_name}</h2>
              <span className={styles.planBadge}>
                {user?.plan_id || quota.plan_id}
              </span>
            </div>
            <div className={styles.limitsGrid}>
              <UsageBar
                label="Daily usage (all agents)"
                used={dailyUsed}
                limit={quota.global_daily_limit}
              />
              <UsageBar
                label="Monthly usage (all agents)"
                used={monthlyUsed}
                limit={quota.global_monthly_limit}
              />
            </div>
          </section>
        )}

        <h2 className={styles.sectionTitle}>Per-agent usage</h2>
        <p className={styles.sectionNote}>
          Limits shown use your plan&apos;s global caps. Per-agent caps may
          differ on your subscription tier.
        </p>

        <table className={styles.agentTable}>
          <thead>
            <tr>
              <th>Agent</th>
              <th>Daily</th>
              <th>Monthly</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {agents.map((agent) => {
              const usage = quota?.by_agent[agent.id] ?? {
                daily_used: 0,
                monthly_used: 0,
              };
              const dailyLimit = quota?.global_daily_limit ?? 0;
              const monthlyLimit = quota?.global_monthly_limit ?? 0;
              return (
                <tr key={agent.id}>
                  <td>
                    <div className={styles.agentCell}>
                      <span className={styles.agentIcon}>{agent.icon}</span>
                      <span>{agent.name}</span>
                    </div>
                  </td>
                  <td>
                    {usage.daily_used} / {dailyLimit}
                  </td>
                  <td>
                    {usage.monthly_used} / {monthlyLimit}
                  </td>
                  <td>
                    <Link
                      href={`/agent/${agent.id}`}
                      className={styles.openLink}
                    >
                      Open →
                    </Link>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </main>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <>
      <Head>
        <title>Dashboard — TheMindSqubit</title>
        <meta name="description" content="Your plan and agent usage" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <ProtectedRoute>
        <DashboardContent />
      </ProtectedRoute>
    </>
  );
}
