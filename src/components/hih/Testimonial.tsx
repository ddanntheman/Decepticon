"use client";

export default function Testimonial() {
  return (
    <section className="section" id="testimonial">
      <div className="container">
        <div className="testimonial">
          <div className="portrait">
            <div className="portrait-placeholder">
              <span>Heart Partner Portrait</span>
            </div>
          </div>
          <div>
            <p className="eyebrow">A Heart Partner&rsquo;s story</p>
            <blockquote>
              &ldquo;I&rsquo;d been giving to one charity for fifteen years. I
              always wondered about the ministries I never got to. Heart In
              Heaven was the answer to a prayer I didn&rsquo;t know I&rsquo;d
              been praying.&rdquo;
            </blockquote>
            <div className="attribution">
              <span className="name">Cathy Mae Williams</span>
              Heart Partner since 2024 &middot; Atlanta, GA
            </div>
            <a
              className="btn btn-ghost"
              style={{ marginTop: 8 }}
              href="#stories"
            >
              Meet more Heart Partners &rarr;
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
