"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X, Dna } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";

const navLinks = [
  { href: "#decouvrir", label: "Découvrir" },
  { href: "#comment-ca-marche", label: "Comment ça marche" },
  { href: "#science", label: "Science" },
  { href: "#blog", label: "Blog" },
];

export default function Header() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [activeSection, setActiveSection] = useState("");

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
      
      // Determine active section
      const sections = navLinks.map(link => link.href.replace("#", ""));
      for (const section of sections.reverse()) {
        const element = document.getElementById(section);
        if (element) {
          const rect = element.getBoundingClientRect();
          if (rect.top <= 100) {
            setActiveSection(section);
            break;
          }
        }
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleNavClick = (href: string) => {
    const element = document.querySelector(href);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <header
      className={`sticky top-0 z-50 h-20 w-full border-b transition-all duration-300 ${
        isScrolled
          ? "border-primary/10 bg-white/95 backdrop-blur-md shadow-sm"
          : "border-transparent bg-white/80 backdrop-blur-sm"
      }`}
    >
      <div className="mx-auto flex h-full max-w-7xl items-center justify-between px-6">
        {/* Logo */}
        <motion.a
          href="#"
          className="flex items-center gap-3"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-white">
            <Dna className="h-5 w-5" />
          </div>
          <span className="text-2xl font-extrabold tracking-tight text-primary">
            BiomeX
          </span>
        </motion.a>

        {/* Desktop Navigation */}
        <nav className="hidden items-center gap-8 lg:flex">
          {navLinks.map((link, index) => (
            <motion.button
              key={link.href}
              onClick={() => handleNavClick(link.href)}
              className={`text-sm font-semibold transition-colors relative ${
                activeSection === link.href.replace("#", "")
                  ? "text-primary"
                  : "text-slate-700 hover:text-primary"
              }`}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              {link.label}
              {activeSection === link.href.replace("#", "") && (
                <motion.div
                  className="absolute -bottom-1 left-0 right-0 h-0.5 bg-accent rounded-full"
                  layoutId="activeSection"
                  transition={{ type: "spring", stiffness: 380, damping: 30 }}
                />
              )}
            </motion.button>
          ))}
        </nav>

        {/* CTA Button */}
        <motion.div
          className="flex items-center gap-4"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Button
            className="hidden rounded-full bg-accent px-6 py-2.5 text-sm font-bold text-white shadow-lg shadow-accent/20 hover:bg-accent/90 transition-all sm:flex"
            onClick={() => handleNavClick("#pricing")}
          >
            Commander mon kit
          </Button>

          {/* Mobile Menu */}
          <Sheet>
            <SheetTrigger asChild className="lg:hidden">
              <Button variant="ghost" size="icon" className="text-primary">
                <Menu className="h-6 w-6" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-[300px] sm:w-[350px]">
              <nav className="flex flex-col gap-4 mt-8">
                {navLinks.map((link) => (
                  <button
                    key={link.href}
                    onClick={() => handleNavClick(link.href)}
                    className="text-left text-lg font-semibold text-slate-700 hover:text-primary transition-colors py-2"
                  >
                    {link.label}
                  </button>
                ))}
                <Button
                  className="mt-4 rounded-full bg-accent px-6 py-3 text-sm font-bold text-white shadow-lg shadow-accent/20"
                  onClick={() => handleNavClick("#pricing")}
                >
                  Commander mon kit
                </Button>
              </nav>
            </SheetContent>
          </Sheet>
        </motion.div>
      </div>
    </header>
  );
}
