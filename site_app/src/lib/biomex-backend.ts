const DEFAULT_BACKEND_URL =
  process.env.NODE_ENV === "production"
    ? "https://biomex-project.onrender.com"
    : "http://127.0.0.1:8000";

function stripTrailingSlashes(value: string) {
  return value.replace(/\/+$/, "");
}

export function getBiomeXBackendBaseUrl() {
  const configured =
    process.env.BIOMEX_BACKEND_URL ||
    process.env.NEXT_PUBLIC_BIOMEX_BACKEND_URL ||
    DEFAULT_BACKEND_URL;

  return stripTrailingSlashes(configured);
}

export function buildBiomeXApiUrl(path: string, query = "") {
  const normalizedPath = path.replace(/^\/+/, "");
  const suffix = query ? `?${query}` : "";
  return `${getBiomeXBackendBaseUrl()}/api/${normalizedPath}${suffix}`;
}
