import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";

export const metadata: Metadata = {
  title: "About Justin · Zion Software Initiative",
};

export default function AboutPage() {
  return (
    <PageShell active="about">
      <section className="page-hero" aria-labelledby="about-title">
        <p className="eyebrow">Engineering portfolio</p>
        <h1 id="about-title">About Justin Wimmer</h1>
        <p className="page-intro">
          I&apos;m Justin Wimmer, an entry-level full-stack/backend developer. Zion is
          where I build in public: real code, real tests, and honest status
          disclosures instead of a polished but unverifiable resume claim.
        </p>
      </section>

      <section aria-labelledby="how-to-verify-title">
        <div className="section-heading">
          <p className="eyebrow">Don&apos;t take my word for it</p>
          <h2 id="how-to-verify-title">How to verify what I actually built</h2>
        </div>
        <div className="card-grid">
          <article>
            <h3>Read the code</h3>
            <p>
              The <a href="/projects">Projects</a> page links straight into the
              source for each piece of this foundation.
            </p>
          </article>
          <article>
            <h3>Run the tests</h3>
            <p>
              Every implemented claim on the <a href="/evidence">Evidence</a> page
              names the automated test that checks it.
            </p>
          </article>
          <article>
            <h3>Read the decisions</h3>
            <p>
              Architecture decision records in the repository explain why each
              boundary exists, not just what it does.
            </p>
          </article>
        </div>
      </section>

      <section className="boundaries" aria-labelledby="contact-title">
        <h2 id="contact-title">Get in touch</h2>
        <p>
          The best way to reach me or review my work history is through GitHub.
          Zion has no contact form, mailing list, or account registration.
        </p>
        <a href="https://github.com/grey-ghost-1" target="_blank" rel="noopener noreferrer">
          View my GitHub profile
        </a>
      </section>
    </PageShell>
  );
}
