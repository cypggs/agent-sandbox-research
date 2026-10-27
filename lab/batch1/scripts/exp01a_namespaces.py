#!/usr/bin/env python3
"""EXP-01a namespace view isolation probe.
Run once on host (baseline) and once inside unshare; driver diffs the two JSONs.
Inner mode also: sets hostname, mounts tmpfs, creates SysV IPC object.
"""
import ctypes, json, os, socket, subprocess, sys

def ns_inodes():
    out = {}
    nsdir = "/proc/self/ns"
    for name in sorted(os.listdir(nsdir)):
        try:
            out[name] = os.readlink(os.path.join(nsdir, name))
        except OSError as e:
            out[name] = f"ERR:{e}"
    return out

def net_ifaces():
    r = subprocess.run(["ip", "-j", "link", "show"], capture_output=True, text=True)
    try:
        return sorted(d["ifname"] for d in json.loads(r.stdout))
    except Exception:
        return ["ERR"]

def probe(inner: bool):
    d = {
        "inner": inner,
        "pid_self": os.getpid(),
        "hostname_before": socket.gethostname(),
        "ns": ns_inodes(),
        "ifaces": net_ifaces(),
        "uid": os.getuid(),
        "uid_map": open("/proc/self/uid_map").read().strip(),
    }
    if inner:
        # UTS: change hostname, only visible inside
        socket.sethostname("exp01a-canary-host")
        d["hostname_after_set"] = socket.gethostname()
        # MNT: mount tmpfs on pre-created target, check own mount table
        target = "/tmp/exp01a_mnt_target"
        os.makedirs(target, exist_ok=True)
        libc = ctypes.CDLL("libc.so.6", use_errno=True)
        rc = libc.mount(b"tmpfs", target.encode(), b"tmpfs", 0, None)
        d["mount_tmpfs_rc"] = rc
        d["mount_tmpfs_errno"] = ctypes.get_errno() if rc != 0 else 0
        mounts = open("/proc/self/mounts").read()
        d["tmpfs_in_own_mounts"] = target in mounts and "tmpfs" in mounts
        # IPC: create a SysV semaphore set inside this IPC ns
        SEMGET = libc.semget
        IPC_PRIVATE, IPC_CREAT = 0, 0o1000
        sid = SEMGET(IPC_PRIVATE, 1, IPC_CREAT | 0o600)
        d["semget_id"] = sid
    return d

if __name__ == "__main__":
    inner = len(sys.argv) > 1 and sys.argv[1] == "inner"
    print(json.dumps(probe(inner)))
