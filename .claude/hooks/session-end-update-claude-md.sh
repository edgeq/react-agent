#!/bin/bash
# SessionEnd hook: diff everything since session start and use headless
# Claude to update CLAUDE.md's "Current state" and "Immediate next steps".

SHA_FILE="$CLAUDE_PROJECT_DIR/.claude/.session-start-sha"
CLAUDE_MD="$CLAUDE_PROJECT_DIR/CLAUDE.md"

# Bail if there's no CLAUDE.md to update
if [ ! -f "$CLAUDE_MD" ]; then
  exit 0
fi

# Read the starting SHA (written by session-start.sh)
if [ -f "$SHA_FILE" ]; then
  START_SHA=$(cat "$SHA_FILE")
else
  # No start SHA recorded — fall back to uncommitted changes only
  START_SHA="HEAD"
fi

# Gather committed changes since session start
COMMITTED=""
if [ "$START_SHA" != "HEAD" ]; then
  CURRENT_SHA=$(git -C "$CLAUDE_PROJECT_DIR" rev-parse HEAD 2>/dev/null)
  if [ "$START_SHA" != "$CURRENT_SHA" ]; then
    COMMITTED=$(git -C "$CLAUDE_PROJECT_DIR" diff "$START_SHA".."$CURRENT_SHA" 2>/dev/null)
  fi
fi

# Gather uncommitted changes (staged + unstaged)
UNCOMMITTED=$(git -C "$CLAUDE_PROJECT_DIR" diff HEAD 2>/dev/null)

# Combine
DIFF="${COMMITTED}${UNCOMMITTED}"

# Nothing changed — skip
if [ -z "$DIFF" ]; then
  rm -f "$SHA_FILE"
  exit 0
fi

# Truncate very large diffs to avoid blowing up the prompt
MAX_CHARS=12000
if [ ${#DIFF} -gt $MAX_CHARS ]; then
  DIFF="${DIFF:0:$MAX_CHARS}

... [diff truncated at $MAX_CHARS chars]"
fi

# Use headless Claude to rewrite the relevant CLAUDE.md sections
claude -p "You are updating a project's CLAUDE.md file after a development session.

Here is the git diff of everything that changed this session:

\`\`\`diff
$DIFF
\`\`\`

Read the current CLAUDE.md at: $CLAUDE_MD

Then update ONLY these two sections:
1. **Current state** — reflect what exists now based on the diff
2. **Immediate next steps** — remove completed items, keep or add remaining work

Rules:
- Keep all other sections untouched
- Be concise and factual — describe what IS, not what was done
- Do not add commentary, timestamps, or session metadata
- Mark completed next steps as done and remove them
- If new next steps are obvious from the work, add them" \
  --bare \
  --allowedTools "Read,Edit" \
  --max-turns 5 \
  --no-session-persistence \
  > /dev/null 2>&1

# Clean up
rm -f "$SHA_FILE"

exit 0
