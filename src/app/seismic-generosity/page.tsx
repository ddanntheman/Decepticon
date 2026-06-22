"use client";

import { useState, useEffect, FormEvent } from "react";
import Link from "next/link";
import "./sg.css";

function SgLogo() {
  return (
    <Link href="/seismic-generosity" className="sg-logo" aria-label="Seismic Generosity home">
      <span className="sg-logo-mark" />
      <span className="sg-logo-text">
        Seismic <em>Generosity</em>
      </span>
    </Link>
  );
}

function SgHeader() {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);
  return (
    <header className={`sg-header${scrolled ? " scrolled" : ""}`}>
      <div className="sg-container sg-header-inner">
        <SgLogo />
        <nav className="sg-nav" aria-label="Primary">
          <a href="#sequence">The Sequence</a>
          <a href="#becoming">Who We Become</a>
          <a href="#scripture">Anchor</a>
          <a href="#heart-in-heaven">Heart In Heaven</a>
          <a href="#join">Join</a>
        </nav>
        <a className="sg-btn sg-btn-primary" href="#join">
          Join the movement
        </a>
      </div>
    </header>
  );
}

function SgHero() {
  return (
    <section className="sg-hero" id="top">
      <svg
        className="sg-rings"
        viewBox="-350 -350 700 700"
        aria-hidden="true"
      >
        {Array.from({ length: 9 }).map((_, i) => (
          <circle key={i} cx="0" cy="0" r={50 + i * 38} strokeWidth="1" />
        ))}
        <circle
          cx="0"
          cy="0"
          r="32"
          fill="rgba(212,162,76,0.08)"
          stroke="rgba(212,162,76,0.4)"
        />
      </svg>
      <div className="sg-container sg-hero-inner">
        <p className="sg-eyebrow">A Christ-centered movement of mercy</p>
        <h1 className="sg-display">
          Generosity, before it is a gift,
          <br />
          is a <em>way of seeing.</em>
        </h1>
        <p className="sg-lead">
          Seismic Generosity is the movement that forms a new way of giving,
          before it asks for a dollar. We shape identity. We shape worldview. We
          shape the kind of person whose hand is already open when the moment
          comes.
        </p>
        <div className="sg-hero-cta">
          <a className="sg-btn sg-btn-primary sg-btn-lg" href="#join">
            Join the movement
          </a>
          <a className="sg-btn sg-btn-link" href="#sequence">
            Read the sequence &rarr;
          </a>
        </div>
      </div>
    </section>
  );
}

function SgSequence() {
  const steps = [
    {
      num: "I",
      title: "Revelation",
      body: "God is not distant from human suffering. He is deeply moved by it. Generosity begins where that truth lands.",
    },
    {
      num: "II",
      title: "Formation",
      body: "A new way of seeing forms a new way of living. Identity is shaped before action.",
    },
    {
      num: "III",
      title: "Expression",
      body: "Compassion becomes a response, not pressure. Generosity becomes overflow, not performance.",
    },
    {
      num: "IV",
      title: "Impact",
      body: "Open hands meet real lives. Movement meets mission. Generations are changed.",
    },
  ];
  return (
    <section className="sg-sequence" id="sequence">
      <div className="sg-container">
        <div className="sg-seq-head">
          <p className="sg-eyebrow center">The sacred sequence</p>
          <h2 className="sg-h2">
            Revelation, Formation, Expression, Impact.
          </h2>
          <p className="sg-lead">
            Four movements in one ecosystem. Each one flows from the one before.
          </p>
        </div>
        <div className="sg-seq-track">
          {steps.map((s, i) => (
            <article key={i} className="sg-seq-step">
              <div className="sg-seq-dot">
                <span className="num">{s.num}</span>
              </div>
              <h3 className="sg-h3">{s.title}</h3>
              <p>{s.body}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function SgBecoming() {
  return (
    <section className="sg-becoming" id="becoming">
      <div className="sg-container sg-becoming-grid">
        <div>
          <p className="sg-eyebrow">Who we are becoming</p>
          <h2 className="sg-h2">
            Identity before action. Worldview before outcome.
          </h2>
          <p>
            Seismic Generosity is not a campaign or a gala. It is a community of
            individuals, families, and partners who have decided that generosity
            is not what they do at the end of the year. It is the shape of how
            they live.
          </p>
          <p>
            When people encounter God&rsquo;s heart of mercy, three things
            change:
          </p>
          <ul className="three">
            <li>Compassion becomes a response, not pressure.</li>
            <li>Generosity becomes overflow, not performance.</li>
            <li>
              Giving becomes participation in what God is already doing.
            </li>
          </ul>
        </div>
        <aside>
          People are increasingly looking for more than charitable transactions.
          They want meaningful impact, authentic connection, and a compelling
          vision they can emotionally and spiritually invest in.
          <cite>Why this movement now</cite>
        </aside>
      </div>
    </section>
  );
}

function SgScripture() {
  return (
    <section className="sg-scripture" id="scripture">
      <div className="sg-container">
        <p className="sg-eyebrow center">Anchor scripture</p>
        <blockquote>
          &ldquo;Do not store up for yourselves treasures on earth, where moths
          and vermin destroy, and where thieves break in and steal. But store up
          for yourselves treasures in heaven... For where your treasure is, there
          your heart will be also.&rdquo;
        </blockquote>
        <div className="sg-cite">Matthew 6:19&ndash;21</div>
      </div>
    </section>
  );
}

function SgSibling() {
  return (
    <section className="sg-sibling" id="heart-in-heaven">
      <div className="sg-container">
        <div className="sg-sibling-card">
          <div>
            <p className="sg-eyebrow">The mission arm of this movement</p>
            <h2 className="sg-h2">Heart In Heaven.</h2>
            <p>
              Where Seismic Generosity forms the heart, Heart In Heaven gives it
              expression. Through the Heart In Heaven Digital Academy in Liberia,
              monthly Heart Partners fund tuition, lunches, uniforms, and the
              next generation of a nation.
            </p>
            <div style={{ display: "flex", gap: 14, flexWrap: "wrap" }}>
              <Link className="sg-btn sg-btn-primary" href="/">
                Visit Heart In Heaven &rarr;
              </Link>
              <Link className="sg-btn sg-btn-ghost" href="/#give">
                Become a Heart Partner
              </Link>
            </div>
          </div>
          <div className="sg-sibling-visual">
            HIHDA students with Liberian flag
          </div>
        </div>
      </div>
    </section>
  );
}

function SgJoin() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const submit = (e: FormEvent) => {
    e.preventDefault();
    if (!email) return;
    setSubmitted(true);
    setTimeout(() => setSubmitted(false), 4000);
    setEmail("");
  };
  return (
    <section className="sg-join" id="join">
      <div className="sg-join-inner">
        <p className="sg-eyebrow center">Join the movement</p>
        <h2 className="sg-h2">A community of mercy, in motion.</h2>
        <p>
          No annual gala. No giving day. A quarterly letter, a community of
          like-hearted partners, and an invitation to live with open hands.
        </p>
        <form onSubmit={submit}>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            aria-label="Email"
          />
          <button type="submit" className="sg-btn sg-btn-primary">
            {submitted ? "Welcome." : "Join"}
          </button>
        </form>
        <p className="sg-join-tag">
          A movement, not a mailing list. We send four letters a year.
        </p>
      </div>
    </section>
  );
}

function SgFooter() {
  return (
    <footer className="sg-footer">
      <div className="sg-container">
        <div className="sg-footer-grid">
          <div className="brand">
            <SgLogo />
            <p>
              &ldquo;Generosity, before it is a gift, is a way of
              seeing.&rdquo;
            </p>
            <div
              style={{
                fontSize: 12,
                color: "var(--sg-cream-faint)",
                lineHeight: 1.6,
              }}
            >
              Seismic Generosity is the worldview arm of the Heart In Heaven
              ecosystem.
              <br />
              Founded by Angelique Cooper McGlotten.
            </div>
          </div>
          <div>
            <h4>The movement</h4>
            <ul>
              <li>
                <a href="#sequence">The sacred sequence</a>
              </li>
              <li>
                <a href="#becoming">Who we&rsquo;re becoming</a>
              </li>
              <li>
                <a href="#scripture">Anchor scripture</a>
              </li>
              <li>
                <a href="#join">Join</a>
              </li>
            </ul>
          </div>
          <div>
            <h4>The mission</h4>
            <ul>
              <li>
                <Link href="/">Heart In Heaven</Link>
              </li>
              <li>
                <Link href="/#where-we-work">HIHDA &middot; Liberia</Link>
              </li>
              <li>
                <Link href="/#give">Become a Heart Partner</Link>
              </li>
              <li>
                <Link href="/#how-it-works">How giving works</Link>
              </li>
            </ul>
          </div>
        </div>
        <div className="sg-footer-bottom">
          <span>
            &copy; 2026 Seismic Generosity &middot; A Heart In Heaven, Inc.
            initiative
          </span>
          <span>
            Sibling to{" "}
            <Link href="/" style={{ color: "var(--sg-gold)" }}>
              heartinheaven.org
            </Link>
          </span>
        </div>
      </div>
    </footer>
  );
}

export default function SeismicGenerosityPage() {
  return (
    <div className="sg-page">
      <SgHeader />
      <main>
        <SgHero />
        <SgSequence />
        <SgBecoming />
        <SgScripture />
        <SgSibling />
        <SgJoin />
      </main>
      <SgFooter />
    </div>
  );
}
