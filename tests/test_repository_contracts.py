import json
import re
from collections import Counter
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


def test_labs_archive_snapshot_matches_immutable_source_contract() -> None:
    snapshot_path = ROOT / "docs/evidence/zion-labs-prior-work.json"
    archive = json.loads(snapshot_path.read_text())
    base_url = (
        "https://github.com/grey-ghost-1/Batcomputer-Portfolio/blob/"
        "148ffe12f60d586d3b7e4769ae1c617e98c31289/"
    )
    ci_url = "https://github.com/grey-ghost-1/Batcomputer-Portfolio/actions/runs/33112674630"

    assert archive["schemaVersion"] == 1
    assert archive["attribution"] == {
        "creator": "Justin Wimmer",
        "origin": "Originally published in the Batcomputer Portfolio.",
        "reuseLicense": None,
    }
    assert archive["sourceSnapshot"] == {
        "repo": "grey-ghost-1/Batcomputer-Portfolio",
        "defaultBranch": "main",
        "commit": "148ffe12f60d586d3b7e4769ae1c617e98c31289",
        "auditedAt": "2026-08-26",
        "inventoryUrl": f"{base_url}project-evidence.json",
        "ciRunUrl": ci_url,
    }

    projects = archive["projects"]
    assert len(projects) == 23
    assert len({project["id"] for project in projects}) == 23
    assert len({project["slug"] for project in projects}) == 23
    assert all(project["id"] == project["slug"] for project in projects)
    assert all(project["media"] == [] for project in projects)
    assert all(project["copyAssets"] is False for project in projects)
    assert all(
        project["source"]["immutableUrl"].startswith(base_url) for project in projects
    )
    assert all("/tree/" not in project["source"]["immutableUrl"] for project in projects)
    assert all(
        "/tree/" not in evidence_url
        for project in projects
        for evidence_url in project["evidenceUrls"]
    )

    assert Counter(project["tier"] for project in projects) == Counter(
        {"secondary": 19, "flagship": 4}
    )
    assert Counter(
        project["category"] for project in projects if project["tier"] == "secondary"
    ) == Counter(
        {
            "defensive security": 5,
            "IT support": 5,
            "networking/systems": 5,
            "software/automation": 4,
        }
    )
    assert Counter(
        project["category"] for project in projects if project["tier"] == "flagship"
    ) == Counter(
        {
            "platform": 1,
            "simulation": 1,
            "algorithms": 1,
            "assistant": 1,
        }
    )

    validation = archive["validationSnapshot"]
    assert validation["projectCount"] == 23
    assert validation["flagshipCount"] == 4
    assert validation["secondaryCount"] == 19
    assert validation["secondaryByCategory"] == {
        "software/automation": 4,
        "defensive security": 5,
        "IT support": 5,
        "networking/systems": 5,
    }
    assert validation["retainedLegacyFolders"] == 20
    assert validation["ciTotals"] == [
        {"label": "site/showcase", "tests": 42},
        {"label": "platform", "tests": 10},
        {"label": "Orbital", "tests": 8},
        {"label": "algorithm", "tests": 7},
        {"label": "Alfred", "tests": 377},
    ]
    assert validation["passingTotal"] == 444
