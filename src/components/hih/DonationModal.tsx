"use client";

import { useState, useRef, FormEvent } from "react";
import Icon from "@/components/shared/Icon";

interface DonationModalProps {
  open: boolean;
  defaultFreq?: string;
  onClose: () => void;
  onGive: (amount: number, freq: string) => void;
}

export default function DonationModal({
  open,
  defaultFreq = "monthly",
  onClose,
  onGive,
}: DonationModalProps) {
  const [freq, setFreq] = useState(defaultFreq);
  const [amount, setAmount] = useState(40);
  const [custom, setCustom] = useState("");
  const [pay, setPay] = useState("card");
  const [first, setFirst] = useState("");
  const [last, setLast] = useState("");
  const [email, setEmail] = useState("");
  const [coverFee, setCoverFee] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const wasOpen = useRef(false);
  if (open && !wasOpen.current) {
    wasOpen.current = true;
    if (freq !== defaultFreq) setFreq(defaultFreq);
    const defaultAmt = defaultFreq === "monthly" ? 40 : 50;
    setAmount(defaultAmt);
    setCustom("");
  }
  if (!open && wasOpen.current) {
    wasOpen.current = false;
  }

  if (!open) return null;

  const tiers: [number, string][] =
    freq === "monthly"
      ? [
          [25, "One student fed for a school week."],
          [40, "A full Heart Partner share funding all 20+ ministries."],
          [75, "A month of clean water for a family."],
          [150, "A new savings group launch kit."],
        ]
      : [
          [50, "A week of school lunches for a classroom."],
          [100, "A Bible translation hour funded."],
          [250, "Clean water for a family for two years."],
          [500, "A savings group facilitator trained."],
        ];

  const chosen = custom !== "" ? Number(custom) || 0 : amount;
  const captionFor = chosen
    ? (
        tiers.find(([a]) => a === chosen) || [
          null,
          `Your $${chosen} ${freq === "monthly" ? "monthly" : "one-time"} gift will be split across all 20+ partner ministries.`,
        ]
      )[1]
    : "";

  const submit = (e: FormEvent) => {
    e.preventDefault();
    if (!chosen) return;
    setSubmitting(true);
    setTimeout(() => {
      setSubmitting(false);
      onGive(chosen, freq);
    }, 700);
  };

  const fmt = (n: number) =>
    `$${n}${freq === "monthly" ? "/mo" : ""}`;

  return (
    <div
      className="modal-backdrop"
      role="dialog"
      aria-modal="true"
      aria-labelledby="give-title"
      onClick={onClose}
    >
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <div>
            <p className="eyebrow no-rule" style={{ marginBottom: 4 }}>
              Heart Partner Giving
            </p>
            <h3 id="give-title">Become a Heart Partner.</h3>
          </div>
          <button className="close" onClick={onClose} aria-label="Close">
            <Icon name="close" size={20} />
          </button>
        </div>
        <div className="modal-body">
          <form onSubmit={submit}>
            <div className="tabs" role="tablist">
              <button
                type="button"
                role="tab"
                aria-selected={freq === "monthly"}
                className={freq === "monthly" ? "active" : ""}
                onClick={() => { setFreq("monthly"); setAmount(40); setCustom(""); }}
              >
                Monthly
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={freq === "once"}
                className={freq === "once" ? "active" : ""}
                onClick={() => { setFreq("once"); setAmount(50); setCustom(""); }}
              >
                One-Time
              </button>
            </div>

            <p
              style={{
                margin: "0 0 14px",
                fontWeight: 600,
                fontSize: 14,
                color: "var(--fg)",
              }}
            >
              Choose your gift
            </p>
            <div className="amount-grid">
              {tiers.map(([amt]) => (
                <button
                  type="button"
                  key={amt}
                  className={`amount-btn${custom === "" && amount === amt ? " selected" : ""}`}
                  onClick={() => {
                    setAmount(amt);
                    setCustom("");
                  }}
                >
                  ${amt}
                </button>
              ))}
              <input
                className={`amount-btn other${custom !== "" ? " selected" : ""}`}
                type="text"
                inputMode="numeric"
                placeholder="Other"
                value={custom ? "$" + custom : ""}
                onChange={(e) =>
                  setCustom(e.target.value.replace(/[^\d]/g, ""))
                }
                style={{ textAlign: "center" }}
              />
            </div>
            <p className="amount-caption">{captionFor}</p>

            <div className="field-row">
              <div className="field">
                <label htmlFor="first">First name</label>
                <input
                  id="first"
                  required
                  value={first}
                  onChange={(e) => setFirst(e.target.value)}
                />
              </div>
              <div className="field">
                <label htmlFor="last">Last name</label>
                <input
                  id="last"
                  required
                  value={last}
                  onChange={(e) => setLast(e.target.value)}
                />
              </div>
            </div>
            <div className="field">
              <label htmlFor="email">Your email</label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="for your tax receipt"
              />
            </div>

            <p
              style={{
                margin: "4px 0 8px",
                fontWeight: 500,
                fontSize: 13,
                color: "var(--fg-muted)",
              }}
            >
              Payment method
            </p>
            <div className="pay-methods">
              {(
                [
                  ["card", "Card"],
                  ["apple", "Apple Pay"],
                  ["paypal", "PayPal"],
                ] as [string, string][]
              ).map(([k, label]) => (
                <button
                  key={k}
                  type="button"
                  className={pay === k ? "selected" : ""}
                  onClick={() => setPay(k)}
                >
                  {label}
                </button>
              ))}
            </div>

            <label className="fee-check">
              <input
                type="checkbox"
                checked={coverFee}
                onChange={(e) => setCoverFee(e.target.checked)}
              />
              <span>
                I&rsquo;ll cover the processing fee so{" "}
                <b>100% goes to programs</b>.
              </span>
            </label>

            <button
              className="btn btn-primary btn-lg"
              disabled={!chosen || submitting}
              style={{ width: "100%" }}
            >
              {submitting ? "Processing\u2026" : `Give ${fmt(chosen || 40)}`}
            </button>

            <div className="trust-row">
              <span>Secured by Stripe</span>
              <span>&middot;</span>
              <span>501(c)(3) Tax-Deductible</span>
              <span>&middot;</span>
              <span>EIN 87-4020929</span>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
