import styles from "./architecture.module.css";

const flow = [
  "Next.js UI",
  "Typed API client",
  "FastAPI modular monolith",
  "PostgreSQL",
] as const;

export function ArchitectureDiagram() {
  return (
    <figure className={styles.figure} aria-labelledby="platform-diagram-title">
      <figcaption id="platform-diagram-title">
        <strong>Zion platform request and persistence flow</strong>
      </figcaption>
      <div className={styles.flow} aria-hidden="true">
        {flow.map((layer, index) => (
          <div className={styles.step} key={layer}>
            <span>{layer}</span>
            {index < flow.length - 1 ? <span className={styles.arrow}>→</span> : null}
          </div>
        ))}
      </div>
      <div className={styles.modules} aria-hidden="true">
        <span>Harbor module</span>
        <span>Haven module</span>
      </div>
      <div className={styles.foundation} aria-hidden="true">
        Shared auth · RBAC · organization isolation · audit · safety · provenance
      </div>
      <p className="visually-hidden">
        Semantic equivalent: requests move from the Next.js user interface through the
        typed API client into a FastAPI modular monolith and then PostgreSQL. Harbor and
        Haven are domain modules within the service. Shared authentication, role-based
        access control, organization isolation, audit, safety, and provenance layers apply
        across both modules.
      </p>
    </figure>
  );
}
