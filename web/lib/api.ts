function apiBase(): string {
  const raw = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (!raw) return "";
  return raw.replace(/\/$/, "");
}

function joinUrl(path: string): string {
  const base = apiBase();
  if (!base) return path;
  return `${base}${path.startsWith("/") ? path : `/${path}`}`;
}

export function getApiBase(): string {
  return apiBase();
}

export async function apiJson<T>(path: string, init?: RequestInit): Promise<T> {
  if (!apiBase()) {
    throw new Error(
      "NEXT_PUBLIC_API_URL is not set — add it to web/.env.local (e.g. http://127.0.0.1:8765)",
    );
  }
  const res = await fetch(joinUrl(path), {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers as Record<string, string>),
    },
  });
  const text = await res.text();
  let data: unknown = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { detail: text || res.statusText };
  }
  if (!res.ok) {
    const d = data as { detail?: unknown };
    const detail = d?.detail;
    const msg =
      typeof detail === "string"
        ? detail
        : detail != null
          ? JSON.stringify(detail)
          : res.statusText;
    throw new Error(msg || `HTTP ${res.status}`);
  }
  return data as T;
}
