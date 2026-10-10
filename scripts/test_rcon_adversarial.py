"""Adversarial RCON tests against an in-process fake server.

The fake mirrors the client's framing rules (payload = everything between
the 8-byte header and the trailing two NULs) rather than the spec's framing;
good enough to exercise transport edge cases, not a spec oracle.
"""
import socket
import struct
import threading
import time

from rcon_client.client import RconClient


def fake_server(host, port, expected_password, seen, stop):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen(5)
    srv.settimeout(0.2)
    while not stop.is_set():
        try:
            conn, _ = srv.accept()
        except socket.timeout:
            continue
        handle_connection(conn, expected_password, seen)
    srv.close()


def handle_connection(conn, expected_password, seen):
    def recv_exact(n):
        data = b""
        while len(data) < n:
            chunk = conn.recv(n - len(data))
            if not chunk:
                raise ConnectionError("closed")
            data += chunk
        return data

    try:
        while True:
            (length,) = struct.unpack("<i", recv_exact(4))
            body = recv_exact(length)
            req_id, ptype = struct.unpack("<ii", body[:8])
            payload = body[8:-2]
            if ptype == 3:  # AUTH
                reply_id = req_id if payload == expected_password else -1
                for rid, pt in [(0, 0), (reply_id, 2)]:
                    out = struct.pack("<ii", rid, pt) + b"\x00\x00"
                    conn.sendall(struct.pack("<i", len(out)) + out)
            elif ptype == 2:  # EXECCOMMAND
                seen.append(payload)
                reply = b"OK:" + payload
                out = struct.pack("<ii", req_id, 0) + reply + b"\x00\x00"
                conn.sendall(struct.pack("<i", len(out)) + out)
            else:
                break
    except (ConnectionError, OSError):
        pass
    finally:
        conn.close()


def start_server(password):
    seen = []
    stop = threading.Event()
    t = threading.Thread(target=fake_server, args=("127.0.0.1", 27998, password, seen, stop), daemon=True)
    t.start()
    time.sleep(0.2)
    return seen


# 1. happy path
seen = start_server(b"pw")
with RconClient("127.0.0.1", 27998, "pw") as c:
    out = c.command("/c game.print('hello')")
assert out == "OK:/c game.print('hello')", out
assert seen == [b"/c game.print('hello')"], seen
print("PASS: happy path, payload intact (header + 2 NULs stripped correctly)")

# 2. empty command
with RconClient("127.0.0.1", 27998, "pw") as c:
    out = c.command("")
assert out == "OK:", repr(out)
print("PASS: empty command")

# 3. unicode command (multi-byte utf-8)
cmd = "/c game.print('pl\u00e4tzen \u2699 \U0001f600')"
with RconClient("127.0.0.1", 27998, "pw") as c:
    out = c.command(cmd)
assert out == "OK:" + cmd, out
print("PASS: unicode command round-trips")

# 4. large command (10 KB)
cmd = "/c " + "x" * 10000
with RconClient("127.0.0.1", 27998, "pw") as c:
    out = c.command(cmd)
assert out == "OK:" + cmd and len(out) > 10000
print("PASS: 10KB command (recv loop coalesces fragments)")

# 5. sequential commands on one connection, ids must differ
with RconClient("127.0.0.1", 27998, "pw") as c:
    a = c.command("one")
    b = c.command("two")
assert a == "OK:one" and b == "OK:two", (a, b)
print("PASS: two sequential commands on one connection")

# 6. wrong password -> RconError('authentication failed')
try:
    RconClient("127.0.0.1", 27998, "wrong").connect()
    raise AssertionError("should have raised")
except Exception as e:
    assert "authentication failed" in str(e), e
    print("PASS: wrong password -> authentication failed")

# 7. connection refused -> error, not hang
try:
    RconClient("127.0.0.1", 27997, "pw", timeout=2).connect()
    raise AssertionError("should have raised")
except Exception as e:
    print("PASS: refused connection ->", type(e).__name__)

print("ALL RCON ADVERSARIAL TESTS PASS")
