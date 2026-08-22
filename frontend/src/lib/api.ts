const isProduction = process.env.NODE_ENV === "production";
const rawApiUrl = process.env.NEXT_PUBLIC_API_URL;

if (isProduction && (!rawApiUrl || rawApiUrl.includes("127.0.0.1") || rawApiUrl.includes("localhost"))) {
  console.error("CRITICAL PRODUCTION CONFIGURATION WARNING: NEXT_PUBLIC_API_URL must be explicitly configured with a production domain URL!");
}

export function getApiBaseUrl(): string {
  if (rawApiUrl && !rawApiUrl.includes("127.0.0.1") && !rawApiUrl.includes("localhost")) {
    return rawApiUrl.replace(/\/$/, "");
  }

  if (typeof window !== "undefined") {
    const host = window.location.hostname;
    if (host === "localhost" || host === "127.0.0.1") {
      return "http://127.0.0.1:8000/api/v1";
    }
  }

  return "https://pm-internship-recommendation-engine-tqaf.onrender.com/api/v1";
}

export function getAuthToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem("pm_internship_token");
  }
  return null;
}

export function setAuthToken(token: string) {
  if (typeof window !== "undefined") {
    localStorage.setItem("pm_internship_token", token);
  }
}

export function removeAuthToken() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("pm_internship_token");
    localStorage.removeItem("pm_internship_user");
  }
}

export function getCurrentUser() {
  if (typeof window !== "undefined") {
    const data = localStorage.getItem("pm_internship_user");
    return data ? JSON.parse(data) : null;
  }
  return null;
}

export async function fetchApi(endpoint: string, options: RequestInit = {}) {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string> || {}),
  };

  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const baseUrl = getApiBaseUrl();
  const response = await fetch(`${baseUrl}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMsg = "API Request Failed";
    try {
      const errJson = await response.json();
      errorMsg = errJson.detail || errorMsg;
    } catch {}
    throw new Error(errorMsg);
  }

  return response.json();
}
