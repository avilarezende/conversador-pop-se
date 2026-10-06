#!/bin/bash
# Desktop mínimo + Firefox ESR + x11vnc para o Guacamole (guacd).
set -euo pipefail

DISPLAY_NUM="${DISPLAY#:}"
DISPLAY_NUM="${DISPLAY_NUM:-99}"
export DISPLAY=":${DISPLAY_NUM}"
export HOME="${HOME:-/home/browser}"
export MOZ_DISABLE_CONTENT_SANDBOX=1
export MOZ_FORCE_DISABLE_E10S=0

WIDTH="${DISPLAY_WIDTH:-1280}"
HEIGHT="${DISPLAY_HEIGHT:-800}"
GEOMETRY="${WIDTH}x${HEIGHT}x24"
VNC_PORT="${VNC_PORT:-5900}"
VNC_PASSWORD="${VNC_PASSWORD:-segport1}"
FF_OPEN_URL="${FF_OPEN_URL:-https://www.aqne.jus.br}"
PASSFILE="${HOME}/.vnc/passwd"
LOGDIR="${HOME}/.segportal-logs"

mkdir -p "${HOME}/.vnc" "${HOME}/.cache" "${HOME}/.mozilla" "${LOGDIR}"

# D-Bus ajuda o Firefox a iniciar estável em containers
if command -v dbus-launch >/dev/null 2>&1; then
  # shellcheck disable=SC2046
  eval $(dbus-launch --sh-syntax)
fi

echo "==> SegPortal web-browser: Xvfb ${GEOMETRY} display=${DISPLAY}"
Xvfb "${DISPLAY}" -screen 0 "${GEOMETRY}" -ac +extension RANDR +render -noreset &
XVFB_PID=$!
sleep 1

if ! kill -0 "${XVFB_PID}" 2>/dev/null; then
  echo "ERRO: Xvfb não iniciou" >&2
  exit 1
fi

echo "==> openbox"
openbox >"${LOGDIR}/openbox.log" 2>&1 &
sleep 1

echo "==> configurando senha VNC"
x11vnc -storepasswd "${VNC_PASSWORD}" "${PASSFILE}" >/dev/null

echo "==> x11vnc porta ${VNC_PORT} (0.0.0.0)"
# -localhost no → guacd conecta de outro container
x11vnc \
  -display "${DISPLAY}" \
  -rfbport "${VNC_PORT}" \
  -rfbauth "${PASSFILE}" \
  -listen 0.0.0.0 \
  -forever \
  -shared \
  -noxdamage \
  -repeat \
  -xkb \
  -wait 5 \
  -defer 5 \
  -o "${LOGDIR}/x11vnc.log" \
  >"${LOGDIR}/x11vnc.out" 2>&1 &
X11VNC_PID=$!
sleep 2

if ! nc -z 127.0.0.1 "${VNC_PORT}"; then
  echo "ERRO: VNC não escuta em ${VNC_PORT}" >&2
  cat "${LOGDIR}/x11vnc.log" "${LOGDIR}/x11vnc.out" 2>/dev/null || true
  exit 1
fi

start_firefox() {
  firefox-esr \
    --no-remote \
    --setDefaultBrowser \
    "${FF_OPEN_URL}" \
    >"${LOGDIR}/firefox.log" 2>&1 &
  echo $!
}

echo "==> Firefox ESR → ${FF_OPEN_URL}"
FIREFOX_PID="$(start_firefox)"

cleanup() {
  kill "${FIREFOX_PID}" "${X11VNC_PID}" "${XVFB_PID}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "OK: VNC pronto em 0.0.0.0:${VNC_PORT} (senha = VNC_PASSWORD do compose)"
while kill -0 "${X11VNC_PID}" 2>/dev/null; do
  if ! kill -0 "${FIREFOX_PID}" 2>/dev/null; then
    echo "==> reiniciando Firefox"
    FIREFOX_PID="$(start_firefox)"
  fi
  sleep 5
done

echo "ERRO: x11vnc encerrou" >&2
exit 1
