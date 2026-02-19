"use client";

import { motion } from "framer-motion";
import { Check, X, Sparkles, Dna, Globe, Zap } from "lucide-react";

const features = [
  {
    name: "Données africaines entraînant l'IA",
    biomex: true,
    others: false,
  },
  {
    name: "Séquençage local (UCAD/Pasteur)",
    biomex: true,
    others: false,
  },
  {
    name: "Prix adapté au marché africain",
    biomex: true,
    others: false,
  },
  {
    name: "Recommandations alimentaires locales",
    biomex: true,
    others: "Partiel",
  },
  {
    name: "App multilingue (FR, Wolof, Dioula)",
    biomex: true,
    others: false,
  },
  {
    name: "Kit stabilisé 14j température ambiante",
    biomex: true,
    others: "Variable",
  },
  {
    name: "Fonctionnalités offline",
    biomex: true,
    others: false,
  },
  {
    name: "Partenariats cliniques africains",
    biomex: true,
    others: false,
  },
  {
    name: "Base de données africaines",
    biomex: "5 000+ cible",
    others: "0",
  },
  {
    name: "Prix du kit",
    biomex: "75 $",
    others: "300-400 $",
  },
];

const competitors = [
  { name: "Viome (USA)", price: "300-400 $", focus: "Données non africaines" },
  { name: "ZOE (UK)", price: "~300 $", focus: "UK/US exclusivement" },
  { name: "Sun Genomics", price: "200 $+", focus: "Pas de présence africaine" },
  { name: "Carbiotix (EU)", price: "100 $+", focus: "Focus Europe" },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, x: -20 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.3 },
  },
};

export default function CompareSection() {
  return (
    <section className="py-24 bg-white">
      <div className="mx-auto max-w-6xl px-6">
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
        >
          <span className="inline-flex items-center gap-2 rounded-full bg-accent/10 px-4 py-1.5 text-sm font-bold text-accent mb-4">
            <Sparkles className="h-4 w-4" />
            Avantage Compétitif
          </span>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-extrabold text-primary">
            BiomeX vs. Concurrents
          </h2>
          <p className="mt-4 text-lg text-slate-600 max-w-2xl mx-auto">
            Le seul acteur à combiner données locales, prix adapté et mission d&apos;équité scientifique.
          </p>
        </motion.div>

        {/* Competitors Grid */}
        <motion.div
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          {competitors.map((comp, i) => (
            <div
              key={i}
              className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-center"
            >
              <p className="font-bold text-slate-700">{comp.name}</p>
              <p className="text-sm text-accent font-semibold">{comp.price}</p>
              <p className="text-xs text-slate-500 mt-1">{comp.focus}</p>
            </div>
          ))}
        </motion.div>

        <motion.div
          className="bg-gradient-to-br from-secondary/50 to-white rounded-3xl overflow-hidden shadow-xl border border-primary/5"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
        >
          {/* Header */}
          <div className="grid grid-cols-3 bg-primary/5 border-b border-primary/10">
            <div className="p-6 md:p-8">
              <h3 className="font-bold text-slate-600">Fonctionnalités</h3>
            </div>
            <div className="p-6 md:p-8 text-center border-x border-primary/10 bg-primary/5">
              <div className="flex flex-col items-center gap-2">
                <div className="h-10 w-10 rounded-xl bg-primary flex items-center justify-center">
                  <Dna className="h-5 w-5 text-white" />
                </div>
                <h3 className="font-extrabold text-primary text-lg">BiomeX</h3>
              </div>
            </div>
            <div className="p-6 md:p-8 text-center">
              <div className="flex flex-col items-center gap-2">
                <div className="h-10 w-10 rounded-xl bg-slate-200 flex items-center justify-center">
                  <Globe className="h-5 w-5 text-slate-400" />
                </div>
                <h3 className="font-semibold text-slate-400">Concurrents</h3>
              </div>
            </div>
          </div>

          {/* Features */}
          {features.map((feature, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              className={`grid grid-cols-3 border-b border-primary/5 last:border-0 hover:bg-primary/5 transition-colors ${
                index === features.length - 1 ? "bg-primary/10" : ""
              }`}
            >
              <div className="p-4 md:p-6 flex items-center">
                <span className="text-sm md:text-base text-slate-700">{feature.name}</span>
              </div>
              <div className="p-4 md:p-6 flex justify-center items-center border-x border-primary/5 bg-primary/5">
                {typeof feature.biomex === "boolean" ? (
                  feature.biomex ? (
                    <div className="h-7 w-7 rounded-full bg-green-500 flex items-center justify-center">
                      <Check className="h-4 w-4 text-white" />
                    </div>
                  ) : (
                    <div className="h-7 w-7 rounded-full bg-slate-200 flex items-center justify-center">
                      <X className="h-4 w-4 text-slate-400" />
                    </div>
                  )
                ) : (
                  <span className="font-bold text-primary text-sm md:text-base">{feature.biomex}</span>
                )}
              </div>
              <div className="p-4 md:p-6 flex justify-center items-center">
                {typeof feature.others === "boolean" ? (
                  feature.others ? (
                    <div className="h-7 w-7 rounded-full bg-green-500 flex items-center justify-center">
                      <Check className="h-4 w-4 text-white" />
                    </div>
                  ) : (
                    <div className="h-7 w-7 rounded-full bg-slate-200 flex items-center justify-center">
                      <X className="h-4 w-4 text-slate-400" />
                    </div>
                  )
                ) : (
                  <span className="text-slate-500 text-sm md:text-base">{feature.others}</span>
                )}
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Bottom CTA */}
        <motion.div
          className="mt-12 text-center"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.3 }}
        >
          <div className="inline-flex flex-col sm:flex-row items-center gap-4 p-6 rounded-2xl bg-accent/10 border border-accent/20">
            <Zap className="h-8 w-8 text-accent" />
            <div className="text-left">
              <p className="font-bold text-primary">Économisez jusqu&apos;à 75%</p>
              <p className="text-sm text-slate-600">75$ vs 300-400$ chez les concurrents internationaux</p>
            </div>
            <a
              href="#pricing"
              className="rounded-full bg-accent px-6 py-3 text-sm font-bold text-white hover:bg-accent/90 transition-colors"
              onClick={(e) => {
                e.preventDefault();
                document.querySelector("#pricing")?.scrollIntoView({ behavior: "smooth" });
              }}
            >
              Commander maintenant
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
