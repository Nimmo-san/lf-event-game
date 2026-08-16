const API_URL = import.meta.env.VITE_API_URL || "/api";

export interface AdminEntry {
  id: string;
  email: string;
  player_name: string;
  company_name: string;
  score: number;
  lightning_collected: number;
  entered_at: string;
}

export interface AnalyticsResponse {
  players: {
    unique_players: number;
    total_games: number;
    repeat_players: number;
    average_games_per_player: number;
    replay_rate: number;
  };

  gameplay: {
    average_score: number;
    highest_score: number;
    average_lightning: number;
    average_duration: number;
  };

  leaderboard: {
    unique_entries: number;
    conversion_rate: number;
  };

  activity: {
    games_over_time: Array<{
      period: string;
      games: number;
    }>;
  };

  distributions: {
    scores: Array<{
      label: string;
      minimum: number;
      maximum: number;
      games: number;
    }>;

    games_per_player: Array<{
      games: number;
      players: number;
    }>;
  };

  companies: Array<{
    company: string;
    players: number;
    games: number;
    best_score: number;
    average_score: number;
  }>;
}

export interface EntryFilters {
  search?: string;
  name?: string;
  email?: string;
  company?: string;
}

/*
 * Thrown by every function below on a 401. AdminLayout.vue
 * will catch this (via the injected handler each child view
 * calls in its own catch block) and bounces back to the
 * login screen.
 */
export class AdminAuthError extends Error {
  constructor() {
    super("Admin session expired or invalid.");
    this.name = "AdminAuthError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    credentials: "include",
    ...init,
  });

  if (response.status === 401) {
    throw new AdminAuthError();
  }

  if (!response.ok) {
    throw new Error(`Admin request failed: ${path}`);
  }

  return response.json();
}

function buildEntryParams(filters: EntryFilters) {
  const params = new URLSearchParams();

  if (filters.search?.trim()) {
    params.set("search", filters.search.trim());
  }

  if (filters.name?.trim()) {
    params.set("name", filters.name.trim());
  }

  if (filters.email?.trim()) {
    params.set("email", filters.email.trim());
  }

  if (filters.company?.trim()) {
    params.set("company", filters.company.trim());
  }

  return params;
}

export async function checkAdminSession(): Promise<boolean> {
  try {
    await request("/admin/session");
    return true;
  } catch {
    return false;
  }
}

export async function adminLogin(key: string): Promise<void> {
  const response = await fetch(`${API_URL}/admin/login`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ key }),
  });

  if (!response.ok) {
    throw new Error("Invalid admin key.");
  }
}

export async function adminLogout(): Promise<void> {
  await fetch(`${API_URL}/admin/logout`, {
    method: "POST",
    credentials: "include",
  });
}

export async function getAdminEntries(
  filters: EntryFilters,
): Promise<AdminEntry[]> {
  const query = buildEntryParams(filters).toString();

  return request<AdminEntry[]>(`/admin/entries${query ? `?${query}` : ""}`);
}

export async function getAdminAnalytics(): Promise<AnalyticsResponse> {
  return request<AnalyticsResponse>("/admin/analytics");
}

export async function exportMarketingCsv(
  filters: EntryFilters,
  excludedIds: string[],
): Promise<Blob> {
  const response = await fetch(`${API_URL}/admin/export/marketing`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      search: filters.search?.trim() || null,
      name: filters.name?.trim() || null,
      email: filters.email?.trim() || null,
      company: filters.company?.trim() || null,
      excluded_ids: excludedIds,
    }),
  });

  if (response.status === 401) {
    throw new AdminAuthError();
  }

  if (!response.ok) {
    throw new Error("Export failed.");
  }

  return response.blob();
}
