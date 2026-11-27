"""
Tests for sensitive_data_scanner.py.

Values that must be detected are assembled at runtime, so this file itself stays clean
when the scanner runs over the repository.
"""

import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# pylint: disable=wrong-import-position
import sensitive_data_scanner as scanner_module
from sensitive_data_scanner import Scanner, parse_added_lines

# pylint: disable=missing-function-docstring


def join(*parts):
    return "".join(parts)


def rule_names(line, scanner=None):
    return [rule_name for rule_name, _, _ in (scanner or Scanner()).scan_line(line)]


@pytest.mark.unit
@pytest.mark.parametrize("line, expected_rule", [
    (join("key = '", "AKIA", "Q" * 16, "'"), "aws-access-key-id"),
    (join("aws_secret_access_key = ", "a" * 20, "B" * 20), "aws-secret-access-key"),
    (join("token = '", "ghp_", "a1" * 18, "'"), "github-token"),
    (join("token = '", "github_pat_", "a1" * 31, "'"), "github-fine-grained-token"),
    (join("token = '", "glpat-", "a1" * 10, "'"), "gitlab-token"),
    (join("token = '", "xoxb-", "1234567890-abcdef", "'"), "slack-token"),
    (join("url = 'https://hooks.slack.com/services/", "T0", "/", "B0", "/", "abc", "'"), "slack-webhook"),
    (join("key = '", "sk-", "ant-", "a1" * 12, "'"), "anthropic-api-key"),
    (join("key = '", "sk-", "proj-", "a1" * 20, "'"), "openai-api-key"),
    (join("key = '", "AIza", "a" * 35, "'"), "google-api-key"),
    (join("-----BEGIN ", "RSA ", "PRIVATE KEY-----"), "private-key"),
    (join("token = '", "1234567890:", "AA", "b" * 33, "'"), "telegram-bot-token"),
    (join("sid = '", "AC", "0f" * 16, "'"), "twilio-key"),
    (join("jwt = '", "eyJ", "a" * 12, ".eyJ", "b" * 12, ".", "c" * 12, "'"), "jwt"),
    (join("url = 'postgresql://admin:", "Qz7rW9mK", "@db.horey.com/db'"), "credentials-in-url"),
    (join("db_password = '", "Qz7rW9mK2", "'"), "hardcoded-secret"),
    (join("account = '", "2119", "2118", "3447", "'"), "aws-account-id"),
    (join("owner = '", "jane.roe", "@", "gmail.com", "'"), "email"),
    (join("ip = '", "84.229.", "1.2", "'"), "public-ip"),
    (join("path = '/", "Users", "/jane.roe/git'"), "home-directory"),
    (join("path = 'C:\\\\", "Users", "\\\\janeroe\\\\git'"), "windows-home-directory"),
    (join("call ", "204-", "930-", "1234"), "phone-number"),
    (join("to = '", "+1", "2049301234", "'"), "international-phone-number"),
])
def test_rule_detects(line, expected_rule):
    assert expected_rule in rule_names(line)


@pytest.mark.unit
@pytest.mark.parametrize("line", [
    "account = '123456789012'",
    "account = '111111111111'",
    "vwap_change=85.879887343608",
    "owner = 'user-horey@horey.com'",
    "owner = 'test.user@gmail.com'",
    "remote = 'git@github.com:org-horey/repo-horey.git'",
    "@pytest.mark.unit",
    "cidr = '10.0.0.0/16'",
    "ip = '198.51.100.12'",
    "dns = '8.8.8.8'",
    "multicast = '224.0.0.18'",
    "path = '/home/ubuntu/efs'",
    "path = '/Users/xxx/.ssh/key'",
    "password = '<MyPassword>'",
    "password = 'p@ss/word'",
    "url = 'driver://user:pass@localhost/dbname'",
    "from_ = 'whatsapp:+14155238886'",
    "phone = '204-555-0199'",
])
def test_rule_ignores_placeholders(line):
    assert rule_names(line) == []


@pytest.mark.unit
def test_allow_marker_suppresses_line():
    line = join("ip = '", "84.229.", "1.2", "'  # horey-security: allow")
    assert rule_names(line) == []


@pytest.mark.unit
def test_secret_values_are_masked():
    value = join("AKIA", "Q" * 16)
    finding = Scanner().scan_lines("file.py", [(1, f"key = '{value}'")])[0]
    assert value not in str(finding)
    assert "AKIA...(20 chars)" in str(finding)


@pytest.mark.unit
def test_denylist_and_allow_context(tmp_path):
    denylist = tmp_path / "denylist.txt"
    denylist.write_text("# comment\n\njanedoe\n!github\\.com/JaneDoe/horey\n", encoding="utf-8")
    scanner = Scanner(*Scanner.load_denylist(str(denylist)))

    assert rule_names("author = 'JaneDoe'", scanner) == ["private-denylist"]
    assert rule_names("url = 'https://github.com/JaneDoe/horey.git'", scanner) == []
    assert rule_names("url = 'https://github.com/JaneDoe/other.git'", scanner) == ["private-denylist"]


@pytest.mark.unit
def test_denylist_invalid_regex(tmp_path):
    denylist = tmp_path / "denylist.txt"
    denylist.write_text("broken[\n", encoding="utf-8")
    with pytest.raises(ValueError):
        Scanner.load_denylist(str(denylist))


@pytest.mark.unit
def test_binary_skips_identifier_rules_but_keeps_paths():
    data = b"\0\0" + join("/", "Users", "/jane.roe/go/main.go").encode() + b"\0" + \
        join("account ", "2119", "2118", "3447").encode() + b"\0"
    findings = Scanner().scan_bytes("lib.dylib", data)
    assert [finding.rule_name for finding in findings] == ["home-directory"]
    assert findings[0].line_number == "binary"


@pytest.mark.unit
def test_parse_added_lines():
    diff = "\n".join([
        "diff --git a/file.py b/file.py",
        "index 1..2 100644",
        "--- a/file.py",
        "+++ b/file.py",
        "@@ -1,0 +2,2 @@",
        "+first",
        "++++ looks like a header but is content",
        "@@ -10 +12 @@",
        "-removed",
        "+replaced",
        "diff --git a/new.txt b/new.txt",
        "new file mode 100644",
        "--- /dev/null",
        "+++ b/new.txt",
        "@@ -0,0 +1 @@",
        "+hello",
    ])
    assert parse_added_lines(diff) == {
        "file.py": [(2, "first"), (3, "+++ looks like a header but is content"), (12, "replaced")],
        "new.txt": [(1, "hello")],
    }


def git(repo, *args):
    subprocess.run(["git", *args], cwd=repo, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


@pytest.fixture(name="repo")
def fixture_repo(tmp_path, monkeypatch):
    repo = tmp_path / "repo_horey"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "user-horey@horey.com")
    git(repo, "config", "user.name", "UserHorey")
    (repo / "clean.py").write_text("ip = '10.0.0.1'\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "init")
    monkeypatch.chdir(repo)
    monkeypatch.setenv(scanner_module.DENYLIST_ENV_VAR, str(tmp_path / "missing_denylist.txt"))
    return repo


@pytest.mark.unit
def test_main_staged_reports_only_added_lines(repo, capsys):
    (repo / "clean.py").write_text(join("ip = '10.0.0.1'\nip2 = '", "84.229.", "1.2", "'\n"), encoding="utf-8")
    git(repo, "add", ".")

    assert scanner_module.main(["--staged"]) == 1
    assert "clean.py:2: [public-ip]" in capsys.readouterr().out


@pytest.mark.unit
def test_main_staged_clean(repo):
    (repo / "clean.py").write_text("ip = '10.0.0.2'\n", encoding="utf-8")
    git(repo, "add", ".")
    assert scanner_module.main([]) == 0


@pytest.mark.unit
def test_main_staged_binary(repo, capsys):
    (repo / "lib.so").write_bytes(b"\0\0" + join("/", "Users", "/jane.roe/main.go").encode() + b"\0")
    git(repo, "add", ".")

    assert scanner_module.main(["--staged"]) == 1
    assert "lib.so:binary: [home-directory]" in capsys.readouterr().out


@pytest.mark.unit
def test_main_all_and_files(repo):
    assert scanner_module.main(["--all"]) == 0
    (repo / "untracked.txt").write_text(join("owner ", "jane.roe", "@", "gmail.com\n"), encoding="utf-8")
    assert scanner_module.main(["--all"]) == 0
    assert scanner_module.main(["untracked.txt"]) == 1
