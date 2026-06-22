"use client";

interface SpotlightProps {
  onDonate: (freq?: string) => void;
}

export default function Spotlight({ onDonate }: SpotlightProps) {
  return (
    <section className="spotlight" id="where-we-work" aria-label="HIHDA spotlight">
      <div className="spotlight-photo">
        <div className="photo-placeholder">
          <span>Founder Angelique with HIHDA students</span>
        </div>
        <div className="photo-caption">
          <span>HIHDA classroom &middot; Duan Town, Gardnersville</span>
        </div>
      </div>
      <div className="spotlight-copy">
        <p className="eyebrow">The class of 2026</p>
        <h2>
          Twenty-four students. <span className="name">One school.</span>
        </h2>
        <p>
          The Heart In Heaven Digital Academy operates Monday through Friday from
          8:00am to 2:30pm, nursery through Grade 6. Every student wears a clean
          uniform. Every student eats lunch. Every student is named on our roll.
        </p>
        <p>
          Tuition is paid by Heart Partners in the United States. The waiting
          list is twice as long as the classroom. Each new monthly pledge of $40
          opens one more seat.
        </p>
        <div className="meta-line">
          <span className="pill">HIHDA</span>
          <span style={{ color: "var(--fg-muted)" }}>
            Gardnersville Township, Monrovia
          </span>
          <span
            style={{
              marginLeft: "auto",
              color: "var(--hh-warm-700)",
              fontWeight: 600,
            }}
          >
            $40 / month opens a seat
          </span>
        </div>
        <div style={{ display: "flex", gap: 14, flexWrap: "wrap" }}>
          <button className="btn btn-primary" onClick={() => onDonate()}>
            Open a seat &middot; $40 / mo
          </button>
          <a className="btn btn-ghost" href="#launch-liberia">
            Visit the school &rarr;
          </a>
        </div>
      </div>
    </section>
  );
}
