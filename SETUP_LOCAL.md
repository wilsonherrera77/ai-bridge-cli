# 🚀 AI-Bridge CLI - Setup Local

## Arquitectura del Sistema

```
AI-Bridge/
├── backend/              # FastAPI + Orquestación  
│   ├── main.py          # Servidor principal (puerto 8000)
│   ├── orchestrator.py  # Motor de coordinación de agentes
│   ├── agents.py        # AgentA (Frontend) + AgentB (Backend) 
│   ├── communication.py # MessageBus para inter-agente comms
│   └── simple_orchestrator.py  # Orquestador funcional
├── frontend/            # React + Vite (puerto 5000)
│   ├── src/             # Dashboard de monitoreo
│   └── package.json     # Frontend dependencies
└── discovery_engine/    # Motor de descubrimiento
    ├── discovery_cli.py # CLI principal
    └── discovery_input.xlsx # Ejemplo de entrada

```

## Cómo Correr Local

### 1. Backend (Terminal 1)
```bash
cd backend
python main.py --port=8000
# Servidor FastAPI corriendo en http://localhost:8000
```

### 2. Frontend (Terminal 2) 
```bash  
cd frontend
npm run dev
# React dashboard en http://localhost:5000
```

### 3. Agentes Autónomos (Terminal 3)
```bash
cd backend  
python simple_orchestrator.py
# 2 agentes Claude CLI dialogando
```

### 4. Motor Descubrimiento (Terminal 4)
```bash
cd discovery_engine
python discovery_cli.py --excel discovery_input.xlsx
# Motor procesando Excel y descubriendo contenido
```

## Flujo de Trabajo

1. **Agentes reciben objetivo** via orquestador
2. **AgentA (Frontend)** implementa CLI, parsing, outputs
3. **AgentB (Backend)** implementa providers, crawling, extraction  
4. **Coordinan entre ellos** autónomamente
5. **Producen solución completa** sin supervisión

## Para Claude CLI Real
```bash
npm install -g @anthropic-ai/claude-cli
claude auth # Configurar con tu API key
```