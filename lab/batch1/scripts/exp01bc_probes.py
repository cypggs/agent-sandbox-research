#!/usr/bin/env python3
"""EXP-01b supplementary (RLIMIT alternative carrier) + EXP-01c seccomp probes.
Subcommands run as child processes; the driver exp01_run.py orchestrates.
"""
import ctypes, errno, os, resource, socket, sys, time

# ---------------- EXP-01b RLIMIT_CPU ----------------
def rlimit_cpu():
    resource.setrlimit(resource.RLIMIT_CPU, (2, 4))
    t0 = time.monotonic()
    n = 0
    while True:  # killed by SIGXCPU at 2s CPU time
        n += 1
        if n % 5_000_000 == 0:
            print(f"alive wall={time.monotonic()-t0:.2f}", flush=True)

# ---------------- EXP-01b RLIMIT_AS ----------------
def rlimit_as():
    cap = 256 * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
    chunks, total = [], 0
    try:
        while True:
            c = bytearray(8 * 1024 * 1024)
            for i in range(0, len(c), 4096):  # commit pages
                c[i] = 1
            chunks.append(c)
            total += len(c)
            time.sleep(0.1)
    except MemoryError:
        pass
    st = {}
    for line in open("/proc/self/status"):
        if ":" in line:
            k, v = line.split(":", 1)
            st[k] = v.strip()
    print(f"RESULT allocated_mib={total//1048576} vmsize_kib={st.get('VmSize','?')} "
          f"vmrss_kib={st.get('VmRSS','?')}", flush=True)

# ---------------- EXP-01b sentinel ----------------
def sentinel(secs):
    t0 = time.monotonic()
    while time.monotonic() - t0 < secs:
        pass
    u = resource.getrusage(resource.RUSAGE_SELF)
    print(f"SENTINEL wall={secs} cpu={u.ru_utime + u.ru_stime:.3f}", flush=True)

# ---------------- EXP-01c seccomp ----------------
BPF_LD_W_ABS, BPF_JMP, BPF_JEQ, BPF_RET = 0x20, 0x05, 0x15, 0x06
SECCOMP_RET_ALLOW, SECCOMP_RET_ERRNO = 0x7FFF0000, 0x00050000
AUDIT_ARCH_X86_64 = 0xC000003E
BLOCKED = {165: "mount", 166: "umount2", 169: "reboot",
           175: "init_module", 176: "delete_module", 313: "finit_module"}

class SockFilter(ctypes.Structure):
    _fields_ = [("code", ctypes.c_uint16), ("jt", ctypes.c_uint8),
                ("jf", ctypes.c_uint8), ("k", ctypes.c_uint32)]

class SockFprog(ctypes.Structure):
    _fields_ = [("len", ctypes.c_ushort), ("filter", ctypes.POINTER(SockFilter))]

def install_seccomp():
    libc = ctypes.CDLL("libc.so.6", use_errno=True)
    if libc.prctl(38, 1, 0, 0, 0) != 0:  # PR_SET_NO_NEW_PRIVS
        raise OSError(ctypes.get_errno(), "PR_SET_NO_NEW_PRIVS failed")
    ins = []
    ins.append(SockFilter(BPF_LD_W_ABS, 0, 0, 4))                     # arch
    ins.append(SockFilter(BPF_JMP | BPF_JEQ, 1, 0, AUDIT_ARCH_X86_64))
    ins.append(SockFilter(BPF_RET, 0, 0, SECCOMP_RET_ERRNO | 1))      # wrong arch -> EPERM
    for nr in BLOCKED:
        ins.append(SockFilter(BPF_LD_W_ABS, 0, 0, 0))                 # nr
        ins.append(SockFilter(BPF_JMP | BPF_JEQ, 0, 1, nr))
        ins.append(SockFilter(BPF_RET, 0, 0, SECCOMP_RET_ERRNO | 1))  # EPERM
    ins.append(SockFilter(BPF_RET, 0, 0, SECCOMP_RET_ALLOW))
    arr = (SockFilter * len(ins))(*ins)
    prog = SockFprog(len(ins), arr)
    if libc.prctl(21, 2, ctypes.byref(prog), 0, 0) != 0:              # PR_SET_SECCOMP/FILTER
        raise OSError(ctypes.get_errno(), "PR_SET_SECCOMP failed")

def try_mount():
    libc = ctypes.CDLL("libc.so.6", use_errno=True)
    target = "/tmp/exp01c_mnt_target"
    os.makedirs(target, exist_ok=True)
    rc = libc.syscall(165, b"tmpfs", target.encode(), b"tmpfs", 0, None)
    err = ctypes.get_errno()
    mounted = any(target in l and "tmpfs" in l
                  for l in open("/proc/self/mounts"))
    return rc, err, mounted

def seccomp_child(filtered: int):
    if filtered:
        install_seccomp()
        print("SECCOMP installed", flush=True)
    rc, err, mounted = try_mount()
    print(f"MOUNT rc={rc} errno={err} ({errno.errorcode.get(err,'-')}) mounted={mounted}", flush=True)
    # other functionality must stay intact
    p = "/tmp/exp01c_io.txt"
    with open(p, "w") as f:
        f.write("canary-io")
    ok_io = open(p).read() == "canary-io"
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    print(f"OTHER getpid={os.getpid()} io_ok={ok_io} socket_ok={s.getsockname()[1] > 0}", flush=True)
    s.close()

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "rlimit-cpu":
        rlimit_cpu()
    elif cmd == "rlimit-as":
        rlimit_as()
    elif cmd == "sentinel":
        sentinel(float(sys.argv[2]))
    elif cmd == "seccomp":
        seccomp_child(int(sys.argv[2]))
