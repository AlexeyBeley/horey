"""
Rules used by sensitive_data_scanner.py.

Only generic patterns and placeholder values live in this file, because it is committed.
Real values (people's names, organization names, account IDs, IPs) belong in the private
denylist file, which lives outside the repository. See README.md.
"""

import ipaddress
import re

# A line containing this marker is never reported.
ALLOW_MARKER = "horey-security: allow"

# Paths (relative to the repo root) that are never scanned.
EXCLUDED_PATH_PATTERNS = [
    re.compile(r"^aws_cleaner/html/"),
    re.compile(r"(^|/)package-lock\.json$"),
    re.compile(r"\.min\.js$"),
    re.compile(r"(^|/)\.DS_Store$"),
    re.compile(r"^selenium_api/kijiji/chromedriver$"),  # vendored third-party binary
]

# Identifier rules are too noisy inside compiled binaries (embedded certificates, DNS
# resolver lists, version strings), so binaries get only the credential, home directory
# and private denylist checks.
BINARY_SKIPPED_RULES = {
    "aws-account-id",
    "email",
    "public-ip",
    "phone-number",
    "international-phone-number",
}

# Well-known placeholder AWS account IDs and public AWS-owned accounts.
ALLOWED_ACCOUNT_IDS = {
    "000000000000",
    "111111111111",
    "123456789012",
    "123456789100",
    "123456789101",
    "012345678910",
    "109876543210",
    "591542846629",  # Amazon-owned public ECS AMI owner
}

# Email domains that are placeholders or service addresses (suffix match).
ALLOWED_EMAIL_DOMAINS = (
    "horey.com",
    "horey-system.com",
    "example.com",
    "example.org",
    "example.net",
    "address.com",
    "common.com",
    "sample.com",
    "mydomain.com",
    "domain.pro",
    "amazonses.com",
    "lists.ubuntu.com",
    "lists.alioth.debian.org",
    "localhost",
    "noreply.github.com",
    "github.com",
    "anthropic.com",
    "internal",
)

# Placeholder emails on public mail domains.
ALLOWED_EMAIL_PATTERNS = [
    re.compile(r"horey", re.IGNORECASE),
    re.compile(r"^(test\.user|john\.doe|doe\.johns)@gmail\.com$", re.IGNORECASE),
]

# Public IPs that are well-known public resolvers or obvious placeholders.
ALLOWED_PUBLIC_IPS = {
    "1.1.1.1",
    "1.1.1.2",
    "1.1.1.3",
    "1.0.0.1",
    "8.8.8.8",
    "8.8.4.4",
    "9.9.9.9",
    "208.67.222.222",
    "208.67.220.220",
    "1.2.3.4",
    "2.2.2.2",
}

# Publicly documented service numbers.
ALLOWED_PHONE_NUMBERS = {
    "+14155238886",  # Twilio WhatsApp sandbox
}

# Home directory names that are generic, not a real person's.
ALLOWED_HOME_USERS = {
    "admin",
    "default",
    "ec2-user",
    "gitlab-runner",
    "horey",
    "jenkins",
    "public",
    "root",
    "runner",
    "shared",
    "ubuntu",
    "user",
    "user_horey",
    "user-horey",
    "username",
    "whoever",
    "xxx",
}

# Values of password-like assignments that are obviously not real secrets.
PLACEHOLDER_SECRET_PATTERN = re.compile(
    r"[{}$<>%*]|horey|example|dummy|pass|p@ss|changeme|change_me|placeholder|xxx|your[_-]|fake|sample|"
    r"redacted|password|secret|token|test|^none$|^null$",
    re.IGNORECASE,
)


def _is_real_account_id(match):
    value = match.group(0)
    return value not in ALLOWED_ACCOUNT_IDS and len(set(value)) > 1


def _is_real_email(match):
    value = match.group(0).lower()
    domain = value.rsplit("@", 1)[1]
    for allowed in ALLOWED_EMAIL_DOMAINS:
        if domain == allowed or domain.endswith("." + allowed):
            return False
    return not any(pattern.search(value) for pattern in ALLOWED_EMAIL_PATTERNS)


def _is_real_public_ip(match):
    value = match.group(0)
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        return False
    if value in ALLOWED_PUBLIC_IPS:
        return False
    return address.is_global and not address.is_multicast


def _is_real_home_user(match):
    return match.group(1).lower() not in ALLOWED_HOME_USERS


def _is_real_secret_value(match):
    return not PLACEHOLDER_SECRET_PATTERN.search(match.group(1))


def _is_real_phone(match):
    value = match.group(0)
    return "555" not in value and value not in ALLOWED_PHONE_NUMBERS


# Each rule: name, compiled regex, whether the match is a secret (masked in output),
# and an optional validator returning True when the match is a real finding.
RULES = [
    # --- Credentials ---------------------------------------------------------------
    ("aws-access-key-id", re.compile(r"(?<![A-Z0-9])(?:AKIA|ASIA)[A-Z0-9]{16}(?![A-Z0-9])"), True, None),
    ("aws-secret-access-key",
     re.compile(r"(?i)aws_?secret_?access_?key[\"']?\s*[:=]\s*[\"']?[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])"), True, None),
    ("github-token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b"), True, None),
    ("github-fine-grained-token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{60,}\b"), True, None),
    ("gitlab-token", re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}\b"), True, None),
    ("slack-token", re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}\b"), True, None),
    ("slack-webhook", re.compile(r"https://hooks\.slack\.com/services/T[A-Za-z0-9_]+/B[A-Za-z0-9_]+/[A-Za-z0-9_]+"),
     True, None),
    ("anthropic-api-key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}"), True, None),
    ("openai-api-key", re.compile(r"\bsk-(?!ant-)(?:proj-)?[A-Za-z0-9_-]{32,}"), True, None),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}(?![0-9A-Za-z_-])"), True, None),
    ("npm-token", re.compile(r"\bnpm_[A-Za-z0-9]{36}\b"), True, None),
    ("pypi-token", re.compile(r"\bpypi-AgEIcHlwaS5vcmc[A-Za-z0-9_-]{50,}"), True, None),
    ("telegram-bot-token", re.compile(r"\b\d{8,10}:AA[A-Za-z0-9_-]{33}(?![A-Za-z0-9_-])"), True, None),
    ("twilio-key", re.compile(r"\b(?:AC|SK)[0-9a-f]{32}\b"), True, None),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"), True, None),
    ("private-key", re.compile(r"-----BEGIN (?:[A-Z]+ )*PRIVATE KEY-----"), True, None),
    ("credentials-in-url",
     re.compile(r"\b[a-z][a-z0-9+.-]*://[^\s/:@'\"]+:([^\s/@'\"]+)@[^\s/'\"]+"), True, _is_real_secret_value),
    ("hardcoded-secret",
     re.compile(r"(?i)\b(?:\w+_)?(?:password|passwd|pwd|secret|api_?key|access_?token|auth_?token|client_?secret)[\"']?"
                r"\s*[:=]\s*[\"']([^\"'\s]{8,})[\"']"), True, _is_real_secret_value),
    # --- Identifiers and personal data ---------------------------------------------
    ("aws-account-id", re.compile(r"(?<![\w.])\d{12}(?![\w.])"), False, _is_real_account_id),
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}\b"), False,
     _is_real_email),
    ("public-ip", re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?!\.?\d)"), False, _is_real_public_ip),
    ("home-directory", re.compile(r"/(?:Users|home)/([A-Za-z0-9._-]+)"), False, _is_real_home_user),
    ("windows-home-directory", re.compile(r"[A-Za-z]:\\{1,2}Users\\{1,2}([A-Za-z0-9._-]+)"), False,
     _is_real_home_user),
    ("phone-number", re.compile(r"(?<![\w-])\(?\d{3}\)?[- ]\d{3}-\d{4}(?![\w-])"), False, _is_real_phone),
    ("international-phone-number", re.compile(r"(?<![\w+])\+\d{10,14}(?!\d)"), False, _is_real_phone),
]
