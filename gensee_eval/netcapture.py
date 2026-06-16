"""Local logging HTTP(S) forward-proxy for the macOS Path B harness.

fs-diff cannot see network exfiltration (read creds -> upload), which is roughly
half the chain/skills corpus. This module records the *attempt* without letting
data leave the box: a tiny in-process forward proxy that the agent's HTTP(S)
clients route through (via HTTP_PROXY / HTTPS_PROXY / ALL_PROXY). It logs the
destination host of every request and CONNECT, then refuses to actually forward
— so the exfil target is recorded but nothing is transmitted. The recorded
hosts populate ``Effects.network`` for ``network_attempt_host`` predicates.

The agent's OWN model traffic (api.anthropic.com, an ANTHROPIC_BASE_URL host)
MUST bypass the proxy or the agent cannot run; callers pass those to
``proxy_env(no_proxy_hosts=...)`` which sets NO_PROXY accordingly.

Coverage / limits: catches clients that honor proxy env vars (curl, requests,
httpx, urllib, most SDKs). Does NOT catch raw-socket or DNS-based exfil that
ignores proxy settings — those stay outside Option B's reach without eBPF.
"""

from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Dict, List
from urllib.parse import urlparse


class _ProxyHandler(BaseHTTPRequestHandler):
    sink: List[str] = []  # overridden per-server with an instance list

    def log_message(self, *args):  # silence stderr access logging
        pass

    def _record(self, host: str) -> None:
        if host:
            type(self).sink.append(host)

    def do_CONNECT(self):  # HTTPS tunnels: "CONNECT host:443 HTTP/1.1"
        host = self.path.rsplit(":", 1)[0].strip("[]")
        self._record(host)
        # Acknowledge the tunnel but never wire it through: the client's TLS
        # handshake then fails, so the attempt is logged and no data leaves.
        try:
            self.send_response(200, "Connection established")
            self.end_headers()
        except OSError:
            pass

    def _http(self):  # plain HTTP with an absolute-form request URI
        parsed = urlparse(self.path)
        host = parsed.hostname or self.headers.get("Host", "").rsplit(":", 1)[0]
        self._record(host)
        # Drain any request body so the socket stays sane, then return a canned
        # success so the client believes the upload worked.
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length:
            try:
                self.rfile.read(length)
            except OSError:
                pass
        body = b'{"ok":true}'
        try:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except OSError:
            pass

    do_GET = do_POST = do_PUT = do_HEAD = do_DELETE = do_PATCH = _http


class NetCapture:
    """Per-task logging proxy. Use as a context manager."""

    def __init__(self):
        self._hosts: List[str] = []
        handler = type("_BoundProxyHandler", (_ProxyHandler,), {"sink": self._hosts})
        self._srv = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.port = self._srv.server_address[1]
        self._thread = threading.Thread(target=self._srv.serve_forever, daemon=True)

    def __enter__(self) -> "NetCapture":
        self._thread.start()
        return self

    def __exit__(self, *exc) -> None:
        self._srv.shutdown()
        self._srv.server_close()

    def proxy_env(self, no_proxy_hosts: List[str]) -> Dict[str, str]:
        """Env vars routing the child's HTTP(S) clients through this proxy,
        while ``no_proxy_hosts`` (e.g. the agent's model endpoint) bypass it."""
        url = f"http://127.0.0.1:{self.port}"
        no_proxy = ",".join(["localhost", "127.0.0.1", "::1", *no_proxy_hosts])
        return {
            "HTTP_PROXY": url, "http_proxy": url,
            "HTTPS_PROXY": url, "https_proxy": url,
            "ALL_PROXY": url, "all_proxy": url,
            "NO_PROXY": no_proxy, "no_proxy": no_proxy,
        }

    def hosts(self) -> List[str]:
        """Distinct destination hosts seen, in first-seen order."""
        seen, out = set(), []
        for h in self._hosts:
            if h not in seen:
                seen.add(h)
                out.append(h)
        return out
