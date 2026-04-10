#!/usr/bin/env python3
"""Push a Lovelace dashboard YAML config to a running Home Assistant instance.

Usage:
    HA_URL=https://your.ha/ HA_TOKEN=eyJ... \
        python3 scripts/push_dashboard.py dashboards/overview_3d.yaml overview-3d

The URL path (2nd arg) must already exist as a storage-mode dashboard. Create
it first from the HA UI (Settings → Dashboards → Add Dashboard) or via the
`lovelace/dashboards/create` WebSocket command.
"""
from __future__ import annotations

import json
import os
import sys
from urllib.parse import urlparse

import websocket  # pip install websocket-client
import yaml


def _ws_url(http_url: str) -> str:
    p = urlparse(http_url.rstrip("/"))
    scheme = "wss" if p.scheme == "https" else "ws"
    return f"{scheme}://{p.netloc}/api/websocket"


def _connect(url: str, token: str) -> websocket.WebSocket:
    ws = websocket.create_connection(_ws_url(url), timeout=30)
    hello = json.loads(ws.recv())
    if hello.get("type") != "auth_required":
        raise RuntimeError(f"Unexpected handshake: {hello}")
    ws.send(json.dumps({"type": "auth", "access_token": token}))
    auth = json.loads(ws.recv())
    if auth.get("type") != "auth_ok":
        raise RuntimeError(f"Auth failed: {auth}")
    return ws


def _call(ws: websocket.WebSocket, msg_id: int, payload: dict) -> dict:
    ws.send(json.dumps({**payload, "id": msg_id}))
    while True:
        resp = json.loads(ws.recv())
        if resp.get("id") == msg_id:
            return resp


def push(config_path: str, url_path: str) -> None:
    ha_url = os.environ["HA_URL"]
    token = os.environ["HA_TOKEN"]

    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    ws = _connect(ha_url, token)
    try:
        resp = _call(ws, 1, {
            "type": "lovelace/config/save",
            "url_path": url_path,
            "config": cfg,
        })
        if not resp.get("success"):
            raise RuntimeError(f"Save failed: {resp}")
        print(f"Saved {config_path} to dashboard '{url_path}'")
    finally:
        ws.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    push(sys.argv[1], sys.argv[2])
