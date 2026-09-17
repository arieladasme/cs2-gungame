#!/usr/bin/env python3
"""Load workshop maps one by one on the production server with 16 bots and report
spawns, bot fill, load time and plugin errors.

A map joins the pool only if it has spawns for the server slots: CS2 won't put more
players in a team than it has spawn points. GunGame logs the count when the first
round starts with players ("***** Read N ct spawn, M t spawn").

    RCON_HOST=... RCON_PORT=... RCON_PASS=... PTK=... \
        python tools/maptest.py 3070260370:aim_map_s2r 3581521460:gg_ctm_cs2,gg_ctm_csgo

Each argument is <workshop id>:<internal map name>[,<name>...]. The internal name is
the maps/<name>.vpk inside the item, not the workshop title. The server ends back on
ar_baggage with the bot cvars reset by its own cfg.
"""
import json, os, re, sys, time, urllib.request
from datetime import datetime, timezone

from rcon import run

HOST, PORT, PASS = os.environ["RCON_HOST"], int(os.environ["RCON_PORT"]), os.environ["RCON_PASS"]
PTK = os.environ["PTK"]
API = "https://panel.rdsnode.com/api/client/servers/9db02da2"
OBSERVE = 120
BOTS = "sv_hibernate_when_empty 0; bot_join_after_player 0; bot_quota_mode normal; bot_quota 16"


def rcon(cmd):
    try:
        return run(HOST, PORT, PASS, cmd, timeout=8)
    except Exception as err:
        return "ERR %s" % err


def status():
    s = rcon("status")
    m = re.search(r"spawngroup\(\s*1\)\s*:\s*SV:\s*\[1: ([^\s|]+)", s)
    p = re.search(r"players\s*:\s*(\d+) humans, (\d+) bots", s)
    return (m.group(1) if m else None), (int(p.group(2)) if p else 0)


def css_log(day):
    # The panel's WAF answers 403 to urllib's default User-Agent.
    req = urllib.request.Request(
        API + "/files/contents?file=%2Fgame%2Fcsgo%2Faddons%2Fcounterstrikesharp%2Flogs%2Flog-all" + day + ".txt",
        headers={"Authorization": "Bearer " + PTK, "User-Agent": "curl/8.5.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read().decode("utf-8", "replace").splitlines()
    except Exception:
        return []


def log(msg):
    print("[%s] %s" % (datetime.now(timezone.utc).strftime("%H:%M:%S"), msg), flush=True)


maps = [(a.split(":")[0], a.split(":")[1].lower().split(",")) for a in sys.argv[1:]]
if not maps:
    sys.exit(__doc__)

windows = []
for wid, names in maps:
    t0 = time.time()
    rcon("host_workshop_map %s" % wid)
    actual = None
    while not actual and time.time() - t0 < 300:
        time.sleep(5)
        cur = status()[0]
        actual = cur if cur and cur.lower() in names else None
    if not actual:
        log("%s no cargo en 300s" % wid)
        windows.append((wid, None, t0, time.time(), None, 0))
        continue
    load_s = round(time.time() - t0)
    bots, t1 = 0, time.time()
    while time.time() - t1 < OBSERVE:
        rcon(BOTS)
        time.sleep(15)
        bots = max(bots, status()[1])
    log("%s cargo en %ss, %d bots" % (actual, load_s, bots))
    windows.append((wid, actual, t0, time.time(), load_s, bots))

rcon("changelevel ar_baggage")
time.sleep(60)  # CSS flushes its log lazily

# CSS rotates the log at UTC midnight: read every day the test touched.
days = sorted({datetime.fromtimestamp(t, timezone.utc).strftime("%Y%m%d") for w in windows for t in w[2:4]})
lines = [l for d in days for l in css_log(d)]

for wid, actual, t0, t2, load_s, bots in windows:
    w = []
    for l in lines:
        try:
            ts = datetime.strptime(l[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp()
        except ValueError:
            continue
        if t0 - 1 <= ts <= t2 + 1:
            w.append(l)
    spawns = [re.search(r"Read (\d+) ct spawn, (\d+) t spawn", l).groups() for l in w if "ct spawn" in l]
    ct_t = tuple(map(int, spawns[-1])) if spawns else None
    probs = [l[24:200] for l in w if ("[EROR]" in l or "[WARN]" in l)
             and "Discord gateway" not in l and "Maps_from_List" not in l]
    print(json.dumps({"id": wid, "map": actual, "load_s": load_s, "bots": bots, "spawns_ct_t": ct_t,
                      "max_players": 2 * min(ct_t) if ct_t else None,
                      "trigger_hurt": sum("trigger_hurt" in p for p in probs), "problems": probs[:5]}))
