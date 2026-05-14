# Docker HTTP 代理构建指南

语言: 中文 | [English](docker_proxy_en.md)

当 Docker 构建因为网络问题无法访问 Docker Hub、apt、pip 或其他外部源时，可以通过 HTTP 代理完成构建。本文假设本机代理地址为 `http://127.0.0.1:7890`，使用时请替换成你的实际代理地址。

## Linux 配置 Docker daemon 代理

先确认代理本身可用：

```bash
curl -I -x http://127.0.0.1:7890 https://registry-1.docker.io/v2/
```

正常情况下，Docker Registry 会返回 `401 Unauthorized`，这说明已经连通到 registry。

然后为 Docker systemd 服务配置代理：

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

验证 Docker daemon 已读取代理：

```bash
docker info | grep -i proxy
docker pull node:22-bookworm
```

如果 `docker pull` 能正常下载基础镜像，说明 daemon 代理已生效。

## macOS 和 Windows

如果使用 Docker Desktop，并且基础镜像拉取也需要代理，请在 Docker Desktop 的代理设置中配置 HTTP/HTTPS proxy。仓库脚本的 `--proxy` 参数会在 macOS/Windows 上自动把 `127.0.0.1:<port>` 改写为 `host.docker.internal:<port>`，让构建容器访问宿主机代理。

## 使用代理运行构建

配置好 Docker daemon 代理后，两个构建步骤都传入相同的 `--proxy` 参数：

```bash
cd _skills_repository
bash buildAll.sh --proxy http://127.0.0.1:7890
cd ..

bash workflow/workflow_step_1_image_builder.sh --proxy http://127.0.0.1:7890
```

## 取消 Docker daemon 代理

如果后续不再需要代理，可以删除 systemd 配置并重启 Docker：

```bash
sudo rm -f /etc/systemd/system/docker.service.d/http-proxy.conf
sudo systemctl daemon-reload
sudo systemctl restart docker
```

再次确认代理已清空：

```bash
docker info | grep -i proxy
```
