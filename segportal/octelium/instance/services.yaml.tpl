# Serviços quando o Octelium é uma instância separada e o SegPortal
# permanece no Docker Compose do host. __UPSTREAM_HOST__ é o gateway
# que a VM enxerga (QEMU user-net: 10.0.2.2).
kind: Service
metadata:
  name: segportal
spec:
  mode: HTTP
  isPublic: true
  port: 443
  authorization:
    policies: ["allow-segportal-users"]
  config:
    upstream:
      url: http://__UPSTREAM_HOST__:8080
---
kind: Service
metadata:
  name: portal-auth
spec:
  mode: HTTP
  isPublic: true
  port: 443
  authorization:
    policies: ["allow-segportal-users"]
  config:
    upstream:
      url: http://__UPSTREAM_HOST__:8090
---
kind: Service
metadata:
  name: desktop-financeiro
spec:
  mode: TCP
  port: 3389
  authorization:
    policies: ["allow-segportal-users"]
  config:
    upstream:
      url: tcp://10.10.20.51:3389
---
kind: Service
metadata:
  name: desktop-admin
spec:
  mode: TCP
  port: 3389
  authorization:
    policies: ["allow-segportal-admins"]
  config:
    upstream:
      url: tcp://10.10.20.10:3389
---
kind: Service
metadata:
  name: jump-ssh
spec:
  mode: SSH
  port: 22
  authorization:
    policies: ["allow-segportal-admins"]
  config:
    upstream:
      url: ssh://10.10.20.10:22
    ssh:
      user: segportal
      upstreamHostKey:
        insecureIgnoreHostKey: true
