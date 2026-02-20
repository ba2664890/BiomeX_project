"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Dna, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "@/hooks/use-toast";

type FooterLink = {
  label: string;
  href: string;
  external?: boolean;
};

const platformLinks = [
  { label: "Commander le kit", href: "#pricing" },
  { label: "Comment ça marche", href: "#comment-ca-marche" },
  { label: "La science", href: "#science" },
  { label: "FAQ", href: "#faq" },
];

const companyLinks: FooterLink[] = [
  { label: "À propos", href: "#science" },
  { label: "Partenaires", href: "#comment-ca-marche" },
  { label: "Blog", href: "#blog" },
  { label: "Presse", href: "mailto:presse@biomex.ai", external: true },
];

const socialLinks = [
  { icon: "share", label: "Partager", href: "https://www.linkedin.com/company/biomex-health/", external: true },
  { icon: "alternate_email", label: "Email", href: "mailto:contact@biomex.ai", external: true },
  { icon: "person_pin", label: "LinkedIn", href: "https://www.linkedin.com/company/biomex-health/", external: true },
];

export default function Footer() {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubscribe = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    try {
      setIsLoading(true);
      const response = await fetch("/api/site/subscribe", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ email }),
      });

      const data = (await response.json()) as {
        status?: string;
        message?: string;
      };

      if (!response.ok || data.status !== "ok") {
        throw new Error(data.message ?? "Inscription impossible.");
      }

      setEmail("");
      toast({
        title: "Inscription réussie !",
        description: data.message ?? "Vous recevrez nos dernières découvertes santé.",
      });
    } catch (error) {
      toast({
        title: "Erreur d'inscription",
        description:
          error instanceof Error
            ? error.message
            : "Une erreur est survenue, merci de réessayer.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleNavClick = (href: string, external = false) => {
    if (external || !href.startsWith("#")) {
      window.open(href, "_blank");
      return;
    }

    const element = document.querySelector(href);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
      return;
    }

    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <footer className="bg-[#141e1b] py-16 md:py-20 text-white mt-auto">
      <div className="mx-auto max-w-7xl px-6">
        <div className="grid gap-12 lg:grid-cols-4">
          {/* Brand */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <button
              type="button"
              className="flex items-center gap-3"
              onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
            >
              <div className="flex h-8 w-8 items-center justify-center rounded bg-primary">
                <Dna className="h-4 w-4" />
              </div>
              <span className="text-xl font-extrabold tracking-tight">
                BiomeX
              </span>
            </button>
            <p className="mt-6 text-slate-400 leading-relaxed text-sm">
              L&apos;avenir de la santé préventive en Afrique, alimenté par la
              génétique et l&apos;intelligence artificielle.
            </p>
          </motion.div>

          {/* Platform Links */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <h4 className="mb-6 font-bold uppercase tracking-widest text-sm text-slate-500">
              Plateforme
            </h4>
            <ul className="space-y-4 text-slate-400">
              {platformLinks.map((link) => (
                <li key={link.label}>
                  <button
                    onClick={() => handleNavClick(link.href)}
                    className="hover:text-accent transition-colors text-sm"
                  >
                    {link.label}
                  </button>
                </li>
              ))}
            </ul>
          </motion.div>

          {/* Company Links */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <h4 className="mb-6 font-bold uppercase tracking-widest text-sm text-slate-500">
              Société
            </h4>
            <ul className="space-y-4 text-slate-400">
              {companyLinks.map((link) => (
                <li key={link.label}>
                  <button
                    onClick={() => handleNavClick(link.href, link.external)}
                    className="hover:text-accent transition-colors text-sm"
                  >
                    {link.label}
                  </button>
                </li>
              ))}
            </ul>
          </motion.div>

          {/* Newsletter */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <h4 className="mb-6 font-bold uppercase tracking-widest text-sm text-slate-500">
              Newsletter
            </h4>
            <p className="mb-4 text-sm text-slate-400">
              Recevez nos dernières découvertes santé.
            </p>
            <form onSubmit={handleSubscribe} className="flex flex-col gap-3">
              <Input
                type="email"
                placeholder="votre@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="rounded-xl border-none bg-white/5 px-4 py-3 text-white placeholder:text-slate-600 focus:ring-2 focus:ring-primary text-sm"
              />
              <Button
                type="submit"
                disabled={isLoading}
                className="rounded-xl bg-primary py-3 font-bold hover:bg-primary/80 transition-all text-sm"
              >
                {isLoading ? (
                  "Envoi en cours..."
                ) : (
                  <span className="flex items-center gap-2">
                    S&apos;abonner
                    <Send className="h-4 w-4" />
                  </span>
                )}
              </Button>
            </form>
          </motion.div>
        </div>

        {/* Bottom Bar */}
        <motion.div
          className="mt-16 flex flex-col items-center justify-between border-t border-white/10 pt-8 md:flex-row gap-4"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <p className="text-sm text-slate-500">
            © 2024 BiomeX Health. Tous droits réservés.
          </p>
          <div className="flex gap-6">
            {socialLinks.map((social, index) => (
              <button
                key={index}
                className="text-slate-500 hover:text-white transition-colors"
                aria-label={social.label}
                onClick={() => handleNavClick(social.href, social.external)}
              >
                <div className="h-5 w-5 rounded-full bg-white/10 hover:bg-white/20 transition-colors" />
              </button>
            ))}
          </div>
        </motion.div>
      </div>
    </footer>
  );
}
