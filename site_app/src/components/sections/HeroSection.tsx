"use client";

import { motion } from "framer-motion";
import { Play, Verified, Microscope, TrendingUp, Leaf, Shield, Award, Users, Sparkles, Dna, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import Image from "next/image";
import { useEffect, useState } from "react";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { VisuallyHidden } from "@radix-ui/react-visually-hidden";

const avatars = [
  { id: 1, src: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face", name: "Mamadou D." },
  { id: 2, src: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop&crop=face", name: "Aminata S." },
  { id: 3, src: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&h=100&fit=crop&crop=face", name: "Ibrahima K." },
  { id: 4, src: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop&crop=face", name: "Fatou N." },
];

const trustBadges = [
  { icon: Shield, label: "Certifié ISO 13485" },
  { icon: Award, label: "Partenariat UCAD" },
  { icon: Users, label: "2 400+ clients" },
];

const floatingCardTemplates = [
  {
    icon: TrendingUp,
    title: "Score Gut-Health",
    color: "from-green-500 to-emerald-600",
    position: "top-16 -left-4 lg:top-24 lg:-left-12",
  },
  {
    icon: Leaf,
    title: "Aliment détecté",
    color: "from-accent to-yellow-600",
    position: "bottom-16 right-0 lg:bottom-32 lg:-right-8",
  },
  {
    icon: Dna,
    title: "Bactéries",
    color: "from-primary to-teal-600",
    position: "top-1/2 -left-2 lg:-left-8 -translate-y-1/2",
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.12,
      delayChildren: 0.2,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: "easeOut" },
  },
};

const MICROBIOME_DEMO_VIDEO_URL = "https://www.youtube.com/embed/1sISguPDlhY?autoplay=1&rel=0";

export default function HeroSection() {
  const [isVideoOpen, setIsVideoOpen] = useState(false);
  const [heroData, setHeroData] = useState({
    overallScore: 82,
    speciesCount: 1247,
    recommendationsCount: 12,
    topSuperfood: "Fonio",
  });

  useEffect(() => {
    let cancelled = false;

    const loadHeroData = async () => {
      try {
        const response = await fetch("/api/site/dashboard", { cache: "no-store" });
        if (!response.ok) return;

        const payload = (await response.json()) as {
          data?: {
            hero?: {
              overallScore?: number;
              speciesCount?: number;
              recommendationsCount?: number;
            };
            superfoods?: Array<{ name?: string }>;
          };
        };

        if (cancelled) return;

        setHeroData((current) => ({
          overallScore: payload.data?.hero?.overallScore ?? current.overallScore,
          speciesCount: payload.data?.hero?.speciesCount ?? current.speciesCount,
          recommendationsCount:
            payload.data?.hero?.recommendationsCount ?? current.recommendationsCount,
          topSuperfood: payload.data?.superfoods?.[0]?.name ?? current.topSuperfood,
        }));
      } catch {
        // Keep fallback values if backend is unavailable.
      }
    };

    void loadHeroData();
    return () => {
      cancelled = true;
    };
  }, []);

  const heroCards = [
    {
      ...floatingCardTemplates[0],
      value: `${heroData.overallScore}/100`,
      change: `+${heroData.recommendationsCount}`,
    },
    {
      ...floatingCardTemplates[1],
      value: heroData.topSuperfood,
      subtitle: "Recommandé par l'IA",
    },
    {
      ...floatingCardTemplates[2],
      value: heroData.speciesCount.toLocaleString("fr-FR"),
      subtitle: "espèces analysées",
    },
  ];

  const scrollToSection = (id: string) => {
    const element = document.querySelector(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <section id="decouvrir" className="relative overflow-hidden py-20 lg:py-32 min-h-[90vh] flex items-center">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        {/* Base gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-white via-secondary/30 to-white" />
        
        {/* Animated blobs */}
        <motion.div
          className="absolute -top-40 -right-40 w-[500px] h-[500px] rounded-full bg-gradient-to-br from-primary/20 to-accent/10 blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 90, 0],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
        <motion.div
          className="absolute -bottom-40 -left-40 w-[600px] h-[600px] rounded-full bg-gradient-to-tr from-accent/15 to-primary/10 blur-3xl"
          animate={{
            scale: [1.2, 1, 1.2],
            rotate: [0, -90, 0],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
        
        {/* Grid pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(26,76,61,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(26,76,61,0.03)_1px,transparent_1px)] bg-[size:60px_60px]" />
        
        {/* Floating particles - fixed positions to avoid hydration mismatch */}
        {[
          { left: "15%", top: "20%" },
          { left: "85%", top: "15%" },
          { left: "25%", top: "75%" },
          { left: "75%", top: "80%" },
          { left: "10%", top: "50%" },
          { left: "90%", top: "45%" },
          { left: "35%", top: "10%" },
          { left: "65%", top: "90%" },
          { left: "45%", top: "35%" },
          { left: "55%", top: "65%" },
          { left: "20%", top: "40%" },
          { left: "80%", top: "60%" },
          { left: "30%", top: "85%" },
          { left: "70%", top: "25%" },
          { left: "40%", top: "55%" },
          { left: "60%", top: "45%" },
          { left: "5%", top: "30%" },
          { left: "95%", top: "70%" },
          { left: "50%", top: "5%" },
          { left: "50%", top: "95%" },
        ].map((pos, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 rounded-full bg-primary/20"
            style={{
              left: pos.left,
              top: pos.top,
            }}
            animate={{
              y: [0, -30, 0],
              opacity: [0.2, 0.5, 0.2],
            }}
            transition={{
              duration: 3 + (i % 3),
              repeat: Infinity,
              delay: i * 0.2,
            }}
          />
        ))}
      </div>

      <div className="mx-auto max-w-7xl px-6 relative z-10">
        <div className="grid items-center gap-12 lg:gap-20 lg:grid-cols-2">
          {/* Left Content */}
          <motion.div
            className="flex flex-col gap-6"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            <motion.div variants={itemVariants}>
              <div className="flex flex-wrap items-center gap-3 mb-6">
                <motion.span
                  className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-5 py-2 text-sm font-bold text-primary border border-primary/20"
                  whileHover={{ scale: 1.05 }}
                >
                  <Verified className="h-4 w-4" />
                  Technologie africaine
                </motion.span>
                <motion.span
                  className="inline-flex items-center gap-2 rounded-full bg-accent/10 px-5 py-2 text-sm font-bold text-accent border border-accent/20"
                  whileHover={{ scale: 1.05 }}
                >
                  🇸🇳 Made in Sénégal
                </motion.span>
              </div>
              
              <h1 className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-extrabold leading-[1.05] tracking-tight">
                <span className="text-primary">Votre microbiome.</span>
                <br />
                <span className="text-primary">Votre ADN.</span>
                <br />
                <span className="bg-gradient-to-r from-accent via-yellow-600 to-accent bg-clip-text text-transparent">
                  Votre santé.
                </span>
              </h1>
              
              <p className="mt-8 text-lg sm:text-xl text-slate-600 leading-relaxed max-w-xl">
                Explorez les <strong className="text-primary">100 trillions de micro-organismes</strong> qui composent votre identité génétique unique. 
                Technologie de séquençage <strong className="text-accent">16S rRNA</strong> conçue pour les populations africaines.
              </p>

              {/* Key benefits */}
              <div className="mt-8 grid grid-cols-2 gap-4">
                {[
                  { icon: Microscope, text: "Séquençage 16S rRNA", highlight: "95% précision" },
                  { icon: TrendingUp, text: "Résultats en 21 jours", highlight: "Rapide" },
                  { icon: Leaf, text: "Aliments locaux analysés", highlight: "Mil, Fonio" },
                  { icon: Shield, text: "Données 100% confidentielles", highlight: "Sécurisé" },
                ].map((benefit, i) => (
                  <motion.div
                    key={i}
                    className="flex items-start gap-3 p-3 rounded-xl bg-white/60 backdrop-blur-sm border border-primary/5 hover:border-primary/20 hover:bg-white/80 transition-all group"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.5 + i * 0.1 }}
                    whileHover={{ y: -2 }}
                  >
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary group-hover:bg-primary group-hover:text-white transition-colors flex-shrink-0">
                      <benefit.icon className="h-5 w-5" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-slate-700">{benefit.text}</p>
                      <p className="text-xs text-accent font-medium">{benefit.highlight}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            <motion.div className="flex flex-wrap gap-4 mt-4" variants={itemVariants}>
              <motion.div
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Button
                  size="lg"
                  className="rounded-full bg-primary px-10 py-7 text-base font-bold text-white shadow-2xl shadow-primary/30 hover:shadow-primary/50 transition-all group"
                  onClick={() => scrollToSection("#pricing")}
                >
                  Commander mon kit
                  <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </Button>
              </motion.div>
              <motion.div
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Button
                  size="lg"
                  variant="outline"
                  className="flex items-center gap-3 rounded-full px-8 py-7 text-base font-bold text-primary border-2 border-primary/20 hover:bg-primary/5 hover:border-primary/40 transition-all"
                  onClick={() => setIsVideoOpen(true)}
                >
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-accent text-white">
                    <Play className="h-5 w-5 ml-0.5" />
                  </div>
                  Voir la démo
                </Button>
              </motion.div>
            </motion.div>

            <motion.div className="flex flex-col sm:flex-row items-start sm:items-center gap-6 mt-4" variants={itemVariants}>
              <div className="flex items-center">
                <div className="flex -space-x-3">
                  {avatars.map((avatar, i) => (
                    <motion.div
                      key={avatar.id}
                      className="h-12 w-12 rounded-full border-3 border-white bg-slate-200 overflow-hidden shadow-lg hover:z-10 cursor-pointer"
                      title={avatar.name}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.8 + i * 0.1 }}
                      whileHover={{ scale: 1.15, zIndex: 10 }}
                    >
                      <Image
                        src={avatar.src}
                        alt={avatar.name}
                        width={48}
                        height={48}
                        className="object-cover"
                      />
                    </motion.div>
                  ))}
                  <motion.div
                    className="h-12 w-12 rounded-full border-3 border-white bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white text-sm font-bold shadow-lg"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 1.2 }}
                  >
                    +2K
                  </motion.div>
                </div>
              </div>
              <div>
                <p className="text-base font-medium text-slate-700">
                  <span className="font-bold text-primary">2 400+ membres</span> à Dakar nous font confiance
                </p>
                <div className="flex items-center gap-2 mt-1">
                  <div className="flex items-center gap-0.5">
                    {[...Array(5)].map((_, i) => (
                      <svg key={i} className="h-4 w-4 text-accent fill-current" viewBox="0 0 20 20">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                    ))}
                  </div>
                  <span className="text-sm font-semibold text-slate-600">4.9/5</span>
                  <span className="text-sm text-slate-400">sur 850+ avis</span>
                </div>
              </div>
            </motion.div>

            {/* Trust badges */}
            <motion.div
              className="flex flex-wrap gap-6 pt-6 mt-4 border-t border-primary/10"
              variants={itemVariants}
            >
              {trustBadges.map((badge, i) => (
                <motion.div
                  key={i}
                  className="flex items-center gap-2 text-sm text-slate-600 group cursor-pointer"
                  whileHover={{ scale: 1.05 }}
                >
                  <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                    <badge.icon className="h-4 w-4 text-primary" />
                  </div>
                  <span className="font-medium">{badge.label}</span>
                </motion.div>
              ))}
            </motion.div>
          </motion.div>

          {/* Right Content - 3D Illustration */}
          <motion.div
            className="relative flex justify-center lg:justify-end"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.3 }}
          >
            <div className="relative w-full max-w-[550px] aspect-square">
              {/* Main circular container */}
              <div className="absolute inset-0 flex items-center justify-center">
                <motion.div
                  className="w-[80%] h-[80%] rounded-full bg-gradient-to-br from-primary/5 via-accent/5 to-primary/5"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 60, repeat: Infinity, ease: "linear" }}
                />
              </div>
              
              {/* Central glow */}
              <div className="absolute inset-0 flex items-center justify-center">
                <motion.div
                  className="w-48 h-48 md:w-64 md:h-64 rounded-full bg-gradient-to-tr from-primary to-accent blur-[100px] opacity-30"
                  animate={{
                    scale: [1, 1.2, 1],
                    opacity: [0.3, 0.4, 0.3],
                  }}
                  transition={{
                    duration: 4,
                    repeat: Infinity,
                    ease: "easeInOut",
                  }}
                />
              </div>

              {/* Central DNA icon */}
              <motion.div
                className="absolute inset-0 flex items-center justify-center"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
              >
                <div className="relative">
                  <motion.div
                    className="absolute inset-0 flex items-center justify-center"
                    animate={{ rotate: -360 }}
                    transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
                  >
                    <Dna className="h-40 w-40 md:h-56 md:w-56 text-primary/5" />
                  </motion.div>
                  <motion.div
                    className="relative z-10 w-32 h-32 md:w-40 md:h-40 rounded-full bg-gradient-to-br from-primary to-primary/80 flex items-center justify-center shadow-2xl"
                    whileHover={{ scale: 1.1 }}
                  >
                    <Microscope className="h-16 w-16 md:h-20 md:w-20 text-white" />
                  </motion.div>
                </div>
              </motion.div>

              {/* Orbiting elements */}
              <motion.div
                className="absolute inset-0"
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              >
                <div className="absolute top-[15%] left-[15%] h-4 w-4 rounded-full bg-accent shadow-lg shadow-accent/50" />
                <div className="absolute bottom-[20%] right-[20%] h-3 w-3 rounded-full bg-green-500 shadow-lg shadow-green-500/50" />
                <div className="absolute top-[30%] right-[10%] h-2 w-2 rounded-full bg-primary shadow-lg shadow-primary/50" />
              </motion.div>

              {/* Floating Glass Cards */}
              {heroCards.map((card, index) => (
                <motion.div
                  key={index}
                  className={`absolute ${card.position}`}
                  initial={{ opacity: 0, y: 30, x: index === 2 ? -30 : 0 }}
                  animate={{ opacity: 1, y: 0, x: 0 }}
                  transition={{ duration: 0.6, delay: 0.8 + index * 0.2 }}
                >
                  <motion.div
                    className="glass rounded-2xl p-4 shadow-xl border border-white/50 backdrop-blur-xl min-w-[160px]"
                    whileHover={{ scale: 1.05, y: -5 }}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br ${card.color} text-white shadow-lg`}>
                        <card.icon className="h-5 w-5" />
                      </div>
                      <div>
                        <p className="text-xs font-bold uppercase tracking-wider text-slate-400">
                          {card.title}
                        </p>
                        <p className="text-xl font-extrabold text-primary">{card.value}</p>
                        {card.change && (
                          <p className="text-xs text-green-600 font-semibold">↑ {card.change}</p>
                        )}
                        {card.subtitle && (
                          <p className="text-xs text-accent font-medium">{card.subtitle}</p>
                        )}
                      </div>
                    </div>
                  </motion.div>
                </motion.div>
              ))}

              {/* Decorative rings */}
              <motion.div
                className="absolute inset-[10%] rounded-full border-2 border-dashed border-primary/10"
                animate={{ rotate: -360 }}
                transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
              />
              <motion.div
                className="absolute inset-[25%] rounded-full border border-accent/20"
                animate={{ rotate: 360 }}
                transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
              />
            </div>
          </motion.div>
        </div>
      </div>

      {/* Video Modal */}
      <Dialog open={isVideoOpen} onOpenChange={setIsVideoOpen}>
        <DialogContent className="w-[95vw] max-w-7xl p-0 overflow-hidden rounded-2xl">
          <VisuallyHidden>
            <DialogTitle>BiomeX - Démonstration</DialogTitle>
          </VisuallyHidden>
          <div className="aspect-video bg-slate-900 relative">
            {isVideoOpen && (
              <iframe
                className="w-full h-full"
                src={MICROBIOME_DEMO_VIDEO_URL}
                title="Microbiome: Meet your microbes"
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
