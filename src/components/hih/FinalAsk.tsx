"use client";

import { FormEvent } from "react";

interface FinalAskProps {
  partners: number;
  goal: number;
  onDonate: (freq?: string) => void;
  onNewsletter: (email: string) => void;
}

export default function FinalAsk({ partners, goal, onDonate, onNewsletter }: FinalAskProps) {
  const pct = Math.min(100, Math.round((partners / goal) * 100));

  return (
    <section className="final-ask" id="give">
      <div className="final-ask-inner">
        <p className="eyebrow center on-ink">An invitation</p>
        <h2>
          Will you be one of the next <em>100 Heart Partners?</em>
        </h2>
        <p className="lead">
          A growing community of monthly givers, quietly funding the school, the
          lunches, and the next year of Liberian students.
        </p>

        <div
          className="progress"
          aria-label={`${partners} of ${goal} Heart Partners`}
        >
          <div className="progress-row">
            <span className="num">{partners}</span>
            <span className="of">
              of {goal} new Heart Partners &middot; {pct}%
            </span>
          </div>
          <div className="bar">
            <span style={{ width: pct + "%" }} />
          </div>
        </div>

        <div className="cta-row">
          <button
            className="btn btn-primary btn-lg"
            onClick={() => onDonate("monthly")}
          >
            Become a Heart Partner &middot; $40/mo
          </button>
          <button
            className="btn btn-inverse btn-lg"
            onClick={() => onDonate("once")}
          >
            Give once
          </button>
        </div>

        <div className="newsletter-aside">
          <p>
            Not ready? Get our 2026 Liberia Impact Report. Sent quarterly, no
            spam.
          </p>
          <form
            onSubmit={(e: FormEvent<HTMLFormElement>) => {
              e.preventDefault();
              const fd = new FormData(e.currentTarget);
              onNewsletter(fd.get("email") as string);
              e.currentTarget.reset();
            }}
          >
            <input
              type="email"
              name="email"
              placeholder="your@email.com"
              aria-label="Email"
              required
            />
            <button className="btn btn-primary" type="submit">
              Get the report
            </button>
          </form>
        </div>
      </div>
    </section>
  );
}
