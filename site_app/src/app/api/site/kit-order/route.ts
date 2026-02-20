import { NextRequest, NextResponse } from "next/server";
import {
  backendPublicRequest,
  normalizeBackendError,
} from "@/lib/biomex-backend-server";

type KitOrderBody = {
  plan?: string;
  fullName?: string;
  email?: string;
  phone?: string;
  city?: string;
  message?: string;
};

export async function POST(req: NextRequest) {
  let body: KitOrderBody = {};

  try {
    body = (await req.json()) as KitOrderBody;
  } catch {
    // keep defaults
  }

  const response = await backendPublicRequest<{
    message?: string;
    request_id?: number;
    status?: string;
  }>("site-content/kit-orders/", {
    method: "POST",
    body: {
      plan: body.plan ?? "Kit Standard",
      full_name: body.fullName ?? "Visiteur BiomeX",
      email: body.email ?? "",
      phone: body.phone ?? "",
      city: body.city ?? "Dakar",
      message: body.message ?? "",
    },
  });

  if (!response.ok) {
    return NextResponse.json(
      {
        status: "error",
        message: normalizeBackendError(
          response,
          "La commande du kit a échoué. Veuillez réessayer.",
        ),
      },
      { status: 502 },
    );
  }

  return NextResponse.json({
    status: "ok",
    message:
      response.data?.message ??
      "Commande enregistrée. Notre équipe vous contacte rapidement.",
    requestId: response.data?.request_id ?? null,
  });
}
