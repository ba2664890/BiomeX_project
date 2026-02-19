"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import { Package, Cpu, Smartphone, Thermometer, Database, Brain } from "lucide-react";

const steps = [
  {
    number: "01",
    title: "BiomeX Kit",
    titleExtra: "Prélèvement à domicile",
    description:
      "Kit stabilisé à température ambiante pendant 14 jours - plus besoin de chaîne du froid. Guide illustré multilingue (français, wolof, dioula). Livraison gratuite à Dakar.",
    image: "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600&h=600&fit=crop",
    imageAlt: "Kit de test BiomeX",
    reverse: false,
    tags: ["14 jours stabilité", "Sans froid", "Multilingue"],
  },
  {
    number: "02",
    title: "BiomeX Lab",
    titleExtra: "Séquençage local",
    description:
      "Séquençage 16S rRNA en partenariat avec UCAD et Institut Pasteur. Coût 40-50$ vs 150-300$ à l'international. Identification taxonomique avec précision ≥ 95%.",
    image: null,
    imageAlt: "",
    reverse: true,
    tags: ["16S rRNA", "UCAD/Pasteur", "95% précision"],
  },
  {
    number: "03",
    title: "BiomeX AI",
    titleExtra: "Analyse intelligente",
    description:
      "Pipeline bioinformatique QIIME2 + modèles prédictifs (Random Forest, XGBoost, PyTorch). Entraîné sur des données africaines pour des recommandations adaptées.",
    image: null,
    imageAlt: "",
    reverse: false,
    tags: ["QIIME2", "XGBoost", "PyTorch"],
  },
  {
    number: "04",
    title: "BiomeX Care",
    titleExtra: "Votre dashboard santé",
    description:
      "Application mobile avec recommandations personnalisées basées sur les aliments locaux (mil, fonio, niébé, baobab). Fonctionne offline. Suivi longitudinal.",
    image: null,
    imageAlt: "",
    reverse: true,
    tags: ["Offline", "Multilingue", "Aliments locaux"],
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 40 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: "easeOut" },
  },
};

function PhoneMockup() {
  return (
    <div className="relative h-[500px] w-[260px] rounded-[2.5rem] border-8 border-slate-900 bg-white shadow-2xl overflow-hidden">
      <div className="absolute top-0 h-8 w-full bg-slate-900"></div>
      <div className="p-4 pt-10">
        <div className="flex items-center justify-between mb-6">
          <div className="h-6 w-6 rounded bg-slate-200"></div>
          <div className="h-8 w-8 rounded-full bg-gradient-to-br from-primary to-accent"></div>
        </div>
        <h4 className="text-lg font-extrabold text-primary mb-4">
          Bonjour Aminata !
        </h4>
        <div className="rounded-2xl bg-primary p-4 text-white mb-4">
          <p className="text-xs opacity-70 mb-1">Diversité microbienne</p>
          <p className="text-2xl font-bold">Excellent</p>
          <div className="mt-2 h-2 bg-white/20 rounded-full overflow-hidden">
            <div className="h-full w-4/5 bg-white rounded-full"></div>
          </div>
        </div>
        <div className="space-y-3">
          <p className="text-xs font-bold text-slate-400">RECOMMANDATIONS</p>
          <div className="flex items-center gap-3 p-3 rounded-xl border border-slate-100 bg-slate-50">
            <div className="h-9 w-9 rounded-lg bg-secondary flex items-center justify-center text-lg">
              🌾
            </div>
            <div className="text-sm font-medium text-slate-700">Pain de Mil</div>
          </div>
          <div className="flex items-center gap-3 p-3 rounded-xl border border-slate-100 bg-slate-50">
            <div className="h-9 w-9 rounded-lg bg-secondary flex items-center justify-center text-lg">
              🥬
            </div>
            <div className="text-sm font-medium text-slate-700">Feuilles de Baobab</div>
          </div>
          <div className="flex items-center gap-3 p-3 rounded-xl border border-slate-100 bg-slate-50">
            <div className="h-9 w-9 rounded-lg bg-secondary flex items-center justify-center text-lg">
              🫘
            </div>
            <div className="text-sm font-medium text-slate-700">Niébé local</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function AIAnalysisCircle() {
  return (
    <div className="relative h-72 w-72 md:h-80 md:w-80">
      <motion.div
        className="absolute inset-0 rounded-full bg-gradient-to-tr from-primary to-accent opacity-20 blur-2xl"
        animate={{
          scale: [1, 1.1, 1],
          opacity: [0.2, 0.3, 0.2],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
      <div className="relative h-full w-full rounded-full bg-gradient-to-br from-primary to-primary/80 flex items-center justify-center text-white overflow-hidden shadow-2xl">
        <motion.div
          className="absolute inset-0 flex items-center justify-center"
          animate={{ rotate: 360 }}
          transition={{ duration: 60, repeat: Infinity, ease: "linear" }}
        >
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="absolute h-2 w-2 rounded-full bg-white/30"
              style={{
                transform: `rotate(${i * 60}deg) translateY(-120px)`,
              }}
            />
          ))}
        </motion.div>
        <Brain className="h-20 w-20 opacity-20 absolute" />
        <div className="relative z-10 text-center">
          <p className="text-4xl md:text-5xl font-black">AI</p>
          <p className="text-xs uppercase tracking-widest font-bold mt-1">
            QIIME2 + XGBoost
          </p>
        </div>
      </div>
    </div>
  );
}

function LabIcon() {
  return (
    <div className="relative h-72 w-72 md:h-80 md:w-80">
      <motion.div
        className="absolute inset-0 rounded-full bg-gradient-to-tr from-primary to-accent opacity-20 blur-2xl"
        animate={{
          scale: [1, 1.1, 1],
          opacity: [0.2, 0.3, 0.2],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
      <div className="relative h-full w-full rounded-full bg-gradient-to-br from-primary to-primary/80 flex items-center justify-center text-white overflow-hidden shadow-2xl">
        <Database className="h-20 w-20 opacity-20 absolute" />
        <div className="relative z-10 text-center">
          <p className="text-3xl md:text-4xl font-black">16S</p>
          <p className="text-xs uppercase tracking-widest font-bold mt-1">
            rRNA Sequencing
          </p>
          <p className="text-[10px] text-white/70 mt-2">UCAD • Pasteur</p>
        </div>
      </div>
    </div>
  );
}

export default function HowItWorksSection() {
  return (
    <section id="comment-ca-marche" className="space-y-24 py-24 bg-white">
      <motion.div
        variants={containerVariants}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-100px" }}
      >
        {/* Step 1 - Kit */}
        <motion.div
          variants={itemVariants}
          className="mx-auto max-w-7xl px-6 mb-24"
        >
          <div className="grid items-center gap-12 lg:gap-16 lg:grid-cols-2">
            <div className="order-2 lg:order-1">
              <div className="relative overflow-hidden rounded-2xl shadow-2xl group">
                <div className="aspect-square bg-slate-100 overflow-hidden">
                  <Image
                    src={steps[0].image!}
                    alt={steps[0].imageAlt}
                    width={600}
                    height={600}
                    className="object-cover w-full h-full transition-transform duration-500 group-hover:scale-105"
                  />
                </div>
                <div className="absolute inset-0 bg-gradient-to-t from-primary/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
            </div>
            <div className="order-1 lg:order-2">
              <span className="text-6xl md:text-7xl font-black text-primary/10">
                {steps[0].number}
              </span>
              <h2 className="mt-4 text-3xl md:text-4xl font-extrabold text-primary leading-tight">
                {steps[0].title}
                <br />
                <span className="text-accent">{steps[0].titleExtra}</span>
              </h2>
              <p className="mt-6 text-lg text-slate-600 leading-relaxed">
                {steps[0].description}
              </p>
              <div className="mt-6 flex items-center gap-3 text-primary">
                <Thermometer className="h-5 w-5" />
                <span className="text-sm font-semibold">Stable 14 jours à température ambiante</span>
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                {steps[0].tags.map((tag, i) => (
                  <span
                    key={i}
                    className="rounded-full bg-primary/10 px-3 py-1 text-xs font-bold text-primary"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Step 2 - Lab */}
        <motion.div variants={itemVariants} className="bg-secondary py-24">
          <div className="mx-auto max-w-7xl px-6">
            <div className="grid items-center gap-12 lg:gap-16 lg:grid-cols-2">
              <div>
                <span className="text-6xl md:text-7xl font-black text-primary/10">
                  {steps[1].number}
                </span>
                <h2 className="mt-4 text-3xl md:text-4xl font-extrabold text-primary leading-tight">
                  {steps[1].title}
                  <br />
                  <span className="text-accent">{steps[1].titleExtra}</span>
                </h2>
                <p className="mt-6 text-lg text-slate-600 leading-relaxed">
                  {steps[1].description}
                </p>
                <div className="mt-8 flex flex-wrap gap-3">
                  {steps[1].tags.map((tag, i) => (
                    <span
                      key={i}
                      className="rounded-full bg-primary/10 px-4 py-2 text-xs font-bold text-primary"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
                <div className="mt-6 p-4 rounded-xl bg-white border border-primary/10">
                  <p className="text-sm text-slate-600">
                    <strong className="text-primary">Économie de 70-75%</strong> vs laboratoires internationaux
                  </p>
                </div>
              </div>
              <div className="flex justify-center">
                <LabIcon />
              </div>
            </div>
          </div>
        </motion.div>

        {/* Step 3 - AI */}
        <motion.div
          variants={itemVariants}
          className="mx-auto max-w-7xl px-6 mb-24"
        >
          <div className="grid items-center gap-12 lg:gap-16 lg:grid-cols-2">
            <div className="order-2 lg:order-1 flex justify-center">
              <AIAnalysisCircle />
            </div>
            <div className="order-1 lg:order-2">
              <span className="text-6xl md:text-7xl font-black text-primary/10">
                {steps[2].number}
              </span>
              <h2 className="mt-4 text-3xl md:text-4xl font-extrabold text-primary leading-tight">
                {steps[2].title}
                <br />
                <span className="text-accent">{steps[2].titleExtra}</span>
              </h2>
              <p className="mt-6 text-lg text-slate-600 leading-relaxed">
                {steps[2].description}
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                {steps[2].tags.map((tag, i) => (
                  <span
                    key={i}
                    className="rounded-full bg-primary/10 px-4 py-2 text-xs font-bold text-primary"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Step 4 - Care App */}
        <motion.div
          variants={itemVariants}
          className="bg-secondary py-24"
        >
          <div className="mx-auto max-w-7xl px-6">
            <div className="grid items-center gap-12 lg:gap-16 lg:grid-cols-2">
              <div className="flex justify-center">
                <PhoneMockup />
              </div>
              <div>
                <span className="text-6xl md:text-7xl font-black text-primary/10">
                  {steps[3].number}
                </span>
                <h2 className="mt-4 text-3xl md:text-4xl font-extrabold text-primary leading-tight">
                  {steps[3].title}
                  <br />
                  <span className="text-accent">{steps[3].titleExtra}</span>
                </h2>
                <p className="mt-6 text-lg text-slate-600 leading-relaxed">
                  {steps[3].description}
                </p>
                <div className="mt-6 flex items-center gap-3 text-primary">
                  <Smartphone className="h-5 w-5" />
                  <span className="text-sm font-semibold">iOS & Android • Fonctionne offline</span>
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  {steps[3].tags.map((tag, i) => (
                    <span
                      key={i}
                      className="rounded-full bg-primary/10 px-3 py-1 text-xs font-bold text-primary"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </section>
  );
}
