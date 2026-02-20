import { NextResponse } from "next/server";
import { buildBiomeXApiUrl } from "@/lib/biomex-backend";

export async function GET() {
  const healthUrl = buildBiomeXApiUrl("health/");

  try {
    const response = await fetch(healthUrl, { cache: "no-store" });
    const rawBody = await response.text();

    let backendPayload: unknown = rawBody;
    try {
      backendPayload = JSON.parse(rawBody);
    } catch {
      // Keep raw text when backend does not return JSON.
    }

    return NextResponse.json(
      {
        site: "site_app",
        status: response.ok ? "ok" : "degraded",
        backend: {
          url: healthUrl,
          statusCode: response.status,
          payload: backendPayload,
        },
      },
      { status: response.ok ? 200 : 502 },
    );
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Unknown backend connection error";

    return NextResponse.json(
      {
        site: "site_app",
        status: "error",
        backend: {
          url: healthUrl,
          error: message,
        },
      },
      { status: 502 },
    );
  }
}
