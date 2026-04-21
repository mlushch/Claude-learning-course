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
ruff check "$FILE" --fix 2>/dev/null || true

echo "Running black on $FILE..."
black "$FILE" 2>/dev/null || true

# Run tests if the file is inside mcp/
if [[ "$FILE" == */mcp/* ]]; then
  echo "Running pytest..."
  cd "$(dirname "$FILE")/.." && pytest tests/ -q 2>/dev/null || true
fi

exit 0
