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
