import axios from "axios";
import {
  getAccessToken,
  getRefreshToken,
  setTokens,
  clearTokens,
  getLastActivity,
} from "./auth";

const rawBase = import.meta.env.VITE_API_BASE as string | undefined;

const base = rawBase && rawBase.trim() !== "" ? rawBase : undefined;

if (import.meta.env.PROD && !base) {
  throw new Error("VITE_API_BASE is required in production");
}

if (base && !base.startsWith("https://") && !base.startsWith("http://localhost")) {
  console.warn("VITE_API_BASE should be HTTPS in production");
}

console.log(`API base URL resolved to ${base ?? "(using Vite proxy)"}`);

export const api = axios.create({
  baseURL: base || "",
});

api.interceptors.request.use((config) => {
  const isAuthEndpoint = config.url?.includes('/auth/');
  const token = getAccessToken();
  
  if (!token && !isAuthEndpoint) {
    window.location.href = "/login";
    return Promise.reject(new Error("no access token"));
  }
  
  if (token) {
    config.headers = config.headers ?? {};
    (config.headers as any).Authorization = `Bearer ${token}`;
  }
  
  return config;
});

let isRefreshing = false;
let pending: Array<() => void> = [];

api.interceptors.response.use(
  (r) => r,
  async (error) => {
    const { response, config } = error;
    if (response?.status === 401 && !config._retry) {
      config._retry = true;
      
      const idleTime = Date.now() - getLastActivity();
      if (idleTime > 5 * 60 * 1000) {
        clearTokens();
        window.location.href = "/login";
        return Promise.reject(error);
      }
      
      if (!isRefreshing) {
        isRefreshing = true;
        try {
          const rt = getRefreshToken();
          if (!rt) throw new Error("no refresh token");
          const res = await axios.post(`${base ?? ""}/auth/refresh`, { token: rt });
          const { access_token, refresh_token } = res.data;
          setTokens(access_token, refresh_token);
          pending.forEach((fn) => fn());
          pending = [];
        } catch (refreshError) {
          clearTokens();
          window.location.href = "/login";
          return Promise.reject(error);
        } finally {
          isRefreshing = false;
        }
      }
      await new Promise<void>((resolve) => pending.push(resolve));
      return api(config);
    }
    return Promise.reject(error);
  }
);

export function setAuthToken(token?: string) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common.Authorization;
  }
}
