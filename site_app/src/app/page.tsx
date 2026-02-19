"use client";

import Header from "@/components/sections/Header";
import HeroSection from "@/components/sections/HeroSection";
import TrustBar from "@/components/sections/TrustBar";
import ProblemSection from "@/components/sections/ProblemSection";
import HowItWorksSection from "@/components/sections/HowItWorksSection";
import VideoSection from "@/components/sections/VideoSection";
import ScienceSection from "@/components/sections/ScienceSection";
import CompareSection from "@/components/sections/CompareSection";
import TestimonialsSection from "@/components/sections/TestimonialsSection";
import PricingSection from "@/components/sections/PricingSection";
import BlogSection from "@/components/sections/BlogSection";
import FAQSection from "@/components/sections/FAQSection";
import TeamSection from "@/components/sections/TeamSection";
import Footer from "@/components/sections/Footer";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1">
        <HeroSection />
        <TrustBar />
        <ProblemSection />
        <HowItWorksSection />
        <VideoSection />
        <ScienceSection />
        <CompareSection />
        <TestimonialsSection />
        <PricingSection />
        <BlogSection />
        <FAQSection />
        <TeamSection />
      </main>
      <Footer />
    </div>
  );
}
