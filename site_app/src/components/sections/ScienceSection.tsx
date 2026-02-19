"use client";

import { motion, useInView } from "framer-motion";
import { useRef, useEffect, useState } from "react";
import { Dna, Microscope, Cpu, Database, Shield, Zap, Brain } from "lucide-react";

const stats = [
  {
    value: 100,
    suffix: " T",
    label: "Micro-organismes analysés",
    description: "Dans votre microbiome intestinal",
  },
  {
    value: 95,
    suffix: "%",
    label: "Précision taxonomique",
    description: "Identification jusqu'au genre",
  },
  {
    value: 75,
    prefix: "",
    suffix: "%",
    label: "Économie vs international",
    description: "75$ vs 300-400$",
  },
];

const scienceFeatures = [
  {
    icon: Dna,
    title: "Séquençage 16S rRNA",
    description:
      "Région V3-V4 optimal pour populations africaines. Identification précise jusqu'au niveau genre avec base de données locale.",
  },
  {
    icon: Brain,
    title: "IA & Machine Learning",
    description:
      "Random Forest, XGBoost, réseaux de neurones PyTorch. Transfer learning depuis base africaine pour corriger le biais occidental.",
  },
  {
    icon: Database,
    title: "Base de données africaine",
    description:
      "Objectif 5 000 profils ouest-africains en année 3. La plus grande base de données microbiomiques africaines annotée cliniquement.",
  },
  {
    icon: Microscope,
    title: "Partenaires certifiés",
    description:
      "Laboratoires UCAD et Institut Pasteur de Dakar. Certification ISO 15189 en objectif année 2.",
  },
];

const partners = [
  { name: "UCAD SÉNÉGAL", description: "Université Cheikh Anta Diop" },
  { name: "INSTITUT PASTEUR", description: "Dakar, Sénégal" },
  { name: "AFRICA CDC", description: "Centres de contrôle des maladies" },
  { name: "GATES FOUNDATION", description: "Bill & Melinda Gates" },
];

const techStack = [
  { name: "QIIME2", category: "Pipeline bioinformatique" },
  { name: "XGBoost", category: "Machine Learning" },
  { name: "PyTorch", category: "Deep Learning" },
  { name: "AWS", category: "Infrastructure cloud" },
];

function AnimatedCounter({
  value,
  prefix = "",
  suffix = "",
}: {
  value: number;
  prefix?: string;
  suffix?: string;
}) {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  useEffect(() => {
    if (isInView) {
      const duration = 2000;
      const steps = 60;
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
      {prefix}
      {count}
      {suffix}
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
    transition: { duration: 0.6, ease: "easeOut" },
  },
};

export default function ScienceSection() {
  return (
    <section id="science" className="bg-[#141e1b] py-24 text-white overflow-hidden">
      <div className="mx-auto max-w-7xl px-6">
        {/* Header */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <span className="inline-flex items-center gap-2 rounded-full bg-accent/20 px-4 py-1.5 text-sm font-bold text-accent mb-4">
            <Microscope className="h-4 w-4" />
            Notre Science
          </span>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-extrabold">
            Technologie de pointe pour
            <span className="text-accent"> l&apos;Afrique</span>
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-slate-400 text-lg">
            Démocratiser la médecine de précision en combinant séquençage local, bioinformatique et IA adaptée.
          </p>
        </motion.div>

        {/* Main Stats */}
        <motion.div
          className="grid gap-8 text-center md:grid-cols-3 mb-20"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
        >
          {stats.map((stat, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              className="p-8 rounded-3xl bg-white/5 border border-white/10 hover:border-accent/30 transition-colors"
            >
              <p className="text-5xl md:text-6xl lg:text-7xl font-extrabold text-accent">
                <AnimatedCounter
                  value={stat.value}
                  prefix={stat.prefix}
                  suffix={stat.suffix}
                />
              </p>
              <p className="mt-2 text-white uppercase tracking-widest font-bold text-sm">
                {stat.label}
              </p>
              <p className="mt-2 text-slate-500 text-sm">{stat.description}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* Science Features Grid */}
        <motion.div
          className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-20"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          {scienceFeatures.map((feature, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              className="group p-6 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 hover:border-accent/30 transition-all"
            >
              <div className="h-12 w-12 rounded-xl bg-accent/20 flex items-center justify-center mb-4 group-hover:bg-accent/30 transition-colors">
                <feature.icon className="h-6 w-6 text-accent" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">{feature.title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </motion.div>

        {/* Process Visualization */}
        <motion.div
          className="mb-20"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2 }}
        >
          <p className="text-center text-sm font-bold text-slate-500 uppercase tracking-widest mb-8">
            Pipeline en 3 étapes
          </p>
          <div className="grid md:grid-cols-5 gap-4 items-center">
            {[
              { icon: Dna, label: "Prélèvement" },
              { icon: Microscope, label: "Extraction ADN" },
              { icon: Database, label: "Séquençage 16S" },
              { icon: Brain, label: "Analyse IA" },
              { icon: Shield, label: "Résultats" },
            ].map((step, i) => (
              <div key={i} className="flex flex-col items-center">
                <motion.div
                  className="h-16 w-16 rounded-2xl bg-gradient-to-br from-primary to-accent flex items-center justify-center mb-3"
                  whileHover={{ scale: 1.1, rotate: 5 }}
                >
                  <step.icon className="h-7 w-7 text-white" />
                </motion.div>
                <p className="text-sm font-semibold text-white text-center">
                  {step.label}
                </p>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Tech Stack */}
        <motion.div
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-20"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.3 }}
        >
          {techStack.map((tech, i) => (
            <div
              key={i}
              className="p-4 rounded-xl bg-white/5 border border-white/10 text-center hover:border-accent/30 transition-colors"
            >
              <p className="font-bold text-white">{tech.name}</p>
              <p className="text-xs text-slate-500 mt-1">{tech.category}</p>
            </div>
          ))}
        </motion.div>

        {/* Partners */}
        <motion.div
          className="border-t border-white/10 pt-12"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.3 }}
        >
          <p className="text-center text-sm font-bold text-slate-500 uppercase tracking-widest mb-8">
            Nos Partenaires Scientifiques
          </p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {partners.map((partner, index) => (
              <motion.div
                key={index}
                className="group p-4 rounded-xl border border-white/10 hover:border-accent/30 transition-colors text-center cursor-pointer"
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ y: -5 }}
              >
                <p className="text-sm md:text-base font-bold text-white/70 group-hover:text-white transition-colors">
                  {partner.name}
                </p>
                <p className="text-xs text-slate-500 mt-1">{partner.description}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
