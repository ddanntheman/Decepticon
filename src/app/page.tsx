"use client";

import { useState } from "react";
import "./hih.css";
import Header from "@/components/hih/Header";
import Hero from "@/components/hih/Hero";
import TrustStrip from "@/components/hih/TrustStrip";
import ProblemStats from "@/components/hih/ProblemStats";
import HowItWorks from "@/components/hih/HowItWorks";
import PledgeTangibles from "@/components/hih/PledgeTangibles";
import WhereMoneyGoes from "@/components/hih/WhereMoneyGoes";
import Spotlight from "@/components/hih/Spotlight";
import Testimonial from "@/components/hih/Testimonial";
import FounderVideo from "@/components/hih/FounderVideo";
import FinalAsk from "@/components/hih/FinalAsk";
import Footer from "@/components/hih/Footer";
import DonationModal from "@/components/hih/DonationModal";
import Icon from "@/components/shared/Icon";

export default function HeartInHeavenPage() {
  const [modalOpen, setModalOpen] = useState(false);
  const [modalFreq, setModalFreq] = useState("monthly");
  const [toast, setToast] = useState<string | null>(null);
  const [partners, setPartners] = useState(63);
  const goal = 100;

  const openDonate = (freq = "monthly") => {
    setModalFreq(freq);
    setModalOpen(true);
  };

  const give = (amount: number, freq: string) => {
    setModalOpen(false);
    if (freq === "monthly") setPartners((p) => Math.min(goal, p + 1));
    const label =
      freq === "monthly"
        ? `$${amount}/mo Heart Partner gift`
        : `$${amount} one-time gift`;
    setToast(`Thank you. Your ${label} was received.`);
    setTimeout(() => setToast(null), 4500);
  };

  const newsletter = (email: string) => {
    setToast(`Thanks. We'll send the report to ${email}.`);
    setTimeout(() => setToast(null), 4000);
  };

  return (
    <>
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <Header onDonate={openDonate} />
      <main id="main">
        <Hero onDonate={openDonate} />
        <TrustStrip />
        <ProblemStats />
        <HowItWorks />
        <PledgeTangibles onDonate={openDonate} />
        <WhereMoneyGoes />
        <Spotlight onDonate={openDonate} />
        <Testimonial />
        <FounderVideo />
        <FinalAsk
          partners={partners}
          goal={goal}
          onDonate={openDonate}
          onNewsletter={newsletter}
        />
      </main>
      <Footer />
      <button className="mobile-give-pill" onClick={() => openDonate("monthly")}>
        Give &middot; $40/mo
      </button>
      <DonationModal
        open={modalOpen}
        defaultFreq={modalFreq}
        onClose={() => setModalOpen(false)}
        onGive={give}
      />
      {toast && (
        <div className="toast" role="status">
          <span className="check">
            <Icon name="seal" size={14} />
          </span>
          <span>{toast}</span>
        </div>
      )}
    </>
  );
}
