#!/usr/bin/env python3
"""EXP-02 workload: runs inside a PID-namespace unit.
 main: writes data/main.tmp; spawns (i) double-fork+setsid daemon binding a
 TCP port + heartbeat file, (ii) setsid child; writes ready.json with HOST
 pids (NSpid first field); mode=normal -> exits by itself after 3s.
"""
import json, os, socket, sys, time

def host_pid():
    for line in open("/proc/self/status"):
        if line.startswith("NSpid:"):
            return int(line.split()[1])
    return os.getpid()

def write_atomic(path, text):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        f.write(text)
    os.rename(tmp, path)

def read_pid_when_ready(path, timeout=5.0):
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        try:
            return int(open(path).read().strip())
        except (OSError, ValueError):
            time.sleep(0.05)
    return None

def daemon(rundir, port):
    # already double-forked + setsid by caller
    write_atomic(os.path.join(rundir, "daemon.hostpid"), str(host_pid()))
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", port))
    srv.listen(8)
    srv.settimeout(0.25)
    hb = os.path.join(rundir, "data", "heartbeat.tmp")
    last = 0.0
    while True:
        try:
            conn, _ = srv.accept()
            conn.close()
        except socket.timeout:
            pass
        if time.monotonic() - last >= 0.5:
            try:
                with open(hb, "a") as f:
                    f.write("hb\n")
            except OSError:
                pass  # heartbeat target may vanish; daemon must not die of it
            last = time.monotonic()

def main():
    rundir, port, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    data = os.path.join(rundir, "data")
    os.makedirs(data, exist_ok=True)
    with open(os.path.join(data, "main.tmp"), "w") as f:
        f.write("main-canary")
    # (i) double-fork daemon
    if os.fork() == 0:
        os.setsid()
        if os.fork() == 0:
            daemon(rundir, port)
            os._exit(0)
        os._exit(0)
    os.wait()
    # (ii) setsid child
    cpid = os.fork()
    if cpid == 0:
        os.setsid()
        write_atomic(os.path.join(rundir, "child.hostpid"), str(host_pid()))
        with open(os.path.join(data, "child.tmp"), "w") as f:
            f.write("child-canary")
        time.sleep(3600)
        os._exit(0)
    # wait until both pid files are fully written and parseable
    ready = {
        "main_hostpid": host_pid(),
        "daemon_hostpid": read_pid_when_ready(os.path.join(rundir, "daemon.hostpid")),
        "child_hostpid": read_pid_when_ready(os.path.join(rundir, "child.hostpid")),
        "port": port,
        "files": ["main.tmp", "heartbeat.tmp", "child.tmp"],
    }
    write_atomic(os.path.join(rundir, "ready.json"), json.dumps(ready))
    if mode == "normal":
        time.sleep(3)
        with open(os.path.join(rundir, "main.exited"), "w") as f:
            f.write("bye")
        sys.exit(0)
    time.sleep(3600)

if __name__ == "__main__":
    main()
