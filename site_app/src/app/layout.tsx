import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "BiomeX - Analyse IA du Microbiome Africain",
  description: "Explorez les 100 billions de microorganismes qui composent votre identité génétique unique. Une technologie de séquençage conçue spécifiquement pour les populations africaines.",
  keywords: ["BiomeX", "microbiome", "ADN", "santé", "Afrique", "génétique", "analyse", "séquençage"],
  authors: [{ name: "BiomeX Health" }],
  icons: {
    icon: "/favicon.ico",
  },
  openGraph: {
    title: "BiomeX - Analyse IA du Microbiome Africain",
    description: "Votre microbiome. Votre ADN. Votre santé. Technologie de séquençage pour l'Afrique.",
    url: "https://biomex.health",
    siteName: "BiomeX",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "BiomeX - Analyse IA du Microbiome Africain",
    description: "Votre microbiome. Votre ADN. Votre santé.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-background text-foreground`}
      >
        {children}
        <Toaster />
      </body>
    </html>
  );
}
