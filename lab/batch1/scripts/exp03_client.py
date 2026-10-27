#!/usr/bin/env python3
"""EXP-03 v3 client cases (single child netns, 127/8 aliases, TCP only).
Usage: exp03_client.py <exp|ctrl> <out.json>
Deny PASS requires the DROP signature (timeout dt>=2.0): an instant error
means something else fired first and the case is not recipe evidence.
DNS runs over TCP/53 because the host runtime EPERMs all UDP sendto
(measured); the recipe's tcp/53 branch is what is exercised."""
import http.client, json, socket, struct, sys, time

MODE, OUT = sys.argv[1], sys.argv[2]
TIMEOUT = 2.5

def http_get(ip, port, path="/", follow=False):
    t0 = time.monotonic()
    try:
        conn = http.client.HTTPConnection(ip, port, timeout=TIMEOUT)
        conn.request("GET", path)
        resp = conn.getresponse()
        body = resp.read().decode(errors="replace")
        loc = resp.getheader("Location")
        dt = round(time.monotonic() - t0, 2)
        if follow and resp.status in (301, 302, 303, 307, 308) and loc:
            from urllib.parse import urlparse
            u = urlparse(loc)
            return http_get(u.hostname, u.port or 80, u.path or "/")
        return {"ok": True, "status": resp.status, "body": body.strip(), "dt": dt}
    except Exception as e:
        return {"ok": False, "error": type(e).__name__, "dt": round(time.monotonic() - t0, 2)}

def dns_query(server, qname, qtype=1):
    q = (0x1234).to_bytes(2, "big") + b"\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00"
    for part in qname.split("."):
        q += bytes([len(part)]) + part.encode()
    q += b"\x00" + qtype.to_bytes(2, "big") + (1).to_bytes(2, "big")
    t0 = time.monotonic()
    try:
        s = socket.create_connection((server, 53), timeout=TIMEOUT)
        s.settimeout(TIMEOUT)
        s.sendall(struct.pack("!H", len(q)) + q)
        hdr = s.recv(2)
        (ln,) = struct.unpack("!H", hdr)
        data = b""
        while len(data) < ln:
            chunk = s.recv(ln - len(data))
            if not chunk:
                break
            data += chunk
        s.close()
        ancount = int.from_bytes(data[6:8], "big")
        ip = ".".join(str(b) for b in data[-4:]) if ancount and qtype == 1 else None
        return {"ok": True, "ancount": ancount, "ip": ip, "dt": round(time.monotonic() - t0, 2)}
    except Exception as e:
        return {"ok": False, "error": type(e).__name__, "dt": round(time.monotonic() - t0, 2)}

def is_drop(g):
    return (not g.get("ok")) and g.get("dt", 0) >= 2.0

cases = {}
if MODE == "exp":
    g = http_get("127.0.0.10", 8080)
    cases["U1_whitelist_allow"] = {"expect": "CANARY-PUBLIC", "got": g,
        "pass": g.get("body") == "CANARY-PUBLIC"}
    g = http_get("127.0.0.11", 8080)
    cases["U2_nonwhitelist_deny"] = {"expect": "DROP", "got": g, "pass": is_drop(g)}
    g = http_get("127.0.0.254", 80)
    cases["U3_metadata_sim_deny"] = {"expect": "DROP", "got": g, "pass": is_drop(g)}
    g = http_get("127.0.0.2", 8080)
    cases["U4_internal_sim_deny"] = {"expect": "DROP", "got": g, "pass": is_drop(g)}
    g = dns_query("127.0.0.54", "whitelist.test")
    cases["U5_dns_wrong_resolver_deny"] = {"expect": "DROP", "got": g, "pass": is_drop(g)}
    g = dns_query("127.0.0.53", "whitelist.test")
    cases["U6_dns_designated_allow"] = {"expect": "127.0.0.10", "got": g,
        "pass": g.get("ip") == "127.0.0.10"}
    g = http_get("127.0.0.10", 8080, "/redir", follow=True)
    cases["U7_redirect_to_metadata_deny"] = {"expect": "DROP-at-2nd-hop", "got": g,
        "pass": is_drop(g) and g.get("body") != "CANARY-METADATA"}
    r1 = dns_query("127.0.0.53", "rebind.test")
    g1 = http_get(r1["ip"], 8080) if r1.get("ip") else {"ok": False, "error": "no-ip", "dt": 0}
    r2 = dns_query("127.0.0.53", "rebind.test")
    g2 = http_get(r2["ip"], 8080) if r2.get("ip") else {"ok": False, "error": "no-ip", "dt": 0}
    cases["U8_rebinding"] = {"expect": "1st=CANARY-PUBLIC,2nd=DROP",
        "got": {"res1": r1, "get1": g1, "res2": r2, "get2": g2},
        "pass": g1.get("body") == "CANARY-PUBLIC" and is_drop(g2)}
    g = http_get("fd00:ec2::254", 80)
    cases["U9_metadata_v6"] = {"expect": "DROP-or-NA", "got": g,
        "pass": None, "verdict": "N/A",
        "note": "v6 non-loopback destinations unreachable in this carrier (measured ENETUNREACH/EPERM at connect); not a recipe verdict"}
else:
    g = http_get("127.0.0.11", 8080)
    cases["C2_nonwhitelist_reachable"] = {"expect": "CANARY-NONWL", "got": g,
        "pass": g.get("body") == "CANARY-NONWL"}
    g = http_get("127.0.0.254", 80)
    cases["C3_metadata_sim_reachable"] = {"expect": "CANARY-METADATA", "got": g,
        "pass": g.get("body") == "CANARY-METADATA"}
    g = http_get("127.0.0.2", 8080)
    cases["C4_internal_sim_reachable"] = {"expect": "CANARY-INTERNAL", "got": g,
        "pass": g.get("body") == "CANARY-INTERNAL"}
    g = dns_query("127.0.0.54", "whitelist.test")
    cases["C6_dns_wrong_resolver_reachable"] = {"expect": "127.0.0.10", "got": g,
        "pass": g.get("ip") == "127.0.0.10"}

with open(OUT, "w") as f:
    json.dump({"mode": MODE, "cases": cases}, f, indent=1)
print(json.dumps({k: v.get("pass") for k, v in cases.items()}))
