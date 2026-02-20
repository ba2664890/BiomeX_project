import { buildBiomeXApiUrl } from "@/lib/biomex-backend";

type JsonRecord = Record<string, unknown>;

export type BackendResponse<T = unknown> = {
  ok: boolean;
  status: number;
  data: T | null;
  raw: string;
};

type BackendRequestOptions = {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  headers?: HeadersInit;
  body?: unknown;
};

function parseJsonSafely(raw: string) {
  if (!raw) return null;
  try {
    return JSON.parse(raw) as unknown;
  } catch {
    return null;
  }
}

export async function backendPublicRequest<T = unknown>(
  path: string,
  options: BackendRequestOptions = {},
): Promise<BackendResponse<T>> {
  const headers = new Headers(options.headers);
  headers.set("accept", "application/json");

  const init: RequestInit = {
    method: options.method ?? "GET",
    headers,
    cache: "no-store",
  };

  if (options.body !== undefined) {
    if (!headers.has("content-type")) {
      headers.set("content-type", "application/json");
    }
    init.body =
      typeof options.body === "string" ? options.body : JSON.stringify(options.body);
  }

  try {
    const response = await fetch(buildBiomeXApiUrl(path), init);
    const raw = await response.text();
    const parsed = parseJsonSafely(raw);

    return {
      ok: response.ok,
      status: response.status,
      data: (parsed as T | null) ?? null,
      raw,
    };
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Network error while contacting backend.";
    return {
      ok: false,
      status: 503,
      data: null,
      raw: message,
    };
  }
}

export function normalizeBackendError(
  response: BackendResponse,
  fallbackMessage: string,
) {
  const messageFromJson =
    (response.data as JsonRecord | null)?.detail ??
    (response.data as JsonRecord | null)?.message ??
    (response.data as JsonRecord | null)?.error;

  if (typeof messageFromJson === "string" && messageFromJson.trim()) {
    return messageFromJson;
  }

  if (response.raw) return response.raw;
  return fallbackMessage;
}
