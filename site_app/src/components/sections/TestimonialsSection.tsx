"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import Image from "next/image";
import { ChevronLeft, ChevronRight, Quote, Star } from "lucide-react";
import { Button } from "@/components/ui/button";

const testimonials = [
  {
    id: 1,
    name: "Aminata Diallo",
    role: "Entrepreneuse, Dakar",
    image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&h=150&fit=crop&crop=face",
    quote: "Grâce à BiomeX, j'ai découvert que mon microbiome réagissait très bien aux aliments locaux comme le mil et le fonio. En 3 mois, mes problèmes de digestion ont disparu. Une révélation pour ma santé !",
    improvement: "+35% diversité",
    rating: 5,
    product: "Kit Standard",
  },
  {
    id: 2,
    name: "Dr. Mamadou Sy",
    role: "Médecin généraliste, Thiès",
    image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
    quote: "En tant que professionnel de santé, je recommande BiomeX à mes patients diabétiques. L'analyse est rigoureuse et les recommandations sont basées sur des données africaines, pas sur des standards occidentaux.",
    improvement: "Expert validé",
    rating: 5,
    product: "B2B Clinique",
  },
  {
    id: 3,
    name: "Fatou Ndiaye",
    role: "Nutritionniste, Saly",
    image: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face",
    quote: "J'utilise BiomeX avec mes clients depuis 6 mois. Je peux enfin leur donner des conseils basés sur leur propre microbiome et sur des aliments qu'ils consomment réellement.",
    improvement: "50+ patients",
    rating: 5,
    product: "Pro Panel",
  },
  {
    id: 4,
    name: "Ibrahima Konaté",
    role: "Athlète amateur, Dakar",
    image: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face",
    quote: "BiomeX m'a aidé à optimiser mon alimentation pour mes entraînements. J'ai découvert que les céréales locales comme le niébé étaient parfaites pour mon microbiome intestinal.",
    improvement: "+20% énergie",
    rating: 5,
    product: "Sport Plan",
  },
  {
    id: 5,
    name: "Mariama Ba",
    role: "Enseignante, Rufisque",
    image: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&h=150&fit=crop&crop=face",
    quote: "Après des années de problèmes digestifs, BiomeX m'a permis de comprendre mon corps. Les recommandations sur le pain de mil et les feuilles de baobab ont changé ma vie quotidienne.",
    improvement: "Santé améliorée",
    rating: 5,
    product: "Kit Standard",
  },
];

export default function TestimonialsSection() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [direction, setDirection] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setDirection(1);
      setCurrentIndex((prev) => (prev + 1) % testimonials.length);
    }, 6000);

    return () => clearInterval(timer);
  }, []);

  const slideVariants = {
    enter: (direction: number) => ({
      x: direction > 0 ? 300 : -300,
      opacity: 0,
    }),
    center: {
      zIndex: 1,
      x: 0,
      opacity: 1,
    },
    exit: (direction: number) => ({
      zIndex: 0,
      x: direction < 0 ? 300 : -300,
      opacity: 0,
    }),
  };

  const next = () => {
    setDirection(1);
    setCurrentIndex((prev) => (prev + 1) % testimonials.length);
  };

  const prev = () => {
    setDirection(-1);
    setCurrentIndex((prev) => (prev - 1 + testimonials.length) % testimonials.length);
  };

  return (
    <section className="py-24 bg-secondary overflow-hidden">
      <div className="mx-auto max-w-7xl px-6">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
        >
          <span className="inline-flex items-center gap-2 rounded-full bg-accent/10 px-4 py-1.5 text-sm font-bold text-accent mb-4">
            <Star className="h-4 w-4" />
            Témoignages
          </span>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-extrabold text-primary">
            Ils ont transformé leur santé
          </h2>
          <p className="mt-4 text-lg text-slate-600 max-w-2xl mx-auto">
            Découvrez comment BiomeX aide les populations africaines à mieux comprendre leur microbiome.
          </p>
        </motion.div>

        <div className="relative">
          {/* Main Testimonial */}
          <div className="relative h-[400px] md:h-[350px] flex items-center justify-center">
            <AnimatePresence initial={false} custom={direction} mode="wait">
              <motion.div
                key={currentIndex}
                custom={direction}
                variants={slideVariants}
                initial="enter"
                animate="center"
                exit="exit"
                transition={{
                  x: { type: "spring", stiffness: 300, damping: 30 },
                  opacity: { duration: 0.2 },
                }}
                className="absolute w-full max-w-4xl mx-auto"
              >
                <div className="bg-white rounded-3xl p-8 md:p-12 shadow-xl border border-primary/5">
                  <div className="flex flex-col md:flex-row gap-8 items-center">
                    {/* Avatar & Info */}
                    <div className="flex flex-col items-center text-center md:text-left md:items-start">
                      <div className="relative">
                        <div className="h-20 w-20 md:h-24 md:w-24 rounded-full overflow-hidden border-4 border-primary/10">
                          <Image
                            src={testimonials[currentIndex].image}
                            alt={testimonials[currentIndex].name}
                            width={96}
                            height={96}
                            className="object-cover"
                          />
                        </div>
                        <div className="absolute -bottom-2 -right-2 bg-accent text-white text-xs px-2 py-1 rounded-full font-bold">
                          {testimonials[currentIndex].improvement}
                        </div>
                      </div>
                      <h4 className="mt-4 text-lg font-bold text-primary">
                        {testimonials[currentIndex].name}
                      </h4>
                      <p className="text-sm text-slate-500">
                        {testimonials[currentIndex].role}
                      </p>
                      <div className="flex items-center gap-1 mt-2">
                        {[...Array(testimonials[currentIndex].rating)].map((_, i) => (
                          <Star key={i} className="h-4 w-4 text-accent fill-current" />
                        ))}
                      </div>
                    </div>

                    {/* Quote */}
                    <div className="flex-1 relative">
                      <Quote className="h-10 w-10 text-primary/10 absolute -top-4 -left-4" />
                      <blockquote className="text-lg md:text-xl text-slate-700 leading-relaxed italic pl-6">
                        &quot;{testimonials[currentIndex].quote}&quot;
                      </blockquote>
                      <div className="mt-4 flex items-center gap-2 pl-6">
                        <span className="text-xs font-semibold text-slate-400">Produit:</span>
                        <span className="text-xs font-bold text-primary bg-primary/10 px-3 py-1 rounded-full">
                          {testimonials[currentIndex].product}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Navigation */}
          <div className="flex items-center justify-center gap-4 mt-8">
            <Button
              variant="outline"
              size="icon"
              className="rounded-full border-primary/20 hover:bg-primary/5"
              onClick={prev}
            >
              <ChevronLeft className="h-5 w-5 text-primary" />
            </Button>

            <div className="flex gap-2">
              {testimonials.map((_, index) => (
                <button
                  key={index}
                  className={`h-2 rounded-full transition-all ${
                    index === currentIndex
                      ? "w-8 bg-primary"
                      : "w-2 bg-primary/20 hover:bg-primary/40"
                  }`}
                  onClick={() => {
                    setDirection(index > currentIndex ? 1 : -1);
                    setCurrentIndex(index);
                  }}
                />
              ))}
            </div>

            <Button
              variant="outline"
              size="icon"
              className="rounded-full border-primary/20 hover:bg-primary/5"
              onClick={next}
            >
              <ChevronRight className="h-5 w-5 text-primary" />
            </Button>
          </div>
        </div>

        {/* Stats */}
        <motion.div
          className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.3 }}
        >
          {[
            { value: "80%+", label: "Précision algorithmes" },
            { value: "500+", label: "Patients pilote An 1" },
            { value: "5", label: "Pays cibles à 36 mois" },
            { value: "NPS 45+", label: "Score satisfaction" },
          ].map((stat, i) => (
            <div key={i} className="text-center p-4 rounded-2xl bg-white border border-primary/5">
              <p className="text-2xl md:text-3xl font-bold text-primary">{stat.value}</p>
              <p className="text-sm text-slate-500 mt-1">{stat.label}</p>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
