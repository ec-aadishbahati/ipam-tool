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

let lastActivity = Date.now();
let activityCheckInterval: NodeJS.Timeout | null = null;

export function trackActivity() {
  lastActivity = Date.now();
}

export function getLastActivity() {
  return lastActivity;
}

export function startActivityTracking() {
  if (typeof window !== "undefined") {
    const updateActivity = () => trackActivity();
    window.addEventListener('mousedown', updateActivity);
    window.addEventListener('keydown', updateActivity);
    window.addEventListener('scroll', updateActivity);
    window.addEventListener('touchstart', updateActivity);
    
    activityCheckInterval = setInterval(() => {
      const idleTime = Date.now() - lastActivity;
      if (idleTime > 5 * 60 * 1000) {
        clearTokens();
        window.location.href = "/login";
      }
    }, 30000);
  }
}

export function stopActivityTracking() {
  if (activityCheckInterval) {
    clearInterval(activityCheckInterval);
    activityCheckInterval = null;
  }
}
