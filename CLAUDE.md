# Horey

## Running horey API packages

Always run any horey API package (its code, tests, or scripts) using the Python virtualenv at
`build/_build/_venv`, relative to the horey repo root (`<horey repo root>/build/_build/_venv`).

- Use the venv interpreter directly: `build/_build/_venv/bin/python ...`
  (e.g. `build/_build/_venv/bin/python -m pytest snyk_api/tests/test_snyk_api.py`)
- Or activate it first: `source build/_build/_venv/bin/activate`
- Never use the system Python or another environment for these packages.

## Code changes: propose, don't apply

Never write, edit, or generate code in the working tree unless the user explicitly asks you to
make the change (e.g. "implement it", "apply the changes", "edit the file", "write the code").

When a task would require code changes and you have not been explicitly asked to apply them:

- Do NOT use Edit, Write, NotebookEdit, or shell commands (sed, heredocs, scripts, etc.) to modify
  files in the repository.
- Instead, produce a list of the required changes and present it in your output. For each change include:
  - the file path (and line numbers where relevant),
  - what needs to change and why,
  - a short code snippet or diff illustrating the change, when helpful.
- Then stop and wait for the user to explicitly ask you to apply the changes.

Reading files, searching, and running read-only commands or tests to investigate are fine.

## No real data in docstrings, examples, or comments

Never put real data in docstrings, code examples, or comments. That includes real organization,
repository, user, team, project, and account names, IDs, emails, URLs, hostnames, tokens, and
values copied from API responses or test output.

Base every placeholder on the `horey` slug, and match the naming style the context expects:

- PascalCase: `OrgHorey`, `RepoHorey`, `UserHorey`
- kebab-case: `org-horey`, `repo-horey`, `team-horey`
- snake_case: `org_horey`, `repo_horey`, `project_horey`
- Compound values: `org-horey/repo-horey`, `user-horey@horey.com`, `https://horey.com/org-horey`

When you edit existing docstrings, examples, or comments that contain real data, replace it with
`horey`-based placeholders.
