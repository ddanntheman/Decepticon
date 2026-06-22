"use client";

export default function FounderVideo() {
  return (
    <section className="section cream-2" id="founder">
      <div className="founder">
        <p className="eyebrow center no-rule">A word from our founder</p>
        <h2
          style={{
            fontFamily: "var(--font-display)",
            fontSize: "clamp(1.875rem, 3.5vw, 2.5rem)",
            textAlign: "center",
            margin: "0 0 36px",
            letterSpacing: "-0.015em",
            color: "var(--hh-indigo-700)",
            fontWeight: 600,
          }}
        >
          &ldquo;If your heart is here, your treasure can be too.&rdquo;
        </h2>
        <div className="video-frame" role="region" aria-label="Founder video">
          <iframe
            src="https://www.youtube.com/embed/5j_GOuMH4jU?rel=0&modestbranding=1"
            title="Heart In Heaven, A word from our founder"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            style={{
              position: "absolute",
              inset: 0,
              width: "100%",
              height: "100%",
              border: 0,
              zIndex: 1,
            }}
          />
        </div>
        <p className="below">
          <a href="#our-mission" style={{ color: "var(--hh-indigo-600)" }}>
            Read our founding story &rarr;
          </a>
        </p>
      </div>
    </section>
  );
}
