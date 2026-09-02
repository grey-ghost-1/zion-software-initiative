import { PageShell } from "@/components/PageShell";

export default function Home() {
  return (
    <PageShell active="home">
      <section className="hero" aria-labelledby="hero-title">
        <p className="eyebrow">Social-impact initiative hub + engineering portfolio</p>
        <h1 id="hero-title">Thoughtful software, built in the open.</h1>
        <p className="hero-copy">
          Zion is an independent home for proposed public-interest software and
          Justin Wimmer&apos;s full-stack/backend engineering work.
        </p>
        <aside className="status" aria-labelledby="status-title">
          <h2 id="status-title">Foundation status</h2>
          <p>
            This repository is an early technical foundation: a shared web shell, API,
            database schema, and authentication/authorization core. It has no live
            product workflows, real users, partners, or measured field outcomes, and
            all accounts and data are synthetic demo material.
          </p>
        </aside>
      </section>

      <section className="explore" aria-labelledby="explore-title">
        <div className="section-heading">
          <p className="eyebrow">Find your way around</p>
          <h2 id="explore-title">Two audiences, one honest map</h2>
        </div>
        <div className="card-grid">
          <article>
            <h3>Initiatives</h3>
            <p>How Zion approaches proposed public-interest work, and what is not built yet.</p>
          </article>
          <article>
            <h3>Projects</h3>
            <p>Engineering case studies of what has actually been implemented so far.</p>
          </article>
          <article>
            <h3>Evidence</h3>
            <p>Every implemented claim linked to the code and tests that back it up.</p>
          </article>
        </div>
      </section>

      <section className="boundaries" aria-labelledby="boundaries-title">
        <h2 id="boundaries-title">Built around truthful boundaries</h2>
        <p>
          Current work uses synthetic examples only: demo user accounts, demo
          organizations, and no real personal, health, or location data. Zion does not
          provide diagnosis, medical advice, emergency response, aid provision, or
          production humanitarian capability, and claims no partners, users, or
          autonomous operation.
        </p>
        <a href="https://github.com/grey-ghost-1/zion-software-initiative/blob/main/README.md">
          Read the project boundaries
        </a>
      </section>
    </PageShell>
  );
}
