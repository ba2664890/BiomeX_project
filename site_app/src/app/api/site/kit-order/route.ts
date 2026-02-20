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
  country?: string;
  quantity?: number;
  unitPriceFcfa?: number;
  amountTotalFcfa?: number;
  currency?: string;
  paymentMethod?: string;
  paymentProvider?: string;
  paymentPhone?: string;
  paymentReference?: string;
  paymentLast4?: string;
  latitude?: number;
  longitude?: number;
  geolocationAccuracyMeters?: number;
  geolocationSource?: string;
  acceptedTerms?: boolean;
  source?: string;
  message?: string;
  metadata?: Record<string, unknown>;
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
    payment_status?: string;
    verification_flags?: string[];
    payment_verification_notes?: string;
    location?: {
      latitude?: number;
      longitude?: number;
      accuracy_meters?: number;
    };
  }>("site-content/kit-orders/", {
    method: "POST",
    body: {
      plan: body.plan ?? "Kit Standard",
      full_name: body.fullName ?? "Visiteur BiomeX",
      email: body.email ?? "",
      phone: body.phone ?? "",
      city: body.city ?? "Dakar",
      country: body.country ?? "Senegal",
      quantity: body.quantity ?? 1,
      unit_price_fcfa: body.unitPriceFcfa ?? 0,
      amount_total_fcfa: body.amountTotalFcfa ?? 0,
      currency: body.currency ?? "XOF",
      payment_method: body.paymentMethod ?? "orange_money",
      payment_provider: body.paymentProvider ?? "",
      payment_phone: body.paymentPhone ?? "",
      payment_reference: body.paymentReference ?? "",
      payment_last4: body.paymentLast4 ?? "",
      latitude: body.latitude,
      longitude: body.longitude,
      geolocation_accuracy_meters: body.geolocationAccuracyMeters,
      geolocation_source: body.geolocationSource ?? "browser_gps",
      accepted_terms: body.acceptedTerms ?? false,
      source: body.source ?? "site_app_pricing",
      message: body.message ?? "",
      metadata: body.metadata ?? {},
    },
  });

  if (!response.ok) {
    const status = response.status >= 400 && response.status < 500 ? response.status : 502;
    return NextResponse.json(
      {
        status: "error",
        upstreamStatus: response.status,
        message: normalizeBackendError(
          response,
          "La commande du kit a échoué. Veuillez réessayer.",
        ),
      },
      { status },
    );
  }

  return NextResponse.json({
    status: "ok",
    message:
      response.data?.message ??
      "Commande enregistrée. Notre équipe vous contacte rapidement.",
    requestId: response.data?.request_id ?? null,
    paymentStatus: response.data?.payment_status ?? "pending",
    verificationFlags: response.data?.verification_flags ?? [],
    paymentVerificationNotes: response.data?.payment_verification_notes ?? "",
    location: response.data?.location ?? null,
  });
}
