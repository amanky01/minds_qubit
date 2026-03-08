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

type ApiError = {
  message: string;
  status?: number;
  original?: any;
};

const getAuthErrorMessage = (error: any): ApiError => {
  if (!error || !error.response) {
    return {
      message: "Unable to connect to the server. Please ensure the backend is running on http://localhost:8000",
      status: undefined,
      original: error,
    };
  }

  const status = error.response?.status;
  // backend may use `detail`, `message`, or nested errors
  const detail =
    error.response?.data?.detail ||
    error.response?.data?.message ||
    (typeof error.response?.data === "string" ? error.response.data : undefined);

  if (status === 401) {
    return {
      message: detail || "Invalid email or password. Please check your credentials and try again.",
      status,
      original: error,
    };
  }

  if (status === 403) {
    return {
      message: detail || "You are not authorized to perform this action.",
      status,
      original: error,
    };
  }

  if (status === 500) {
    return {
      message: "Server error occurred. Please try again later.",
      status,
      original: error,
    };
  }

  if (status === 400) {
    return {
      message: detail || "Invalid request. Please check your input and try again.",
      status,
      original: error,
    };
  }

  return {
    message: detail || "An unexpected error occurred. Please try again.",
    status,
    original: error,
  };
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
      const apiError = getAuthErrorMessage(error);
      console.debug("Login error:", apiError.original || error);
      const authError = new Error(apiError.message) as Error & { status?: number; original?: any };
      authError.status = apiError.status;
      authError.original = apiError.original;
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
      const apiError = getAuthErrorMessage(error);
      console.debug("Registration error:", apiError.original || error);
      const authError = new Error(apiError.message) as Error & { status?: number; original?: any };
      authError.status = apiError.status;
      authError.original = apiError.original;
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
