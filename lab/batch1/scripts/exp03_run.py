#!/usr/bin/env python3
"""EXP-03 v3 driver: ONE child netns per phase; sentinel + client in it.
Sentinel binds 127/8 aliases on lo (kernel routes 127/8 via lo automatically).
exp phase loads the nft recipe before the client runs; ctrl phase doesn't.
Teardown kills the shell's process group; the netns dies with it."""
import json, os, shutil, signal, subprocess, time

LAB = os.path.expanduser("~/workspace/goals/agent-sandbox/hidden_files/lab")
SCR, RAW = os.path.join(LAB, "scripts"), os.path.join(LAB, "raw")
WORK = "/tmp/lab-exp03"

SHELL = r"""
set -x
ip link set lo up
ip -6 addr add fd00:ec2::254/128 dev lo 2>/tmp/lab-exp03/v6addr.err || true
python3 SCRDIR/exp03_sentinel.py /tmp/lab-exp03 &
for i in $(seq 1 100); do [ -f /tmp/lab-exp03/sentinel-ready.json ] && break; sleep 0.1; done
if [ "MODE" = "exp" ]; then nft -f SCRDIR/exp03_rules.nft && echo nft-loaded > /tmp/lab-exp03/nft.status || echo nft-FAILED > /tmp/lab-exp03/nft.status; fi
python3 SCRDIR/exp03_client.py MODE /tmp/lab-exp03/cases-MODE.json
touch /tmp/lab-exp03/cli-done-MODE
sleep 2
"""

def wait_file(path, timeout=60):
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        if os.path.exists(path):
            return True
        time.sleep(0.15)
    return False

def phase(mode):
    shutil.rmtree(WORK, ignore_errors=True)
    os.makedirs(WORK)
    proc = subprocess.Popen(["setsid", "unshare", "-n", "bash", "-c",
                             SHELL.replace("SCRDIR", SCR).replace("MODE", mode)],
                            stdout=open(f"{WORK}/shell.log", "w"), stderr=subprocess.STDOUT)
    out = {"mode": mode, "cli_done": wait_file(f"{WORK}/cli-done-{mode}", timeout=90)}
    if os.path.exists(f"{WORK}/sentinel-ready.json"):
        out["sentinel"] = json.load(open(f"{WORK}/sentinel-ready.json"))
    if os.path.exists(f"{WORK}/cases-{mode}.json"):
        out["cases"] = json.load(open(f"{WORK}/cases-{mode}.json"))["cases"]
    if os.path.exists(f"{WORK}/nft.status"):
        out["nft"] = open(f"{WORK}/nft.status").read().strip()
    if os.path.exists(f"{WORK}/v6addr.err"):
        out["v6addr_err"] = open(f"{WORK}/v6addr.err").read().strip()
    out["shell_log_tail"] = open(f"{WORK}/shell.log").read()[-500:]
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass
    time.sleep(0.5)
    return out

res = {"exp": "EXP-03-v3", "phases": {}}
for mode in ("exp", "ctrl"):
    res["phases"][mode] = phase(mode)
    print(f"phase {mode} done", flush=True)
with open(f"{RAW}/exp03.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
for mode in ("exp", "ctrl"):
    cs = res["phases"][mode].get("cases", {})
    print(mode, {k: v.get("pass") for k, v in cs.items()})
    print(mode, "sentinel:", res["phases"][mode].get("sentinel"), "nft:", res["phases"][mode].get("nft"))
