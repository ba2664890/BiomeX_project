"use client";

import { motion, useInView } from "framer-motion";
import { useRef, useEffect, useState } from "react";
import { Globe, TrendingUp, Heart, AlertTriangle, Users, Activity } from "lucide-react";

const problems = [
  {
    icon: Globe,
    iconBg: "bg-red-50",
    iconColor: "text-red-500",
    title: "Données africaines absentes",
    description:
      "Les référentiels microbiome et génomiques restent dominés par des données occidentales, alors que les régimes alimentaires africains produisent des profils biologiques distincts.",
    stat: "1,1%",
    statLabel: "des GWAS publiées en 2025",
  },
  {
    icon: TrendingUp,
    iconBg: "bg-orange-50",
    iconColor: "text-orange-500",
    title: "Errance digestive longue",
    description:
      "Dysbiose, intolérances, ballonnements, douleurs abdominales et troubles fonctionnels restent trop souvent sous-diagnostiqués faute d'outils adaptés.",
    stat: "5-7 ans",
    statLabel: "de délai fréquent",
  },
  {
    icon: Heart,
    iconBg: "bg-blue-50",
    iconColor: "text-blue-500",
    title: "Nutrition trop générique",
    description:
      "Les conseils \"manger moins gras, moins sucré, plus de fibres\" ne suffisent pas lorsque deux personnes tolèrent différemment le mil, le lait, le riz ou le niébé.",
    stat: "1,4 Md+",
    statLabel: "d'habitants concernés en Afrique",
  },
];

const additionalStats = [
  { value: 70, suffix: "%", label: "des maladies chroniques influencées par le microbiome" },
  { value: 90, suffix: "%", label: "de sérotonine produite dans l'intestin" },
  { value: 150, suffix: "x", label: "plus de gènes que le génome humain" },
];

function AnimatedNumber({ value, suffix }: { value: number; suffix: string }) {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  useEffect(() => {
    if (isInView) {
      const duration = 1500;
      const steps = 40;
      const stepDuration = duration / steps;
      let current = 0;

      const timer = setInterval(() => {
        current += 1;
        const progress = current / steps;
        const easeOut = 1 - Math.pow(1 - progress, 3);
        setCount(Math.floor(value * easeOut));

        if (current >= steps) {
          clearInterval(timer);
          setCount(value);
        }
      }, stepDuration);

      return () => clearInterval(timer);
    }
  }, [isInView, value]);

  return (
    <span ref={ref}>
      {count}{suffix}
    </span>
  );
}

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

export default function ProblemSection() {
  return (
    <section className="py-24">
      <div className="mx-auto max-w-7xl px-6">
        <motion.div
          className="mb-16 text-center"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
        >
          <span className="inline-flex items-center gap-2 rounded-full bg-red-50 px-4 py-1.5 text-sm font-bold text-red-500 mb-4">
            <AlertTriangle className="h-4 w-4" />
            Le Problème
          </span>
          <h2 className="text-3xl font-extrabold text-primary md:text-4xl lg:text-5xl">
            Pourquoi BiomeX est nécessaire
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-slate-500 text-lg">
            Les patients ont besoin d&apos;une nutrition fondée sur leur biologie réelle, pas sur des recommandations importées.
          </p>
        </motion.div>

        {/* Main Problems */}
        <motion.div
          className="grid gap-8 md:grid-cols-3"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
        >
          {problems.map((problem, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              className="group rounded-2xl bg-white p-8 shadow-sm transition-all duration-300 hover:-translate-y-2 hover:shadow-xl border border-transparent hover:border-primary/10"
            >
              <div
                className={`mb-6 inline-flex h-14 w-14 items-center justify-center rounded-full ${problem.iconBg} ${problem.iconColor}`}
              >
                <problem.icon className="h-7 w-7" />
              </div>
              <h3 className="mb-4 text-xl font-bold text-primary">
                {problem.title}
              </h3>
              <p className="text-slate-600 leading-relaxed mb-4">
                {problem.description}
              </p>
              <div className="pt-4 border-t border-slate-100">
                <p className={`text-2xl font-bold ${problem.iconColor}`}>
                  {problem.stat}
                </p>
                <p className="text-sm text-slate-500">{problem.statLabel}</p>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Additional Stats */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.3 }}
        >
          {additionalStats.map((stat, index) => (
            <div
              key={index}
              className="flex items-center gap-4 p-6 rounded-2xl bg-gradient-to-br from-primary/5 to-accent/5 border border-primary/10"
            >
              <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                {index === 0 && <Activity className="h-6 w-6 text-primary" />}
                {index === 1 && <Users className="h-6 w-6 text-primary" />}
                {index === 2 && <Heart className="h-6 w-6 text-primary" />}
              </div>
              <div>
                <p className="text-2xl font-bold text-primary">
                  <AnimatedNumber value={stat.value} suffix={stat.suffix} />
                </p>
                <p className="text-sm text-slate-600">{stat.label}</p>
              </div>
            </div>
          ))}
        </motion.div>

        {/* Quote */}
        <motion.div
          className="mt-16 p-8 rounded-3xl bg-primary text-white text-center"
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2 }}
        >
          <blockquote className="text-xl md:text-2xl font-medium leading-relaxed max-w-4xl mx-auto">
            &quot;BiomeX adapte l&apos;alimentation au microbiome intestinal pour réduire l&apos;incertitude, mieux orienter la prise en charge et valoriser les aliments locaux africains.&quot;
          </blockquote>
          <p className="mt-4 text-white/70 text-sm">
            — Positionnement issu du pitch deck BiomeX
          </p>
        </motion.div>
      </div>
    </section>
  );
}
