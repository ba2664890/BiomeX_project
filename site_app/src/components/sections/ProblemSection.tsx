"use client";

import { motion, useInView } from "framer-motion";
import { useRef, useEffect, useState } from "react";
import { Globe, TrendingUp, Heart, AlertTriangle, Users, Activity } from "lucide-react";

const problems = [
  {
    icon: Globe,
    iconBg: "bg-red-50",
    iconColor: "text-red-500",
    title: "95% de manque de données",
    description:
      "Les études microbiomiques mondiales proviennent de populations occidentales. L'Afrique subsaharienne représente moins de 3% des participants aux études mondiales.",
    stat: "< 3%",
    statLabel: "de représentation africaine",
  },
  {
    icon: TrendingUp,
    iconBg: "bg-orange-50",
    iconColor: "text-orange-500",
    title: "+60% hausse du diabète",
    description:
      "Transition nutritionnelle accélérée en Afrique entre 2010 et 2024, aggravée par l'urbanisation rapide et les régimes occidentalisés.",
    stat: "500K+",
    statLabel: "diabétiques au Sénégal",
  },
  {
    icon: Heart,
    iconBg: "bg-blue-50",
    iconColor: "text-blue-500",
    title: "Probiotiques inefficaces",
    description:
      "Les probiotiques standardisés montrent une efficacité réduite sur les populations locales. Les modèles occidentaux sont inadaptés aux profils métaboliques africains.",
    stat: "3x",
    statLabel: "moins efficace localement",
  },
];

const additionalStats = [
  { value: 70, suffix: "%", label: "des maladies chroniques liées au microbiome" },
  { value: 90, suffix: "%", label: "de sérotonine produite par le microbiome" },
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
            Un biais scientifique majeur que nous devons corriger pour l&apos;Afrique.
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
            &quot;L&apos;Afrique subsaharienne représente moins de 3% des participants aux études microbiomiques mondiales, 
            alors qu&apos;elle abrite la plus grande diversité génétique humaine.&quot;
          </blockquote>
          <p className="mt-4 text-white/70 text-sm">
            — Nature Microbiology, 2023
          </p>
        </motion.div>
      </div>
    </section>
  );
}
