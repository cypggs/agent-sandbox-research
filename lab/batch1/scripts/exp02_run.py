#!/usr/bin/env python3
"""EXP-02 driver: timeout/cancel/normal x {unit-teardown, kill-main-only} x10.
Unit carrier: PID namespace (unshare --pid --fork, bash as ns init that then
execs sleep). Experimental destroy = SIGKILL ns init + rm data dir.
Control destroy = SIGKILL workload main only, nothing else.
Residual checks (host-side) at T+2s per run and a T+10s sweep at the end.
Raw results -> raw/exp02_results.jsonl ; per-run dirs under /tmp (cleaned).
"""
import json, os, shutil, signal, socket, subprocess, time

LAB = os.path.expanduser("~/workspace/goals/agent-sandbox/hidden_files/lab")
SCR, RAW = os.path.join(LAB, "scripts"), os.path.join(LAB, "raw")
WORK = "/tmp/lab-exp02"
os.makedirs(RAW, exist_ok=True)
shutil.rmtree(WORK, ignore_errors=True)
os.makedirs(WORK)

def pid_alive(pid):
    if not pid:
        return False
    try:
        with open(f"/proc/{pid}/stat", "rb") as f:
            state = f.read().rsplit(b")", 1)[1].split()[0]
        return state != b"Z"
    except OSError:
        return False

def port_open(port):
    s = socket.socket()
    s.settimeout(0.4)
    try:
        return s.connect_ex(("127.0.0.1", port)) == 0
    finally:
        s.close()

def enumerate_residual(run):
    alive = [n for n in ("main_hostpid", "daemon_hostpid", "child_hostpid")
             if pid_alive(run["pids"].get(n))]
    files = []
    data = os.path.join(run["rundir"], "data")
    if os.path.isdir(data):
        files = sorted(os.listdir(data))
    return {"procs_alive": alive, "n_procs": len(alive),
            "port_open": port_open(run["port"]), "files_left": files,
            "total": len(alive) + (1 if port_open(run["port"]) else 0) + len(files)}

results = []
counter = 0

def one_run(group, mode, idx):
    global counter
    counter += 1
    port = 23300 + counter
    rid = f"{group}-{mode}-{idx}"
    rundir = os.path.join(WORK, rid)
    os.makedirs(rundir)
    init_sh = (f"python3 {SCR}/exp02_workload.py {rundir} {port} {mode} & "
               f"exec sleep infinity")
    proc = subprocess.Popen(["unshare", "--pid", "--fork", "bash", "-c", init_sh],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    run = {"run": rid, "group": group, "mode": mode, "idx": idx, "port": port,
           "rundir": rundir}
    # wait ready
    ready = None
    t_start = time.monotonic()
    while time.monotonic() - t_start < 8:
        rj = os.path.join(rundir, "ready.json")
        if os.path.exists(rj):
            try:
                ready = json.load(open(rj))
                break
            except json.JSONDecodeError:
                pass
        time.sleep(0.1)
    if not ready:
        run["failed"] = "no-ready"
        results.append(run)
        subprocess.run(["pkill", "-9", "-f", f"exp02_workload.py {rundir}"], capture_output=True)
        return
    run["pids"] = ready
    # init host pid = parent of workload main, read on HOST procfs (reliable;
    # batches 1-2 proved in-ns /proc/$$ tricks resolve to the wrong process)
    def ppid_of(pid):
        with open(f"/proc/{pid}/stat", "rb") as f:
            return int(f.read().rsplit(b")", 1)[1].split()[1])
    def cmdline_of(pid):
        try:
            return open(f"/proc/{pid}/cmdline", "rb").read().replace(b"\0", b" ").decode(errors="replace")
        except OSError:
            return ""
    run["init_hostpid"] = ppid_of(ready["main_hostpid"])
    run["init_cmdline"] = cmdline_of(run["init_hostpid"])
    # termination trigger per mode
    if mode == "timeout":
        while time.monotonic() - t_start < 2.0:
            time.sleep(0.05)
    elif mode == "cancel":
        time.sleep(0.5)
    elif mode == "normal":
        while not os.path.exists(os.path.join(rundir, "main.exited")) and time.monotonic() - t_start < 10:
            time.sleep(0.1)
    # destroy
    t_destroy = time.time()
    if group == "exp":
        # SAFETY: only ever signal the unit init after verifying its identity;
        # never signal pid<=10 (batch 2 recorded init as pid 1 - guarded now)
        ip = run["init_hostpid"]
        assert ip > 10 and "sleep" in run["init_cmdline"] and "infinity" in run["init_cmdline"], \
            f"refusing to signal unverified init pid {ip} cmd={run['init_cmdline']!r}"
        try:
            os.kill(ip, signal.SIGKILL)
        except ProcessLookupError:
            pass
        t_k = time.monotonic()
        while pid_alive(ip) and time.monotonic() - t_k < 1.5:
            time.sleep(0.05)
        run["destroy_confirmed_init_dead"] = not pid_alive(ip)
        shutil.rmtree(os.path.join(rundir, "data"), ignore_errors=True)
    else:
        mp = ready["main_hostpid"]
        if not pid_alive(mp):
            run["ctrl_main_already_dead"] = True  # normal mode: main exited by design
        else:
            assert mp > 10 and "exp02_workload.py" in cmdline_of(mp), \
                f"refusing to signal unverified main pid {mp}"
            try:
                os.kill(mp, signal.SIGKILL)
            except ProcessLookupError:
                pass
    run["destroy_ts"] = t_destroy
    time.sleep(2.0)
    run["check_t2"] = enumerate_residual(run)
    run["check_t2"]["at"] = round(time.time() - t_destroy, 2)
    results.append(run)
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        pass

for idx in range(10):
    for mode in ("timeout", "cancel", "normal"):
        for group in ("exp", "ctrl"):
            one_run(group, mode, idx)
    print(f"idx {idx} done", flush=True)

# T+10 sweep: wait until every run is >=10s past its destroy, then re-enumerate
if results:
    last = max(r.get("destroy_ts", 0) for r in results if "destroy_ts" in r)
    wait = last + 10.5 - time.time()
    if wait > 0:
        time.sleep(wait)
for run in results:
    if "pids" in run:
        run["check_t10"] = enumerate_residual(run)
        run["check_t10"]["at"] = round(time.time() - run["destroy_ts"], 2)

with open(f"{RAW}/exp02_results.jsonl", "w") as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

def summ(group):
    out = {}
    for mode in ("timeout", "cancel", "normal"):
        rs = [r for r in results if r["group"] == group and r["mode"] == mode and "check_t2" in r]
        out[mode] = {
            "n": len(rs),
            "t2_residual_runs": sum(1 for r in rs if r["check_t2"]["total"] > 0),
            "t10_residual_runs": sum(1 for r in rs if r.get("check_t10", {}).get("total", 0) > 0),
            "t2_totals": [r["check_t2"]["total"] for r in rs],
            "t10_totals": [r.get("check_t10", {}).get("total") for r in rs],
        }
    return out

print(json.dumps({"exp": summ("exp"), "ctrl": summ("ctrl"),
                  "failed_runs": [r["run"] for r in results if "failed" in r]}, indent=1))
