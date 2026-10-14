#!/usr/bin/env bash
# Publica o site: gera out/dist e envia ao Cloudflare Pages (projeto seumarketing360), como no chordo-pro.
set -euo pipefail
cd "$(dirname "$0")"
python3 build.py
wrangler pages deploy out/dist --project-name seumarketing360 --branch main --commit-dirty=true
