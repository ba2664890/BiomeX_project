"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import Image from "next/image";

type BlogPost = {
  category: string;
  title: string;
  excerpt: string;
  image: string;
  imageAlt: string;
  href: string;
};

const fallbackBlogPosts: BlogPost[] = [
  {
    category: "SUPERFOOD",
    title: "Le Mil : Le probiotique naturel ignoré.",
    excerpt:
      "Comment les fibres de mil agissent spécifiquement sur les bactéries Bifido des populations d'Afrique de l'Ouest.",
    image:
      "https://images.unsplash.com/photo-1515543237350-b3eea1ec8082?w=600&h=400&fit=crop",
    imageAlt: "Bol de mil perlé cuit avec des légumes",
    href: "#science",
  },
  {
    category: "RECHERCHE",
    title: "Fonio et Digestion : Ce que dit la science.",
    excerpt:
      "Une étude de l'UCAD révèle les bénéfices du fonio sur la régulation de l'insuline.",
    image:
      "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600&h=400&fit=crop",
    imageAlt: "Champs de fonio doré au soleil",
    href: "#comment-ca-marche",
  },
  {
    category: "TECH",
    title: "IA & Microbiome : Pourquoi 16S ?",
    excerpt:
      "Comprendre la technologie derrière le séquençage de l'ARN ribosomal 16S.",
    image:
      "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=600&h=400&fit=crop",
    imageAlt: "Laboratoire moderne avec séquençage ADN",
    href: "#pricing",
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: "easeOut" },
  },
};

export default function BlogSection() {
  const [blogPosts, setBlogPosts] = useState<BlogPost[]>(fallbackBlogPosts);

  useEffect(() => {
    let cancelled = false;

    const loadBackendContent = async () => {
      try {
        const response = await fetch("/api/site/dashboard", { cache: "no-store" });
        if (!response.ok) return;

        const payload = (await response.json()) as {
          data?: { blogCards?: BlogPost[] };
        };

        const cards = payload.data?.blogCards;
        if (!cancelled && cards && cards.length > 0) {
          setBlogPosts(cards.slice(0, 3));
        }
      } catch {
        // Keep fallback cards when backend is unavailable.
      }
    };

    void loadBackendContent();

    return () => {
      cancelled = true;
    };
  }, []);

  const handleLink = (href: string) => {
    if (href.startsWith("#")) {
      const section = document.querySelector(href);
      if (section) {
        section.scrollIntoView({ behavior: "smooth" });
      }
      return;
    }

    window.open(href, "_blank");
  };

  return (
    <section id="blog" className="py-24">
      <div className="mx-auto max-w-7xl px-6">
        <motion.div
          className="mb-12 flex flex-col md:flex-row md:items-end md:justify-between gap-4"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.5 }}
        >
          <div>
            <h2 className="text-3xl md:text-4xl font-extrabold text-primary">
              Science & Nutrition
            </h2>
            <p className="mt-4 text-slate-500 text-lg">
              Derniers articles sur l&apos;alimentation africaine.
            </p>
          </div>
          <button
            type="button"
            className="font-bold text-primary hover:underline inline-flex items-center gap-2 group"
            onClick={() => handleLink("#faq")}
          >
            Voir les analyses
            <span className="group-hover:translate-x-1 transition-transform">→</span>
          </button>
        </motion.div>

        <motion.div
          className="grid gap-8 md:grid-cols-3"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
        >
          {blogPosts.map((post, index) => (
            <motion.article
              key={index}
              variants={itemVariants}
              className="group cursor-pointer"
              whileHover={{ y: -5 }}
              transition={{ duration: 0.3 }}
              onClick={() => handleLink(post.href)}
            >
              <div className="overflow-hidden rounded-2xl">
                <div className="aspect-video bg-slate-200 overflow-hidden">
                  <Image
                    src={post.image}
                    alt={post.imageAlt}
                    width={600}
                    height={400}
                    className="object-cover w-full h-full transition-transform duration-500 group-hover:scale-110"
                  />
                </div>
              </div>
              <div className="mt-6">
                <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-bold text-primary">
                  {post.category}
                </span>
                <h3 className="mt-3 text-xl font-bold text-primary group-hover:text-accent transition-colors">
                  {post.title}
                </h3>
                <p className="mt-2 text-slate-500 line-clamp-2">{post.excerpt}</p>
                <div className="mt-4 flex items-center gap-2 text-sm text-accent font-semibold opacity-0 group-hover:opacity-100 transition-opacity">
                  Lire l&apos;article
                  <span className="group-hover:translate-x-1 transition-transform">→</span>
                </div>
              </div>
            </motion.article>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
