# Repository Readiness Check

A small GitHub Action that checks for common signals that make an open-source repository easier to understand, contribute to, and release.

It looks for a README, license, contributor guide, code of conduct, GitHub Actions workflow, issue template, and Git release tags. The result is written to the **GitHub Actions job summary** with evidence and practical suggestions. Findings are informational; the action exits successfully when a signal is missing.

## Use it

Add this workflow to `.github/workflows/repository-readiness.yml`:

```yaml
name: Repository readiness

on:
  workflow_dispatch:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  readiness:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
        with:
          # Fetch tags so the report can inspect the release history.
          fetch-depth: 0
      - uses: arturperer12-ops/repository-readiness@v1
```

Replace `arturperer12-ops` with the account or organization that publishes this action. The `v1` reference should be a maintained major-version tag in the action's repository. The action needs only the checked-out workspace and GitHub's built-in step-summary path; it does not need a personal access token or network access.

## What it checks

| Signal | Files or evidence checked |
| --- | --- |
| README | `README.md`, `.rst`, `.txt`, or `README` |
| License | Common `LICENSE`, `LICENCE`, or `COPYING` names |
| Contributor guide | `CONTRIBUTING.md` at the root or in `.github/` |
| Code of conduct | `CODE_OF_CONDUCT.md` at the root or in `.github/` |
| Continuous integration | YAML workflows in `.github/workflows/` |
| Issue templates | Markdown or YAML templates in `.github/ISSUE_TEMPLATE/` |
| Release history | Git tags available in the checkout |

Missing signals are suggestions, not universal requirements. The report does not inspect document quality, validate licenses, or call external APIs. GitHub Actions checkout uses a shallow clone by default, so set `fetch-depth: 0` if you want release tags to be visible.

## Development

Requires Python 3.10 or newer. The action itself uses only the Python standard library.

```bash
python -m unittest discover -s tests -v
```

## Contributing

Bug reports, documentation improvements, and focused pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) before opening a change.

## License

This project is distributed under the MIT License. See [LICENSE](LICENSE).
