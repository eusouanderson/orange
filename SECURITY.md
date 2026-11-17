# Security Policy

## Supported Versions

The Orange project is actively maintained. Security updates are provided for the latest stable release.

| Version | Supported |
| ------- | --------- |
| Latest stable release | :white_check_mark: |
| Development branch (`main`) | :white_check_mark: |
| Older releases | :x: |

Security fixes are prioritized for the latest stable release. Users are strongly encouraged to keep their installations updated.

## Reporting a Vulnerability

The Orange project takes security seriously. We appreciate the efforts of security researchers and users who responsibly disclose vulnerabilities.

**Please do not report security vulnerabilities through public GitHub Issues or public Pull Requests.**

To report a security vulnerability, please use GitHub's private vulnerability reporting feature:

[Report a vulnerability privately](https://github.com/eusouanderson/orange/security/advisories/new)

If private vulnerability reporting is unavailable, contact the project maintainers through the contact information provided in the repository.

### What to Include

When reporting a vulnerability, please provide as much information as possible:

- A clear description of the vulnerability.
- The affected Orange version or commit.
- The affected component or functionality.
- Steps to reproduce the issue.
- Potential security impact.
- Proof of concept, if available.
- Suggested remediation, if known.

Please avoid including sensitive personal information or confidential data in your report.

### Response Timeline

The maintainers aim to follow these response targets:

| Activity | Expected timeframe |
| -------- | ------------------ |
| Initial acknowledgment | Within 72 hours |
| Initial assessment | Within 7 days |
| Status update | At least every 7 days |
| Resolution target | Depends on severity and complexity |

These are response targets rather than guaranteed deadlines.

### Vulnerability Handling

After receiving a report, the maintainers will:

1. Review and validate the reported vulnerability.
2. Determine its severity and potential impact.
3. Identify affected versions and components.
4. Develop and test an appropriate fix.
5. Prepare a security release when necessary.
6. Publish relevant security advisories and remediation guidance.

If a report is accepted, the maintainers will coordinate remediation and disclosure with the reporter whenever possible.

If a report is declined, the reporter will receive an explanation when sufficient information is available.

### Responsible Disclosure

We ask security researchers to:

- Give maintainers reasonable time to investigate and address reported issues.
- Avoid publicly disclosing vulnerabilities before a fix is available.
- Avoid accessing, modifying, or deleting data belonging to others.
- Avoid disrupting services or causing damage during security research.
- Perform testing only on systems they own or are explicitly authorized to assess.

We appreciate responsible disclosure and will credit reporters in security advisories when they wish to be acknowledged.

## Security Scope

Security reports relevant to Orange include issues affecting:

- Python compilation and code processing.
- File handling and filesystem operations.
- Build and packaging processes.
- External command execution and subprocess management.
- Dependency management.
- Configuration parsing and validation.
- Plugin loading and execution.
- Temporary files and generated artifacts.
- GitHub Actions integration and CI/CD workflows.
- Distribution and release processes.

## Security Updates

Security updates and relevant announcements will be published through:

- [GitHub Security Advisories](https://github.com/eusouanderson/orange/security/advisories)
- [GitHub Releases](https://github.com/eusouanderson/orange/releases)

Users should monitor these channels and update to supported releases as soon as security fixes become available.

---

Thank you for helping keep Orange and its community secure.

**Orange Maintainers**
