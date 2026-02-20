import { NextResponse } from "next/server";
import {
  backendPublicRequest,
  normalizeBackendError,
} from "@/lib/biomex-backend-server";

type SiteMetric = {
  key?: string;
  value?: string;
};

type SiteArticle = {
  category?: string;
  title?: string;
  excerpt?: string;
  image_url?: string;
  slug?: string;
};

type SiteHomePayload = {
  data?: {
    metrics?: SiteMetric[];
    latest_articles?: SiteArticle[];
  };
};

const fallbackImages = [
  "https://images.unsplash.com/photo-1515543237350-b3eea1ec8082?w=600&h=400&fit=crop",
  "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600&h=400&fit=crop",
  "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=600&h=400&fit=crop",
];

function getMetric(metrics: SiteMetric[] | undefined, key: string, fallback = "") {
  const found = metrics?.find((metric) => metric.key === key)?.value;
  return found ?? fallback;
}

function toNumber(value: string, fallback = 0) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function buildBlogCards(articles: SiteArticle[] | undefined) {
  const cards =
    articles?.slice(0, 3).map((article, index) => ({
      category: article.category?.toUpperCase() ?? "BLOG",
      title: article.title ?? "Article BiomeX",
      excerpt:
        article.excerpt ??
        "Découvrez les dernières recommandations issues de votre écosystème intestinal.",
      image: article.image_url || fallbackImages[index % fallbackImages.length],
      imageAlt: article.title ?? "Article BiomeX",
      href: article.slug ? `/blog/${article.slug}` : "#blog",
    })) ?? [];

  while (cards.length < 3) {
    const index = cards.length;
    cards.push({
      category: "BIOMEX",
      title: "Nutrition personnalisée",
      excerpt: "Des conseils pratiques issus de vos données biologiques.",
      image: fallbackImages[index % fallbackImages.length],
      imageAlt: "Article BiomeX",
      href: "#blog",
    });
  }

  return cards;
}

export async function GET() {
  const response = await backendPublicRequest<SiteHomePayload>("site-content/home/");

  if (!response.ok) {
    return NextResponse.json(
      {
        status: "error",
        message: normalizeBackendError(
          response,
          "Impossible de charger le contenu du site.",
        ),
      },
      { status: 502 },
    );
  }

  const metrics = response.data?.data?.metrics ?? [];
  const articles = response.data?.data?.latest_articles ?? [];

  const overallScore = toNumber(getMetric(metrics, "overall_score", "82"), 82);
  const diversityScore = toNumber(getMetric(metrics, "diversity_score", "78"), 78);
  const speciesCount = toNumber(getMetric(metrics, "species_count", "1247"), 1247);
  const recommendationsCount = toNumber(
    getMetric(metrics, "recommendations_count", "12"),
    12,
  );
  const topSuperfood = getMetric(metrics, "top_superfood", "Fonio");

  return NextResponse.json({
    status: "ok",
    data: {
      hero: {
        overallScore,
        diversityScore,
        speciesCount,
        recommendationsCount,
      },
      superfoods: [{ name: topSuperfood }],
      blogCards: buildBlogCards(articles),
      raw: response.data?.data ?? {},
    },
  });
}
