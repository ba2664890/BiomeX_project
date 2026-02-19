"use client";

import { motion } from "framer-motion";
import { Check, Sparkles, Star } from "lucide-react";
import { Button } from "@/components/ui/button";

const features = [
  "Kit de prélèvement stabilisé 14 jours",
  "Analyse 16S rRNA haute résolution",
  "Guide nutritionnel personnalisé",
  "Recommandations aliments locaux (Mil, Fonio, Niébé)",
  "Tableau de bord IA à vie",
  "App multilingue (FR, Wolof, Dioula)",
  "Support prioritaire WhatsApp",
];

const pricingPlans = [
  {
    name: "Kit Standard",
    price: "75$",
    priceFCFA: "75 000 FCFA",
    description: "Analyse 16S rRNA complète",
    features: features,
    popular: true,
  },
  {
    name: "Kit Premium",
    price: "200$",
    priceFCFA: "120 000 FCFA",
    description: "Métagénomique Shotgun",
    features: [...features, "Profil fonctionnel complet", "Analyse mycobiome"],
    popular: false,
  },
];

const containerVariants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: "easeOut",
    },
  },
};

export default function PricingSection() {
  return (
    <section id="pricing" className="bg-secondary py-24">
      <div className="mx-auto max-w-5xl px-6">
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <span className="inline-flex items-center gap-2 rounded-full bg-accent/10 px-4 py-1.5 text-sm font-bold text-accent mb-4">
            <Sparkles className="h-4 w-4" />
            Tarifs Accessibles
          </span>
          <h2 className="text-3xl md:text-4xl font-extrabold text-primary">
            Des prix adaptés à l&apos;Afrique
          </h2>
          <p className="mt-4 text-lg text-slate-600 max-w-2xl mx-auto">
            60-75% moins cher que les concurrents internationaux grâce au séquençage local.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-8">
          {pricingPlans.map((plan, index) => (
            <motion.div
              key={index}
              className={`rounded-3xl bg-white p-8 md:p-10 shadow-xl relative overflow-hidden ${
                plan.popular ? "border-4 border-accent/30" : "border border-primary/10"
              }`}
              variants={containerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-100px" }}
            >
              {plan.popular && (
                <div className="absolute top-0 right-0 bg-accent text-white text-xs font-bold px-4 py-2 rounded-bl-xl flex items-center gap-1">
                  <Star className="h-3 w-3" />
                  Plus populaire
                </div>
              )}

              <div className="text-center mb-8">
                <h3 className="text-xl font-bold text-primary">{plan.name}</h3>
                <p className="text-sm text-slate-500 mt-1">{plan.description}</p>
                <div className="mt-4">
                  <span className="text-4xl md:text-5xl font-black text-primary">{plan.price}</span>
                  <p className="text-sm text-slate-400 mt-1">{plan.priceFCFA}</p>
                </div>
              </div>

              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, i) => (
                  <motion.li
                    key={i}
                    className="flex items-center gap-3 text-sm text-slate-600"
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.1 + i * 0.05 }}
                  >
                    <div className="flex h-5 w-5 items-center justify-center rounded-full bg-accent/10 text-accent flex-shrink-0">
                      <Check className="h-3 w-3" />
                    </div>
                    {feature}
                  </motion.li>
                ))}
              </ul>

              <Button
                size="lg"
                className={`w-full rounded-full py-5 text-base font-bold transition-transform ${
                  plan.popular
                    ? "bg-accent text-white shadow-xl shadow-accent/30 hover:scale-[1.02]"
                    : "bg-primary text-white shadow-xl shadow-primary/20 hover:scale-[1.02]"
                }`}
              >
                Commander maintenant
              </Button>

              <p className="mt-4 text-xs text-center text-slate-500">
                🔒 Paiement sécurisé • Livraison gratuite Dakar
              </p>
            </motion.div>
          ))}
        </div>

        {/* B2B CTA */}
        <motion.div
          className="mt-12 p-6 rounded-2xl bg-primary/5 border border-primary/10 text-center"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.3 }}
        >
          <h4 className="font-bold text-primary text-lg">Vous êtes une clinique ou un professionnel de santé ?</h4>
          <p className="text-sm text-slate-600 mt-2">
            Tarifs B2B spéciaux à partir de <strong className="text-primary">67$</strong> par kit en volume.
            Contactez-nous pour un partenariat.
          </p>
          <Button
            variant="outline"
            className="mt-4 rounded-full border-primary/20 text-primary hover:bg-primary/5"
          >
            Contacter l&apos;équipe B2B
          </Button>
        </motion.div>
      </div>
    </section>
  );
}
