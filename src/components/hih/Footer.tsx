"use client";

import Link from "next/link";
import Icon from "@/components/shared/Icon";

export default function Footer() {
  return (
    <footer className="site-footer" id="about">
      <div className="container">
        <div className="footer-grid">
          <div className="brand">
            <span className="footer-logo">Heart In Heaven</span>
            <p>&ldquo;One gift. Twenty ministries. Eternal impact.&rdquo;</p>
            <div className="legal">
              Heart In Heaven, Inc. is a 501(c)(3) nonprofit.
              <br />
              EIN{" "}
              <span style={{ fontFeatureSettings: '"tnum" 1' }}>
                87-4020929
              </span>{" "}
              &middot; Your gift is tax-deductible.
              <br />
              PO Box 86624, Vint Hill Farms, VA 20187
              <br />
              +1 540.316.0679 &middot; angelique@heartinheaven.org
            </div>
          </div>
          <div>
            <h4>Mission</h4>
            <ul>
              <li>
                <a href="#our-mission">Our Mission</a>
              </li>
              <li>
                <a href="#how-it-works">How It Works</a>
              </li>
              <li>
                <a href="#where-we-work">Where We Work</a>
              </li>
              <li>
                <a href="#stories">Stories</a>
              </li>
              <li>
                <a href="#about">FAQ</a>
              </li>
            </ul>
          </div>
          <div>
            <h4>Trust</h4>
            <ul>
              <li>
                <a href="#">Financials &amp; 990</a>
              </li>
              <li>
                <a href="#">Annual report</a>
              </li>
              <li>
                <a href="#">Partner ministries</a>
              </li>
              <li>
                <a href="#">Accountability</a>
              </li>
              <li>
                <a href="#">Privacy</a>
              </li>
            </ul>
          </div>
          <div className="newsletter">
            <h4>Stay connected</h4>
            <form onSubmit={(e) => e.preventDefault()}>
              <input
                type="email"
                placeholder="your@email.com"
                aria-label="Email for newsletter"
              />
              <button type="submit">Join</button>
            </form>
            <p
              style={{
                fontSize: 12,
                color: "rgba(247,242,231,0.55)",
                margin: 0,
              }}
            >
              Quarterly impact updates, never spam.
            </p>
            <div className="socials" aria-label="Social media">
              <a
                href="https://www.facebook.com/aheartinheaven/"
                aria-label="Facebook"
              >
                <Icon name="facebook" size={18} />
              </a>
              <a
                href="https://twitter.com/Heart_InHeaven"
                aria-label="Twitter / X"
              >
                <Icon name="twitter" size={18} />
              </a>
              <a
                href="https://www.instagram.com/aheartinheaven/"
                aria-label="Instagram"
              >
                <Icon name="instagram" size={18} />
              </a>
              <a
                href="https://www.youtube.com/@yourheartinheaven"
                aria-label="YouTube"
              >
                <Icon name="youtube" size={18} />
              </a>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <span>&copy; 2026 Heart In Heaven, Inc. All rights reserved.</span>
          <div className="footer-bottom-links">
            <Link
              href="/seismic-generosity"
              style={{ color: "var(--hh-gold-300)" }}
            >
              Part of the Seismic Generosity ecosystem &nearr;
            </Link>
            <a href="#">Sitemap</a>
            <a href="#">Privacy</a>
            <a href="#">Terms</a>
            <a href="#">Accessibility</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
