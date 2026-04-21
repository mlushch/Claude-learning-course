#!/usr/bin/env bash
# Pre-edit hook: scan for hardcoded secrets before allowing file modification
FILE="$1"

if [ -z "$FILE" ]; then
  exit 0
fi

# Only scan files that exist (skip deletes)
if [ ! -f "$FILE" ]; then
  exit 0
fi

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
