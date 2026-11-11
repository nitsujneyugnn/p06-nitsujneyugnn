#!/usr/bin/env bash
# CSE 490 Project 6: build thumbor's environment inside the codespace.
# Same recipe as AGENTS.md and the checks workflow: Python 3.12, the test extras, the C extensions,
# gifsicle, jpegtran, ffmpeg and redis. Runs once, when the codespace is created.
set -euo pipefail
cd "$(dirname "$0")/.."
# Wait for any apt the image is still running at first boot, then install the programs the tests need.
while sudo fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1; do sleep 3; done
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq gifsicle libjpeg-turbo-progs ffmpeg redis-server libcurl4-openssl-dev >/dev/null
python3 -m venv .venv
.venv/bin/pip install -q -U pip setuptools wheel
.venv/bin/pip install -q -e ".[tests,opencv,extra-libs]"
.venv/bin/python setup.py build_ext -i >/dev/null
# The harness's own environment, beside the repository: mcp, dotenv, requests, as the setup guide's harness step.
python3 -m venv ../.venv-harness
../.venv-harness/bin/pip install -q python-dotenv mcp requests
# The GitHub MCP server, the release the course pins, beside the harness.
rel="v2.0.2"
mkdir -p ../mcp && curl -sL "https://github.com/github/github-mcp-server/releases/download/${rel}/github-mcp-server_Linux_x86_64.tar.gz" | tar -xz -C ../mcp github-mcp-server
echo "setup done: $(.venv/bin/python -c 'import thumbor; print(thumbor.__version__)'), github-mcp-server $(../mcp/github-mcp-server --version 2>&1 | grep -o 'Version: [0-9.]*')"
