"use client";

export default function WhereMoneyGoes() {
  const segments = [
    { name: "Programs", pct: 92, color: "#1F2A5C" },
    { name: "Operations", pct: 6, color: "#43527E" },
    { name: "Fundraising", pct: 2, color: "#D4A24C" },
  ];

  const radius = 100;
  const stroke = 32;
  const c = 2 * Math.PI * radius;
  let offset = 0;

  const partners = [
    "Heart In Heaven Digital Academy",
    "IEL Innovative Education",
    "ELWA Ministries",
    "Peachtree UMC",
    "Red Meets Green",
    "Chalmers Center",
    "New Harvest Global",
    "Local Ministry Partner",
  ];

  return (
    <section className="section" id="transparency">
      <div className="container">
        <div className="section-header">
          <p className="eyebrow">Where your money goes</p>
          <h2>Audited, transparent, accountable.</h2>
          <p className="lead">
            We publish our financials, name every partner ministry, and hold the
            Candid Platinum Seal of Transparency.
          </p>
        </div>
        <div className="money-grid">
          <div className="donut-wrap">
            <div className="donut">
              <svg
                width={280}
                height={280}
                viewBox="-130 -130 260 260"
                aria-label="Allocation donut"
              >
                <g transform="rotate(-90)">
                  <circle
                    cx="0"
                    cy="0"
                    r={radius}
                    fill="none"
                    stroke="var(--hh-warm-200)"
                    strokeWidth={stroke}
                  />
                  {segments.map((s, i) => {
                    const len = (s.pct / 100) * c;
                    const dash = `${len} ${c - len}`;
                    const el = (
                      <circle
                        key={i}
                        cx="0"
                        cy="0"
                        r={radius}
                        fill="none"
                        stroke={s.color}
                        strokeWidth={stroke}
                        strokeDasharray={dash}
                        strokeDashoffset={-offset}
                        strokeLinecap="butt"
                      />
                    );
                    offset += len;
                    return el;
                  })}
                </g>
              </svg>
              <div className="donut-center">
                <div className="pct">
                  92
                  <span
                    style={{
                      fontSize: "0.55em",
                      color: "var(--hh-gold-500)",
                      verticalAlign: "super",
                      marginLeft: 4,
                    }}
                  >
                    %
                  </span>
                </div>
                <div className="label">To programs</div>
              </div>
            </div>
            <div className="donut-legend">
              {segments.map((s, i) => (
                <div className="row" key={i}>
                  <span className="dot" style={{ background: s.color }} />
                  <span className="nm">{s.name}</span>
                  <span className="vl" style={{ marginLeft: "auto" }}>
                    {s.pct}%
                  </span>
                </div>
              ))}
            </div>
            <p
              style={{
                fontSize: 12,
                color: "var(--hh-warm-500)",
                textAlign: "center",
                margin: 0,
                maxWidth: 280,
              }}
            >
              FY2025 illustrative allocation.{" "}
              <a href="#" style={{ color: "var(--hh-indigo-600)" }}>
                View audited 990 &rarr;
              </a>
            </p>
          </div>
          <div>
            <p className="eyebrow no-rule" style={{ marginBottom: 20 }}>
              Our ministry partners
            </p>
            <div className="partner-grid">
              {partners.map((p) => (
                <div className="partner-tile" key={p}>
                  {p}
                </div>
              ))}
            </div>
            <p
              style={{
                fontSize: 13,
                color: "var(--hh-warm-500)",
                marginTop: 20,
              }}
            >
              We work with a small, vetted network of Liberian and US ministry
              partners. Each one meets the same standards of doctrinal alignment,
              financial accountability, and on-the-ground impact. Your gift
              reaches them through a single trusted channel.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
