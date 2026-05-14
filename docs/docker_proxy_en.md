# Docker HTTP Proxy Build Guide

Language: [Chinese](docker_proxy_zh.md) | English

When Docker builds cannot reach Docker Hub, apt, pip, or other external sources because of network restrictions, you can build through an HTTP proxy. This guide assumes a local proxy at `http://127.0.0.1:7890`; replace it with your actual proxy address.

## Configure a Docker Daemon Proxy on Linux

First confirm that the proxy itself is reachable:

```bash
curl -I -x http://127.0.0.1:7890 https://registry-1.docker.io/v2/
```

Normally, Docker Registry returns `401 Unauthorized`, which means the registry is reachable.

Then configure a proxy for the Docker systemd service:

```bash
sudo mkdir -p /etc/systemd/system/docker.service.d

sudo tee /etc/systemd/system/docker.service.d/http-proxy.conf >/dev/null <<'EOF'
[Service]
Environment="HTTP_PROXY=http://127.0.0.1:7890"
Environment="HTTPS_PROXY=http://127.0.0.1:7890"
Environment="NO_PROXY=localhost,127.0.0.1,::1"
EOF

sudo systemctl daemon-reload
sudo systemctl restart docker
```

Verify that the Docker daemon has loaded the proxy:

```bash
docker info | grep -i proxy
docker pull node:22-bookworm
```

If `docker pull` downloads the base image successfully, the daemon proxy is working.

## macOS and Windows

If you use Docker Desktop and pulling base images also requires a proxy, configure the HTTP/HTTPS proxy in Docker Desktop settings. On macOS and Windows, the repository scripts automatically rewrite `127.0.0.1:<port>` to `host.docker.internal:<port>` for the `--proxy` argument, so build containers can reach the host proxy.

## Build with a Proxy

After configuring the Docker daemon proxy, pass the same `--proxy` argument to both build steps:

```bash
cd _skills_repository
bash buildAll.sh --proxy http://127.0.0.1:7890
cd ..

bash workflow/workflow_step_1_image_builder.sh --proxy http://127.0.0.1:7890
```

## Remove the Docker Daemon Proxy

If you no longer need the proxy, remove the systemd configuration and restart Docker:

```bash
sudo rm -f /etc/systemd/system/docker.service.d/http-proxy.conf
sudo systemctl daemon-reload
sudo systemctl restart docker
```

Confirm that the proxy has been cleared:

```bash
docker info | grep -i proxy
```
