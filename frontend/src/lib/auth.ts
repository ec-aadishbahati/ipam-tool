let accessToken: string | null = null;
let refreshToken: string | null = null;

const accessKey = "accessToken";
const refreshKey = "refreshToken";

if (typeof window !== "undefined") {
  accessToken = window.localStorage.getItem(accessKey);
  refreshToken = window.localStorage.getItem(refreshKey);
}

export function setTokens(at: string, rt: string) {
  accessToken = at;
  refreshToken = rt;
  if (typeof window !== "undefined") {
    window.localStorage.setItem(accessKey, at);
    window.localStorage.setItem(refreshKey, rt);
  }
}

export function getAccessToken() {
  return accessToken;
}

export function getRefreshToken() {
  return refreshToken;
}

export function clearTokens() {
  accessToken = null;
  refreshToken = null;
  if (typeof window !== "undefined") {
    window.localStorage.removeItem(accessKey);
    window.localStorage.removeItem(refreshKey);
  }
}
