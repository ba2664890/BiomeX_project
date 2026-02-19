"use client";

import { motion } from "framer-motion";
import { Microscope, Handshake, Clock, Shield, Award, Zap } from "lucide-react";

const trustItems = [
  {
    icon: Microscope,
    title: "Séquençage 16S rRNA",
    description: "Précision ≥ 95%",
    gradient: "from-primary to-teal-600",
  },
  {
    icon: Handshake,
    title: "Partenariat UCAD & Pasteur",
    description: "Laboratoires certifiés",
    gradient: "from-accent to-yellow-600",
  },
  {
    icon: Clock,
    title: "Résultats en 21 jours",
    description: "Livraison gratuite Dakar",
    gradient: "from-green-500 to-emerald-600",
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
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: "easeOut" },
  },
};

export default function TrustBar() {
  return (
    <section className="relative py-12 overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-r from-primary via-primary/95 to-primary" />
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:40px_40px]" />
      
      {/* Animated gradient orbs */}
      <motion.div
        className="absolute top-0 left-1/4 w-64 h-64 bg-accent/20 rounded-full blur-3xl"
        animate={{
          x: [0, 50, 0],
          opacity: [0.2, 0.3, 0.2],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
      <motion.div
        className="absolute bottom-0 right-1/4 w-64 h-64 bg-white/10 rounded-full blur-3xl"
        animate={{
          x: [0, -50, 0],
          opacity: [0.1, 0.2, 0.1],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      <div className="mx-auto max-w-7xl px-6 relative z-10">
        <motion.div
          className="grid grid-cols-1 gap-6 md:grid-cols-3"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
        >
          {trustItems.map((item, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              className="group relative"
            >
              <div className={`
                flex items-center gap-4 p-5 rounded-2xl 
                bg-white/10 backdrop-blur-sm border border-white/10 
                hover:bg-white/15 hover:border-white/20 
                transition-all duration-300 cursor-pointer
              `}>
                <motion.div
                  className={`flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br ${item.gradient} shadow-lg`}
                  whileHover={{ scale: 1.1, rotate: 5 }}
                >
                  <item.icon className="h-7 w-7 text-white" />
                </motion.div>
                <div>
                  <h3 className="text-base font-bold text-white uppercase tracking-wide">
                    {item.title}
                  </h3>
                  <p className="text-sm text-white/70 mt-0.5">{item.description}</p>
                </div>
                <motion.div
                  className="absolute inset-0 rounded-2xl bg-white/5 opacity-0 group-hover:opacity-100 transition-opacity"
                  initial={false}
                />
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Additional badges row */}
        <motion.div
          className="flex flex-wrap justify-center gap-8 mt-10 pt-8 border-t border-white/10"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.3 }}
        >
          {[
            { icon: Shield, text: "Données sécurisées AES-256" },
            { icon: Award, text: "Certification ISO 15189 objectif An 2" },
            { icon: Zap, text: "75$ vs 300-400$ international" },
          ].map((badge, i) => (
            <motion.div
              key={i}
              className="flex items-center gap-2 text-white/80 hover:text-white transition-colors cursor-pointer"
              whileHover={{ scale: 1.05 }}
            >
              <badge.icon className="h-4 w-4 text-accent" />
              <span className="text-sm font-medium">{badge.text}</span>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
