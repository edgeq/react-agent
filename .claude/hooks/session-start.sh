#!/bin/bash
# Save the commit SHA at the start of a session so the SessionEnd hook
# can diff against it and capture everything that changed — committed or not.

SHA_FILE="$CLAUDE_PROJECT_DIR/.claude/.session-start-sha"
git -C "$CLAUDE_PROJECT_DIR" rev-parse HEAD > "$SHA_FILE" 2>/dev/null

exit 0
