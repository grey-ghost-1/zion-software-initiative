# @zion/ui

Small, framework-light React primitives shared by every page in `apps/web`:

- `StatusBadge` — renders one of a narrow, truthful status vocabulary
  (`implemented` / `in-development` / `planned`). No other status values exist,
  so a caller cannot invent an unsupported claim like "live" or "validated".
- `CaseStudyCard` — a single card shape for both the public-interest
  ("impact") and technical ("engineering") framings of the same underlying
  work, each carrying a status and an optional link to inspectable evidence.

Styling lives in `apps/web`'s global stylesheet (this package ships markup and
class names only, matching how `@zion/config` centralizes the shared design
tokens those class names read from).
