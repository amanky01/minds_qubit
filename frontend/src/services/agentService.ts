import { isAxiosError } from "axios";
import api from "@/network/core/axiosInstance";

export interface Agent {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: string;
  features: string[];
}

function getDetailFromData(data: unknown): string | undefined {
  if (data == null) return undefined;
  if (typeof data === "string") return data;
  if (typeof data === "object" && "detail" in data) {
    const d = (data as { detail: unknown }).detail;
    if (typeof d === "string") return d;
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
        return "Unable to connect to the server. Please ensure the backend is running on http://localhost:8000";
      }
      return "Network error. Please check your connection and try again.";
    }

    const status = error.response.status;
    const detail = getDetailFromData(error.response.data);

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
};
