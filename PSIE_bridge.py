#!/usr/bin/env python3
import os
import sys
import json
import socket
import platform
import urllib.request
import urllib.error
import time
import functools

HYDRA_APP_URL = os.environ.get("HYDRA_APP_URL", "https://hidra-smart-core.base44.app")
HYDRA_SYNC_TOKEN = os.environ.get("HYDRA_SYNC_TOKEN", "")
GITHUB_OWNER = os.environ.get("GITHUB_OWNER", "bogdanstancu1119-maker")
REPO = "hydra-core"
STATE_URL = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{REPO}/main/SYSTEM_STATE.json"

def retry_with_backoff(retries=3, backoff_in_seconds=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if x == retries:
                        return {"error": str(e)}
                    sleep = (backoff_in_seconds * 2 ** x)
                    time.sleep(sleep)
                    x += 1
        return wrapper
    return decorator

def node_identity():
    return {"hostname": socket.gethostname(), "platform": platform.system(), "python": platform.python_version(), "node_type": "psie_bridge"}

@retry_with_backoff()
def post(path, payload, with_token=True):
    url = f"{HYDRA_APP_URL}/functions/{path}"
    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if with_token and HYDRA_SYNC_TOKEN: headers["Authorization"] = f"Bearer {HYDRA_SYNC_TOKEN}"
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

@retry_with_backoff()
def fetch_state():
    req = urllib.request.Request(STATE_URL, method="GET")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))

def cmd_heartbeat():
    res = post("hydraAsimilareAgenti", {"action": "heartbeat", **node_identity()})
    print("[PSIE bridge] heartbeat trimis:")
    print(json.dumps(res, indent=2, ensure_ascii=False))

def cmd_state():
    state = fetch_state()
    print(f"[PSIE bridge] SYSTEM_STATE live din {GITHUB_OWNER}/{REPO}:")
    print(json.dumps(state, indent=2, ensure_ascii=False))

def cmd_recontextualize(nume, context):
    res = post("hydraRecontextualizareOportuna", {"actiune": "corectie", "entitate": {"nume": nume, "tip": "local", "context": context}})
    print(f"[PSIE bridge] recontextualizare cu auto-corectare pentru '{nume}':")
    print(json.dumps(res, indent=2, ensure_ascii=False))
    corectie = res.get("corectie") or {}
    if corectie.get("a_corectat"): print(f"  >> V initial '{corectie.get('v_initial')}' corectat la '{corectie.get('v_corectat')}'")

def main():
    if len(sys.argv) < 2: print(__doc__); return
    cmd = sys.argv[1]
    if cmd == "heartbeat": cmd_heartbeat()
    elif cmd == "state": cmd_state()
    elif cmd == "recontextualize":
        if len(sys.argv) < 3: print("Usage: PSIE_bridge.py recontextualize <nume> [context]"); return
        nume, context = sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else ""
        cmd_recontextualize(nume, context)
    else: print(f"Comanda necunoscuta: {cmd}"); print(__doc__)

if __name__ == "__main__": main()