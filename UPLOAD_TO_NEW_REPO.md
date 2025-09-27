# ARCHIVOS PARA SUBIR AL NUEVO REPOSITORIO

## ✅ SOLO ESTOS ARCHIVOS (Limpios y Funcionales):

### 📁 ROOT FILES:
- `requirements.txt` - Dependencias Python
- `start_ai_bridge.py` - Launcher local principal
- `README_LOCAL.md` - Instrucciones de instalación

### 🤖 BACKEND/ (Sistema AI-Bridge CLI):
- `backend/__init__.py`
- `backend/main.py` - Servidor principal
- `backend/agents.py` - AgentA/AgentB CLI
- `backend/orchestrator.py` - Orquestador
- `backend/communication.py` - MessageBus
- `backend/cli_orchestrator.py` - Coordinador CLI
- `backend/terminal_manager.py` - Gestor terminales
- `backend/process_communicator.py` - stdin/stdout
- `backend/terminal_monitor.py` - Monitor procesos
- `backend/workflow.py` - Engine workflows
- `backend/evidence_capture.py` - Sistema evidencia
- `backend/logging_config.py` - Configuración logs

### 🎮 FRONTEND/ (Cabina Control React):
- `frontend/package.json` - Dependencias Node.js
- `frontend/vite.config.js` - Configuración Vite
- `frontend/index.html` - HTML principal
- `frontend/src/App.jsx` - Aplicación principal
- `frontend/src/main.jsx` - Entry point
- `frontend/src/components/AgentPanel.jsx` - Panel agentes
- `frontend/src/components/ConversationView.jsx` - Vista conversaciones
- `frontend/src/components/LogViewer.jsx` - Visor logs
- `frontend/src/components/SystemMetrics.jsx` - Métricas sistema
- `frontend/src/hooks/useWebSocket.js` - Hook WebSocket
- Archivos CSS, config eslint, tailwind, etc.

## ❌ NO SUBIR:
- Directorios: `.cache`, `.pythonlibs`, `__pycache__`, `.git`
- Archivos: `.replit`, `.upm`, `.gitignore` (crear nuevo)

## 🎯 RESULTADO:
Repositorio limpio con SOLO el sistema AI-Bridge CLI funcional.