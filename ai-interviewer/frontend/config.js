const API_BASE = "/api";
const WS_URL = `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}/ws`;

function buildApiUrl(path) {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE}${normalizedPath}`;
}

window.APP_CONFIG = {
  API_BASE,
  WS_URL,
  buildApiUrl,
};

export const APP_CONFIG = window.APP_CONFIG;
export { buildApiUrl };