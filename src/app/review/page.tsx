import Link from "next/link";
import "./review.css";

const colors = [
  { name: "Heaven Indigo 600", hex: "#1F2A5C", role: "Primary brand" },
  { name: "Heaven Indigo 700", hex: "#161E44", role: "Headings" },
  { name: "Heaven Indigo 800", hex: "#0D132C", role: "Footer / inverse" },
  { name: "Heart Gold 400", hex: "#D4A24C", role: "Accent / CTAs" },
  { name: "Heart Gold 300", hex: "#DFB661", role: "Emphasis on dark" },
  { name: "Cream Linen", hex: "#F7F2E7", role: "Default canvas" },
  { name: "Cream 2", hex: "#F0E9D8", role: "Section alternate" },
  { name: "Paper", hex: "#FCFAF3", role: "Card surface" },
  { name: "Night", hex: "#0A0F22", role: "SG canvas" },
  { name: "Coral Hope", hex: "#E45A3B", role: "Reserved accent" },
  { name: "Warm 500", hex: "#6B6557", role: "Muted text" },
  { name: "Earth Charcoal", hex: "#1A1A1A", role: "Body text" },
];

export default function ReviewPage() {
  return (
    <div className="review-page">
      <header className="review-header">
        <div className="container">
          <p
            style={{
              fontSize: 12,
              letterSpacing: "0.22em",
              textTransform: "uppercase",
              color: "var(--hh-gold-300)",
              marginBottom: 16,
            }}
          >
            Founder Review
          </p>
          <h1>Heart In Heaven Ecosystem</h1>
          <p>
            A unified brand system for Heart In Heaven (mission arm) and Seismic
            Generosity (movement arm). Shared design tokens, complementary
            palettes, sibling navigation.
          </p>
        </div>
      </header>

      <nav className="review-nav">
        <div className="review-nav-inner">
          <a href="#ecosystem">Ecosystem</a>
          <a href="#palette">Color Palette</a>
          <a href="#typography">Typography</a>
          <a href="#sites">Live Sites</a>
        </div>
      </nav>

      <section className="review-section" id="ecosystem">
        <div className="container">
          <h2>Sibling Architecture</h2>
          <p className="subtitle">
            Two parallel brands, one shared design language, interconnected via
            footer links and cross-promotion.
          </p>
          <div className="ecosystem-diagram">
            <div className="eco-card hih">
              <p className="eco-label">Mission Arm</p>
              <p className="eco-title">Heart In Heaven</p>
              <p className="eco-desc">
                The donor-facing site. Cream Linen canvas, Heaven Indigo
                headings, Heart Gold CTAs. Drives monthly Heart Partner pledges
                to fund the HIHDA in Liberia.
              </p>
              <Link href="/" className="eco-link">
                View Heart In Heaven &rarr;
              </Link>
            </div>
            <div className="eco-card sg">
              <p className="eco-label">Movement Arm</p>
              <p className="eco-title">Seismic Generosity</p>
              <p className="eco-desc">
                The worldview site. Night canvas, cream type, gold accent. Forms
                identity and conviction before asking for a dollar.
              </p>
              <Link href="/seismic-generosity" className="eco-link">
                View Seismic Generosity &rarr;
              </Link>
            </div>
          </div>
          <div
            style={{
              textAlign: "center",
              padding: "32px",
              background: "var(--hh-cream-2)",
              borderRadius: 12,
              border: "1px solid var(--border)",
            }}
          >
            <p
              style={{
                fontFamily: "var(--font-display)",
                fontStyle: "italic",
                fontSize: 22,
                color: "var(--hh-indigo-700)",
                margin: "0 0 8px",
              }}
            >
              &ldquo;Where the heart is, the treasure follows.&rdquo;
            </p>
            <p
              style={{
                fontSize: 13,
                color: "var(--hh-warm-500)",
                margin: 0,
              }}
            >
              Heart In Heaven, Inc. &middot; 501(c)(3) &middot; EIN 87-4020929
            </p>
          </div>
        </div>
      </section>

      <section className="review-section" id="palette">
        <div className="container">
          <h2>Color Palette</h2>
          <p className="subtitle">
            Shared token system across both brands. Heart Gold reserved for CTAs
            only.
          </p>
          <div className="token-grid">
            {colors.map((c) => (
              <div className="token-card" key={c.hex}>
                <div className="token-swatch" style={{ background: c.hex }} />
                <div className="token-info">
                  <p className="name">{c.name}</p>
                  <p className="value">{c.hex}</p>
                  <p className="role">{c.role}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="review-section" id="typography">
        <div className="container">
          <h2>Typography</h2>
          <p className="subtitle">
            Source Serif 4 (display) + IBM Plex Sans (body) + IBM Plex Mono
            (stats). 8px base spacing unit.
          </p>
          <div className="type-specimen">
            <p className="label">Display &mdash; Source Serif 4</p>
            <p className="sample-display">
              Where the heart is, the treasure follows.
            </p>
          </div>
          <div className="type-specimen">
            <p className="label">Body &mdash; IBM Plex Sans</p>
            <p className="sample-body">
              Every monthly pledge feeds, teaches, and equips a child at the
              Heart In Heaven Digital Academy. Twenty-four students. One
              classroom. The next generation of a nation. Your gift is
              tax-deductible, and 92% of every dollar goes directly to programs.
            </p>
          </div>
          <div className="type-specimen">
            <p className="label">Mono &mdash; IBM Plex Mono</p>
            <p className="sample-mono">
              EIN 87-4020929 &middot; 501(c)(3) &middot; $40/mo &middot; 92%
              &middot; 24 students
            </p>
          </div>
        </div>
      </section>

      <section className="review-section" id="sites">
        <div className="container">
          <h2>Live Site Links</h2>
          <p className="subtitle">
            Navigate between the unified sites.
          </p>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(3, 1fr)",
              gap: 20,
            }}
          >
            <Link
              href="/"
              style={{
                display: "block",
                padding: "32px",
                background: "var(--hh-paper)",
                border: "1px solid var(--border)",
                borderRadius: 8,
                textAlign: "center",
              }}
            >
              <p
                style={{
                  fontFamily: "var(--font-display)",
                  fontWeight: 600,
                  fontSize: 20,
                  color: "var(--hh-indigo-700)",
                  margin: "0 0 8px",
                }}
              >
                Heart In Heaven
              </p>
              <p
                style={{
                  fontSize: 13,
                  color: "var(--hh-warm-500)",
                  margin: 0,
                }}
              >
                Mission arm &middot; Cream canvas
              </p>
            </Link>
            <Link
              href="/seismic-generosity"
              style={{
                display: "block",
                padding: "32px",
                background: "var(--hh-indigo-800)",
                border: "1px solid var(--border)",
                borderRadius: 8,
                textAlign: "center",
              }}
            >
              <p
                style={{
                  fontFamily: "var(--font-display)",
                  fontWeight: 600,
                  fontSize: 20,
                  color: "var(--hh-cream)",
                  margin: "0 0 8px",
                }}
              >
                Seismic Generosity
              </p>
              <p
                style={{
                  fontSize: 13,
                  color: "rgba(247,242,231,0.6)",
                  margin: 0,
                }}
              >
                Movement arm &middot; Night canvas
              </p>
            </Link>
            <Link
              href="/review"
              style={{
                display: "block",
                padding: "32px",
                background: "var(--hh-cream-2)",
                border: "2px solid var(--hh-gold-400)",
                borderRadius: 8,
                textAlign: "center",
              }}
            >
              <p
                style={{
                  fontFamily: "var(--font-display)",
                  fontWeight: 600,
                  fontSize: 20,
                  color: "var(--hh-indigo-700)",
                  margin: "0 0 8px",
                }}
              >
                Founder Review
              </p>
              <p
                style={{
                  fontSize: 13,
                  color: "var(--hh-warm-500)",
                  margin: 0,
                }}
              >
                Brand system overview
              </p>
            </Link>
          </div>
        </div>
      </section>

      <footer className="review-footer">
        <div className="container">
          <p>
            Heart In Heaven, Inc. &middot; 501(c)(3) &middot; EIN 87-4020929
          </p>
          <p style={{ marginTop: 8 }}>
            <Link href="/">heartinheaven.org</Link>
            {" \u00B7 "}
            <Link href="/seismic-generosity">seismicgenerosity.org</Link>
          </p>
        </div>
      </footer>
    </div>
  );
}
