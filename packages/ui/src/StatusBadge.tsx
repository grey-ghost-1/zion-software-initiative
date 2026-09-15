/**
 * A truthful, small vocabulary for describing implementation state. Kept
 * intentionally narrow so callers cannot invent unsupported claims (e.g. no
 * "live", "production", or "validated" status exists here).
 */
export type WorkStatus = "implemented" | "in-development" | "planned";

const STATUS_LABEL: Record<WorkStatus, string> = {
  implemented: "Implemented",
  "in-development": "In development",
  planned: "Planned",
};

export interface StatusBadgeProps {
  status: WorkStatus;
  /** Optional override for the visible label (still describes the same status). */
  label?: string;
}

export function StatusBadge({ status, label }: StatusBadgeProps) {
  return (
    <span className={`status-badge status-badge--${status}`}>
      {label ?? STATUS_LABEL[status]}
    </span>
  );
}
