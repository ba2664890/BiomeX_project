"use client";

import { motion } from "framer-motion";
import { Building2, FlaskConical, HeartPulse, MapPin, Stethoscope, Users } from "lucide-react";

const segments = [
  {
    icon: HeartPulse,
    title: "Enfants et familles",
    description:
      "Troubles digestifs récurrents, intolérances suspectées, suivi prudent à 3 mois et retest à 6 mois.",
  },
  {
    icon: Stethoscope,
    title: "Patients dysbiose",
    description:
      "Syndrome de l'intestin irritable, douleurs chroniques, ballonnements, constipation ou diarrhée chronique.",
  },
  {
    icon: Building2,
    title: "Laboratoires partenaires",
    description:
      "Kits co-brandés, protocole de collecte, analyse IA BiomeX et partage de revenus.",
  },
  {
    icon: FlaskConical,
    title: "Recherche et pharma",
    description:
      "Cohortes anonymisées, biomarqueurs, probiotiques, prébiotiques et aliments fonctionnels africains.",
  },
];

const roadmap = [
  {
    phase: "Phase 1",
    period: "0 à 12 mois",
    title: "Validation au Sénégal",
    items: ["2 à 3 laboratoires partenaires", "10 à 20 médecins prescripteurs", "500 à 1 000 tests pilotes"],
  },
  {
    phase: "Phase 2",
    period: "12 à 24 mois",
    title: "Expansion régionale",
    items: ["Côte d'Ivoire, Bénin, Cameroun, Ghana", "Portail médecin", "Réseau BiomeX Certified Practitioners"],
  },
  {
    phase: "Phase 3",
    period: "24 à 60 mois",
    title: "Scale panafricain",
    items: ["Hub de séquençage régional", "Base microbiome africaine", "Nigeria, Kenya, Maroc, Afrique du Sud"],
  },
];

export default function MarketSection() {
  return (
    <section id="marche" className="bg-white py-24">
      <div className="mx-auto max-w-7xl px-6">
        <motion.div
          className="mb-14 max-w-3xl"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.5 }}
        >
          <span className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-1.5 text-sm font-bold text-primary mb-4">
            <MapPin className="h-4 w-4" />
            Marché et go-to-market
          </span>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-extrabold text-primary">
            Du pilote sénégalais à la référence africaine
          </h2>
          <p className="mt-4 text-lg text-slate-600">
            BiomeX démarre par les cas où la douleur patient est forte, puis structure un réseau de laboratoires, médecins et partenaires de recherche pour créer une infrastructure microbiome africaine.
          </p>
        </motion.div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {segments.map((segment, index) => (
            <motion.div
              key={segment.title}
              className="rounded-2xl border border-primary/10 bg-secondary/40 p-6"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.4, delay: index * 0.08 }}
            >
              <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-xl bg-primary text-white">
                <segment.icon className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-bold text-primary">{segment.title}</h3>
              <p className="mt-3 text-sm leading-relaxed text-slate-600">{segment.description}</p>
            </motion.div>
          ))}
        </div>

        <div className="mt-14 grid gap-6 lg:grid-cols-3">
          {roadmap.map((step, index) => (
            <motion.div
              key={step.phase}
              className="rounded-2xl border border-primary/10 bg-white p-6 shadow-sm"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.4, delay: index * 0.08 }}
            >
              <div className="flex items-center justify-between gap-4">
                <span className="rounded-full bg-accent/10 px-3 py-1 text-xs font-bold text-accent">
                  {step.phase}
                </span>
                <span className="text-sm font-semibold text-slate-500">{step.period}</span>
              </div>
              <h3 className="mt-5 text-xl font-extrabold text-primary">{step.title}</h3>
              <ul className="mt-5 space-y-3">
                {step.items.map((item) => (
                  <li key={item} className="flex gap-3 text-sm text-slate-600">
                    <Users className="mt-0.5 h-4 w-4 flex-shrink-0 text-accent" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
