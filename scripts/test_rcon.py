"""Test RconClient against an in-process fake RCON server."""
import socket
import struct
import threading

from rcon_client.client import RconClient


def fake_server(host, port, results):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen(1)
    results["ready"] = True
    conn, _ = srv.accept()

    def recv_exact(n):
        data = b""
        while len(data) < n:
            data += conn.recv(n - len(data))
        return data

    while True:
        header = recv_exact(4)
        (length,) = struct.unpack("<i", header)
        body = recv_exact(length)
        req_id, ptype = struct.unpack("<ii", body[:8])
        if ptype == 3:  # AUTH: empty RESPONSE_VALUE then AUTH_RESPONSE
            for rid, pt in [(0, 0), (req_id, 2)]:
                payload = struct.pack("<ii", rid, pt) + b"\x00\x00"
                conn.sendall(struct.pack("<i", len(payload)) + payload)
        elif ptype == 2:  # EXECCOMMAND: echo back
            text = body[8:-2].decode()
            reply = f"pong: {text}".encode()
            payload = struct.pack("<ii", req_id, 0) + reply + b"\x00\x00"
            conn.sendall(struct.pack("<i", len(payload)) + payload)
        else:
            break
    conn.close()
    srv.close()


results = {}
t = threading.Thread(target=fake_server, args=("127.0.0.1", 27999, results), daemon=True)
t.start()
import time
time.sleep(0.2)

with RconClient("127.0.0.1", 27999, "pw") as c:
    out = c.command("/c game.print('hello')")
print("RCON reply:", out)
assert out == "pong: /c game.print('hello')", out
print("PASS")
