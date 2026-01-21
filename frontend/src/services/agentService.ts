import api from "@/network/core/axiosInstance";

export interface Agent {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: string;
  features: string[];
}

const getErrorMessage = (error: any): string => {
  // Check for network/connection errors
  if (!error.response) {
    if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
      return "Unable to connect to the server. Please ensure the backend is running on http://localhost:8000";
    }
    return "Network error. Please check your connection and try again.";
  }
  
  const status = error.response?.status;
  const detail = error.response?.data?.detail || error.response?.data?.message;
  
  if (status === 500) {
    return "Server error occurred. Please try again later or contact support.";
  }
  
  if (status === 404) {
    return "The requested resource was not found.";
  }
  
  return detail || "An unexpected error occurred. Please try again.";
};

export const agentService = {
  async getAllAgents(): Promise<Agent[]> {
    try {
      const response = await api.get("/api/v1/agents");
      return response.data;
    } catch (error: any) {
      const message = getErrorMessage(error);
      console.error("Error fetching agents:", error);
      throw new Error(message);
    }
  },

  async getAgentById(agentId: string): Promise<Agent> {
    try {
      const response = await api.get(`/api/v1/agents/${agentId}`);
      return response.data;
    } catch (error: any) {
      const message = getErrorMessage(error);
      console.error("Error fetching agent:", error);
      throw new Error(message);
    }
  },

  async getCategories(): Promise<string[]> {
    try {
      const response = await api.get("/api/v1/agents/categories");
      return response.data;
    } catch (error: any) {
      const message = getErrorMessage(error);
      console.error("Error fetching categories:", error);
      throw new Error(message);
    }
  },
};
