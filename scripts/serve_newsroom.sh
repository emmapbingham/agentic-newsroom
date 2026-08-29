#!/usr/bin/env bash
# Browse the corpus + newsroom ledgers in Datasette (facets, ad-hoc SQL,
# point-and-click charts via datasette-vega, canned citation queries).
#
#   scripts/serve_newsroom.sh            # http://localhost:8001
#   scripts/serve_newsroom.sh -p 8080    # extra args pass through
set -euo pipefail
cd "$(dirname "$0")/.."

exec uvx --with datasette-vega datasette serve \
  --immutable db/gain.db \
  investigations/newsroom.db \
  --metadata datasette/metadata.json \
  --setting sql_time_limit_ms 15000 \
  "$@"
