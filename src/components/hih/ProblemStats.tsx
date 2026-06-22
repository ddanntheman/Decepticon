"use client";

export default function ProblemStats() {
  const stats = [
    {
      big: "80%",
      label: "Unemployment in Liberia today. Families cannot afford fees, uniforms, or daily meals.",
      source: "Liberia Institute of Statistics",
    },
    {
      big: "1 in 4",
      label: "Children under five face stunting from chronic malnutrition.",
      source: "UNICEF \u00b7 WHO Joint Estimates",
    },
    {
      big: "24",
      label: "Students enrolled at the Heart In Heaven Digital Academy. The waiting list is longer than the classroom.",
      source: "HIHDA \u00b7 Duan Town, Gardnersville",
    },
  ];

  return (
    <section className="section" id="problem">
      <div className="container">
        <div className="section-header">
          <p className="eyebrow">Why this matters</p>
          <h2>Liberia is rebuilding. We are part of it.</h2>
          <p className="lead">
            The numbers are heavy. The work is concrete. Every pledge moves a
            student from waiting list to classroom.
          </p>
        </div>
        <div className="problem-grid">
          {stats.map((s, i) => (
            <div className="stat" key={i}>
              <div className="big numeral">{s.big}</div>
              <div className="label">{s.label}</div>
              <div className="source">Source &middot; {s.source}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
