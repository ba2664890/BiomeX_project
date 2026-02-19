"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import { ChevronDown, MessageCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const faqCategories = [
  {
    title: "Le Test",
    questions: [
      {
        question: "Comment fonctionne le kit BiomeX ?",
        answer:
          "Le kit contient un tube stabilisant RNAlater adapté au climat tropical, un swab stérile et un guide illustré multilingue (français, wolof, dioula). L'échantillon reste stable 14 jours à température ambiante - pas besoin de chaîne du froid. Nous livrons gratuitement à Dakar et environs.",
      },
      {
        question: "Combien de temps pour recevoir mes résultats ?",
        answer:
          "Vous recevrez vos résultats complets sous 21 jours maximum après réception de votre échantillon. Un email vous notifiera dès que votre tableau de bord personnalisé est prêt sur l'application BiomeX Care.",
      },
      {
        question: "Quelle est la différence entre Standard et Premium ?",
        answer:
          "Le Kit Standard (75$) utilise le séquençage 16S rRNA avec identification taxonomique jusqu'au genre. Le Kit Premium (200$) utilise la métagénomique Shotgun pour un profil fonctionnel complet, incluant l'analyse du mycobiome et des voies métaboliques.",
      },
      {
        question: "À quelle fréquence refaire le test ?",
        answer:
          "Nous recommandons un nouveau test tous les 6 à 12 mois, surtout après un traitement antibiotique, un changement alimentaire important, ou pour suivre l'évolution de votre diversité microbienne.",
      },
    ],
  },
  {
    title: "La Science",
    questions: [
      {
        question: "Qu'est-ce que le séquençage 16S rRNA ?",
        answer:
          "Le séquençage 16S rRNA analyse la région V3-V4 de l'ARN ribosomal bactérien, permettant d'identifier précisément les espèces présentes dans votre microbiome. Cette technique offre une précision ≥ 95% pour l'identification taxonomique jusqu'au niveau genre.",
      },
      {
        question: "Pourquoi des données africaines sont importantes ?",
        answer:
          "L'Afrique subsaharienne représente moins de 3% des participants aux études microbiomiques mondiales, alors qu'elle abrite la plus grande diversité génétique humaine. Les régimes alimentaires traditionnels (mil, sorgho, fonio) génèrent des profils distincts ignorés des référentiels actuels. Nos algorithmes sont entraînés sur des données locales pour des recommandations adaptées.",
      },
      {
        question: "Comment fonctionne l'IA de BiomeX ?",
        answer:
          "Notre pipeline utilise QIIME2 pour le prétraitement, puis des modèles Random Forest et XGBoost pour la classification des risques, et des réseaux de neurones PyTorch pour l'analyse multi-omiques. Un GPT francophone fine-tuné génère des recommandations personnalisées en langues locales.",
      },
      {
        question: "Que contiennent mes résultats ?",
        answer:
          "Vos résultats incluent : 1) Score de diversité microbienne, 2) Liste des bactéries détectées avec leur abondance, 3) Indicateurs de risque métabolique, 4) Recommandations alimentaires personnalisées basées sur les aliments locaux (mil, fonio, niébé, baobab), 5) Suivi longitudinal de votre évolution.",
      },
    ],
  },
  {
    title: "Tarifs & Livraison",
    questions: [
      {
        question: "Quels sont les tarifs pratiqués ?",
        answer:
          "Kit Standard : 75$ (75 000 FCFA) - Séquençage 16S rRNA. Kit Premium : 200$ (120 000 FCFA) - Métagénomique Shotgun. Abonnement BiomeX Care : 7,5-12,5$/mois. Tarifs B2B pour cliniques à partir de 67$ en volume. Nos prix sont 60-75% inférieurs aux concurrents internationaux grâce au séquençage local.",
      },
      {
        question: "Livrez-vous partout au Sénégal ?",
        answer:
          "Livraison gratuite à Dakar, Pikine, Guédiawaye, Rufisque, Thiès, Saly et Mbour. Pour les autres villes, des frais de 2 500 FCFA s'appliquent. Nous livrons également en Côte d'Ivoire, Ghana, Nigeria et Burkina Faso.",
      },
      {
        question: "Quels moyens de paiement acceptez-vous ?",
        answer:
          "Nous acceptons les cartes bancaires (Visa, Mastercard), Mobile Money (Orange Money, Wave, Free Money), et virements bancaires. Tous les paiements sont sécurisés avec cryptage SSL.",
      },
    ],
  },
  {
    title: "Confidentialité",
    questions: [
      {
        question: "Que faites-vous de mes données ?",
        answer:
          "Vos données sont 100% confidentielles et ne sont jamais partagées. Conformément à la loi sénégalaise n° 2008-12 et au RGPD, vous êtes propriétaire de vos données. Pseudonymisation AES-256 et séparation physique des données cliniques/génétiques.",
      },
      {
        question: "Mes données sont-elles sécurisées ?",
        answer:
          "Stockage AWS S3 avec chiffrement AES-256, conformité ISO 27001, authentification à deux facteurs. Nos partenaires laboratoires sont certifiés et respectent les normes de biosécurité internationales.",
      },
    ],
  },
];

export default function FAQSection() {
  const [activeCategory, setActiveCategory] = useState(0);

  return (
    <section id="faq" className="py-24 bg-secondary">
      <div className="mx-auto max-w-5xl px-6">
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
        >
          <span className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-1.5 text-sm font-bold text-primary mb-4">
            <MessageCircle className="h-4 w-4" />
            FAQ
          </span>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-extrabold text-primary">
            Questions fréquentes
          </h2>
          <p className="mt-4 text-lg text-slate-600 max-w-2xl mx-auto">
            Tout ce que vous devez savoir sur BiomeX. Contactez-nous sur WhatsApp pour plus d&apos;informations.
          </p>
        </motion.div>

        {/* Category Tabs */}
        <div className="flex flex-wrap justify-center gap-2 mb-8">
          {faqCategories.map((category, index) => (
            <motion.button
              key={index}
              onClick={() => setActiveCategory(index)}
              className={`px-6 py-2.5 rounded-full text-sm font-semibold transition-all ${
                activeCategory === index
                  ? "bg-primary text-white shadow-lg"
                  : "bg-white text-slate-600 hover:bg-primary/5 border border-primary/10"
              }`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {category.title}
            </motion.button>
          ))}
        </div>

        {/* FAQ Accordion */}
        <motion.div
          key={activeCategory}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="bg-white rounded-3xl p-6 md:p-8 shadow-sm border border-primary/5"
        >
          <Accordion type="single" collapsible className="w-full">
            {faqCategories[activeCategory].questions.map((item, index) => (
              <AccordionItem
                key={index}
                value={`item-${index}`}
                className="border-b border-primary/10 last:border-0"
              >
                <AccordionTrigger className="text-left py-6 hover:no-underline group">
                  <span className="text-base md:text-lg font-semibold text-primary group-hover:text-accent transition-colors pr-4">
                    {item.question}
                  </span>
                </AccordionTrigger>
                <AccordionContent className="text-slate-600 leading-relaxed pb-6">
                  {item.answer}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </motion.div>

        {/* Contact CTA */}
        <motion.div
          className="mt-12 text-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.3 }}
        >
          <p className="text-slate-500 mb-4">
            Vous avez d&apos;autres questions ?
          </p>
          <Button
            className="rounded-full bg-[#25D366] hover:bg-[#25D366]/90 text-white px-8 py-6 font-bold shadow-lg"
            onClick={() => window.open("https://wa.me/221771234567", "_blank")}
          >
            <svg className="h-5 w-5 mr-2" viewBox="0 0 24 24" fill="currentColor">
              <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
            </svg>
            Nous contacter sur WhatsApp
          </Button>
          <p className="mt-4 text-sm text-slate-500">
            Email : <a href="mailto:abdou.ba@biomex.ai" className="text-primary hover:underline">abdou.ba@biomex.ai</a> • <a href="mailto:m.dia@biomex.ai" className="text-primary hover:underline">m.dia@biomex.ai</a>
          </p>
        </motion.div>
      </div>
    </section>
  );
}
