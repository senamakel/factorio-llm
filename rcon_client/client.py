"""Minimal Factorio RCON client (pure stdlib, protocol per https://wiki.rcon.online)."""
import socket
import struct

SERVERDATA_AUTH = 3
SERVERDATA_AUTH_RESPONSE = 2
SERVERDATA_EXECCOMMAND = 2
SERVERDATA_RESPONSE_VALUE = 0


class RconError(Exception):
    pass


class RconClient:
    def __init__(self, host="127.0.0.1", port=27015, password="", timeout=5.0):
        self.host, self.port, self.password, self.timeout = host, port, password, timeout
        self.sock = None
        self._id = 0

    def _next_id(self):
        self._id += 1
        return self._id

    def connect(self):
        self.sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
        return self.authenticate()

    def _send(self, req_id, ptype, payload: bytes):
        body = struct.pack("<ii", req_id, ptype) + payload + b"\x00\x00"
        self.sock.sendall(struct.pack("<i", len(body)) + body)

    def _recv_exact(self, n):
        data = b""
        while len(data) < n:
            chunk = self.sock.recv(n - len(data))
            if not chunk:
                raise RconError("connection closed")
            data += chunk
        return data

    def _recv(self):
        (length,) = struct.unpack("<i", self._recv_exact(4))
        body = self._recv_exact(length)
        req_id, ptype = struct.unpack("<ii", body[:8])
        payload = body[8:-2]
        return req_id, ptype, payload

    def authenticate(self):
        rid = self._next_id()
        self._send(rid, SERVERDATA_AUTH, self.password.encode("utf-8"))
        # Factorio may send an empty RESPONSE_VALUE before AUTH_RESPONSE
        rid2, ptype, _ = self._recv()
        if ptype == SERVERDATA_RESPONSE_VALUE:
            rid2, ptype, _ = self._recv()
        if ptype != SERVERDATA_AUTH_RESPONSE or rid2 == -1:
            raise RconError("authentication failed")
        return True

    def command(self, cmd: str) -> str:
        rid = self._next_id()
        self._send(rid, SERVERDATA_EXECCOMMAND, cmd.encode("utf-8"))
        got_id, ptype, payload = self._recv()
        if ptype != SERVERDATA_RESPONSE_VALUE:
            raise RconError(f"unexpected packet type {ptype}")
        return payload.decode("utf-8", errors="replace")

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *a):
        self.close()
