import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def test_evidence_inventory_matches_schema_and_references_real_files() -> None:
    schema = json.loads((ROOT / "docs/evidence/inventory.schema.json").read_text())
    inventory = json.loads((ROOT / "docs/evidence/inventory.json").read_text())

    Draft202012Validator(schema).validate(inventory)
    for claim in inventory["claims"]:
        assert (ROOT / claim["evidence"]).is_file()


def test_public_surfaces_do_not_make_unsupported_claims() -> None:
    paths = [
        ROOT / "README.md",
        ROOT / "apps/web/src/app/page.tsx",
        ROOT / "apps/web/src/app/initiatives/page.tsx",
        ROOT / "apps/web/src/app/projects/page.tsx",
        ROOT / "apps/web/src/app/evidence/page.tsx",
        ROOT / "apps/web/src/app/about/page.tsx",
        ROOT / "apps/web/src/app/harbor/page.tsx",
        ROOT / "apps/web/src/app/harbor/HarborWorkflow.tsx",
        *sorted((ROOT / "docs/case-studies").glob("*.md")),
    ]
    prohibited_patterns = {
        "real-world adoption": r"\b(?:serving|used by)\s+\d+\s+(?:people|users|organizations)\b",
        "partnership": r"\b(?:our|official)\s+partners?\b",
        "clinical validation": r"\bclinically (?:validated|proven)\b",
        "production readiness": r"\bproduction[- ]ready\b",
        "field impact": r"\b(?:proven|measurable) field impact\b",
    }

    violations: list[str] = []
    for path in paths:
        content = path.read_text(encoding="utf-8")
        for label, pattern in prohibited_patterns.items():
            if re.search(pattern, content, flags=re.IGNORECASE):
                violations.append(f"{path.relative_to(ROOT)}: {label}")

    assert violations == []
