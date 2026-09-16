#!/usr/bin/env python3
"""A2S_INFO query: shows the server exactly as the CS2 browser sees it.

RCON reports the hostname cvar as stored; this reports what actually travels to
clients, which is what matters for things like leading whitespace.

    A2S_HOST=45.236.90.224 A2S_PORT=26260 python tools/a2s.py
"""
import os
import socket
import struct
import sys

CHALLENGE = b"\xff\xff\xff\xffTSource Engine Query\x00"


def _cstr(data, pos):
    end = data.index(b"\x00", pos)
    return data[pos:end].decode("utf-8", "replace"), end + 1


def query(host, port, timeout=5.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        sock.sendto(CHALLENGE, (host, port))
        data, _ = sock.recvfrom(4096)
        # 'A' means the server wants the challenge echoed back before answering.
        if data[4:5] == b"A":
            sock.sendto(CHALLENGE[:-1] + data[5:9], (host, port))
            data, _ = sock.recvfrom(4096)
        if data[4:5] != b"I":
            raise ValueError("respuesta inesperada: %r" % data[4:5])
        pos = 6  # header + protocol byte
        name, pos = _cstr(data, pos)
        mapname, pos = _cstr(data, pos)
        folder, pos = _cstr(data, pos)
        game, pos = _cstr(data, pos)
        pos += 2  # app id
        players, maxplayers, bots = data[pos], data[pos + 1], data[pos + 2]
        return {"name": name, "map": mapname, "game": game,
                "players": players, "max": maxplayers, "bots": bots}
    finally:
        sock.close()


if __name__ == "__main__":
    host = os.environ.get("A2S_HOST")
    if not host:
        sys.exit("set A2S_HOST (and optionally A2S_PORT)")
    info = query(host, int(os.environ.get("A2S_PORT", "27015")))
    print("nombre  : %r" % info["name"])
    print("          longitud %d, empieza con espacio: %s"
          % (len(info["name"]), info["name"][:1] == " "))
    print("mapa    : %s" % info["map"])
    print("jugadores: %d/%d (%d bots)" % (info["players"], info["max"], info["bots"]))
