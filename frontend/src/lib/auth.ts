let accessToken: string | null = null;
let refreshToken: string | null = null;

export function setTokens(at: string, rt: string) {
  accessToken = at;
  refreshToken = rt;
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
}
