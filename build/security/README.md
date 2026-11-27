# Sensitive data scanner

`sensitive_data_scanner.py` blocks commits that add credentials, real account IDs,
personal data, or values from a private denylist. It uses only the Python standard library.

## Usage

Run from anywhere inside the repository:

```bash
build/_build/_venv/bin/python build/security/sensitive_data_scanner.py              # lines added in staged changes (default)
build/_build/_venv/bin/python build/security/sensitive_data_scanner.py --all        # every tracked file
build/_build/_venv/bin/python build/security/sensitive_data_scanner.py FILE [FILE]  # specific files
```

Exit codes: `0` clean, `1` findings, `2` error. Secret values are masked in the output.

In `--staged` mode only added lines are checked, so existing findings never block an
unrelated commit. Staged binary files are scanned whole, via their printable strings.

## Pre-commit hook

`build/pre-commit` runs the scanner before pylint. Install it with a symlink, so changes to
the hook take effect without copying:

```bash
ln -sf ../../build/pre-commit .git/hooks/pre-commit
```

## Rules

| Layer | File | Committed |
|---|---|---|
| Generic rules: credentials, AWS account IDs, emails, public IPs, home paths, phone numbers | `sensitive_data_rules.py` | yes |
| Private denylist: real names, organizations, account IDs, IPs | `<repo parent>/ignore/horey_security/denylist.txt`, or the path in `$HOREY_SECURITY_DENYLIST` | **never** |

`sensitive_data_rules.py` holds only patterns and placeholder allowlists. Put real values in
the private denylist, since writing them into the repository would publish them.

If the private denylist is missing, the scanner prints a warning and applies only the
generic rules.

### Private denylist format

One case-insensitive regex per line:

```text
# comment
org-horey-real-name          report any match
!github\.com/OrgHorey/horey  allow context: matches fully inside this span are not reported
```

## False positives

- Append `horey-security: allow` to a line to skip it.
- Add placeholder values to the allowlists in `sensitive_data_rules.py`
  (`ALLOWED_ACCOUNT_IDS`, `ALLOWED_EMAIL_DOMAINS`, `ALLOWED_PUBLIC_IPS`, `ALLOWED_HOME_USERS`, ...).
- Add vendored files to `EXCLUDED_PATH_PATTERNS`.

## Tests

```bash
build/_build/_venv/bin/python -m pytest build/security/tests
```
