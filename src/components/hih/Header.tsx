"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import Icon from "@/components/shared/Icon";

interface HeaderProps {
  onDonate: (freq?: string) => void;
}

export default function Header({ onDonate }: HeaderProps) {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const navItems: [string, string][] = [
    ["Our Mission", "#our-mission"],
    ["How It Works", "#how-it-works"],
    ["Where We Work", "#where-we-work"],
    ["Stories", "#stories"],
    ["About", "#about"],
  ];

  return (
    <>
      <header className={`site-header${scrolled ? " scrolled" : ""}`}>
        <div className="container site-header-inner">
          <Link href="/" aria-label="Heart In Heaven home" className="logo-link">
            <span className="logo-text">Heart In Heaven</span>
          </Link>
          <nav className="site-nav" aria-label="Primary">
            {navItems.map(([label, href]) => (
              <a key={href} href={href}>
                {label}
              </a>
            ))}
          </nav>
          <button className="btn btn-primary" onClick={() => onDonate()}>
            Give
          </button>
          <button
            className="mobile-toggle"
            onClick={() => setMenuOpen((o) => !o)}
            aria-label="Toggle menu"
          >
            <Icon name={menuOpen ? "close" : "menu"} size={28} />
          </button>
        </div>
      </header>
      <div
        className={`mobile-menu${menuOpen ? " open" : ""}`}
        aria-hidden={!menuOpen}
      >
        {navItems.map(([label, href]) => (
          <a key={href} href={href} onClick={() => setMenuOpen(false)}>
            {label}
          </a>
        ))}
      </div>
    </>
  );
}
