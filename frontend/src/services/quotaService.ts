import { isAxiosError } from "axios";
import api from "@/network/core/axiosInstance";
import config from "@/network/config/config";

export interface AgentQuotaUsage {
  daily_used: number;
  monthly_used: number;
}

export interface QuotaMeResponse {
  plan_id: string;
  plan_name: string;
  global_daily_limit: number;
  global_monthly_limit: number;
  by_agent: Record<string, AgentQuotaUsage>;
}

function getErrorMessage(error: unknown): string {
  if (isAxiosError(error)) {
    if (!error.response) {
      return `Unable to connect to the server at ${config.API_BASE_URL}`;
    }
    const data = error.response.data as { detail?: string };
    if (typeof data?.detail === "string") return data.detail;
    return `Request failed (${error.response.status})`;
  }
  if (error instanceof Error) return error.message;
  return "An unexpected error occurred.";
}

export const quotaService = {
  async getMyQuota(): Promise<QuotaMeResponse> {
    try {
      const response = await api.get<QuotaMeResponse>("/api/v1/quota/me");
      return response.data;
    } catch (error: unknown) {
      throw new Error(getErrorMessage(error));
    }
  },
};
