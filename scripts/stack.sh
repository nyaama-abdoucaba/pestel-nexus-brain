#!/usr/bin/env bash
# Point d'entrée unique de la stack locale Pestel Nexus.
# Source de vérité : infra/services.yaml + ui/infra.py (statut/sondes).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
N8N_DIR="$(cd "$ROOT_DIR/../n8n" && pwd)"
PY="$ROOT_DIR/.venv/bin/python"
SHARED_NET="pestel_shared"

cd "$ROOT_DIR"

# ── Helpers ───────────────────────────────────────────────────────────────────
say() { printf '\033[1;36m[stack]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[stack]\033[0m %s\n' "$*" >&2; }

ensure_network() {
  if docker network inspect "$SHARED_NET" >/dev/null 2>&1; then
    say "réseau $SHARED_NET déjà présent"
  else
    say "création du réseau $SHARED_NET"
    docker network create "$SHARED_NET" >/dev/null
  fi
}

ensure_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    warn "commande docker introuvable — installe Docker Desktop puis relance"
    exit 1
  fi

  if docker info >/dev/null 2>&1; then
    say "Docker déjà en ligne"
    return
  fi

  if [[ "$(uname)" == "Darwin" ]] && command -v open >/dev/null 2>&1; then
    say "démarrage de Docker Desktop…"
    if ! open -a Docker; then
      warn "impossible de lancer Docker Desktop — ouvre l'application manuellement"
      exit 1
    fi

    say "attente du moteur Docker (60 s maximum)…"
    for _ in $(seq 1 60); do
      docker info >/dev/null 2>&1 && { say "Docker prêt"; return; }
      sleep 1
    done

    warn "Docker ne répond pas après 60 s — vérifie Docker Desktop puis relance"
    exit 1
  fi

  warn "moteur Docker indisponible — démarre Docker puis relance"
  exit 1
}

ensure_ollama() {
  if curl -sf -m 3 http://localhost:11434/api/version >/dev/null 2>&1; then
    say "Ollama natif déjà en ligne"
    return
  fi
  if [[ "$(uname)" == "Darwin" ]] && [[ -d /Applications/Ollama.app ]]; then
    say "démarrage d'Ollama (app macOS)…"
    open -a Ollama
    for _ in $(seq 1 15); do
      curl -sf -m 2 http://localhost:11434/api/version >/dev/null 2>&1 && { say "Ollama prêt"; return; }
      sleep 1
    done
    warn "Ollama ne répond pas après 15 s — vérifier l'app manuellement"
  else
    warn "Ollama introuvable (pas d'app macOS) — service natif à lancer manuellement"
  fi
}

# ── Commandes ─────────────────────────────────────────────────────────────────
cmd_status() {
  if [[ ! -x "$PY" ]]; then
    warn "venv absent ($PY). Lance d'abord : python3 -m venv .venv && .venv/bin/pip install -r requirements.txt -r ui/requirements.txt"
    exit 1
  fi
  "$PY" - <<'PYEOF'
import sys
sys.path.insert(0, "ui")
from infra import load_services, check_service

ICON = {"up": "🟢", "down": "🔴", "unknown": "⚪"}
print(f"{'':2} {'SERVICE':16} {'MODE':7} {'LATENCE':>8}  CIBLE")
print("-" * 60)
for s in load_services():
    r = check_service(s)
    lat = f"{r['latency_ms']} ms" if r["latency_ms"] is not None else "–"
    print(f"{ICON.get(r['status'],'⚪'):2} {s['name']:16} {s['runtime']:7} {lat:>8}  {r['detail']}")
PYEOF
}

cmd_start() {
  ensure_docker
  ensure_network
  ensure_ollama
  say "démarrage du stack DB (PostgreSQL + pgAdmin + brain-api)"
  # --build est obligatoire : brain-api est construit depuis ce dépôt. Sans lui,
  # `up -d` réutilise l'image déjà en cache et le conteneur fait tourner du code
  # périmé sans rien signaler. Les couches Docker sont cachées, donc un démarrage
  # sans changement de code reste rapide.
  docker compose --env-file .env -f docker-compose.db.yml up -d --build
  say "démarrage du stack n8n"
  ( cd "$N8N_DIR" && docker compose up -d )
  echo
  cmd_status
}

cmd_stop() {
  if ! command -v docker >/dev/null 2>&1; then
    say "commande docker introuvable — rien à arrêter"
  elif docker info >/dev/null 2>&1; then
    say "arrêt du stack n8n"
    ( cd "$N8N_DIR" && docker compose down )
    say "arrêt du stack DB (PostgreSQL + pgAdmin + brain-api)"
    docker compose --env-file .env -f docker-compose.db.yml down
  else
    say "moteur Docker déjà arrêté — pas de conteneur à arrêter"
  fi

  if [[ "$(uname)" == "Darwin" ]]; then
    if pgrep -qi "docker desktop" 2>/dev/null; then
      say "fermeture de Docker Desktop"
      osascript -e 'quit app "Docker"' >/dev/null 2>&1 \
        || warn "impossible de fermer Docker Desktop automatiquement — ferme-la depuis la barre de menu"
    else
      say "Docker Desktop déjà fermé"
    fi
  fi
}

cmd_update() {
  local stamp; stamp="$(date +%Y%m%d-%H%M)"
  ensure_docker
  if docker ps --format '{{.Names}}' | grep -qx n8n-postgres; then
    say "sauvegarde n8n -> $ROOT_DIR/../n8n-backup-$stamp.sql"
    docker exec n8n-postgres pg_dump -U n8n n8n > "$ROOT_DIR/../n8n-backup-$stamp.sql" || warn "dump échoué (on continue)"
  fi
  ensure_network
  say "pull images DB"
  docker compose --env-file .env -f docker-compose.db.yml pull
  say "pull images n8n"
  ( cd "$N8N_DIR" && docker compose pull )
  cmd_start
}

cmd_ui() {
  # Charge .env (DATABASE_URL, etc.) : Streamlit ne le fait pas tout seul.
  if [[ -f "$ROOT_DIR/.env" ]]; then
    say "chargement de .env"
    set -a; . "$ROOT_DIR/.env"; set +a
  else
    warn ".env introuvable — DATABASE_URL risque d'être absente"
  fi
  say "lancement Streamlit"
  exec "$ROOT_DIR/.venv/bin/streamlit" run ui/app.py
}

cmd_help() {
  cat <<EOF
Usage: ./scripts/stack.sh [commande]

  status   (défaut)  Sonde tous les services et affiche leur état.
  start              Démarre Docker Desktop si besoin, puis Ollama + db + n8n.
  stop               Arrête les conteneurs (db + n8n) et ferme Docker Desktop.
  update             Sauvegarde n8n, pull les images (db + n8n), puis start.
  ui                 Lance l'UI Streamlit en natif.
  help               Cette aide.
EOF
}

case "${1:-status}" in
  status) cmd_status ;;
  start)  cmd_start ;;
  stop)   cmd_stop ;;
  update) cmd_update ;;
  ui)     cmd_ui ;;
  help|-h|--help) cmd_help ;;
  *) warn "commande inconnue : $1"; cmd_help; exit 1 ;;
esac
