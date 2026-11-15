# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of Digital Career Twin seriously. If you discover a security vulnerability, please do **NOT** open a public issue.

Instead, please send an email with the details to **security@digitalcareertwin.org** (or contact maintainers directly via private repository disclosure).

Please include:
- A description of the vulnerability and its potential impact.
- Step-by-step instructions to reproduce the issue (proof-of-concept script or screenshot).
- Any suggested mitigations.

We will acknowledge receipt within 48 hours and provide regular updates on progress toward a fix.

## Security Principles in DCT

1. **User Privacy by Design**: User career data, assessments, and resumes are confidential.
2. **Untrusted Document Handling**: Resumes and uploads are parsed in isolated sandboxes with content-injection defenses.
3. **Prompt Injection Mitigations**: External inputs to LLMs are wrapped in `<untrusted_document>` delimiters.
4. **Credential Security**: OAuth tokens are encrypted at rest with Fernet. Passwords use argon2id.
