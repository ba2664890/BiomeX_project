import { NextRequest, NextResponse } from "next/server";
import { buildBiomeXApiUrl } from "@/lib/biomex-backend";

type Params = { params: { path: string[] } };

const METHODS_WITH_BODY = new Set(["POST", "PUT", "PATCH", "DELETE"]);

function pickRequestHeaders(req: NextRequest) {
  const headers = new Headers();
  const forwardable = ["authorization", "content-type", "accept", "x-requested-with"];

  for (const headerName of forwardable) {
    const value = req.headers.get(headerName);
    if (value) headers.set(headerName, value);
  }

  return headers;
}

async function proxyRequest(req: NextRequest, path: string[]) {
  const targetUrl = buildBiomeXApiUrl(path.join("/"), req.nextUrl.searchParams.toString());
  const headers = pickRequestHeaders(req);
  const init: RequestInit = {
    method: req.method,
    headers,
    cache: "no-store",
  };

  if (METHODS_WITH_BODY.has(req.method)) {
    init.body = await req.text();
  }

  try {
    const upstream = await fetch(targetUrl, init);
    const body = await upstream.text();
    const responseHeaders = new Headers();
    const contentType = upstream.headers.get("content-type");

    if (contentType) {
      responseHeaders.set("content-type", contentType);
    }

    return new NextResponse(body, {
      status: upstream.status,
      headers: responseHeaders,
    });
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Unexpected upstream connection error";

    return NextResponse.json(
      {
        status: "error",
        message: "Failed to reach BiomeX backend",
        targetUrl,
        details: message,
      },
      { status: 502 },
    );
  }
}

export async function GET(req: NextRequest, { params }: Params) {
  return proxyRequest(req, params.path);
}

export async function POST(req: NextRequest, { params }: Params) {
  return proxyRequest(req, params.path);
}

export async function PUT(req: NextRequest, { params }: Params) {
  return proxyRequest(req, params.path);
}

export async function PATCH(req: NextRequest, { params }: Params) {
  return proxyRequest(req, params.path);
}

export async function DELETE(req: NextRequest, { params }: Params) {
  return proxyRequest(req, params.path);
}
