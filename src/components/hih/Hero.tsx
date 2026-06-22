"use client";

interface HeroProps {
  onDonate: (freq?: string) => void;
}

export default function Hero({ onDonate }: HeroProps) {
  return (
    <section className="hero" id="top" aria-label="Heart In Heaven home hero">
      <div className="hero-media" aria-hidden="false">
        <div className="hero-placeholder">
          <span>Heart In Heaven Digital Academy &middot; Duan Town, Liberia</span>
        </div>
      </div>
      <div className="hero-caption">
        <span>Heart In Heaven Digital Academy &middot; Duan Town, Liberia</span>
      </div>
      <div className="container hero-inner">
        <div className="hero-copy">
          <p
            className="eyebrow"
            style={{ color: "rgba(247,242,231,0.78)", marginBottom: 28 }}
          >
            <span style={{ color: "var(--hh-gold-300)" }}>&#9679;</span> Heart
            In Heaven &middot; Liberia
          </p>
          <h1>
            Where the heart is,
            <br />
            the <span className="gold">treasure</span> follows.
          </h1>
          <p className="lead">
            Every monthly pledge feeds, teaches, and equips a child at the Heart
            In Heaven Digital Academy. Twenty-four students. One classroom. The
            next generation of a nation.
          </p>
          <div className="cta-row">
            <button
              className="btn btn-primary btn-lg"
              onClick={() => onDonate()}
            >
              Become a Heart Partner &middot; $40 a month
            </button>
            <a
              className="btn btn-ghost"
              href="#give"
              onClick={(e) => {
                e.preventDefault();
                onDonate("once");
              }}
              style={{ color: "rgba(247,242,231,0.8)" }}
            >
              or give once &rarr;
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
