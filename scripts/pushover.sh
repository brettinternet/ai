#!/bin/bash

# Pushover notification script
# Usage: ./pushover.sh "Your message here"

MESSAGE="$1"
TITLE="${2:-"AI Agent"}"

if [ -z "$MESSAGE" ]; then
  echo "Usage: $0 \"message\" [\"title\"]"
  exit 1
fi

DIR=$(basename "$PWD")
BRANCH=$(git branch --show-current 2>/dev/null || echo "no-git")
CONTEXT_MESSAGE="[$DIR:$BRANCH] $MESSAGE"

curl -s \
  --form-string "token=$PUSHOVER_TOKEN" \
  --form-string "user=$PUSHOVER_USER" \
  --form-string "message=$CONTEXT_MESSAGE" \
  --form-string "title=$TITLE" \
  https://api.pushover.net/1/messages.json
