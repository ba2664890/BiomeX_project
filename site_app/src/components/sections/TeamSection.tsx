"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import { Linkedin, Twitter, Award, GraduationCap } from "lucide-react";

const teamMembers = [
  {
    name: "Mouhammadou Dia",
    role: "CEO & Co-Fondateur",
    image: "",
    bio: "Data Scientist avec une vision stratégique pour démocratiser la médecine de précision en Afrique.",
    credentials: ["Data Scientist", "Fundraising", "Vision stratégique"],
    social: { linkedin: "#", twitter: "#" },
  },
  {
    name: "Abdou Bâ",
    role: "CTO & Co-Fondateur",
    image: "",
    bio: "Data Scientist & Ingénieur logiciel. Architecture technique, MLOps et pipeline bioinformatique.",
    credentials: ["Ingénieur Logiciel", "MLOps", "Bioinformatique"],
    social: { linkedin: "#", twitter: "#" },
  },
  {
    name: "Fatou Soumaya Wade",
    role: "CMO",
    image: "",
    bio: "Experte en Marketing Digital. Acquisition client et brand building pour la santé digitale.",
    credentials: ["Marketing Digital", "Brand Building", "Community"],
    social: { linkedin: "#", twitter: "#" },
  },
  {
    name: "Yaye Maimouna Sakho",
    role: "Chief Scientific Officer",
    image: "",
    bio: "Microbiologiste . Validation clinique et relations académiques.",
    credentials: ["MD PhD", "Microbiologie", "Recherche"],
    social: { linkedin: "#", twitter: "#" },
  },
];

const partners = [
  { name: "UCAD Sénégal", logo: "🎓", description: "Université Cheikh Anta Diop" },
  { name: "Institut Pasteur", logo: "🧬", description: "Dakar, Sénégal" },
  { name: "Africa CDC", logo: "🌍", description: "Centres de contrôle des maladies" },
  { name: "Gates Foundation", logo: "🏥", description: "Bill & Melinda Gates Foundation" },
];

const achievements = [
  { value: "350K$", label: "Levée Seed" },
  { value: "5 000+", label: "Profils cibles An 3" },
  { value: "5", label: "Pays cibles à 36 mois" },
  { value: "BEP", label: "Fin année 3" },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5 },
  },
};

export default function TeamSection() {
  return (
    <section id="about" className="py-24 bg-secondary">
      <div className="mx-auto max-w-7xl px-6">
        {/* Header */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
        >
          <span className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-1.5 text-sm font-bold text-primary mb-4">
            <GraduationCap className="h-4 w-4" />
            Notre Équipe
          </span>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-extrabold text-primary">
            Une équipe passionnée
          </h2>
          <p className="mt-4 text-lg text-slate-600 max-w-3xl mx-auto">
            Deux cofondateurs data scientists avec les compétences techniques pour livrer 
            le produit sans dépendance externe coûteuse.
          </p>
        </motion.div>

        {/* Team Grid */}
        <motion.div
          className="grid gap-8 md:grid-cols-2 lg:grid-cols-4"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
        >
          {teamMembers.map((member, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              className="group bg-white rounded-2xl p-6 shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-2 border border-primary/5"
            >
              <div className="relative mb-4">
                <div className="h-28 w-28 mx-auto rounded-full overflow-hidden border-4 border-primary/10 group-hover:border-accent transition-colors">
                  <Image
                    src={member.image}
                    alt={member.name}
                    width={112}
                    height={112}
                    className="object-cover w-full h-full group-hover:scale-110 transition-transform duration-500"
                  />
                </div>
                <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 bg-accent text-white text-[10px] px-2 py-0.5 rounded-full font-bold whitespace-nowrap">
                  {member.role.split(" ")[0]}
                </div>
              </div>

              <div className="text-center">
                <h3 className="text-lg font-bold text-primary">{member.name}</h3>
                <p className="text-sm text-accent font-semibold mt-1">{member.role}</p>
                <p className="text-sm text-slate-500 mt-3 leading-relaxed">
                  {member.bio}
                </p>

                <div className="flex flex-wrap justify-center gap-1 mt-4">
                  {member.credentials.map((credential, i) => (
                    <span
                      key={i}
                      className="text-[10px] bg-primary/10 text-primary px-2 py-0.5 rounded-full font-semibold"
                    >
                      {credential}
                    </span>
                  ))}
                </div>

                <div className="flex justify-center gap-3 mt-4 pt-4 border-t border-primary/5">
                  <a
                    href={member.social.linkedin}
                    className="h-8 w-8 rounded-full bg-slate-100 hover:bg-primary/10 flex items-center justify-center text-slate-500 hover:text-primary transition-colors"
                  >
                    <Linkedin className="h-4 w-4" />
                  </a>
                  <a
                    href={member.social.twitter}
                    className="h-8 w-8 rounded-full bg-slate-100 hover:bg-primary/10 flex items-center justify-center text-slate-500 hover:text-primary transition-colors"
                  >
                    <Twitter className="h-4 w-4" />
                  </a>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Achievements */}
        <motion.div
          className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.3 }}
        >
          {achievements.map((stat, i) => (
            <div
              key={i}
              className="text-center p-6 rounded-2xl bg-white border border-primary/5"
            >
              <Award className="h-8 w-8 text-accent mx-auto mb-2" />
              <p className="text-3xl font-bold text-primary">{stat.value}</p>
              <p className="text-sm text-slate-500 mt-1">{stat.label}</p>
            </div>
          ))}
        </motion.div>

        {/* Partners */}
        <motion.div
          className="mt-16 pt-12 border-t border-primary/10"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.3 }}
        >
          <p className="text-center text-sm font-bold text-slate-400 uppercase tracking-widest mb-8">
            Nos Partenaires & Collaborateurs
          </p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {partners.map((partner, i) => (
              <motion.div
                key={i}
                className="flex flex-col items-center text-center p-4 rounded-xl border border-primary/10 hover:border-accent/30 transition-colors cursor-pointer group"
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                whileHover={{ y: -5 }}
              >
                <span className="text-3xl mb-2">{partner.logo}</span>
                <span className="font-semibold text-sm text-slate-700 group-hover:text-primary transition-colors">
                  {partner.name}
                </span>
                <p className="text-xs text-slate-500 mt-1">{partner.description}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
