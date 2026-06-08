#!/usr/bin/env bash
set -euo pipefail

version="3.13.0"

if command -v vale >/dev/null 2>&1; then
  echo "vale is already installed: $(vale --version)"
  exit 0
fi

case "$(uname -s)" in
  Darwin)
    if command -v brew >/dev/null 2>&1; then
      brew install vale
      vale --version
      exit 0
    fi
    ;;
  Linux)
    echo "Install Vale ${version} from https://github.com/errata-ai/vale/releases" >&2
    exit 1
    ;;
esac

echo "Install Vale ${version} from https://github.com/errata-ai/vale/releases" >&2
exit 1

