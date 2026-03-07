#!/bin/bash

cd "$(dirname "$0")" || exit 1

echo "Type 'commit' for the latest commits or 'stable' for the stable version:"
echo "Tip: If you are not a developer, select 'stable'."
read -p "> " choix

if [ "$choix" = "commit" ]; then
    git checkout main
    git pull
elif [ "$choix" = "stable" ]; then
    git fetch --tags
    git checkout $(git describe --tags `git rev-list --tags --max-count=1`)
else
    echo "Invalid choice"
fi