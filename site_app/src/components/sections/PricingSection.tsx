"use client";

import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { Check, Loader2, LocateFixed, Sparkles, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { toast } from "@/hooks/use-toast";

const features = [
  "Kit de prelevement stabilise 14 jours",
  "Analyse 16S rRNA haute resolution",
  "Guide nutritionnel personnalise",
  "Recommandations aliments locaux (Mil, Fonio, Niebe)",
  "Tableau de bord IA a vie",
  "App multilingue (FR, Wolof, Dioula)",
  "Support prioritaire WhatsApp",
];

type PricingPlan = {
  name: string;
  price: string;
  priceFCFA: string;
  priceFcfaValue: number;
  description: string;
  features: string[];
  popular: boolean;
};

const pricingPlans: PricingPlan[] = [
  {
    name: "Kit Standard",
    price: "75$",
    priceFCFA: "75 000 FCFA",
    priceFcfaValue: 75000,
    description: "Analyse 16S rRNA complete",
    features: features,
    popular: true,
  },
  {
    name: "Kit Premium",
    price: "200$",
    priceFCFA: "120 000 FCFA",
    priceFcfaValue: 120000,
    description: "Metagenomique Shotgun",
    features: [...features, "Profil fonctionnel complet", "Analyse mycobiome"],
    popular: false,
  },
];

const paymentMethods = [
  { value: "orange_money", label: "Orange Money" },
  { value: "wave", label: "Wave" },
  { value: "mtn_momo", label: "MTN Mobile Money" },
  { value: "moov_money", label: "Moov Money" },
  { value: "card", label: "Carte bancaire" },
  { value: "bank_transfer", label: "Virement bancaire" },
  { value: "cash_on_delivery", label: "Paiement a la livraison" },
];

const mobilePaymentMethods = new Set([
  "orange_money",
  "wave",
  "mtn_momo",
  "moov_money",
]);

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PHONE_REGEX = /^\+?[0-9]{8,15}$/;

type PreKitQuestionnaireState = {
  age: string;
  sexe: string;
  tailleCm: string;
  poidsKg: string;
  zone: string;
  antibio3Mois: string;
  ballonnements: string;
  transit: string;
  fatigue: string;
  fibersG: string;
  sugarG: string;
  milletFreq: string;
  niebeFreq: string;
  fishPortions: string;
  glycemie: string;
  hba1c: string;
  crp: string;
  tensionSys: string;
  cholesterol: string;
  triglycerides: string;
};

const initialPreKitQuestionnaire: PreKitQuestionnaireState = {
  age: "",
  sexe: "",
  tailleCm: "",
  poidsKg: "",
  zone: "",
  antibio3Mois: "",
  ballonnements: "",
  transit: "",
  fatigue: "",
  fibersG: "",
  sugarG: "",
  milletFreq: "",
  niebeFreq: "",
  fishPortions: "",
  glycemie: "",
  hba1c: "",
  crp: "",
  tensionSys: "",
  cholesterol: "",
  triglycerides: "",
};

const requiredQuestionnaireFields: Array<keyof PreKitQuestionnaireState> = [
  "age",
  "sexe",
  "tailleCm",
  "poidsKg",
  "zone",
  "antibio3Mois",
  "ballonnements",
  "transit",
  "fatigue",
  "fibersG",
  "sugarG",
  "milletFreq",
  "niebeFreq",
  "fishPortions",
];

const selectBaseClassName =
  "border-input focus-visible:border-ring focus-visible:ring-ring/50 flex h-9 w-full min-w-0 rounded-md border bg-transparent px-3 py-1 text-sm shadow-xs outline-none focus-visible:ring-[3px]";

const questionnaireSectionCardClassName =
  "space-y-4 rounded-xl border border-primary/10 bg-white/85 p-4 shadow-sm";

const questionnaireStepTitleClassName =
  "inline-flex items-center gap-2 text-sm font-semibold text-primary";

const questionnaireSelectClassName = `${selectBaseClassName} bg-white`;

const parseOptionalNumber = (value: string): number | null => {
  const normalized = value.trim();
  if (!normalized) return null;
  const parsed = Number(normalized);
  return Number.isFinite(parsed) ? parsed : null;
};

type OrderFormState = {
  fullName: string;
  email: string;
  phone: string;
  city: string;
  country: string;
  latitude: number | null;
  longitude: number | null;
  geolocationAccuracyMeters: number | null;
  geolocationSource: string;
  quantity: number;
  paymentMethod: string;
  paymentPhone: string;
  paymentReference: string;
  paymentLast4: string;
  message: string;
  acceptedTerms: boolean;
  questionnaire: PreKitQuestionnaireState;
};

const initialOrderForm: OrderFormState = {
  fullName: "",
  email: "",
  phone: "",
  city: "Dakar",
  country: "Senegal",
  latitude: null,
  longitude: null,
  geolocationAccuracyMeters: null,
  geolocationSource: "browser_gps",
  quantity: 1,
  paymentMethod: "orange_money",
  paymentPhone: "",
  paymentReference: "",
  paymentLast4: "",
  message: "",
  acceptedTerms: false,
  questionnaire: initialPreKitQuestionnaire,
};

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
  const [isOrderDialogOpen, setIsOrderDialogOpen] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<PricingPlan | null>(null);
  const [isSubmittingOrder, setIsSubmittingOrder] = useState(false);
  const [isLocating, setIsLocating] = useState(false);
  const [orderForm, setOrderForm] = useState<OrderFormState>(initialOrderForm);

  const isMobilePayment = mobilePaymentMethods.has(orderForm.paymentMethod);
  const hasExactLocation =
    orderForm.latitude !== null && orderForm.longitude !== null;
  const amountTotalFcfa = useMemo(() => {
    return (selectedPlan?.priceFcfaValue ?? 0) * Math.max(orderForm.quantity, 1);
  }, [selectedPlan, orderForm.quantity]);

  const setOrderField = <K extends keyof OrderFormState>(
    key: K,
    value: OrderFormState[K],
  ) => {
    setOrderForm((prev) => ({ ...prev, [key]: value }));
  };

  const setQuestionnaireField = <K extends keyof PreKitQuestionnaireState>(
    key: K,
    value: PreKitQuestionnaireState[K],
  ) => {
    setOrderForm((prev) => ({
      ...prev,
      questionnaire: { ...prev.questionnaire, [key]: value },
    }));
  };

  const filledRequiredFieldCount = useMemo(() => {
    return requiredQuestionnaireFields.filter(
      (field) => orderForm.questionnaire[field].trim().length > 0,
    ).length;
  }, [orderForm.questionnaire]);

  const questionnaireCompletion = useMemo(() => {
    return Math.round(
      (filledRequiredFieldCount / requiredQuestionnaireFields.length) * 100,
    );
  }, [filledRequiredFieldCount]);

  const missingRequiredFieldCount =
    requiredQuestionnaireFields.length - filledRequiredFieldCount;

  const bodyMassIndex = useMemo(() => {
    const tailleCm = parseOptionalNumber(orderForm.questionnaire.tailleCm);
    const poidsKg = parseOptionalNumber(orderForm.questionnaire.poidsKg);
    if (tailleCm === null || poidsKg === null || tailleCm <= 0 || poidsKg <= 0) {
      return null;
    }
    const imc = poidsKg / (tailleCm / 100) ** 2;
    return Number(imc.toFixed(1));
  }, [orderForm.questionnaire.poidsKg, orderForm.questionnaire.tailleCm]);

  const validatePreKitQuestionnaire = () => {
    const q = orderForm.questionnaire;

    for (const field of requiredQuestionnaireFields) {
      if (!q[field].trim()) {
        return "Merci de completer le questionnaire pre-kit avant de valider.";
      }
    }

    const age = parseOptionalNumber(q.age);
    if (age === null || age < 18 || age > 90) {
      return "Age invalide (18 a 90 ans).";
    }

    if (!["0", "1"].includes(q.sexe)) {
      return "Veuillez renseigner le sexe biologique (Femme ou Homme).";
    }

    const tailleCm = parseOptionalNumber(q.tailleCm);
    if (tailleCm === null || tailleCm < 120 || tailleCm > 230) {
      return "Taille invalide (120 a 230 cm).";
    }

    const poidsKg = parseOptionalNumber(q.poidsKg);
    if (poidsKg === null || poidsKg < 30 || poidsKg > 250) {
      return "Poids invalide (30 a 250 kg).";
    }

    if (!["Urbain", "Banlieue", "Rural"].includes(q.zone)) {
      return "Veuillez selectionner la zone de residence.";
    }

    if (!["0", "1"].includes(q.antibio3Mois)) {
      return "Veuillez indiquer si vous avez pris des antibiotiques dans les 3 derniers mois.";
    }

    if (!["0", "1", "2", "3"].includes(q.ballonnements)) {
      return "Niveau de ballonnements invalide.";
    }

    if (!["0", "1", "2", "3"].includes(q.transit)) {
      return "Type de transit invalide.";
    }

    if (!["0", "1", "2", "3"].includes(q.fatigue)) {
      return "Niveau de fatigue invalide.";
    }

    const fibersG = parseOptionalNumber(q.fibersG);
    if (fibersG === null || fibersG < 0 || fibersG > 90) {
      return "Apport en fibres invalide (0 a 90 g/jour).";
    }

    const sugarG = parseOptionalNumber(q.sugarG);
    if (sugarG === null || sugarG < 0 || sugarG > 300) {
      return "Apport en sucres ajoutes invalide (0 a 300 g/jour).";
    }

    const milletFreq = parseOptionalNumber(q.milletFreq);
    if (milletFreq === null || milletFreq < 0 || milletFreq > 14) {
      return "Frequence mil/sorgho invalide (0 a 14 fois/semaine).";
    }

    const niebeFreq = parseOptionalNumber(q.niebeFreq);
    if (niebeFreq === null || niebeFreq < 0 || niebeFreq > 14) {
      return "Frequence niebe invalide (0 a 14 fois/semaine).";
    }

    const fishPortions = parseOptionalNumber(q.fishPortions);
    if (fishPortions === null || fishPortions < 0 || fishPortions > 14) {
      return "Frequence poisson invalide (0 a 14 portions/semaine).";
    }

    const optionalRanges: Array<{ value: string; min: number; max: number; label: string }> = [
      { value: q.glycemie, min: 2, max: 20, label: "glycemie" },
      { value: q.hba1c, min: 3, max: 15, label: "HbA1c" },
      { value: q.crp, min: 0, max: 100, label: "CRP" },
      { value: q.tensionSys, min: 70, max: 230, label: "tension systolique" },
      { value: q.cholesterol, min: 1, max: 15, label: "cholesterol" },
      { value: q.triglycerides, min: 0, max: 20, label: "triglycerides" },
    ];

    for (const item of optionalRanges) {
      const parsed = parseOptionalNumber(item.value);
      if (parsed !== null && (parsed < item.min || parsed > item.max)) {
        return `Valeur ${item.label} hors plage attendue (${item.min}-${item.max}).`;
      }
    }

    return null;
  };

  const buildQuestionnairePayload = () => {
    const q = orderForm.questionnaire;
    return {
      version: "v1_biomex_full_pipeline_2026_02",
      notebook_reference: "Scripts_model/BiomeX_Full_Pipeline.ipynb",
      completion_percent: questionnaireCompletion,
      answers: {
        age: parseOptionalNumber(q.age),
        sexe: parseOptionalNumber(q.sexe),
        taille_cm: parseOptionalNumber(q.tailleCm),
        poids_kg: parseOptionalNumber(q.poidsKg),
        IMC: bodyMassIndex,
        zone: q.zone,
        antibio_3mois: parseOptionalNumber(q.antibio3Mois),
        ballonnements: parseOptionalNumber(q.ballonnements),
        transit: parseOptionalNumber(q.transit),
        fatigue: parseOptionalNumber(q.fatigue),
        fibers_g: parseOptionalNumber(q.fibersG),
        sugar_g: parseOptionalNumber(q.sugarG),
        millet_freq: parseOptionalNumber(q.milletFreq),
        niebe_freq: parseOptionalNumber(q.niebeFreq),
        fish_portions: parseOptionalNumber(q.fishPortions),
        glycemie: parseOptionalNumber(q.glycemie),
        HbA1c: parseOptionalNumber(q.hba1c),
        CRP: parseOptionalNumber(q.crp),
        tension_sys: parseOptionalNumber(q.tensionSys),
        cholesterol: parseOptionalNumber(q.cholesterol),
        triglycerides: parseOptionalNumber(q.triglycerides),
      },
    };
  };

  const openOrderDialog = (plan: PricingPlan) => {
    setSelectedPlan(plan);
    setOrderForm(initialOrderForm);
    setIsOrderDialogOpen(true);
  };

  const requestExactLocation = () => {
    if (typeof navigator === "undefined" || !navigator.geolocation) {
      toast({
        title: "Geolocalisation indisponible",
        description: "Votre navigateur ne supporte pas la geolocalisation GPS.",
        variant: "destructive",
      });
      return;
    }

    setIsLocating(true);

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const latitude = Number(position.coords.latitude.toFixed(6));
        const longitude = Number(position.coords.longitude.toFixed(6));
        const accuracy = Number(position.coords.accuracy.toFixed(1));

        setOrderForm((prev) => ({
          ...prev,
          latitude,
          longitude,
          geolocationAccuracyMeters: accuracy,
          geolocationSource: "browser_gps",
        }));

        // Optional reverse geocoding to prefill city/country from GPS coordinates.
        try {
          const reverseResponse = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${latitude}&lon=${longitude}`,
            { headers: { accept: "application/json" } },
          );
          if (reverseResponse.ok) {
            const reverseData = (await reverseResponse.json()) as {
              address?: {
                city?: string;
                town?: string;
                village?: string;
                country?: string;
              };
            };
            const resolvedCity =
              reverseData.address?.city ??
              reverseData.address?.town ??
              reverseData.address?.village ??
              "";
            const resolvedCountry = reverseData.address?.country ?? "";
            if (resolvedCity || resolvedCountry) {
              setOrderForm((prev) => ({
                ...prev,
                city: resolvedCity || prev.city,
                country: resolvedCountry || prev.country,
              }));
            }
          }
        } catch {
          // Non-blocking: coordinates remain available even if reverse geocoding fails.
        } finally {
          setIsLocating(false);
        }
      },
      (error) => {
        setIsLocating(false);
        const message =
          error.code === error.PERMISSION_DENIED
            ? "Autorisez la localisation GPS dans votre navigateur."
            : "Impossible de recuperer votre position exacte. Reessayez.";
        toast({
          title: "Localisation non recuperee",
          description: message,
          variant: "destructive",
        });
      },
      {
        enableHighAccuracy: true,
        timeout: 20000,
        maximumAge: 0,
      },
    );
  };

  const validateOrderForm = () => {
    if (!selectedPlan) return "Plan invalide.";

    if (orderForm.fullName.trim().length < 3) {
      return "Veuillez renseigner votre nom complet.";
    }

    const hasEmail = orderForm.email.trim().length > 0;
    const hasPhone = orderForm.phone.trim().length > 0;
    if (!hasEmail && !hasPhone) {
      return "Veuillez fournir au moins un email ou un numero de telephone.";
    }

    if (hasEmail && !EMAIL_REGEX.test(orderForm.email.trim())) {
      return "Adresse email invalide.";
    }

    if (hasPhone && !PHONE_REGEX.test(orderForm.phone.trim())) {
      return "Numero de telephone invalide.";
    }

    if (orderForm.quantity < 1 || orderForm.quantity > 20) {
      return "La quantite doit etre entre 1 et 20.";
    }

    const questionnaireError = validatePreKitQuestionnaire();
    if (questionnaireError) {
      return questionnaireError;
    }

    if (!orderForm.paymentMethod) {
      return "Veuillez choisir un moyen de paiement.";
    }

    if (!hasExactLocation) {
      return "Veuillez recuperer votre localisation exacte avant de valider la commande.";
    }

    if (
      orderForm.geolocationAccuracyMeters !== null &&
      orderForm.geolocationAccuracyMeters > 250
    ) {
      return "La precision GPS est insuffisante. Rapprochez-vous d'une zone degagee puis reessayez.";
    }

    if (isMobilePayment && !PHONE_REGEX.test(orderForm.paymentPhone.trim())) {
      return "Numero de paiement Mobile Money invalide.";
    }

    if (
      orderForm.paymentMethod !== "cash_on_delivery" &&
      orderForm.paymentReference.trim().length < 6
    ) {
      return "La reference de paiement doit contenir au moins 6 caracteres.";
    }

    if (
      orderForm.paymentMethod === "card" &&
      !/^\d{4}$/.test(orderForm.paymentLast4.trim())
    ) {
      return "Veuillez saisir les 4 derniers chiffres de la carte.";
    }

    if (!orderForm.acceptedTerms) {
      return "Vous devez accepter les conditions d'achat.";
    }

    return null;
  };

  const submitOrder = async () => {
    if (!selectedPlan) return;

    const validationError = validateOrderForm();
    if (validationError) {
      toast({
        title: "Verification du formulaire",
        description: validationError,
        variant: "destructive",
      });
      return;
    }

    try {
      setIsSubmittingOrder(true);
      const questionnairePayload = buildQuestionnairePayload();

      const response = await fetch("/api/site/kit-order", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          plan: selectedPlan.name,
          fullName: orderForm.fullName.trim(),
          email: orderForm.email.trim(),
          phone: orderForm.phone.trim(),
          city: orderForm.city.trim(),
          country: orderForm.country.trim(),
          quantity: orderForm.quantity,
          unitPriceFcfa: selectedPlan.priceFcfaValue,
          amountTotalFcfa,
          currency: "XOF",
          paymentMethod: orderForm.paymentMethod,
          paymentProvider: orderForm.paymentMethod,
          paymentPhone: orderForm.paymentPhone.trim(),
          paymentReference: orderForm.paymentReference.trim(),
          paymentLast4: orderForm.paymentLast4.trim(),
          latitude: orderForm.latitude,
          longitude: orderForm.longitude,
          geolocationAccuracyMeters: orderForm.geolocationAccuracyMeters,
          geolocationSource: orderForm.geolocationSource,
          acceptedTerms: orderForm.acceptedTerms,
          source: "site_app_pricing",
          message: orderForm.message.trim(),
          metadata: {
            channel: "pricing_section",
            campaign: "direct_checkout",
            location_capture: "browser_gps",
            pre_kit_questionnaire: questionnairePayload,
          },
        }),
      });

      const data = (await response.json()) as {
        status?: string;
        message?: string;
        requestId?: number | null;
        paymentStatus?: string;
        verificationFlags?: string[];
        paymentVerificationNotes?: string;
      };

      if (!response.ok || data.status !== "ok") {
        throw new Error(data.message ?? "Echec de la commande.");
      }

      const statusLine =
        data.paymentStatus === "manual_review"
          ? `Paiement en verification manuelle. ${data.paymentVerificationNotes ?? ""}`
          : "Commande enregistree avec succes.";

      toast({
        title: "Commande confirmee",
        description: `${statusLine} ID: ${data.requestId ?? "N/A"}.`,
      });

      setIsOrderDialogOpen(false);
      setOrderForm(initialOrderForm);
    } catch (error) {
      toast({
        title: "Commande impossible",
        description:
          error instanceof Error
            ? error.message
            : "Une erreur est survenue. Reessayez dans un instant.",
        variant: "destructive",
      });
    } finally {
      setIsSubmittingOrder(false);
    }
  };

  const contactB2B = () => {
    window.open(
      "mailto:partenariats@biomex.ai?subject=Demande%20partenariat%20B2B",
      "_blank",
    );
  };

  return (
    <section id="pricing" className="bg-secondary py-24">
      <div className="mx-auto max-w-5xl px-6">
        <motion.div
          className="mb-12 text-center"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <span className="mb-4 inline-flex items-center gap-2 rounded-full bg-accent/10 px-4 py-1.5 text-sm font-bold text-accent">
            <Sparkles className="h-4 w-4" />
            Tarifs Accessibles
          </span>
          <h2 className="text-3xl font-extrabold text-primary md:text-4xl">
            Des prix adaptes a l&apos;Afrique
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-slate-600">
            60-75% moins cher que les concurrents internationaux grace au sequencage local.
          </p>
        </motion.div>

        <div className="grid gap-8 md:grid-cols-2">
          {pricingPlans.map((plan, index) => (
            <motion.div
              key={index}
              className={`relative overflow-hidden rounded-3xl bg-white p-8 shadow-xl md:p-10 ${
                plan.popular ? "border-4 border-accent/30" : "border border-primary/10"
              }`}
              variants={containerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-100px" }}
            >
              {plan.popular && (
                <div className="absolute right-0 top-0 flex items-center gap-1 rounded-bl-xl bg-accent px-4 py-2 text-xs font-bold text-white">
                  <Star className="h-3 w-3" />
                  Plus populaire
                </div>
              )}

              <div className="mb-8 text-center">
                <h3 className="text-xl font-bold text-primary">{plan.name}</h3>
                <p className="mt-1 text-sm text-slate-500">{plan.description}</p>
                <div className="mt-4">
                  <span className="text-4xl font-black text-primary md:text-5xl">
                    {plan.price}
                  </span>
                  <p className="mt-1 text-sm text-slate-400">{plan.priceFCFA}</p>
                </div>
              </div>

              <ul className="mb-8 space-y-3">
                {plan.features.map((feature, i) => (
                  <motion.li
                    key={i}
                    className="flex items-center gap-3 text-sm text-slate-600"
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.1 + i * 0.05 }}
                  >
                    <div className="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-accent/10 text-accent">
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
                onClick={() => openOrderDialog(plan)}
              >
                Commander maintenant
              </Button>

              <p className="mt-4 text-center text-xs text-slate-500">
                Paiement securise - Verification commande et paiement activees.
              </p>
            </motion.div>
          ))}
        </div>

        <motion.div
          className="mt-12 rounded-2xl border border-primary/10 bg-primary/5 p-6 text-center"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.3 }}
        >
          <h4 className="text-lg font-bold text-primary">
            Vous etes une clinique ou un professionnel de sante ?
          </h4>
          <p className="mt-2 text-sm text-slate-600">
            Tarifs B2B speciaux a partir de <strong className="text-primary">67$</strong> par
            kit en volume. Contactez-nous pour un partenariat.
          </p>
          <Button
            variant="outline"
            className="mt-4 rounded-full border-primary/20 text-primary hover:bg-primary/5"
            onClick={contactB2B}
          >
            Contacter l&apos;equipe B2B
          </Button>
        </motion.div>
      </div>

      <Dialog open={isOrderDialogOpen} onOpenChange={setIsOrderDialogOpen}>
        <DialogContent className="max-h-[90vh] max-w-3xl overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Formulaire d&apos;achat</DialogTitle>
            <DialogDescription>
              Completez les informations de commande et de paiement pour lancer la verification.
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="plan">Plan</Label>
              <Input
                id="plan"
                value={selectedPlan?.name ?? ""}
                disabled
                className="bg-slate-50"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="quantity">Quantite</Label>
              <Input
                id="quantity"
                type="number"
                min={1}
                max={20}
                value={orderForm.quantity}
                onChange={(event) => {
                  const parsed = Number(event.target.value);
                  setOrderField("quantity", Number.isFinite(parsed) ? parsed : 1);
                }}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="fullName">Nom complet</Label>
              <Input
                id="fullName"
                value={orderForm.fullName}
                onChange={(event) => setOrderField("fullName", event.target.value)}
                placeholder="Prenom Nom"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={orderForm.email}
                onChange={(event) => setOrderField("email", event.target.value)}
                placeholder="vous@exemple.com"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="phone">Telephone</Label>
              <Input
                id="phone"
                value={orderForm.phone}
                onChange={(event) => setOrderField("phone", event.target.value)}
                placeholder="+221770000000"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="city">Ville</Label>
              <Input
                id="city"
                value={orderForm.city}
                onChange={(event) => setOrderField("city", event.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="country">Pays</Label>
              <Input
                id="country"
                value={orderForm.country}
                onChange={(event) => setOrderField("country", event.target.value)}
              />
            </div>

            <div className="space-y-5 rounded-2xl border border-primary/15 bg-gradient-to-br from-primary/5 via-white to-accent/10 p-5 md:col-span-2">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div className="space-y-1">
                  <div className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
                    Questionnaire pre-kit
                  </div>
                  <p className="text-sm font-semibold text-primary">
                    Questionnaire clinique et nutritionnel (obligatoire)
                  </p>
                  <p className="text-xs text-slate-600">
                    Remplissez ces informations avant validation du kit. Donnees alignees sur
                    BiomeX_Full_Pipeline.ipynb.
                  </p>
                </div>
                <div
                  className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold ${
                    questionnaireCompletion === 100
                      ? "bg-emerald-100 text-emerald-700"
                      : "bg-amber-100 text-amber-800"
                  }`}
                >
                  <Check className="h-3.5 w-3.5" />
                  {questionnaireCompletion}% complete
                </div>
              </div>

              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs text-slate-600">
                  <span>Progression</span>
                  <span>
                    {filledRequiredFieldCount}/{requiredQuestionnaireFields.length} champs
                    obligatoires
                  </span>
                </div>
                <div className="h-2.5 w-full overflow-hidden rounded-full bg-white shadow-inner">
                  <div
                    className={`h-full rounded-full transition-all ${
                      questionnaireCompletion === 100 ? "bg-emerald-500" : "bg-accent"
                    }`}
                    style={{ width: `${questionnaireCompletion}%` }}
                  />
                </div>
                {missingRequiredFieldCount > 0 && (
                  <p className="text-xs font-medium text-amber-700">
                    Il reste {missingRequiredFieldCount} champ(s) obligatoire(s) a completer.
                  </p>
                )}
              </div>

              <div className={questionnaireSectionCardClassName}>
                <p className={questionnaireStepTitleClassName}>
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/10 text-xs">
                    1
                  </span>
                  Profil de base
                </p>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="q_age">Age (ans)</Label>
                    <Input
                      id="q_age"
                      className="bg-white"
                      type="number"
                      min={18}
                      max={90}
                      value={orderForm.questionnaire.age}
                      onChange={(event) => setQuestionnaireField("age", event.target.value)}
                      placeholder="Ex: 34"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="q_sexe">Sexe biologique</Label>
                    <select
                      id="q_sexe"
                      className={questionnaireSelectClassName}
                      value={orderForm.questionnaire.sexe}
                      onChange={(event) => setQuestionnaireField("sexe", event.target.value)}
                    >
                      <option value="">Selectionner</option>
                      <option value="0">Femme</option>
                      <option value="1">Homme</option>
                    </select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="q_taille">Taille (cm)</Label>
                    <Input
                      id="q_taille"
                      className="bg-white"
                      type="number"
                      min={120}
                      max={230}
                      value={orderForm.questionnaire.tailleCm}
                      onChange={(event) => setQuestionnaireField("tailleCm", event.target.value)}
                      placeholder="Ex: 172"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="q_poids">Poids (kg)</Label>
                    <Input
                      id="q_poids"
                      className="bg-white"
                      type="number"
                      min={30}
                      max={250}
                      value={orderForm.questionnaire.poidsKg}
                      onChange={(event) => setQuestionnaireField("poidsKg", event.target.value)}
                      placeholder="Ex: 72"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="q_zone">Zone de residence</Label>
                    <select
                      id="q_zone"
                      className={questionnaireSelectClassName}
                      value={orderForm.questionnaire.zone}
                      onChange={(event) => setQuestionnaireField("zone", event.target.value)}
                    >
                      <option value="">Selectionner</option>
                      <option value="Urbain">Urbain</option>
                      <option value="Banlieue">Banlieue</option>
                      <option value="Rural">Rural</option>
                    </select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="q_antibio">Antibiotiques (&lt; 3 mois)</Label>
                    <select
                      id="q_antibio"
                      className={questionnaireSelectClassName}
                      value={orderForm.questionnaire.antibio3Mois}
                      onChange={(event) =>
                        setQuestionnaireField("antibio3Mois", event.target.value)
                      }
                    >
                      <option value="">Selectionner</option>
                      <option value="0">Non</option>
                      <option value="1">Oui</option>
                    </select>
                  </div>
                </div>

                <div className="rounded-lg border border-primary/10 bg-primary/5 p-3 text-xs text-slate-700">
                  <p className="font-medium text-primary">IMC calcule automatiquement</p>
                  <p className="mt-1">
                    Valeur actuelle:{" "}
                    <strong>{bodyMassIndex !== null ? `${bodyMassIndex}` : "non disponible"}</strong>
                  </p>
                </div>
              </div>

              <div className={questionnaireSectionCardClassName}>
                <p className={questionnaireStepTitleClassName}>
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/10 text-xs">
                    2
                  </span>
                  Symptomes digestifs
                </p>
                <p className="-mt-2 text-xs text-slate-600">Echelle 0 (aucun) a 3 (severe).</p>
                <div className="grid gap-4 md:grid-cols-3">
                  <div className="space-y-2">
                    <Label htmlFor="q_ballonnements">Ballonnements</Label>
                    <select
                      id="q_ballonnements"
                      className={questionnaireSelectClassName}
                      value={orderForm.questionnaire.ballonnements}
                      onChange={(event) =>
                        setQuestionnaireField("ballonnements", event.target.value)
                      }
                    >
                      <option value="">Selectionner</option>
                      <option value="0">0 - Aucun</option>
                      <option value="1">1 - Leger</option>
                      <option value="2">2 - Modere</option>
                      <option value="3">3 - Severe</option>
                    </select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="q_transit">Transit</Label>
                    <select
                      id="q_transit"
                      className={questionnaireSelectClassName}
                      value={orderForm.questionnaire.transit}
                      onChange={(event) => setQuestionnaireField("transit", event.target.value)}
                    >
                      <option value="">Selectionner</option>
                      <option value="0">0 - Normal</option>
                      <option value="1">1 - Constipation</option>
                      <option value="2">2 - Diarrhee</option>
                      <option value="3">3 - Alternance</option>
                    </select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="q_fatigue">Fatigue</Label>
                    <select
                      id="q_fatigue"
                      className={questionnaireSelectClassName}
                      value={orderForm.questionnaire.fatigue}
                      onChange={(event) => setQuestionnaireField("fatigue", event.target.value)}
                    >
                      <option value="">Selectionner</option>
                      <option value="0">0 - Aucune</option>
                      <option value="1">1 - Legere</option>
                      <option value="2">2 - Moderee</option>
                      <option value="3">3 - Severe</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className={questionnaireSectionCardClassName}>
                <p className={questionnaireStepTitleClassName}>
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/10 text-xs">
                    3
                  </span>
                  Habitudes alimentaires
                </p>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="q_fibers">Fibres estimees (g/jour)</Label>
                    <Input
                      id="q_fibers"
                      className="bg-white"
                      type="number"
                      min={0}
                      max={90}
                      value={orderForm.questionnaire.fibersG}
                      onChange={(event) => setQuestionnaireField("fibersG", event.target.value)}
                      placeholder="Ex: 22"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="q_sugar">Sucres ajoutes (g/jour)</Label>
                    <Input
                      id="q_sugar"
                      className="bg-white"
                      type="number"
                      min={0}
                      max={300}
                      value={orderForm.questionnaire.sugarG}
                      onChange={(event) => setQuestionnaireField("sugarG", event.target.value)}
                      placeholder="Ex: 60"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="q_millet">Mil/Sorgho (fois/semaine)</Label>
                    <Input
                      id="q_millet"
                      className="bg-white"
                      type="number"
                      min={0}
                      max={14}
                      value={orderForm.questionnaire.milletFreq}
                      onChange={(event) => setQuestionnaireField("milletFreq", event.target.value)}
                      placeholder="Ex: 3"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="q_niebe">Niebe (fois/semaine)</Label>
                    <Input
                      id="q_niebe"
                      className="bg-white"
                      type="number"
                      min={0}
                      max={14}
                      value={orderForm.questionnaire.niebeFreq}
                      onChange={(event) => setQuestionnaireField("niebeFreq", event.target.value)}
                      placeholder="Ex: 2"
                    />
                  </div>

                  <div className="space-y-2 md:col-span-2">
                    <Label htmlFor="q_fish">Poisson (portions/semaine)</Label>
                    <Input
                      id="q_fish"
                      className="bg-white"
                      type="number"
                      min={0}
                      max={14}
                      value={orderForm.questionnaire.fishPortions}
                      onChange={(event) => setQuestionnaireField("fishPortions", event.target.value)}
                      placeholder="Ex: 3"
                    />
                  </div>
                </div>
              </div>

              <div className={questionnaireSectionCardClassName}>
                <p className={questionnaireStepTitleClassName}>
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/10 text-xs">
                    4
                  </span>
                  Biomarqueurs recents
                  <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600">
                    Optionnel
                  </span>
                </p>
                <p className="-mt-2 text-xs text-slate-600">
                  Ajoutez uniquement des resultats biologiques recents si disponibles.
                </p>
                <div className="grid gap-4 md:grid-cols-3">
                  <div className="space-y-2">
                    <Label htmlFor="q_glycemie">Glycemie (mmol/L)</Label>
                    <Input
                      id="q_glycemie"
                      className="bg-white"
                      type="number"
                      min={2}
                      max={20}
                      value={orderForm.questionnaire.glycemie}
                      onChange={(event) => setQuestionnaireField("glycemie", event.target.value)}
                      placeholder="Optionnel"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="q_hba1c">HbA1c (%)</Label>
                    <Input
                      id="q_hba1c"
                      className="bg-white"
                      type="number"
                      min={3}
                      max={15}
                      value={orderForm.questionnaire.hba1c}
                      onChange={(event) => setQuestionnaireField("hba1c", event.target.value)}
                      placeholder="Optionnel"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="q_crp">CRP (mg/L)</Label>
                    <Input
                      id="q_crp"
                      className="bg-white"
                      type="number"
                      min={0}
                      max={100}
                      value={orderForm.questionnaire.crp}
                      onChange={(event) => setQuestionnaireField("crp", event.target.value)}
                      placeholder="Optionnel"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="q_tension">Tension systolique (mmHg)</Label>
                    <Input
                      id="q_tension"
                      className="bg-white"
                      type="number"
                      min={70}
                      max={230}
                      value={orderForm.questionnaire.tensionSys}
                      onChange={(event) => setQuestionnaireField("tensionSys", event.target.value)}
                      placeholder="Optionnel"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="q_cholesterol">Cholesterol (mmol/L)</Label>
                    <Input
                      id="q_cholesterol"
                      className="bg-white"
                      type="number"
                      min={1}
                      max={15}
                      value={orderForm.questionnaire.cholesterol}
                      onChange={(event) =>
                        setQuestionnaireField("cholesterol", event.target.value)
                      }
                      placeholder="Optionnel"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="q_triglycerides">Triglycerides (mmol/L)</Label>
                    <Input
                      id="q_triglycerides"
                      className="bg-white"
                      type="number"
                      min={0}
                      max={20}
                      value={orderForm.questionnaire.triglycerides}
                      onChange={(event) =>
                        setQuestionnaireField("triglycerides", event.target.value)
                      }
                      placeholder="Optionnel"
                    />
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-3 rounded-lg border border-primary/10 bg-primary/5 p-4 md:col-span-2">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm font-semibold text-primary">Localisation exacte (GPS)</p>
                  <p className="text-xs text-slate-600">
                    Requise pour verifier la zone de livraison et la commande.
                  </p>
                </div>
                <Button
                  type="button"
                  variant="outline"
                  className="border-primary/20 text-primary hover:bg-primary/10"
                  onClick={requestExactLocation}
                  disabled={isLocating || isSubmittingOrder}
                >
                  {isLocating ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Localisation...
                    </>
                  ) : (
                    <>
                      <LocateFixed className="mr-2 h-4 w-4" />
                      Utiliser ma localisation exacte
                    </>
                  )}
                </Button>
              </div>
              {hasExactLocation ? (
                <p className="text-xs text-slate-700">
                  Lat: <strong>{orderForm.latitude}</strong> | Lon:{" "}
                  <strong>{orderForm.longitude}</strong> | Precision:{" "}
                  <strong>{orderForm.geolocationAccuracyMeters ?? "N/A"} m</strong>
                </p>
              ) : (
                <p className="text-xs text-amber-700">
                  Localisation non capturee. Cliquez sur le bouton pour continuer.
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="paymentMethod">Moyen de paiement</Label>
              <select
                id="paymentMethod"
                className={selectBaseClassName}
                value={orderForm.paymentMethod}
                onChange={(event) => setOrderField("paymentMethod", event.target.value)}
              >
                {paymentMethods.map((method) => (
                  <option key={method.value} value={method.value}>
                    {method.label}
                  </option>
                ))}
              </select>
            </div>

            {isMobilePayment && (
              <div className="space-y-2">
                <Label htmlFor="paymentPhone">Telephone de paiement</Label>
                <Input
                  id="paymentPhone"
                  value={orderForm.paymentPhone}
                  onChange={(event) => setOrderField("paymentPhone", event.target.value)}
                  placeholder="+22177xxxxxxx"
                />
              </div>
            )}

            {orderForm.paymentMethod !== "cash_on_delivery" && (
              <div className="space-y-2">
                <Label htmlFor="paymentReference">Reference de paiement</Label>
                <Input
                  id="paymentReference"
                  value={orderForm.paymentReference}
                  onChange={(event) => setOrderField("paymentReference", event.target.value)}
                  placeholder="TRX-2026-0001"
                />
              </div>
            )}

            {orderForm.paymentMethod === "card" && (
              <div className="space-y-2">
                <Label htmlFor="paymentLast4">4 derniers chiffres carte</Label>
                <Input
                  id="paymentLast4"
                  value={orderForm.paymentLast4}
                  onChange={(event) => setOrderField("paymentLast4", event.target.value)}
                  maxLength={4}
                  placeholder="1234"
                />
              </div>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="message">Message (optionnel)</Label>
            <Textarea
              id="message"
              value={orderForm.message}
              onChange={(event) => setOrderField("message", event.target.value)}
              placeholder="Infos complementaires pour la livraison ou la verification."
            />
          </div>

          <div className="rounded-lg border border-primary/10 bg-primary/5 p-4 text-sm">
            <p>
              Montant unitaire: <strong>{selectedPlan?.priceFCFA ?? "N/A"}</strong>
            </p>
            <p className="mt-1">
              Montant total estime:{" "}
              <strong>{amountTotalFcfa.toLocaleString("fr-FR")} FCFA</strong>
            </p>
            <p className="mt-1 text-xs text-slate-600">
              Nous ne stockons pas le numero complet de carte. Seuls les elements de verification
              et references de transaction sont enregistres.
            </p>
          </div>

          <div className="flex items-start gap-3">
            <Checkbox
              id="acceptedTerms"
              checked={orderForm.acceptedTerms}
              onCheckedChange={(checked) => setOrderField("acceptedTerms", checked === true)}
            />
            <Label htmlFor="acceptedTerms" className="leading-5">
              J&apos;accepte les conditions d&apos;achat, la verification de paiement et le
              stockage des informations de commande.
            </Label>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsOrderDialogOpen(false)}
              disabled={isSubmittingOrder}
            >
              Annuler
            </Button>
            <Button type="button" onClick={submitOrder} disabled={isSubmittingOrder}>
              {isSubmittingOrder ? "Verification en cours..." : "Valider la commande"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </section>
  );
}
