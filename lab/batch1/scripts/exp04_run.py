#!/usr/bin/env python3
"""EXP-04 driver: ST-1/ST-2/ST-4 smoke, n=30 each, LAB-MINI carrier =
namespace unit (unshare user/mount/pid/uts/ipc/net). Timing: process launch
-> workload exit; afterwards driver verifies no unit process survives.
Statistics per 09 freeze: n<100 -> (n, P50, max) + failures only."""
import json, os, shutil, subprocess, time

LAB = os.path.expanduser("~/workspace/goals/agent-sandbox/hidden_files/lab")
SCR, RAW = os.path.join(LAB, "scripts"), os.path.join(LAB, "raw")
UNSHARE = ["unshare", "-Urmpfniu"]

def nearest_rank_p50(samples):
    s = sorted(samples)
    import math
    return s[max(0, math.ceil(0.50 * len(s)) - 1)]

def leftover_units():
    n = 0
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            cmd = open(f"/proc/{pid}/cmdline", "rb").read().decode(errors="replace")
            if "exp04_suites.py" in cmd:
                n += 1
        except OSError:
            pass
    return n

def run_suite(suite, n=30):
    times, fails, evid = [], 0, None
    for i in range(n):
        workdir = f"/tmp/lab-exp04-{suite}-{i}"
        shutil.rmtree(workdir, ignore_errors=True)
        cmd = UNSHARE + ["python3", f"{SCR}/exp04_suites.py", suite]
        if suite == "ST-4":
            cmd += [workdir]
        t0 = time.monotonic()
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        dt = time.monotonic() - t0
        ok = p.returncode == 0
        if ok and suite == "ST-1":
            ok = "LABMINI-PROBE-OK" in p.stdout
            evid = p.stdout.strip()
        if ok and suite == "ST-2":
            evid = p.stdout.strip()
        if ok:
            times.append(round(dt * 1000, 1))
        else:
            fails += 1
            evid = (p.stdout + p.stderr).strip()[-300:]
        shutil.rmtree(workdir, ignore_errors=True)
        if os.path.exists(workdir + ".tar"):
            os.remove(workdir + ".tar")
        if os.path.exists(f"/tmp/lab-exp04-{suite}-{i}.tar"):
            os.remove(f"/tmp/lab-exp04-{suite}-{i}.tar")
    return {"suite": suite, "n": n, "failures": fails,
            "failure_rate": round(fails / n, 3),
            "p50_ms": nearest_rank_p50(times) if times else None,
            "max_ms": max(times) if times else None,
            "times_ms": times, "last_evidence": evid,
            "leftover_unit_processes": leftover_units()}

res = {"exp": "EXP-04"}
# ST-2 baseline on host (no unit) for hash comparison
base = subprocess.run(["python3", f"{SCR}/exp04_suites.py", "ST-2"],
                      capture_output=True, text=True, timeout=120)
res["st2_host_baseline"] = base.stdout.strip()
for suite in ("ST-1", "ST-2", "ST-4"):
    res[suite] = run_suite(suite)
    print(suite, "p50", res[suite]["p50_ms"], "max", res[suite]["max_ms"],
          "fails", res[suite]["failures"], "leftover", res[suite]["leftover_unit_processes"],
          flush=True)
with open(f"{RAW}/exp04.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
print("baseline:", res["st2_host_baseline"])
print("unit ST-2 evidence:", res["ST-2"]["last_evidence"])
