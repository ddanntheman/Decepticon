"use client";

interface PledgeTangiblesProps {
  onDonate: (freq?: string) => void;
}

export default function PledgeTangibles({ onDonate }: PledgeTangiblesProps) {
  const tiers = [
    {
      amount: "$25",
      label: "Per month",
      title: "A week of school lunches.",
      body: "Five hot meals on five school days. The thing that keeps a child in their seat through the afternoon.",
      cta: "Cover a week",
      highlight: false,
    },
    {
      amount: "$40",
      label: "Per month",
      title: "A Heart Partner share.",
      body: "Tuition, supplies, and lunch toward one student. The default monthly pledge of the Heart Partner movement.",
      highlight: true,
      cta: "Become a Heart Partner",
    },
    {
      amount: "$75",
      label: "Per month",
      title: "Full sponsorship.",
      body: "Uniform, books, fees, and meals for one named student through a full academic year.",
      cta: "Sponsor a student",
      highlight: false,
    },
    {
      amount: "$150",
      label: "Per month",
      title: "A classroom partner.",
      body: "Teacher pay, a stack of laptops, and a season of operating support for the whole HIHDA classroom.",
      cta: "Partner with a classroom",
      highlight: false,
    },
  ];

  return (
    <section className="section pledge-section" id="pledge">
      <div className="container">
        <div className="section-header">
          <p className="eyebrow">What your pledge buys</p>
          <h2>Concrete things, paid for on schedule.</h2>
          <p className="lead">
            No abstract impact reports. Real receipts, real children, real
            classrooms. Pick a tier that fits your month.
          </p>
        </div>
        <div className="pledge-grid">
          {tiers.map((t) => (
            <article
              key={t.amount}
              className={`pledge-card${t.highlight ? " highlight" : ""}`}
            >
              {t.highlight && <span className="pledge-flag">Most chosen</span>}
              <div className="pledge-amt">
                <span className="numeral">{t.amount}</span>
                <span className="pledge-cadence">{t.label}</span>
              </div>
              <h3 className="pledge-title">{t.title}</h3>
              <p className="pledge-body">{t.body}</p>
              <button
                className={`btn ${t.highlight ? "btn-primary" : "btn-secondary"}`}
                onClick={() => onDonate()}
              >
                {t.cta}
              </button>
            </article>
          ))}
        </div>
        <p className="pledge-foot">
          Every pledge is tax-deductible. Heart In Heaven, Inc. is a 501(c)(3);
          EIN 87-4020929. We&rsquo;ll send a receipt by email within five
          minutes.
        </p>
      </div>
    </section>
  );
}
