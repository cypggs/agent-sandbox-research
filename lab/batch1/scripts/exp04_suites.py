#!/usr/bin/env python3
"""EXP-04 suite workloads (run inside a fresh namespace unit).
ST-1 probe / ST-2 fixed compute / ST-4 file-intensive per 09 freeze v1.0.
Prints one JSON line with the success evidence."""
import hashlib, io, json, os, socket, sys, tarfile

def st1():
    print(json.dumps({"suite": "ST-1", "probe": "LABMINI-PROBE-OK",
                      "pid": os.getpid(), "hostname": socket.gethostname(),
                      "cgroup": open("/proc/self/cgroup").read().strip()}))
    return True

def st2_compute():
    h = b"labmini-st2-seed"
    for i in range(1_000_000):
        h = hashlib.sha256(h + i.to_bytes(4, "little")).digest()
    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)
    f = fib(25)
    out = hashlib.sha256(h + str(f).encode()).hexdigest()
    print(json.dumps({"suite": "ST-2", "fib25": f, "output_hash": out}))
    return True

def st4(workdir):
    os.makedirs(workdir, exist_ok=True)
    hashes = []
    for i in range(1000):
        content = (hashlib.sha256(f"st4-{i}".encode()).digest() * 128)[:4096]
        with open(os.path.join(workdir, f"f{i:04d}.bin"), "wb") as fh:
            fh.write(content)
    for i in range(1000):  # full read-back verify
        with open(os.path.join(workdir, f"f{i:04d}.bin"), "rb") as fh:
            hashes.append(hashlib.sha256(fh.read()).hexdigest())
    manifest = hashlib.sha256("".join(sorted(hashes)).encode()).hexdigest()
    tarpath = workdir.rstrip("/") + ".tar"
    with tarfile.open(tarpath, "w") as tar:
        for i in range(1000):
            tar.add(os.path.join(workdir, f"f{i:04d}.bin"), arcname=f"f{i:04d}.bin")
    back = []  # re-derive manifest from the tar itself
    with tarfile.open(tarpath) as tar:
        for m in tar.getmembers():
            back.append(hashlib.sha256(tar.extractfile(m).read()).hexdigest())
    manifest2 = hashlib.sha256("".join(sorted(back)).encode()).hexdigest()
    print(json.dumps({"suite": "ST-4", "files": len(back), "manifest": manifest,
                      "manifest_from_tar": manifest2, "match": manifest == manifest2}))
    return manifest == manifest2

if __name__ == "__main__":
    suite = sys.argv[1]
    if suite == "ST-1":
        ok = st1()
    elif suite == "ST-2":
        ok = st2_compute()
    elif suite == "ST-4":
        ok = st4(sys.argv[2])
    sys.exit(0 if ok else 1)
