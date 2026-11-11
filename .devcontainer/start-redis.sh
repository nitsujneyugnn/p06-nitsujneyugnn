#!/usr/bin/env bash
# Start redis each time the codespace starts; the suite's storage tests use it.
# The repository's redis.conf daemonizes it on port 6668, the port the tests expect.
cd "$(dirname "$0")/.."
pgrep -x redis-server >/dev/null || redis-server redis.conf >/dev/null 2>&1
