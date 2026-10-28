# CipherEye: Comprehensive Overview & Architecture

**CipherEye** is a high-performance static analysis security tool built to scan source code repositories, configuration files, and CI/CD artifacts for accidental credential leaks (such as API keys, cryptographic private keys, and database passwords) before they make it into production or public version control.

---

## What CipherEye Does

Modern development relies heavily on third-party APIs, cloud providers, and databases, increasing the risk that a developer might accidentally hardcode sensitive secrets directly into source code. CipherEye automates the discovery of these vulnerabilities by:

1. **Detecting Hardcoded Secrets:** Scans codebases for high-risk patterns like AWS Access Keys (`AKIA...`), Stripe live keys, JWT secrets, private key blocks (`-----BEGIN RSA PRIVATE KEY-----`), and database connection strings.
2. **Preventing Leaks Pre-Commit:** Integrates into local Git workflows via pre-commit hooks to block commits containing sensitive strings before they touch remote repositories.
3. **Providing Actionable Reports:** Generates structured terminal output and CI/CD logs detailing the exact file path, line number, and risk level of any detected secret.

---

## How CipherEye Does It (Under the Hood)

CipherEye combines **Regular Expression (Regex) Pattern Matching** and **Shannon Entropy Analysis** to scan code efficiently and accurately.

### 1. High-Performance Regex Pattern Matching

CipherEye uses a library of curated, highly optimized regular expressions tailored to specific credential formats.

* **Example (AWS Access Key):** `AKIA[0-9A-Z]{16}`
* **Example (Generic Secret Assignment):** Looks for variable assignments like `password = "..."` or `secret_key = "..."` where string lengths and character sets match known token formats.

### 2. Shannon Entropy Analysis (Reducing False Positives)

Simply matching regex can lead to false positives (e.g., random test strings or base64-encoded UI assets). CipherEye calculates **Shannon Entropy** on matched strings.

* Real API keys and cryptographic secrets have high randomness (entropy).
* Plain English words or low-entropy test strings are automatically filtered out, ensuring high signal-to-noise ratio.

---

## Integration Points

* **Local Pre-Commit Hooks:** Intercepts `git commit` commands locally using a Git hook wrapper, executing scan checks in milliseconds.
* **CI/CD Pipelines (GitHub Actions / GitLab CI):** Runs as a lightweight container or binary step during pull requests to catch secrets introduced by automated merges or team members bypassing local hooks.
