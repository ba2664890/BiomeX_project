"use client";

import { motion } from "framer-motion";
import { Play, Clock, BookOpen, CheckCircle } from "lucide-react";
import Image from "next/image";
import { useState } from "react";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { VisuallyHidden } from "@radix-ui/react-visually-hidden";

const videoFeatures = [
  { icon: Clock, text: "Analyse en 3 semaines" },
  { icon: BookOpen, text: "Guide nutritionnel inclus" },
  { icon: CheckCircle, text: "Résultats garantis" },
];

const MICROBIOME_DEMO_VIDEO_URL = "https://www.youtube.com/embed/1sISguPDlhY?autoplay=1&rel=0";

export default function VideoSection() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <section className="py-24 bg-white">
      <div className="mx-auto max-w-7xl px-6">
        <motion.div
          className="grid lg:grid-cols-2 gap-12 items-center"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
        >
          {/* Video Thumbnail */}
          <div className="relative group cursor-pointer" onClick={() => setIsOpen(true)}>
            <div className="relative rounded-3xl overflow-hidden shadow-2xl aspect-video">
              <Image
                src="https://images.unsplash.com/photo-1576086213369-97a306d36557?w=800&h=450&fit=crop"
                alt="Comment fonctionne BiomeX"
                width={800}
                height={450}
                className="object-cover w-full h-full transition-transform duration-500 group-hover:scale-105"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-primary/60 via-transparent to-transparent" />
              
              {/* Play Button */}
              <div className="absolute inset-0 flex items-center justify-center">
                <motion.div
                  className="h-20 w-20 md:h-24 md:w-24 rounded-full bg-white/90 flex items-center justify-center shadow-2xl"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Play className="h-8 w-8 md:h-10 md:w-10 text-primary ml-1" />
                </motion.div>
              </div>

              {/* Duration */}
              <div className="absolute bottom-4 right-4 bg-black/70 text-white text-sm px-3 py-1 rounded-full flex items-center gap-2">
                <Clock className="h-4 w-4" />
                3:45
              </div>

              {/* Title overlay */}
              <div className="absolute bottom-4 left-4 right-16">
                <h3 className="text-white text-lg md:text-xl font-bold">
                  Comment ça marche ?
                </h3>
                <p className="text-white/80 text-sm mt-1">
                  Découvrez le processus en 3 étapes
                </p>
              </div>
            </div>

            {/* Decorative elements */}
            <div className="absolute -z-10 -top-4 -right-4 w-full h-full rounded-3xl bg-accent/20" />
            <div className="absolute -z-10 -bottom-4 -left-4 w-full h-full rounded-3xl bg-primary/10" />
          </div>

          {/* Content */}
          <div>
            <span className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-1.5 text-sm font-bold text-primary mb-4">
              🎬 Vidéo explicative
            </span>
            <h2 className="text-3xl md:text-4xl font-extrabold text-primary leading-tight">
              Découvrez comment BiomeX
              <span className="text-accent"> transforme votre santé</span>
            </h2>
            <p className="mt-6 text-lg text-slate-600 leading-relaxed">
              Notre technologie de pointe combine le séquençage ADN avec l&apos;intelligence artificielle 
              pour vous offrir des recommandations nutritionnelles personnalisées, basées sur votre 
              microbiome unique et votre alimentation locale.
            </p>

            <div className="mt-8 space-y-4">
              {videoFeatures.map((feature, i) => (
                <motion.div
                  key={i}
                  className="flex items-center gap-4 p-4 rounded-xl bg-secondary/50 hover:bg-secondary transition-colors"
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                >
                  <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <feature.icon className="h-5 w-5 text-primary" />
                  </div>
                  <span className="font-medium text-slate-700">{feature.text}</span>
                </motion.div>
              ))}
            </div>

            <div className="mt-8 p-4 rounded-xl bg-accent/10 border border-accent/20">
              <p className="text-sm text-accent font-medium">
                💡 Le saviez-vous ? Votre microbiome est unique à 99.9%, comme vos empreintes digitales.
                C&apos;est pourquoi une approche personnalisée est essentielle.
              </p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Video Modal */}
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="w-[95vw] max-w-7xl p-0 overflow-hidden rounded-2xl">
          <VisuallyHidden>
            <DialogTitle>BiomeX - Comment ça marche</DialogTitle>
          </VisuallyHidden>
          <div className="aspect-video bg-slate-900 relative">
            {isOpen && (
              <iframe
                className="w-full h-full"
                src={MICROBIOME_DEMO_VIDEO_URL}
                title="Microbiome: Meet your microbes"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            )}
          </div>
        </DialogContent>
      </Dialog>
    </section>
  );
}
