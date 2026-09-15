import { PageShell } from "@/components/PageShell";

export default function Home() {
  return (
    <PageShell>
      <section className="hero" aria-labelledby="hero-title">
        <p className="eyebrow">Zion software platform</p>
        <h1 id="hero-title">Zion — software rooted in peace, justice, and human goodwill.</h1>
        <p className="hero-copy">
          Zion is a peacekeeping software initiative with two implemented flagship
          projects. The site keeps a cloud-bright, navy-accented feel so the work stays
          calm, legible, and grounded in a castle-like sense of structure.
        </p>
        <aside className="status" aria-labelledby="status-title">
          <h2 id="status-title">Foundation status</h2>
          <p>
            This repository includes the shared technical foundation plus the Harbor
            and Haven flagship demonstrations. It has no deployed service, real users,
            partners, or measured field outcomes; all accounts and workflow data are
            synthetic demo material.
          </p>
        </aside>
      </section>

      <section className="explore" aria-labelledby="explore-title">
        <div className="section-heading">
          <p className="eyebrow">Find your way around</p>
          <h2 id="explore-title">Two flagships, one honest map</h2>
        </div>
        <div className="card-grid">
          <article>
            <h3><a href="/flagships/harbor">Harbor</a></h3>
            <p>A synthetic, human-approved community coordination workflow.</p>
          </article>
          <article>
            <h3><a href="/flagships/haven">Haven</a></h3>
            <p>Synthetic, non-diagnostic navigation with fixed safety guidance.</p>
          </article>
        </div>
      </section>

      <section className="project-index" aria-labelledby="projects-title">
        <div className="section-heading">
          <p className="eyebrow">Project areas</p>
          <h2 id="projects-title">Two canonical Zion flagship pages</h2>
          <p>
            Each project area has its own page with purpose, audience, features,
            limitations, and evidence, so the site can point to real work instead of a
            shell.
          </p>
        </div>
        <nav className="project-index-nav" aria-label="Flagship pages">
          <a href="/flagships/harbor">Explore Harbor</a>
          <a href="/flagships/haven">Explore Haven</a>
          <a href="/flagships">Open the flagship catalog</a>
        </nav>
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
