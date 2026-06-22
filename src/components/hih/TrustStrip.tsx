"use client";

import Icon from "@/components/shared/Icon";

export default function TrustStrip() {
  return (
    <div className="trust-strip" aria-label="Trust and accountability">
      <div className="container trust-strip-inner">
        <div className="item">
          <Icon name="shield-check" size={20} />
          <span>
            <b>501(c)(3)</b> &middot; EIN 87-4020929
          </span>
        </div>
        <div className="item">
          <Icon name="seal" size={20} />
          <span>
            <b>Candid</b> Platinum Seal of Transparency
          </span>
        </div>
        <div className="item">
          <Icon name="transparency" size={20} />
          <span>
            <b>100%</b> of public donations go to programs
            <sup style={{ fontSize: 9, color: "var(--hh-warm-500)" }}>&dagger;</sup>
          </span>
        </div>
        <div className="item">
          <Icon name="heart" size={20} />
          <span>
            <b>Vetted</b> local Liberian ministry partners
          </span>
        </div>
      </div>
    </div>
  );
}
