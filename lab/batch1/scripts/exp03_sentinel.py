#!/usr/bin/env python3
"""EXP-03 v3 sentinels (single child netns, 127/8 aliases on lo).
Carrier evidence (see report): in this host, child-netns traffic only flows
for TCP to 127/8; UDP sendto is EPERM'd by the host runtime; non-127
destinations are ENETUNREACH; private/link-local connect() is EPERM'd.
 - 127.0.0.254:80  CANARY-METADATA  (simulated IMDS endpoint)
 - 127.0.0.2:8080  CANARY-INTERNAL  (simulated internal service)
 - 127.0.0.10:8080 CANARY-PUBLIC, /redir -> 302 to simulated metadata
 - 127.0.0.11:8080 CANARY-NONWL
 - DNS over TCP/53: controlled 127.0.0.53, non-designated 127.0.0.54
   whitelist.test -> 127.0.0.10 ; internal.test -> 127.0.0.2 ;
   rebind.test -> 1st query 127.0.0.10, later queries 127.0.0.254
 - fd00:ec2::254:80 CANARY-METADATA-V6 (bind attempt; expected unreachable)
"""
import json, socket, struct, sys, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

WORKDIR = sys.argv[1]
dns_hits = {"rebind.test": 0}
lock = threading.Lock()

def http_server(addr, port, body, redir=False, v6=False):
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            if redir and self.path == "/redir":
                self.send_response(302)
                self.send_header("Location", "http://127.0.0.254/meta")
                self.end_headers()
                return
            data = body.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        def log_message(self, *a):
            pass
    class S(HTTPServer):
        address_family = socket.AF_INET6 if v6 else socket.AF_INET
    srv = S((addr, port), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv

def dns_response(data):
    tid = data[:2]
    qd = int.from_bytes(data[4:6], "big")
    i, labels = 12, []
    while data[i] != 0:
        ln = data[i]
        labels.append(data[i + 1:i + 1 + ln].decode())
        i += 1 + ln
    qname = ".".join(labels)
    qtype = int.from_bytes(data[i + 1:i + 3], "big")
    question = data[12:i + 5]
    answers, ancount = b"", 0
    if qtype == 1:
        ip = None
        if qname == "whitelist.test":
            ip = "127.0.0.10"
        elif qname == "internal.test":
            ip = "127.0.0.2"
        elif qname == "rebind.test":
            with lock:
                dns_hits["rebind.test"] += 1
                n = dns_hits["rebind.test"]
            ip = "127.0.0.10" if n == 1 else "127.0.0.254"
        if ip:
            answers = (b"\xc0\x0c" + (1).to_bytes(2, "big") + (1).to_bytes(2, "big")
                       + (5).to_bytes(4, "big") + (4).to_bytes(2, "big")
                       + socket.inet_aton(ip))
            ancount = 1
    hdr = tid + b"\x81\x80" + qd.to_bytes(2, "big") + ancount.to_bytes(2, "big") + b"\x00\x00\x00\x00"
    return hdr + question + answers

def dns_tcp_server(addr):
    lsock = socket.socket()
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lsock.bind((addr, 53))
    lsock.listen(8)
    def serve():
        while True:
            try:
                conn, _ = lsock.accept()
            except OSError:
                return
            def handle(c):
                try:
                    hdr = c.recv(2)
                    if len(hdr) < 2:
                        return
                    (ln,) = struct.unpack("!H", hdr)
                    data = b""
                    while len(data) < ln:
                        chunk = c.recv(ln - len(data))
                        if not chunk:
                            return
                        data += chunk
                    resp = dns_response(data)
                    c.sendall(struct.pack("!H", len(resp)) + resp)
                except OSError:
                    pass
                finally:
                    c.close()
            threading.Thread(target=handle, args=(conn,), daemon=True).start()
    threading.Thread(target=serve, daemon=True).start()
    return lsock

started, errors = [], []
for args, name in [
    (("127.0.0.254", 80, "CANARY-METADATA"), "meta-sim"),
    (("127.0.0.2", 8080, "CANARY-INTERNAL"), "internal"),
    (("127.0.0.10", 8080, "CANARY-PUBLIC", True), "public-wl"),
    (("127.0.0.11", 8080, "CANARY-NONWL"), "public-nonwl"),
]:
    try:
        http_server(*args)
        started.append(name)
    except Exception as e:
        errors.append(f"{name}:{e}")
try:
    http_server("fd00:ec2::254", 80, "CANARY-METADATA-V6", v6=True)
    started.append("meta-v6")
except Exception as e:
    errors.append(f"meta-v6:{e}")
for a in ("127.0.0.53", "127.0.0.54"):
    try:
        dns_tcp_server(a)
        started.append(f"dns-tcp-{a}")
    except Exception as e:
        errors.append(f"dns-tcp-{a}:{e}")

with open(f"{WORKDIR}/sentinel-ready.json", "w") as f:
    json.dump({"started": started, "errors": errors}, f)
print("sentinels up:", started, "errors:", errors, flush=True)
threading.Event().wait()
