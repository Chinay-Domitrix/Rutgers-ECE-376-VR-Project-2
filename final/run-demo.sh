#!/usr/bin/env sh
set -eu

PORT="${1:-5173}"
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
URL="http://localhost:${PORT}/"

if command -v python3 >/dev/null 2>&1; then
	PYTHON=python3
elif command -v python >/dev/null 2>&1; then
	PYTHON=python
else
	echo "Python was not found on PATH." >&2
	echo "Install Python or run: python -m http.server ${PORT}" >&2
	exit 1
fi

echo "Serving Rover Ready from ${ROOT}"
echo "Opening ${URL}"

if command -v cmd.exe >/dev/null 2>&1; then
	cmd.exe /c start "" "${URL}" >/dev/null 2>&1 || true
elif command -v open >/dev/null 2>&1; then
	open "${URL}" >/dev/null 2>&1 || true
elif command -v xdg-open >/dev/null 2>&1; then
	xdg-open "${URL}" >/dev/null 2>&1 || true
fi

cd "${ROOT}"
exec "${PYTHON}" -m http.server "${PORT}"
