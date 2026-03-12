#!/usr/bin/env bash
# ── Hybrid Trading Bot — one-shot local setup ─────────────────────────────
set -e
echo ""
echo "═══════════════════════════════════════════"
echo "  Hybrid Trading Bot — Local Setup"
echo "═══════════════════════════════════════════"
echo ""

# Backend
echo "▶ Setting up backend..."
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

if [ ! -f .env ]; then
  cp .env.example .env
  echo "  ✅ Created backend/.env — add your API keys before running"
else
  echo "  ✅ backend/.env already exists"
fi
deactivate
cd ..

# Frontend
echo ""
echo "▶ Setting up frontend..."
cd frontend
npm install --silent

if [ ! -f .env ]; then
  cp .env.example .env
  echo "  ✅ Created frontend/.env"
fi
cd ..

echo ""
echo "═══════════════════════════════════════════"
echo "  Setup complete!"
echo ""
echo "  Start backend:   cd backend && source .venv/bin/activate && uvicorn app.main:app --reload"
echo "  Start frontend:  cd frontend && npm run dev"
echo ""
echo "  Then open: http://localhost:5173"
echo "═══════════════════════════════════════════"
echo ""
