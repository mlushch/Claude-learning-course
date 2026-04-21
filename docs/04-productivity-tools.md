# Step 4: Productivity Tools (Skills, Sub-Agents, Hooks)

## Goal

Implement two skills, two sub-agents, and two hooks (pre-edit and post-edit) to boost development productivity.

---

## 4.1 Skills

Skills are custom slash commands for Claude Code stored as Markdown prompt files.

### Directory structure

```
.claude/
└── skills/
    ├── git-commit.md
    └── add-test.md
```

---

### Skill: `/git-commit`

File: `.claude/skills/git-commit.md`

```markdown
---
name: git-commit
description: Generate a conventional commit message based on staged changes
---

Review the output of `git diff --staged` and generate a commit message following
the Conventional Commits specification (https://www.conventionalcommits.org).

Format:
```
<type>(<scope>): <short description>

[optional body]

[optional footer]
```

Types: feat, fix, docs, style, refactor, test, chore

Rules:
- Subject line must be under 72 characters
- Use imperative mood ("add" not "added")
- Reference issue numbers in footer if relevant

Run `git diff --staged` first, then output only the commit message — no extra explanation.
```

---

### Skill: `/add-test`

File: `.claude/skills/add-test.md`

```markdown
---
name: add-test
description: Create a unit test skeleton for the selected or described function
---

Given a function or class description (or selected code), generate a unit test skeleton.

For C# code: use xUnit with the Arrange/Act/Assert pattern.
For Python code: use pytest with descriptive test function names.

Rules:
- Cover the happy path first
- Add one test for each edge case (null input, empty collection, boundary values)
- Use descriptive test names: `MethodName_Scenario_ExpectedResult`
- Do not implement the test body — leave `// TODO: implement` comments in the assertions
- Output only the test code, no explanation
```

---

## 4.2 Sub-Agents

Sub-agents are specialized agent definitions that Claude Code can invoke for focused tasks.

### Directory structure

```
.claude/
└── agents/
    ├── code-reviewer.md
    └── test-writer.md
```

---

### Sub-Agent: `code-reviewer`

File: `.claude/agents/code-reviewer.md`

```markdown
---
name: code-reviewer
description: Reviews code for quality, security, and adherence to project conventions
---

You are a senior code reviewer. When given code to review, analyze it for:

1. **Correctness** — logic errors, off-by-one errors, null reference risks
2. **Security** — hardcoded secrets, SQL injection, exposed API keys, improper auth
3. **Code quality** — naming, single responsibility, unnecessary complexity
4. **Conventions** — follows project style (PascalCase in C#, PEP 8 in Python)
5. **Test coverage** — are edge cases handled?

Output a structured review:
- Summary (1-2 sentences)
- Issues found (severity: Critical / Warning / Suggestion)
- Suggested improvements (with code snippets if helpful)

Be concise. Flag Critical issues first.
```

---

### Sub-Agent: `test-writer`

File: `.claude/agents/test-writer.md`

```markdown
---
name: test-writer
description: Writes complete unit tests for provided code
---

You are an expert test engineer. When given code, write complete, runnable unit tests.

For C# code:
- Use xUnit
- Use Moq for mocking dependencies
- Follow Arrange/Act/Assert pattern
- Include tests for: happy path, invalid inputs, boundary conditions, exception cases

For Python code:
- Use pytest
- Use `unittest.mock` or `pytest-mock` for mocking
- Include fixtures where appropriate

Rules:
- Write COMPLETE tests — no TODO stubs
- Each test must have a single assertion (or grouped related assertions)
- Test names must be self-documenting
- Output only the test file content
```

---

## 4.3 Hooks

Hooks are shell scripts that Claude Code executes automatically before and after file edits.

### Directory structure

```
hooks/
├── pre-edit.sh
└── post-edit.sh
```

Register hooks in `.claude/settings.json`:
```json
{
  "hooks": {
    "preToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "bash hooks/pre-edit.sh $CLAUDE_FILE_PATH" }]
      }
    ],
    "postToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "bash hooks/post-edit.sh $CLAUDE_FILE_PATH" }]
      }
    ]
  }
}
```

---

### Pre-Edit Hook: Secret Scanner

File: `hooks/pre-edit.sh`

```bash
#!/usr/bin/env bash
# Pre-edit hook: scan for secrets before allowing file modification
FILE="$1"

if [ -z "$FILE" ]; then
  exit 0
fi

# Patterns that indicate a hardcoded secret
PATTERNS=(
  'api[_-]?key\s*=\s*"[^"]{8,}"'
  'password\s*=\s*"[^"]{4,}"'
  'secret\s*=\s*"[^"]{4,}"'
  'bearer\s+[a-zA-Z0-9\-_\.]{20,}'
)

for pattern in "${PATTERNS[@]}"; do
  if grep -iE "$pattern" "$FILE" 2>/dev/null; then
    echo "ERROR: Possible hardcoded secret detected in $FILE"
    echo "Move secrets to environment variables or .env files."
    exit 1
  fi
done

exit 0
```

---

### Post-Edit Hook: Linting and Tests

File: `hooks/post-edit.sh`

```bash
#!/usr/bin/env bash
# Post-edit hook: run linting and tests after Python file changes
FILE="$1"

if [ -z "$FILE" ]; then
  exit 0
fi

# Only run for Python files
if [[ "$FILE" != *.py ]]; then
  exit 0
fi

echo "Running ruff on $FILE..."
ruff check "$FILE" --fix

echo "Running black on $FILE..."
black "$FILE"

# Run tests if in the mcp directory
if [[ "$FILE" == */mcp/* ]]; then
  echo "Running pytest..."
  cd mcp && pytest tests/ -q
fi

exit 0
```

Make both scripts executable:
```bash
chmod +x hooks/pre-edit.sh hooks/post-edit.sh
```

---

## 4.4 Verification Checklist

Skills:
- [ ] `/git-commit` appears in Claude Code slash command list
- [ ] `/git-commit` produces a valid conventional commit message
- [ ] `/add-test` produces a correct xUnit/pytest skeleton

Sub-agents:
- [ ] `code-reviewer` can be invoked and produces a structured review
- [ ] `test-writer` produces complete, runnable test files

Hooks:
- [ ] Pre-edit hook blocks edits that contain hardcoded secrets (test with a dummy secret)
- [ ] Post-edit hook runs `ruff` and `black` after editing a `.py` file
- [ ] Post-edit hook runs `pytest` after editing a file inside `mcp/`
