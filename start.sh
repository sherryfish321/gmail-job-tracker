#!/usr/bin/env bash
# ============================================================
# start.sh — Gmail JobTracker launcher
# Starts: FastAPI backend + React frontend (+ optional sync)
#
# Usage:
#   ./start.sh              # start backend + frontend
#   ./start.sh --sync       # sync first, then start both
#   ./start.sh --sync --after 2026/02/15 --max 50
#
# Press Ctrl+C to stop everything.
# ============================================================

set -e

# --------------------------------------------------
# Parse args: extract --sync and pass the rest to main.py
# --------------------------------------------------
DO_SYNC=false
SYNC_ARGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --sync)
            DO_SYNC=true
            shift
            ;;
        *)
            SYNC_ARGS+=("$1")
            shift
            ;;
    esac
done

# --------------------------------------------------
# Activate venv
# --------------------------------------------------
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "ERROR: venv not found. Run ./setup.sh first."
    exit 1
fi

echo "============================================================"
echo "  Gmail JobTracker — Starting"
echo "============================================================"
echo ""

# --------------------------------------------------
# Check Ollama (warn only, not blocking)
# --------------------------------------------------
if curl -s http://localhost:11434 > /dev/null 2>&1; then
    echo "[✔] Ollama is running"
else
    echo "[⚠] Ollama not detected at localhost:11434"
    echo "    AI Chat will be unavailable. Dashboard still works."
    echo "    To fix: run 'ollama serve' in another terminal."
    echo ""
fi

# --------------------------------------------------
# Optional: Sync (fetch + analyze)
# --------------------------------------------------
if [ "$DO_SYNC" = true ]; then
    echo "[Sync] Running fetch + analyze..."
    python main.py --sync "${SYNC_ARGS[@]}"
    echo ""
fi

# --------------------------------------------------
# Trap Ctrl+C to kill background processes
# --------------------------------------------------
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "Goodbye!"
    exit 0
}
trap cleanup SIGINT SIGTERM

# --------------------------------------------------
# Start backend (FastAPI)
# --------------------------------------------------
echo "[Starting] FastAPI backend → http://localhost:8000"
python main.py --serve &
BACKEND_PID=$!

# Wait a moment for backend to boot
sleep 2

# --------------------------------------------------
# Start frontend (Vite)
# --------------------------------------------------
if [ -d "frontend" ]; then
    echo "[Starting] React frontend → http://localhost:5173"
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
else
    echo "[⚠] frontend/ not found. Skipping frontend."
    FRONTEND_PID=0
fi

echo ""
echo "============================================================"
echo "  All services running!"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo "  Press Ctrl+C to stop everything"
echo "============================================================"

# --------------------------------------------------
# Wait for processes (keeps script alive for Ctrl+C)
# --------------------------------------------------
wait