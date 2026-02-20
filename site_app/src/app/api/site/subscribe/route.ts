import { NextRequest, NextResponse } from "next/server";
import {
  backendPublicRequest,
  normalizeBackendError,
} from "@/lib/biomex-backend-server";

type SubscribeBody = {
  email?: string;
  fullName?: string;
};

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export async function POST(req: NextRequest) {
  let body: SubscribeBody = {};

  try {
    body = (await req.json()) as SubscribeBody;
  } catch {
    // keep defaults
  }

  const email = body.email?.trim().toLowerCase();

  if (!email || !EMAIL_REGEX.test(email)) {
    return NextResponse.json(
      {
        status: "error",
        message: "Veuillez fournir un email valide.",
      },
      { status: 400 },
    );
  }

  const response = await backendPublicRequest<{
    message?: string;
    subscription_id?: number;
  }>("site-content/newsletter/", {
    method: "POST",
    body: {
      email,
      full_name: body.fullName ?? "",
      source: "site_app_footer",
    },
  });

  if (!response.ok) {
    return NextResponse.json(
      {
        status: "error",
        message: normalizeBackendError(
          response,
          "Impossible de traiter l'inscription newsletter.",
        ),
      },
      { status: 502 },
    );
  }

  return NextResponse.json({
    status: "ok",
    message:
      response.data?.message ??
      "Inscription réussie. Vous recevrez nos prochaines mises à jour.",
    subscriptionId: response.data?.subscription_id ?? null,
  });
}
