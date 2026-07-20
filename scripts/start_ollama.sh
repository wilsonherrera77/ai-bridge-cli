#!/bin/bash
# ============================================================
# Ollama Start Script - AI-Bridge CLI
# ============================================================
# systemd no está disponible en este entorno, así que este
# script arranca el servidor Ollama manualmente en segundo plano.
#
# Uso:
#   ./scripts/start_ollama.sh          # arranca el servidor
#   ./scripts/start_ollama.sh --status # verifica estado
# ============================================================

set -e

OLLAMA_HOST="${OLLAMA_HOST:-127.0.0.1:11434}"
LOG_FILE="${OLLAMA_LOG:-/tmp/ollama.log}"

check_status() {
  if curl -s "http://${OLLAMA_HOST}/api/version" >/dev/null 2>&1; then
    echo "✅ Ollama corriendo en ${OLLAMA_HOST}"
    echo "   Versión: $(curl -s http://${OLLAMA_HOST}/api/version)"
    echo ""
    echo "   Modelos instalados:"
    ollama list
    return 0
  else
    echo "❌ Ollama NO está corriendo"
    return 1
  fi
}

if [ "$1" = "--status" ]; then
  check_status
  exit $?
fi

# Verificar si ya está corriendo
if curl -s "http://${OLLAMA_HOST}/api/version" >/dev/null 2>&1; then
  echo "✅ Ollama ya está corriendo en ${OLLAMA_HOST}"
  exit 0
fi

echo ">>> Iniciando Ollama en ${OLLAMA_HOST}..."
OLLAMA_HOST="${OLLAMA_HOST}" nohup ollama serve > "${LOG_FILE}" 2>&1 &

# Esperar a que arranque
for i in $(seq 1 10); do
  if curl -s "http://${OLLAMA_HOST}/api/version" >/dev/null 2>&1; then
    echo "✅ Ollama listo en ${OLLAMA_HOST}"
    echo "   Log: ${LOG_FILE}"
    exit 0
  fi
  sleep 1
done

echo "⚠️  Ollama no respondió a tiempo. Revisa el log: ${LOG_FILE}"
exit 1
