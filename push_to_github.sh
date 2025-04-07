#!/bin/bash

# Setup credential
git config --global credential.helper store

# Set origin URL with token auth
git remote set-url origin https://x-access-token:${GITHUB_TOKEN}@github.com/DanielDeenik/SustainaTrendTm.git

# Push to GitHub
git push -u origin main

echo "Push completed!"