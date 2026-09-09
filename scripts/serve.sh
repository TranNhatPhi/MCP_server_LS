#!/usr/bin/env bash
# Chạy lsth-mcp và mở ra internet để thử với Claude Cowork.
#
#   ./scripts/serve.sh            # local + tunnel công khai
#   ./scripts/serve.sh --local    # chỉ local, không mở ra internet
#   ./scripts/serve.sh --stop     # dừng tất cả
#
# Claude gọi MCP server từ hạ tầng đám mây của Anthropic, KHÔNG phải từ máy này,
# nên muốn thử với Cowork thì bắt buộc phải có một URL HTTPS công khai.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PORT="${LSTH_HTTP_PORT:-8787}"
RUN_DIR="$ROOT/data/state"
PID_SERVER="$RUN_DIR/server.pid"
PID_TUNNEL="$RUN_DIR/tunnel.pid"
LOG_SERVER="$RUN_DIR/server.log"
LOG_TUNNEL="$RUN_DIR/tunnel.log"
URL_FILE="$RUN_DIR/public_url.txt"
TOKEN_FILE="$RUN_DIR/mcp_token.txt"

stop_all() {
  for f in "$PID_TUNNEL" "$PID_SERVER"; do
    [ -f "$f" ] && kill "$(cat "$f")" 2>/dev/null && echo "Đã dừng $(basename "$f" .pid)" || true
    rm -f "$f"
  done
  rm -f "$URL_FILE"
}

if [ "${1:-}" = "--stop" ]; then stop_all; exit 0; fi

mkdir -p "$RUN_DIR"
stop_all 2>/dev/null || true

PY="$ROOT/.venv/bin/python"
[ -x "$PY" ] || { echo "Chưa có .venv. Chạy: python3.13 -m venv .venv && .venv/bin/pip install -e ."; exit 1; }

# macOS hay gắn cờ hidden lên file .pth trong thư mục Desktop, khiến Python bỏ qua
# nó và không import được gói. Gỡ cờ, và vẫn đặt PYTHONPATH để chắc chắn.
find "$ROOT/.venv" -name "*.pth" -exec chflags nohidden {} \; 2>/dev/null || true
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"

# Nạp cấu hình kho object nếu có. LSTH_STORAGE=minio thì mọi tool đọc/ghi đi qua
# MinIO thay vì thư mục data/ trên đĩa.
if [ -f "$ROOT/.env" ]; then
  set -a; . "$ROOT/.env"; set +a
fi
if [ "${LSTH_STORAGE:-local}" = "minio" ]; then
  echo "Kho dữ liệu: MinIO tại ${LSTH_S3_ENDPOINT:-localhost:9000}"
  curl -sf "http://${LSTH_S3_ENDPOINT:-localhost:9000}/minio/health/live" >/dev/null \
    || { echo "MinIO chưa chạy. Bật: docker compose -f docker/docker-compose.yml up -d"; exit 1; }
else
  echo "Kho dữ liệu: thư mục data/ trên đĩa"
fi

# Token bảo vệ endpoint công khai. Giữ nguyên giữa các lần chạy để khỏi phải sửa
# lại cấu hình connector bên Cowork.
if [ ! -f "$TOKEN_FILE" ]; then
  "$PY" -c "import secrets; print(secrets.token_urlsafe(32))" > "$TOKEN_FILE"
  chmod 600 "$TOKEN_FILE"
fi
export LSTH_MCP_TOKEN="$(cat "$TOKEN_FILE")"

PUBLIC_HOST=""
if [ "${1:-}" != "--local" ]; then
  command -v cloudflared >/dev/null || { echo "Chưa có cloudflared. Cài: brew install cloudflared"; exit 1; }
  echo "Đang mở tunnel..."
  nohup cloudflared tunnel --url "http://127.0.0.1:$PORT" --no-autoupdate > "$LOG_TUNNEL" 2>&1 &
  echo $! > "$PID_TUNNEL"
  for _ in $(seq 1 30); do
    sleep 1
    URL="$(grep -aoE 'https://[a-z0-9-]+\.trycloudflare\.com' "$LOG_TUNNEL" | head -1 || true)"
    [ -n "$URL" ] && break
  done
  [ -n "${URL:-}" ] || { echo "Không lấy được URL tunnel. Xem $LOG_TUNNEL"; exit 1; }
  echo "$URL" > "$URL_FILE"
  PUBLIC_HOST="${URL#https://}"
  export LSTH_PUBLIC_HOST="$PUBLIC_HOST"
fi

nohup "$PY" -m lsth_mcp --transport http --host 127.0.0.1 --port "$PORT" \
  ${PUBLIC_HOST:+--public-host "$PUBLIC_HOST"} > "$LOG_SERVER" 2>&1 &
echo $! > "$PID_SERVER"
sleep 4

if ! curl -sf "http://127.0.0.1:$PORT/health" >/dev/null; then
  echo "Server chưa lên. Log:"; tail -20 "$LOG_SERVER"; exit 1
fi

echo
echo "=================================================================="
echo " lsth-mcp đang chạy"
echo "=================================================================="
TOK="$(cat "$TOKEN_FILE")"
echo " Local        http://127.0.0.1:$PORT/mcp/$TOK"
[ -n "$PUBLIC_HOST" ] && echo " Công khai    https://$PUBLIC_HOST/mcp/$TOK"
echo
echo " DÁN URL NÀY vào Cowork -> Customize -> Connectors -> + -> Add custom connector:"
echo
[ -n "$PUBLIC_HOST" ] && echo "   https://$PUBLIC_HOST/mcp/$TOK"
echo
echo " (Cowork chỉ nhận URL và OAuth, không nhập được header — nên token nằm"
echo "  trong đường dẫn. Coi URL này như mật khẩu, đừng dán vào chat chung.)"
echo
echo " Dừng lại:    ./scripts/serve.sh --stop"
echo " Log:         $LOG_SERVER"
echo "=================================================================="
