# Security policy

## Supported versions

Only the latest release and the `main` branch receive security fixes.

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability. Report it privately through
[GitHub private vulnerability reporting](https://github.com/ks6088ts/template-python/security/advisories/new)
and include:

- the affected version or commit,
- steps to reproduce or a proof of concept,
- the impact you expect.

You should receive an acknowledgement within 5 business days. Please allow time for a fix
before any public disclosure.

## Automated safeguards

The repository continuously runs dependency auditing (pip-audit), secret scanning
(gitleaks), file and image scanning (Trivy), static analysis (CodeQL, Ruff security rules),
workflow analysis (actionlint, zizmor), and OpenSSF Scorecard. Release images are published
with an SBOM and signed build provenance. See the
[engineering guide](docs/architecture/README.md#security-and-supply-chain) for details.
