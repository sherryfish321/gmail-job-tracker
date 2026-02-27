const BASE = "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
  return res.json();
}

// Dashboard data
export const getStats = () => request("/api/stats");
export const getApplications = (params = {}) => {
  const q = new URLSearchParams(params).toString();
  return request(`/api/applications${q ? `?${q}` : ""}`);
};
export const getFunnel = () => request("/api/funnel");
export const getWeekly = () => request("/api/weekly");
export const getActions = () => request("/api/actions");
export const getFilters = () => request("/api/filters");

// Sync — fetch Gmail + analyze with Ollama
export const syncEmails = ({ after, before, maxResults } = {}) => {
  const body = {};
  if (after) body.after = after;
  if (before) body.before = before;
  if (maxResults) body.max_results = maxResults;

  return request("/api/sync", {
    method: "POST",
    body: JSON.stringify(body),
  });
};

// Application emails (for expanded row detail)
export const getApplicationEmails = (appId) => request(`/api/applications/${appId}/emails`);

// Toggle action done
export const toggleActionDone = (appId) =>
  request(`/api/applications/${appId}/action-done`, { method: "PATCH" });

// Update application status
export const updateApplicationStatus = (appId, status) =>
  request(`/api/applications/${appId}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });

// AI Insight — chat with Ollama via backend
export const chatAI = (message) =>
  request("/api/chat", {
    method: "POST",
    body: JSON.stringify({ message }),
  });