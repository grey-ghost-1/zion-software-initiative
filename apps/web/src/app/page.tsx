import { PageShell } from "@/components/PageShell";

export default function Home() {
  return (
    <PageShell active="home">
      <section className="hero" aria-labelledby="hero-title">
        <p className="eyebrow">Zion software platform</p>
        <h1 id="hero-title">Zion — software rooted in peace, justice, and human goodwill.</h1>
        <p className="hero-copy">
          Zion is a peacekeeping software initiative built on three core avenues of
          impact. Each one exists to prove a simple truth: technology can heal,
          protect, and uplift — not harm.
        </p>
        <aside className="status" aria-labelledby="status-title">
          <h2 id="status-title">Foundation status</h2>
          <p>
            This repository includes the shared technical foundation plus the three
            Zion avenues of impact. It has no deployed service, real users,
            partners, or measured field outcomes; all accounts and workflow data are
            synthetic demo material.
          </p>
        </aside>
      </section>

      <section className="explore" aria-labelledby="explore-title">
        <div className="section-heading">
          <p className="eyebrow">Find your way around</p>
          <h2 id="explore-title">Three core avenues, one honest map</h2>
        </div>
        <div className="card-grid">
          <article>
            <h3>Care for the Vulnerable</h3>
            <p>Community Aid Hub connects food, shelter, transportation, and emergency support.</p>
          </article>
          <article>
            <h3>Healing &amp; Health Access</h3>
            <p>Health Navigator and Care Routing Directory make care easier to understand.</p>
          </article>
          <article>
            <h3>AI Infrastructure, Automation &amp; Empowerment</h3>
            <p>Humanitarian Automation Pipeline and AI Empowerment &amp; Education Suite.</p>
          </article>
        </div>
      </section>

      <section aria-labelledby="philosophy-title">
        <div className="section-heading">
          <p className="eyebrow">Our philosophy</p>
          <h2 id="philosophy-title">Software should serve humanity</h2>
        </div>
        <p>
          Not profit. Not surveillance. Not division. Zion builds tools that reflect
          goodwill, justice, and peace — technology that protects instead of
          exploits, clarifies instead of confuses, and empowers instead of replaces.
        </p>
      </section>

      <section aria-labelledby="mission-title">
        <div className="section-heading">
          <p className="eyebrow">Our mission</p>
          <h2 id="mission-title">Make the world gentler, safer, and more connected</h2>
        </div>
        <p>
          One line of code, one act of service, one community at a time.
        </p>
      </section>

      <section className="boundaries" aria-labelledby="boundaries-title">
        <h2 id="boundaries-title">Built around truthful boundaries</h2>
        <p>
          Current work uses synthetic examples only: demo user accounts, demo
          organizations, and no real personal, health, or location data. Zion does
          not provide diagnosis, medical advice, emergency response, aid provision,
          or production humanitarian capability, and claims no partners, users, or
          autonomous operation.
        </p>
        <a
          href="https://github.com/grey-ghost-1/zion-software-initiative/blob/main/README.md"
          target="_blank"
          rel="noopener noreferrer"
        >
          Read the project boundaries
        </a>
      </section>
    </PageShell>
  );
}
