"use client";

import Icon from "@/components/shared/Icon";

export default function HowItWorks() {
  const steps = [
    {
      num: "STEP 01",
      icon: "heart",
      title: "You pledge $40 a month.",
      body: "One simple, recurring gift. Set it up in two minutes. Cancel any time. Tax-deductible to the dollar.",
    },
    {
      num: "STEP 02",
      icon: "converge",
      title: "Funds land in Liberia.",
      body: "Pledges pool into one stewarded account, then move directly to HIHDA and our local partners on the ground in Duan Town.",
    },
    {
      num: "STEP 03",
      icon: "tree",
      title: "The school runs.",
      body: "Tuition is paid. Lunches are served. Teachers are paid. Books are bought. You get a monthly note showing where every dollar landed.",
    },
  ];

  return (
    <section className="section cream-2" id="how-it-works">
      <div className="container">
        <div className="section-header center">
          <p className="eyebrow center no-rule">
            How your pledge becomes a classroom
          </p>
          <h2>Every dollar lands in Liberia.</h2>
          <p className="lead">
            No middlemen. No campaign-of-the-month. One pledge, one school, one
            country, one generation.
          </p>
        </div>
        <div className="steps">
          {steps.map((s, i) => (
            <div key={i} className="step-group">
              <article className="step">
                <span className="step-num">{s.num}</span>
                <div className="icon">
                  <Icon name={s.icon} size={28} />
                </div>
                <h3>{s.title}</h3>
                <p>{s.body}</p>
              </article>
              {i < steps.length - 1 && (
                <div className="arrow" aria-hidden="true">
                  <Icon name="arrow-long" />
                </div>
              )}
            </div>
          ))}
        </div>
        <div style={{ textAlign: "center" }}>
          <a className="btn btn-ghost" href="#how-it-works">
            Read the full accounting &rarr;
          </a>
        </div>
      </div>
    </section>
  );
}
