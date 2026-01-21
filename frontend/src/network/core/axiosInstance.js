import axios from "axios";
import config from "../config/config";

const api = axios.create({
    baseURL: config.API_BASE_URL,
    timeout: config.API_TIMEOUT
});

// Add request interceptor to include auth token
api.interceptors.request.use(
    (config) => {
        const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Add response interceptor to handle token refresh
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // If error is 401 and we haven't tried to refresh yet
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = typeof window !== "undefined" ? localStorage.getItem("refresh_token") : null;
                if (refreshToken) {
                    const response = await axios.post(
                        `${config.API_BASE_URL}api/v1/auth/refresh`,
                        { refresh_token: refreshToken }
                    );
                    const { access_token } = response.data;
                    
                    if (typeof window !== "undefined") {
                        localStorage.setItem("access_token", access_token);
                    }
                    
                    originalRequest.headers.Authorization = `Bearer ${access_token}`;
                    return api(originalRequest);
                }
            } catch (refreshError) {
                // Refresh failed, logout user
                if (typeof window !== "undefined") {
                    localStorage.removeItem("access_token");
                    localStorage.removeItem("refresh_token");
                    window.location.href = "/login";
                }
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

export default api;