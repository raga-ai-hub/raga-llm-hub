#!/bin/sh
# .hooks/prevent-main-commit.sh

# Get the current branch name
current_branch=$(git branch --show-current)

# Check if the current branch is main
if [ "$current_branch" = "main" ]; then
  echo "Direct commits to the main branch are not allowed."
  exit 1
fi
