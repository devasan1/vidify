import type {
  CategoryDetail,
  CategorySummary,
  InstallState,
  Job,
  ModelSpec,
} from "./types";

async function get<T>(url: string): Promise<T> {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url}: ${r.status}`);
  return r.json() as Promise<T>;
}

async function post<T>(url: string, body?: FormData | object): Promise<T> {
  const init: RequestInit = { method: "POST" };
  if (body instanceof FormData) {
    init.body = body;
  } else if (body) {
    init.headers = { "Content-Type": "application/json" };
    init.body = JSON.stringify(body);
  }
  const r = await fetch(url, init);
  if (!r.ok) throw new Error(`${url}: ${r.status}`);
  return r.json() as Promise<T>;
}

async function put<T>(url: string, body?: object): Promise<T> {
  const r = await fetch(url, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!r.ok) throw new Error(`${url}: ${r.status}`);
  return r.json() as Promise<T>;
}

async function del<T>(url: string): Promise<T> {
  const r = await fetch(url, { method: "DELETE" });
  if (!r.ok) throw new Error(`${url}: ${r.status}`);
  return r.json() as Promise<T>;
}

export const api = {
  health: () => get<{ ok: boolean; version: string; gpu: { available: boolean; backend: string } }>("/api/health"),
  categories: () => get<CategorySummary[]>("/api/categories"),
  category: (id: string) => get<CategoryDetail>(`/api/categories/${id}`),
  models: () => get<ModelSpec[]>("/api/models"),
  model: (id: string) => get<ModelSpec>(`/api/models/${id}`),
  installed: () => get<Record<string, InstallState>>("/api/models/installed"),
  downloadModel: (id: string) => post<{ status: string }>(`/api/models/${id}/download`),
  removeModel: (id: string) => del<{ status: string }>(`/api/models/${id}`),
  submitJob: (form: FormData) => post<Job>("/api/jobs", form),
  job: (id: string) => get<Job>(`/api/jobs/${id}`),
  jobs: () => get<Job[]>("/api/jobs"),
  jobOutputUrl: (id: string) => `/api/jobs/${id}/output`,
  hfTokenStatus: () =>
    get<{ configured: boolean; sources: string[]; masked: string | null }>(
      "/api/settings/hf-token",
    ),
  setHfToken: (token: string) =>
    put<{ configured: boolean; sources: string[]; masked: string | null }>(
      "/api/settings/hf-token",
      { token },
    ),
  clearHfToken: () =>
    del<{ configured: boolean; sources: string[]; masked: string | null }>(
      "/api/settings/hf-token",
    ),
};
