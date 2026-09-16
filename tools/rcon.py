#!/usr/bin/env python3
"""Minimal Source RCON client for the CS2 server.

CS2 speaks the classic Source RCON protocol over TCP, so a socket and ~40 lines
cover everything we need. Credentials come from the environment, never argv:
arguments show up in process listings and shell history.

    RCON_HOST=45.236.90.224 RCON_PORT=26260 RCON_PASS=... python tools/rcon.py status
"""
import os
import socket
import struct
import sys

AUTH, EXEC, RESP_VALUE, RESP_AUTH = 3, 2, 0, 2


def _pack(req_id, kind, body):
    payload = struct.pack("<ii", req_id, kind) + body.encode() + b"\x00\x00"
    return struct.pack("<i", len(payload)) + payload


def _read(sock):
    raw = b""
    while len(raw) < 4:
        chunk = sock.recv(4 - len(raw))
        if not chunk:
            raise ConnectionError("server closed the connection")
        raw += chunk
    size = struct.unpack("<i", raw)[0]
    payload = b""
    while len(payload) < size:
        chunk = sock.recv(size - len(payload))
        if not chunk:
            raise ConnectionError("server closed the connection")
        payload += chunk
    req_id, kind = struct.unpack("<ii", payload[:8])
    return req_id, kind, payload[8:-2].decode("utf-8", "replace")


def run(host, port, password, command, timeout=10.0):
    with socket.create_connection((host, port), timeout) as sock:
        sock.settimeout(timeout)
        sock.sendall(_pack(1, AUTH, password))
        req_id, kind, _ = _read(sock)
        # Some builds answer the auth with an empty RESP_VALUE first; skip it.
        if kind == RESP_VALUE:
            req_id, kind, _ = _read(sock)
        if req_id == -1:
            raise PermissionError("RCON auth rejected (wrong password)")

        sock.sendall(_pack(2, EXEC, command))
        # A reply can arrive split across packets; stop when one comes up short.
        out = []
        while True:
            _, _, body = _read(sock)
            out.append(body)
            if len(body) < 4000:
                break
        return "".join(out)


if __name__ == "__main__":
    try:
        host = os.environ["RCON_HOST"]
        password = os.environ["RCON_PASS"]
    except KeyError as missing:
        sys.exit("set RCON_HOST, RCON_PORT and RCON_PASS in the environment (%s)" % missing)
    port = int(os.environ.get("RCON_PORT", "27015"))
    command = " ".join(sys.argv[1:]) or "status"
    try:
        print(run(host, port, password, command))
    except Exception as err:
        sys.exit("rcon: %s" % err)
