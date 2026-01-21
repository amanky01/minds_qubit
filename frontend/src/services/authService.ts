import api from "@/network/core/axiosInstance";

export interface User {
  id: string;
  email: string;
  full_name?: string;
  is_active: boolean;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user?: User;
}

const getAuthErrorMessage = (error: any): string => {
  if (!error.response) {
    // Network error - backend not reachable
    return "Unable to connect to the server. Please ensure the backend is running on http://localhost:8000";
  }
  
  const status = error.response?.status;
  const detail = error.response?.data?.detail || error.response?.data?.message;
  
  if (status === 401) {
    return detail || "Invalid email or password. Please check your credentials and try again.";
  }
  
  if (status === 500) {
    return "Server error occurred. This might be due to database connection issues. Please try again later.";
  }
  
  if (status === 400) {
    return detail || "Invalid request. Please check your input and try again.";
  }
  
  return detail || "An unexpected error occurred. Please try again.";
};

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await api.post("/api/v1/auth/login", credentials);
      const data = response.data;
      
      // Store tokens
      if (typeof window !== "undefined") {
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("refresh_token", data.refresh_token);
      }
      
      return data;
    } catch (error: any) {
      const message = getAuthErrorMessage(error);
      console.error("Login error:", error);
      const authError = new Error(message);
      (authError as any).response = error.response;
      throw authError;
    }
  },

  async register(data: RegisterData): Promise<AuthResponse> {
    try {
      const response = await api.post("/api/v1/auth/register", data);
      const authData = response.data;
      
      // Store tokens
      if (typeof window !== "undefined") {
        localStorage.setItem("access_token", authData.access_token);
        localStorage.setItem("refresh_token", authData.refresh_token);
      }
      
      return authData;
    } catch (error: any) {
      const message = getAuthErrorMessage(error);
      console.error("Registration error:", error);
      const authError = new Error(message);
      (authError as any).response = error.response;
      throw authError;
    }
  },

  async getCurrentUser(): Promise<User> {
    try {
      const response = await api.get("/api/v1/auth/me");
      return response.data;
    } catch (error: any) {
      console.error("Get user error:", error);
      throw error;
    }
  },

  async refreshToken(): Promise<string> {
    try {
      const refreshToken = localStorage.getItem("refresh_token");
      if (!refreshToken) {
        throw new Error("No refresh token available");
      }
      
      const response = await api.post("/api/v1/auth/refresh", {
        refresh_token: refreshToken,
      });
      
      const newAccessToken = response.data.access_token;
      localStorage.setItem("access_token", newAccessToken);
      
      return newAccessToken;
    } catch (error: any) {
      console.error("Token refresh error:", error);
      this.logout();
      throw error;
    }
  },

  logout(): void {
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    }
  },

  getAccessToken(): string | null {
    if (typeof window !== "undefined") {
      return localStorage.getItem("access_token");
    }
    return null;
  },

  isAuthenticated(): boolean {
    return !!this.getAccessToken();
  },
};
