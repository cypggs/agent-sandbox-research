#!/usr/bin/env python3
"""EXP-01 driver: namespaces (a), cgroup-unavailability evidence + RLIMIT
supplementary probes (b), seccomp (c). Writes raw JSON to raw/exp01.json."""
import json, os, resource, socket, subprocess, sys, time

LAB = os.path.expanduser("~/workspace/goals/agent-sandbox/hidden_files/lab")
SCR = os.path.join(LAB, "scripts")
RAW = os.path.join(LAB, "raw")
os.makedirs(RAW, exist_ok=True)
res = {"exp": "EXP-01", "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z")}

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)

# ---------- (a) namespaces ----------
host = json.loads(run(["python3", f"{SCR}/exp01a_namespaces.py"]).stdout)
inner_p = run(["unshare", "-Urmpfniu", "python3", f"{SCR}/exp01a_namespaces.py", "inner"])
inner = json.loads(inner_p.stdout)
host_after = {"hostname": socket.gethostname(),
              "tmpfs_target_in_host_mounts": "/tmp/exp01a_mnt_target" in open("/proc/self/mounts").read()}
checks = {
    "inner_pid_is_1": inner["pid_self"] == 1,
    "inner_pid_differs_from_host_view": inner["pid_self"] != host["pid_self"],
    "uts_hostname_set_inside": inner.get("hostname_after_set") == "exp01a-canary-host",
    "uts_host_unaffected": host_after["hostname"] == host["hostname_before"],
    "net_ifaces_only_lo": inner["ifaces"] == ["lo"],
    "mnt_tmpfs_mounted_inside": inner.get("tmpfs_in_own_mounts") is True and inner.get("mount_tmpfs_rc") == 0,
    "mnt_not_visible_on_host": not host_after["tmpfs_target_in_host_mounts"],
    "ipc_object_created_inside": inner.get("semget_id", -1) >= 0,
    "unshared_ns_inodes_differ": all(inner["ns"][k] != host["ns"][k] for k in ("user", "mnt", "pid", "net", "uts", "ipc")),
    "shared_by_design_ns_same": {k: inner["ns"][k] == host["ns"][k] for k in ("cgroup", "time")},
    "user_uid_mapped_root": inner["uid"] == 0,
}
res["a_namespaces"] = {"host": host, "inner": inner, "host_after": host_after,
                       "checks": checks, "pass": all(checks.values())}

# ---------- (b) cgroup unavailability evidence ----------
ev = {}
ev["root_controllers_file"] = open("/sys/fs/cgroup/cgroup.controllers").read().strip()
probe_dir = "/sys/fs/cgroup/exp01probe"
try:
    os.mkdir(probe_dir)
    ev["child_files"] = sorted(os.listdir(probe_dir))
    ev["child_has_quota_files"] = any(f in ev["child_files"] for f in ("cpu.max", "memory.max", "pids.max"))
    try:
        with open("/sys/fs/cgroup/cgroup.subtree_control", "w") as f:
            f.write("+cpu")
        ev["subtree_write"] = "ok"
    except OSError as e:
        ev["subtree_write"] = f"FAIL errno={e.errno} {e.strerror}"
    os.rmdir(probe_dir)
    ev["probe_dir_removed"] = not os.path.exists(probe_dir)
except OSError as e:
    ev["mkdir_error"] = str(e)
res["b_cgroup_evidence"] = ev

def spawn_wait(cmd):
    """Spawn, wait, return (rc, stdout, child_rusage_cpu, wall)."""
    t0 = time.monotonic()
    pid = os.fork()
    if pid == 0:
        os.execvp(cmd[0], cmd)
    _, status, ru = os.wait4(pid, 0)
    wall = time.monotonic() - t0
    return status, ru.ru_utime + ru.ru_stime, wall

# RLIMIT_CPU probe (supplementary carrier, NOT a C1 verdict)
st, ccpu, cwall = spawn_wait(["python3", f"{SCR}/exp01bc_probes.py", "rlimit-cpu"])
res["b_rlimit_cpu"] = {"limit_s": 2, "child_cpu_s": round(ccpu, 3), "wall_s": round(cwall, 3),
                       "rel_err_pct": round(abs(ccpu - 2) / 2 * 100, 2),
                       "killed_by_signal": os.WIFSIGNALED(st), "signal": os.WTERMSIG(st) if os.WIFSIGNALED(st) else None}
# RLIMIT_AS probe (supplementary carrier, NOT a C2 verdict)
p = run(["python3", f"{SCR}/exp01bc_probes.py", "rlimit-as"], timeout=60)
res["b_rlimit_as"] = {"stdout": p.stdout.strip(), "rc": p.returncode}
# Sentinel solo vs concurrent (supplementary, C1-style neighbor check on this carrier)
solo = run(["python3", f"{SCR}/exp01bc_probes.py", "sentinel", "6"])
solo_cpu = float(solo.stdout.split("cpu=")[1])
conc_proc = subprocess.Popen(["python3", f"{SCR}/exp01bc_probes.py", "sentinel", "6"],
                             stdout=subprocess.PIPE, text=True)
st2, ccpu2, _ = spawn_wait(["python3", f"{SCR}/exp01bc_probes.py", "rlimit-cpu"])
conc_out = conc_proc.communicate()[0]
conc_cpu = float(conc_out.split("cpu=")[1])
res["b_sentinel"] = {"solo_cpu_6s": solo_cpu, "concurrent_cpu_6s": conc_cpu,
                     "degradation_pct": round((solo_cpu - conc_cpu) / solo_cpu * 100, 2)}

# ---------- (c) seccomp (C probe; python/ctypes prctl failed in attempt 1) ----------
binpath = "/tmp/exp01c_seccomp"
if not os.path.exists(binpath):
    subprocess.run(["gcc", "-O2", "-o", binpath, f"{SCR}/exp01c_seccomp.c"], check=True)
def seccomp_run(filtered):
    p = run(["unshare", "-Urmpf", binpath, str(filtered)], timeout=30)
    return {"rc": p.returncode, "stdout": p.stdout.strip(), "stderr": p.stderr.strip()[-300:]}
res["c_seccomp"] = {"control_unfiltered": seccomp_run(0), "filtered": seccomp_run(1)}

with open(f"{RAW}/exp01.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
print(json.dumps({"a_pass": res["a_namespaces"]["pass"],
                  "b_evidence": ev,
                  "b_rlimit_cpu": res["b_rlimit_cpu"],
                  "b_rlimit_as": res["b_rlimit_as"]["stdout"],
                  "b_sentinel": res["b_sentinel"],
                  "c_control": res["c_seccomp"]["control_unfiltered"]["stdout"],
                  "c_filtered": res["c_seccomp"]["filtered"]["stdout"]}, indent=1, ensure_ascii=False))
