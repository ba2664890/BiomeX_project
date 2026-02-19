"use client";

import { motion } from "framer-motion";
import { ArrowRight, Play, ShieldCheck, Sparkles, TimerReset } from "lucide-react";
import { Button } from "@/components/ui/button";
import Image from "next/image";
import { useState } from "react";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { VisuallyHidden } from "@radix-ui/react-visually-hidden";

const points = [
  { icon: ShieldCheck, label: "Données privées et sécurisées" },
  { icon: TimerReset, label: "Résultats livrés en 21 jours" },
  { icon: Sparkles, label: "Recommandations adaptées au contexte local" },
];

const stats = [
  { value: "2 400+", label: "analyses réalisées" },
  { value: "4.9/5", label: "satisfaction moyenne" },
  { value: "14 j", label: "stabilité du kit" },
];

export default function HeroSection() {
  const [isVideoOpen, setIsVideoOpen] = useState(false);

  const scrollToSection = (id: string) => {
    const element = document.querySelector(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <section id="decouvrir" className="relative overflow-hidden py-20 lg:py-28">
      <div className="absolute inset-0 bg-gradient-to-b from-white via-secondary/40 to-white" />
      <div className="absolute inset-x-0 top-0 h-[340px] bg-[radial-gradient(ellipse_at_top,rgba(26,76,61,0.14),transparent_70%)]" />
      <motion.div
        className="absolute -top-14 right-10 h-52 w-52 rounded-full bg-accent/15 blur-3xl"
        animate={{ scale: [1, 1.08, 1], opacity: [0.4, 0.55, 0.4] }}
        transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute -bottom-16 left-0 h-64 w-64 rounded-full bg-primary/10 blur-3xl"
        animate={{ scale: [1.05, 1, 1.05], opacity: [0.35, 0.5, 0.35] }}
        transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
      />
      <div className="absolute inset-0 bg-[linear-gradient(rgba(26,76,61,0.025)_1px,transparent_1px),linear-gradient(90deg,rgba(26,76,61,0.025)_1px,transparent_1px)] bg-[size:52px_52px]" />

      <div className="relative z-10 mx-auto max-w-7xl px-6">
        <div className="grid items-center gap-12 lg:grid-cols-[1.05fr_0.95fr] lg:gap-14">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <span className="inline-flex items-center gap-2 rounded-full border border-primary/15 bg-white/85 px-4 py-1.5 text-xs font-semibold uppercase tracking-[0.15em] text-primary shadow-sm">
              <Sparkles className="h-3.5 w-3.5" />
              Découvrir BiomeX
            </span>

            <h1 className="mt-5 max-w-2xl text-4xl font-extrabold leading-tight tracking-tight text-primary sm:text-5xl lg:text-6xl">
              Comprenez votre microbiome,
              <span className="block bg-gradient-to-r from-accent via-yellow-600 to-accent bg-clip-text text-transparent">
                puis agissez simplement.
              </span>
            </h1>

            <p className="mt-6 max-w-xl text-base leading-relaxed text-slate-600 sm:text-lg">
              Un kit à domicile, une analyse fiable, puis des recommandations nutritionnelles concrètes
              pour votre profil et vos habitudes alimentaires locales.
            </p>

            <div className="mt-7 space-y-3">
              {points.map((point) => (
                <div
                  key={point.label}
                  className="flex items-center gap-3 rounded-xl border border-primary/10 bg-white/80 px-4 py-3 shadow-sm backdrop-blur-sm"
                >
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary">
                    <point.icon className="h-4 w-4" />
                  </div>
                  <span className="text-sm font-medium text-slate-700">{point.label}</span>
                </div>
              ))}
            </div>

            <div className="mt-8 flex flex-wrap gap-3">
              <Button
                size="lg"
                className="rounded-full bg-primary px-8 py-6 text-base font-bold text-white shadow-xl shadow-primary/25 hover:shadow-primary/40"
                onClick={() => scrollToSection("#pricing")}
              >
                Commander mon kit
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="rounded-full border-primary/20 px-8 py-6 text-base font-semibold text-primary hover:bg-white"
                onClick={() => setIsVideoOpen(true)}
              >
                <Play className="mr-2 h-4 w-4 fill-current" />
                Regarder la démo
              </Button>
            </div>

            <div className="mt-8 grid max-w-xl grid-cols-3 gap-3">
              {stats.map((stat) => (
                <div
                  key={stat.label}
                  className="rounded-2xl border border-primary/10 bg-white/75 px-4 py-3 text-center shadow-sm backdrop-blur-sm"
                >
                  <p className="text-lg font-extrabold text-primary sm:text-xl">{stat.value}</p>
                  <p className="mt-0.5 text-xs text-slate-500">{stat.label}</p>
                </div>
              ))}
            </div>
          </motion.div>

          <motion.div
            className="relative"
            initial={{ opacity: 0, y: 28 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.65, delay: 0.15 }}
          >
            <button
              type="button"
              className="group relative block w-full text-left"
              onClick={() => setIsVideoOpen(true)}
            >
              <div className="relative overflow-hidden rounded-3xl border border-primary/15 bg-white shadow-2xl shadow-primary/10">
                <div className="aspect-[16/10]">
                  <Image
                    src="https://images.unsplash.com/photo-1576086213369-97a306d36557?w=1200&h=800&fit=crop"
                    alt="Démo BiomeX"
                    width={1200}
                    height={800}
                    className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                    priority
                  />
                </div>
                <div className="absolute inset-0 bg-gradient-to-t from-primary/70 via-primary/10 to-transparent" />

                <div className="absolute left-5 top-5 rounded-full bg-white/90 px-3 py-1 text-xs font-semibold text-primary shadow-sm">
                  Démo rapide • 2 min
                </div>

                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-white/90 text-primary shadow-2xl transition-transform group-hover:scale-110">
                    <Play className="h-7 w-7 fill-current" />
                  </div>
                </div>

                <div className="absolute bottom-5 left-5 right-5">
                  <h2 className="text-xl font-bold text-white sm:text-2xl">
                    Comment BiomeX fonctionne concrètement
                  </h2>
                  <p className="mt-1 text-sm text-white/85">
                    De l’échantillon aux recommandations personnalisées.
                  </p>
                </div>
              </div>
            </button>

            <div className="pointer-events-none absolute -z-10 -right-6 -top-6 h-full w-full rounded-3xl border border-primary/10 bg-gradient-to-br from-primary/10 via-transparent to-accent/10" />
          </motion.div>
        </div>
      </div>

      {/* Video Modal */}
      <Dialog open={isVideoOpen} onOpenChange={setIsVideoOpen}>
        <DialogContent className="max-w-4xl w-full p-0 overflow-hidden rounded-2xl">
          <VisuallyHidden>
            <DialogTitle>BiomeX - Démonstration</DialogTitle>
          </VisuallyHidden>
          <div className="aspect-video bg-slate-900 relative">
            {isVideoOpen && (
              <iframe
                className="w-full h-full"
                src="https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1"
                title="BiomeX Demo"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            )}
          </div>
        </DialogContent>
      </Dialog>
    </section>
  );
}
