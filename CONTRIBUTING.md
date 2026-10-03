# Contributing

Thanks for helping improve Repository Readiness Check.

## Report a bug or suggest a check

Open an issue with a short description, the repository layout that triggered it, and what you expected the report to say. Do not include secrets, private repository contents, or personal data.

## Make a change

1. Fork the repository and create a focused branch.
2. Keep the action dependency-free unless a dependency has a clear maintenance benefit.
3. Add or update a test for behavior changes.
4. Run `python -m unittest discover -s tests -v`.
5. Update the README if user-visible behavior changes.
6. Open a pull request explaining the problem and the change.

All checks in the report should remain advisory by default. This tool should help maintainers, not impose a universal definition of a healthy project.
