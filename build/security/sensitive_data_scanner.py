"""
Scan the repository for sensitive data: credentials, real account IDs, emails, public IPs,
home directory paths, phone numbers and private denylist values.

Usage (from anywhere inside the repository):
    python build/security/sensitive_data_scanner.py              # lines added in staged changes
    python build/security/sensitive_data_scanner.py --all        # every tracked file
    python build/security/sensitive_data_scanner.py FILE [FILE]  # specific files

Exit codes: 0 - clean, 1 - findings, 2 - error.
"""

import argparse
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# pylint: disable=wrong-import-position
import sensitive_data_rules as rules

DENYLIST_ENV_VAR = "HOREY_SECURITY_DENYLIST"
BINARY_SNIFF_SIZE = 8000
BINARY_MIN_STRING_LENGTH = 6
BINARY_LINE = "binary"


class Finding:
    """
    One reported match.
    """

    def __init__(self, path, line_number, rule_name, value, secret):
        self.path = path
        self.line_number = line_number
        self.rule_name = rule_name
        self.value = value
        self.secret = secret

    def display_value(self):
        """
        Value as printed: secrets are masked so they do not end up in terminal logs.

        :return:
        """
        if not self.secret:
            return self.value
        return f"{self.value[:4]}...({len(self.value)} chars)"

    def __str__(self):
        return f"{self.path}:{self.line_number}: [{self.rule_name}] {self.display_value()}"


class Scanner:
    """
    Applies the generic rules and the private denylist to lines of text.
    """

    def __init__(self, deny_patterns=None, allow_context_patterns=None):
        self.deny_patterns = deny_patterns or []
        self.allow_context_patterns = allow_context_patterns or []

    @staticmethod
    def load_denylist(file_path):
        """
        Private denylist format, one regex per line, matched case-insensitively:
            # comment
            regex          - report any match
            !regex         - allow context: matches inside its span are not reported

        :param file_path:
        :return: (deny_patterns, allow_context_patterns)
        """

        deny_patterns = []
        allow_context_patterns = []
        with open(file_path, encoding="utf-8") as file_handler:
            for line_number, raw_line in enumerate(file_handler, start=1):
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                target = allow_context_patterns if line.startswith("!") else deny_patterns
                pattern = line[1:] if line.startswith("!") else line
                try:
                    target.append(re.compile(pattern, re.IGNORECASE))
                except re.error as error_instance:
                    raise ValueError(f"{file_path}:{line_number}: invalid regex '{pattern}': {error_instance}") \
                        from error_instance
        return deny_patterns, allow_context_patterns

    def _allowed_spans(self, line):
        return [match.span() for pattern in self.allow_context_patterns for match in pattern.finditer(line)]

    @staticmethod
    def _inside(span, allowed_spans):
        return any(start <= span[0] and span[1] <= end for start, end in allowed_spans)

    def scan_line(self, line, binary=False):
        """
        Return list of (rule_name, value, secret) found in the line.

        :param line:
        :param binary: line is a printable string extracted from a binary file
        :return:
        """

        if rules.ALLOW_MARKER in line:
            return []

        allowed_spans = self._allowed_spans(line)
        ret = []
        for rule_name, regex, secret, validator in rules.RULES:
            if binary and rule_name in rules.BINARY_SKIPPED_RULES:
                continue
            for match in regex.finditer(line):
                if validator is not None and not validator(match):
                    continue
                if self._inside(match.span(), allowed_spans):
                    continue
                ret.append((rule_name, match.group(0), secret))

        for pattern in self.deny_patterns:
            for match in pattern.finditer(line):
                if self._inside(match.span(), allowed_spans):
                    continue
                ret.append(("private-denylist", match.group(0), False))
        return ret

    def scan_lines(self, path, numbered_lines, binary=False):
        """
        Scan (line_number, line) pairs of a file.

        :param path:
        :param numbered_lines:
        :param binary:
        :return:
        """

        findings = []
        for line_number, line in numbered_lines:
            for rule_name, value, secret in self.scan_line(line, binary=binary):
                findings.append(Finding(path, line_number, rule_name, value, secret))
        return findings

    def scan_bytes(self, path, data):
        """
        Scan full file content. Binary files are scanned via their printable strings.

        :param path:
        :param data:
        :return:
        """

        if is_binary(data):
            strings = re.findall(rb"[\x20-\x7e]{%d,}" % BINARY_MIN_STRING_LENGTH, data)
            return self.scan_lines(path, ((BINARY_LINE, item.decode("ascii")) for item in strings),
                                   binary=True)
        text = data.decode("utf-8", errors="replace")
        return self.scan_lines(path, enumerate(text.splitlines(), start=1))


def is_binary(data):
    """
    Same heuristic git uses: a NUL byte in the first chunk.

    :param data:
    :return:
    """
    return b"\0" in data[:BINARY_SNIFF_SIZE]


def is_excluded(path):
    """
    Check the path against the excluded path patterns.

    :param path:
    :return:
    """
    return any(pattern.search(path) for pattern in rules.EXCLUDED_PATH_PATTERNS)


def run_git(args, repo_root):
    """
    Run a git command and return stdout bytes.

    :param args:
    :param repo_root:
    :return:
    """
    return subprocess.run(["git", "-c", "core.quotePath=false", *args], cwd=repo_root, check=True,
                          stdout=subprocess.PIPE).stdout


def get_repo_root():
    """
    Top level directory of the current git repository.

    :return:
    """
    return subprocess.run(["git", "rev-parse", "--show-toplevel"], check=True, stdout=subprocess.PIPE,
                          text=True).stdout.strip()


def parse_added_lines(diff_text):
    """
    Parse `git diff -U0` output into {path: [(line_number, line), ...]} of added lines.

    :param diff_text:
    :return:
    """

    ret = {}
    hunk_header = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")
    path = None
    in_header = False
    line_number = 0
    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            in_header = True
            path = None
            continue
        if in_header:
            if line.startswith("+++ "):
                target = line[4:]
                path = None if target == "/dev/null" else target[2:] if target.startswith("b/") else target
                continue
            match = hunk_header.match(line)
            if match:
                in_header = False
                line_number = int(match.group(1))
            continue
        match = hunk_header.match(line)
        if match:
            line_number = int(match.group(1))
            continue
        if line.startswith("+") and path is not None:
            ret.setdefault(path, []).append((line_number, line[1:]))
            line_number += 1
    return ret


def scan_staged(scanner, repo_root):
    """
    Scan lines added by staged changes. Binary staged files are scanned whole.

    :param scanner:
    :param repo_root:
    :return:
    """

    findings = []
    numstat = run_git(["diff", "--cached", "--numstat", "-z", "--diff-filter=ACMR", "--no-renames"], repo_root)
    binary_paths = []
    for entry in numstat.decode("utf-8", errors="replace").split("\0"):
        if entry.startswith("-\t-\t"):
            binary_paths.append(entry[4:])

    for path in binary_paths:
        if not is_excluded(path):
            findings += scanner.scan_bytes(path, run_git(["show", f":{path}"], repo_root))

    diff = run_git(["diff", "--cached", "-U0", "--no-color", "--no-ext-diff", "--no-renames",
                    "--diff-filter=ACMR"], repo_root)
    for path, numbered_lines in parse_added_lines(diff.decode("utf-8", errors="replace")).items():
        if not is_excluded(path):
            findings += scanner.scan_lines(path, numbered_lines)
    return findings


def scan_files(scanner, repo_root, paths):
    """
    Scan working tree files. Paths are relative to the repo root.

    :param scanner:
    :param repo_root:
    :param paths:
    :return:
    """

    findings = []
    for path in paths:
        full_path = os.path.join(repo_root, path)
        if is_excluded(path) or os.path.islink(full_path) or not os.path.isfile(full_path):
            continue
        with open(full_path, "rb") as file_handler:
            findings += scanner.scan_bytes(path, file_handler.read())
    return findings


def default_denylist_path(repo_root):
    """
    Private denylist location: env var, else <repo parent>/ignore/horey_security/denylist.txt

    :param repo_root:
    :return:
    """
    return os.environ.get(DENYLIST_ENV_VAR) or os.path.join(os.path.dirname(repo_root), "ignore",
                                                            "horey_security", "denylist.txt")


def main(argv=None):
    """
    CLI entry point.

    :param argv:
    :return:
    """

    parser = argparse.ArgumentParser(description="Scan for sensitive data.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--staged", action="store_true", help="Scan lines added in staged changes (default).")
    mode.add_argument("--all", action="store_true", help="Scan every tracked file in the working tree.")
    parser.add_argument("--denylist", help=f"Private denylist file. Default: ${DENYLIST_ENV_VAR} or "
                                           "<repo parent>/ignore/horey_security/denylist.txt")
    parser.add_argument("files", nargs="*", help="Specific files to scan, relative to the current directory.")
    args = parser.parse_args(argv)

    try:
        repo_root = get_repo_root()
        denylist_path = args.denylist or default_denylist_path(repo_root)
        if os.path.isfile(denylist_path):
            scanner = Scanner(*Scanner.load_denylist(denylist_path))
        else:
            print(f"WARNING: private denylist not found at '{denylist_path}', only generic rules applied.",
                  file=sys.stderr)
            scanner = Scanner()

        if args.files:
            paths = [os.path.relpath(os.path.abspath(path), repo_root) for path in args.files]
            findings = scan_files(scanner, repo_root, paths)
        elif args.all:
            tracked = run_git(["ls-files", "-z"], repo_root).decode("utf-8", errors="replace").split("\0")
            findings = scan_files(scanner, repo_root, [path for path in tracked if path])
        else:
            findings = scan_staged(scanner, repo_root)
    except (subprocess.CalledProcessError, ValueError, OSError) as error_instance:
        print(f"ERROR: sensitive data scan failed: {error_instance}", file=sys.stderr)
        return 2

    if not findings:
        print("Sensitive data scan: no findings.")
        return 0

    for finding in findings:
        print(str(finding))
    print(f"\nSensitive data scan: {len(findings)} finding(s).\n"
          f"Replace real values with horey-based placeholders, or append '{rules.ALLOW_MARKER}' "
          "to a line that is a false positive.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
