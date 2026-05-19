import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import {
  agentService,
  OpportunitySubscribePayload,
} from "@/services/agentService";
import styles from "@/styles/Agent.module.css";

const NOTIFICATION_OPTIONS = [
  { id: "daily_digest", label: "Daily digest (~7 PM IST summary)" },
  { id: "instant_alert", label: "Instant alerts (high-score opportunities)" },
] as const;

const OPPORTUNITY_OPTIONS = [
  { id: "internship", label: "Internships" },
  { id: "job", label: "Jobs" },
  { id: "hackathon", label: "Hackathons" },
  { id: "research", label: "Research" },
  { id: "all", label: "All types" },
] as const;

interface Props {
  accentColor: string;
  accentSecondary: string;
}

export default function OpportunityAlertSubscription({
  accentColor,
  accentSecondary,
}: Props) {
  const { user } = useAuth();
  const [email, setEmail] = useState(user?.email ?? "");
  const [notificationCategories, setNotificationCategories] = useState<string[]>([
    "daily_digest",
  ]);
  const [opportunityTypes, setOpportunityTypes] = useState<string[]>(["internship", "job"]);
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const toggleItem = (list: string[], id: string, checked: boolean) => {
    if (checked) return [...list, id];
    return list.filter((x) => x !== id);
  };

  const buildPayload = (): OpportunitySubscribePayload => ({
    email,
    notification_categories: notificationCategories,
    opportunity_types: opportunityTypes,
  });

  const handleSubscribe = async () => {
    setLoading(true);
    setStatusMessage(null);
    setErrorMessage(null);
    try {
      const result = await agentService.subscribeOpportunityAlert(buildPayload());
      setStatusMessage(`Subscription ${result.status}. You will receive emails at ${result.email}.`);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : "Subscription failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async () => {
    setLoading(true);
    setStatusMessage(null);
    setErrorMessage(null);
    try {
      const result = await agentService.updateOpportunityAlertSubscription(buildPayload());
      setStatusMessage(`Preferences updated (${result.status}).`);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : "Update failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleUnsubscribe = async () => {
    setLoading(true);
    setStatusMessage(null);
    setErrorMessage(null);
    try {
      const result = await agentService.unsubscribeOpportunityAlert({ email });
      setStatusMessage(`Unsubscribed: ${result.status}`);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : "Unsubscribe failed.");
    } finally {
      setLoading(false);
    }
  };

  const canSubmit =
    Boolean(email) &&
    notificationCategories.length > 0 &&
    opportunityTypes.length > 0 &&
    !loading;

  return (
    <div className={styles.subscriptionPanel}>
      <p className={styles.subscriptionIntro}>
        Subscribe to job, internship, and hackathon emails. Choose notification types and
        opportunity categories you care about.
      </p>

      <label className={styles.subscriptionLabel}>
        Email
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className={styles.subscriptionInput}
          placeholder="you@example.com"
        />
      </label>

      <fieldset className={styles.subscriptionFieldset}>
        <legend>Notification types</legend>
        {NOTIFICATION_OPTIONS.map((opt) => (
          <label key={opt.id} className={styles.checkboxRow}>
            <input
              type="checkbox"
              checked={notificationCategories.includes(opt.id)}
              onChange={(e) =>
                setNotificationCategories(
                  toggleItem(notificationCategories, opt.id, e.target.checked)
                )
              }
            />
            {opt.label}
          </label>
        ))}
      </fieldset>

      <fieldset className={styles.subscriptionFieldset}>
        <legend>Opportunity types</legend>
        {OPPORTUNITY_OPTIONS.map((opt) => (
          <label key={opt.id} className={styles.checkboxRow}>
            <input
              type="checkbox"
              checked={opportunityTypes.includes(opt.id)}
              onChange={(e) =>
                setOpportunityTypes(toggleItem(opportunityTypes, opt.id, e.target.checked))
              }
            />
            {opt.label}
          </label>
        ))}
      </fieldset>

      {statusMessage && <p className={styles.subscriptionSuccess}>{statusMessage}</p>}
      {errorMessage && <p className={styles.subscriptionError}>{errorMessage}</p>}

      <div className={styles.subscriptionActions}>
        <button
          type="button"
          disabled={!canSubmit}
          onClick={handleSubscribe}
          className={styles.sendButton}
          style={{
            background: `linear-gradient(135deg, ${accentColor}, ${accentSecondary})`,
          }}
        >
          Subscribe
        </button>
        <button
          type="button"
          disabled={loading || !email}
          onClick={handleUpdate}
          className={styles.secondaryButton}
          style={{ borderColor: accentColor, color: accentColor }}
        >
          Update preferences
        </button>
        <button
          type="button"
          disabled={loading || !email}
          onClick={handleUnsubscribe}
          className={styles.secondaryButton}
        >
          Unsubscribe
        </button>
      </div>
    </div>
  );
}
