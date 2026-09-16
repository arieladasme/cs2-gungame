#!/usr/bin/env bash
# Disk report for the RDSNode CS2 container.
#
# The container is capped at 80 GiB and the CS2 install alone takes ~66.5, so the
# usable margin is thin. Run this before every CS2 update: SteamCMD writes the new
# files before dropping the old ones, and a large update can need several GiB.
#
# Usage:  PTK=<pterodactyl client api key> ./tools/rdsnode-disk.sh
# The key lives in the panel under Account > API. Never commit it.
set -euo pipefail

PANEL="https://panel.rdsnode.com"
SERVER="9db02da2"
WARN_GIB=10   # ponytail: flat threshold; revisit if the disk cap changes

: "${PTK:?set PTK to your Pterodactyl client API key}"

api() { curl -s -H "Authorization: Bearer $PTK" -H "Accept: application/json" "$@"; }

limit=$(api "$PANEL/api/client/servers/$SERVER" \
  | python -c "import sys,json;print(json.load(sys.stdin)['attributes']['limits']['disk'])")

api "$PANEL/api/client/servers/$SERVER/resources" \
  | LIMIT_MB="$limit" WARN="$WARN_GIB" python -c "
import sys, json, os

d = json.load(sys.stdin)
if 'errors' in d:
    sys.exit(d['errors'][0]['detail'])

used  = d['attributes']['resources']['disk_bytes'] / 1024**3
limit = int(os.environ['LIMIT_MB']) / 1024
warn  = float(os.environ['WARN'])
free  = limit - used

print('estado: %s' % d['attributes']['current_state'])
print('disco : %.2f / %.2f GiB  (libre %.2f)' % (used, limit, free))
print('barra : [%s%s]' % ('#' * int(used / limit * 40), '.' * (40 - int(used / limit * 40))))
if free < warn:
    print()
    print('AVISO: menos de %g GiB libres. Limpiar antes de actualizar CS2.' % warn)
    sys.exit(1)
"

# Files worth pruning when space runs low. Kept as a plain listing: deleting is a
# judgement call, not something a disk report should do on its own.
echo
echo "candidatos a limpieza:"
# Paths are written without a leading slash: Git Bash rewrites Unix-looking
# arguments into Windows paths, which would mangle the remote path.
for dir in game/csgo/logs game/csgo/addons/counterstrikesharp/logs; do
  enc="%2F$(printf '%s' "$dir" | sed 's:/:%2F:g')"
  api "$PANEL/api/client/servers/$SERVER/files/list?directory=$enc" \
    | DIR="$dir" python -c "
import sys, json, os
d = json.load(sys.stdin)
if 'errors' in d:
    print('  /%s -- no existe' % os.environ['DIR']); sys.exit()
files = [f['attributes'] for f in d['data'] if f['attributes']['is_file']]
total = sum(f['size'] for f in files)
print('  /%s -- %d archivos, %.1f MiB' % (os.environ['DIR'], len(files), total / 1024**2))
for f in sorted(files, key=lambda x: x['size'], reverse=True)[:5]:
    print('      %8.1f MiB  %s' % (f['size'] / 1024**2, f['name']))
"
done
