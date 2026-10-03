"""Create an informational GitHub Actions summary for repository maintainers."""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Check:
    name: str
    found: bool | None
    evidence: str
    recommendation: str


def _first_file(root: Path, candidates: Iterable[str]) -> str | None:
    for candidate in candidates:
        if (root / candidate).is_file():
            return candidate
    return None


def _git_tags(root: Path) -> tuple[list[str], str | None]:
    try:
        result = subprocess.run(
            ["git", "tag", "--list"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return [], f"Could not inspect Git tags ({error.__class__.__name__})."

    if result.returncode != 0:
        return [], "Could not inspect Git tags in this checkout."
    return [tag.strip() for tag in result.stdout.splitlines() if tag.strip()], None


def evaluate_repository(
    root: Path, release_tags: Iterable[str] | None = None
) -> list[Check]:
    """Inspect common community and release signals in ``root``."""
    root = root.resolve()
    checks: list[Check] = []

    file_checks = (
        (
            "README",
            ("README.md", "README.rst", "README.txt", "README"),
            "Add a README that explains the project, installation, and a first example.",
        ),
        (
            "License",
            ("LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE", "COPYING"),
            "Add a license file so users know how they may use and share the project.",
        ),
        (
            "Contributor guide",
            ("CONTRIBUTING.md", ".github/CONTRIBUTING.md"),
            "Add contribution instructions covering setup, changes, and pull requests.",
        ),
        (
            "Code of conduct",
            ("CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md"),
            "Add a code of conduct that explains community expectations and reporting.",
        ),
    )
    for name, candidates, recommendation in file_checks:
        path = _first_file(root, candidates)
        checks.append(
            Check(
                name=name,
                found=path is not None,
                evidence=f"Found `{path}`." if path else "No common file found.",
                recommendation="Looks good." if path else recommendation,
            )
        )

    workflows_dir = root / ".github" / "workflows"
    workflows = sorted(
        path.relative_to(root).as_posix()
        for pattern in ("*.yml", "*.yaml")
        for path in workflows_dir.glob(pattern)
        if path.is_file()
    ) if workflows_dir.is_dir() else []
    checks.append(
        Check(
            name="Continuous integration",
            found=bool(workflows),
            evidence=(
                "Found " + ", ".join(f"`{path}`" for path in workflows[:3]) + "."
                if workflows
                else "No workflow files found in `.github/workflows/`."
            ),
            recommendation=(
                "Looks good."
                if workflows
                else "Add a GitHub Actions workflow to run checks on pull requests."
            ),
        )
    )

    issue_dir = root / ".github" / "ISSUE_TEMPLATE"
    issue_templates = []
    if issue_dir.is_dir():
        issue_templates = sorted(
            path.relative_to(root).as_posix()
            for path in issue_dir.iterdir()
            if path.is_file()
            and path.suffix.lower() in {".md", ".yml", ".yaml"}
            and path.name.lower() not in {"config.yml", "config.yaml"}
        )
    legacy_template = root / ".github" / "ISSUE_TEMPLATE.md"
    if legacy_template.is_file():
        issue_templates.append(legacy_template.relative_to(root).as_posix())
    issue_templates = sorted(set(issue_templates))
    checks.append(
        Check(
            name="Issue templates",
            found=bool(issue_templates),
            evidence=(
                "Found "
                + ", ".join(f"`{path}`" for path in issue_templates[:3])
                + "."
                if issue_templates
                else "No issue templates found."
            ),
            recommendation=(
                "Looks good."
                if issue_templates
                else "Add at least one issue template under `.github/ISSUE_TEMPLATE/`."
            ),
        )
    )

    tag_error = None
    tags: list[str]
    if release_tags is None:
        tags, tag_error = _git_tags(root)
    else:
        tags = sorted({tag.strip() for tag in release_tags if tag.strip()})
    checks.append(
        Check(
            name="Release history",
            found=bool(tags) if tag_error is None else None,
            evidence=(
                tag_error
                if tag_error
                else (
                    "Found Git tags: "
                    + ", ".join(f"`{tag}`" for tag in tags[-3:])
                    + "."
                    if tags
                    else "No Git tags found in the checkout."
                )
            ),
            recommendation=(
                "Looks good."
                if tags
                else ""
                if tag_error
                else "Tag a release when the project is ready to publish a version."
            ),
        )
    )
    return checks


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def render_summary(checks: Iterable[Check]) -> str:
    checks = list(checks)
    found_count = sum(check.found is True for check in checks)
    unavailable_count = sum(check.found is None for check in checks)
    count_note = f" ({unavailable_count} unavailable)" if unavailable_count else ""
    lines = [
        "# Repository readiness report",
        "",
        (
            f"**{found_count} of {len(checks)} checks found a readiness signal"
            f"{count_note}.** "
            "This report is informational and does not fail the workflow."
        ),
        "",
        "| Check | Status | Evidence and next step |",
        "| --- | --- | --- |",
    ]
    for check in checks:
        if check.found is True:
            status = "Found"
        elif check.found is False:
            status = "Suggested"
        else:
            status = "Unavailable"
        detail = check.evidence
        if check.recommendation and check.recommendation != "Looks good.":
            detail += " " + check.recommendation
        lines.append(
            f"| {_cell(check.name)} | {status} | {_cell(detail)} |"
        )
    lines.extend(
        [
            "",
            "A missing signal is a suggestion for maintainers, not a requirement for every project.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    workspace = Path(os.environ.get("GITHUB_WORKSPACE", Path.cwd()))
    summary = render_summary(evaluate_repository(workspace))
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with Path(summary_path).open("a", encoding="utf-8") as summary_file:
            summary_file.write(summary)
    else:
        sys.stdout.write(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
