import Link from "next/link";

export default function Home() {
  return (
    <>
      <a className="skip-link" href="#main-content">
        Skip to main content
      </a>
      <header className="site-header">
        <Link className="brand" href="/" aria-label="Zion home">
          Zion
        </Link>
        <a
          className="repository-link"
          href="https://github.com/grey-ghost-1/zion-software-initiative"
        >
          View source
        </a>
      </header>
      <main id="main-content">
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
              This repository is an early technical foundation. It has no live
              workflows, real users, partnerships, or measured field outcomes.
            </p>
          </aside>
        </section>

        <section className="initiatives" aria-labelledby="initiatives-title">
          <div className="section-heading">
            <p className="eyebrow">Proposed initiatives</p>
            <h2 id="initiatives-title">Three directions, not yet products</h2>
          </div>
          <div className="card-grid">
            <article>
              <h3>Harbor</h3>
              <p>Exploring care, resource, shelter, and volunteer coordination.</p>
            </article>
            <article>
              <h3>Haven</h3>
              <p>Exploring non-diagnostic health navigation with clear safety limits.</p>
            </article>
            <article>
              <h3>Beacon</h3>
              <p>
                Exploring responsible AI orchestration and public-interest workflows.
              </p>
            </article>
          </div>
        </section>

        <section className="boundaries" aria-labelledby="boundaries-title">
          <h2 id="boundaries-title">Built around truthful boundaries</h2>
          <p>
            Current work uses synthetic examples and curated public data only.
            Zion does not provide diagnosis, medical advice, emergency response,
            or production humanitarian capability.
          </p>
          <a href="https://github.com/grey-ghost-1/zion-software-initiative/blob/main/README.md">
            Read the project boundaries
          </a>
        </section>
      </main>
      <footer>
        <p>Zion Software Initiative - Foundation stage</p>
      </footer>
    </>
  );
}
