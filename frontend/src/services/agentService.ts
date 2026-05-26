import { isAxiosError } from "axios";
import api from "@/network/core/axiosInstance";
import config from "@/network/config/config";

export interface Agent {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: string;
  features: string[];
  is_live: boolean;
}

export interface OpportunitySubscribePayload {
  email: string;
  notification_categories: string[];
  opportunity_types: string[];
}

export interface OpportunitySubscribeResponse {
  email: string;
  status: string;
  subscriber: Record<string, unknown>;
}

export interface OpportunityUnsubscribePayload {
  email: string;
}

export type ProxyMethod = "GET" | "POST" | "PATCH" | "PUT" | "DELETE";

function getDetailFromData(data: unknown): string | undefined {
  if (data == null) return undefined;
  if (typeof data === "string") return data;
  if (typeof data === "object" && "detail" in data) {
    const d = (data as { detail: unknown }).detail;
    if (typeof d === "string") return d;
    if (typeof d === "object" && d !== null && "message" in d) {
      const m = (d as { message: unknown }).message;
      if (typeof m === "string") return m;
    }
  }
  if (typeof data === "object" && "message" in data) {
    const m = (data as { message: unknown }).message;
    if (typeof m === "string") return m;
  }
  return undefined;
}

const getErrorMessage = (error: unknown): string => {
  if (isAxiosError(error)) {
    if (!error.response) {
      const code = error.code;
      const msg = error.message;
      if (
        code === "ECONNREFUSED" ||
        code === "ERR_NETWORK" ||
        msg?.includes("Network Error")
      ) {
        return `Unable to connect to the server. Please ensure the backend is running at ${config.API_BASE_URL}`;
      }
      return "Network error. Please check your connection and try again.";
    }

    const status = error.response.status;
    const detail = getDetailFromData(error.response.data);

    if (status === 503) {
      return detail || "This agent is not available yet.";
    }

    if (status === 500) {
      return "Server error occurred. Please try again later or contact support.";
    }

    if (status === 404) {
      return "The requested resource was not found.";
    }

    return detail || "An unexpected error occurred. Please try again.";
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "An unexpected error occurred. Please try again.";
};

export const agentService = {
  async getAllAgents(): Promise<Agent[]> {
    try {
      const response = await api.get("/api/v1/agents");
      return response.data;
    } catch (error: unknown) {
      const message = getErrorMessage(error);
      console.error("Error fetching agents:", error);
      throw new Error(message);
    }
  },

  async getAgentById(agentId: string): Promise<Agent> {
    try {
      const response = await api.get(`/api/v1/agents/${agentId}`);
      return response.data;
    } catch (error: unknown) {
      const message = getErrorMessage(error);
      console.error("Error fetching agent:", error);
      throw new Error(message);
    }
  },

  async getCategories(): Promise<string[]> {
    try {
      const response = await api.get("/api/v1/agents/categories");
      return response.data;
    } catch (error: unknown) {
      const message = getErrorMessage(error);
      console.error("Error fetching categories:", error);
      throw new Error(message);
    }
  },

  async proxyAgent<T = unknown>(
    agentId: string,
    method: ProxyMethod,
    path: string,
    body?: unknown,
    params?: Record<string, string>
  ): Promise<T> {
    const cleanPath = path.replace(/^\//, "");
    try {
      const response = await api.request<T>({
        method,
        url: `/api/v1/agents/${agentId}/proxy/${cleanPath}`,
        data: body,
        params,
      });
      return response.data;
    } catch (error: unknown) {
      throw new Error(getErrorMessage(error));
    }
  },

  async subscribeOpportunityAlert(
    payload: OpportunitySubscribePayload
  ): Promise<OpportunitySubscribeResponse> {
    return agentService.proxyAgent<OpportunitySubscribeResponse>(
      "opportunityalert",
      "POST",
      "subscribe",
      payload
    );
  },

  async updateOpportunityAlertSubscription(
    payload: OpportunitySubscribePayload
  ): Promise<OpportunitySubscribeResponse> {
    return agentService.proxyAgent<OpportunitySubscribeResponse>(
      "opportunityalert",
      "PATCH",
      "subscribe",
      payload
    );
  },

  async unsubscribeOpportunityAlert(
    payload: OpportunityUnsubscribePayload
  ): Promise<{ email: string; status: string }> {
    return agentService.proxyAgent<{ email: string; status: string }>(
      "opportunityalert",
      "POST",
      "subscribe/unsubscribe",
      payload
    );
  },
};
