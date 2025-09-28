# MOTOR DE DESCUBRIMIENTO - AGENTES CLAUDE CODE

## ESTRUCTURA DEL PROYECTO
```
discovery_windows_test/
├── AgentA_Frontend/          # Agente Frontend
│   ├── MISION_FRONTEND.md   # Tu misión detallada
│   ├── discovery_cli.py     # CLI principal (crear)
│   ├── excel_parser.py      # Parser Excel (crear)
│   └── output_manager.py    # Formatos salida (crear)
├── AgentB_Backend/           # Agente Backend  
│   ├── MISION_BACKEND.md    # Tu misión detallada
│   ├── discovery_engine.py  # Motor principal (crear)
│   ├── providers/           # Directorio providers (crear)
│   ├── extraction.py        # Extracción contenido (crear)
│   ├── deduplication.py     # Eliminar duplicados (crear)
│   └── scoring.py           # Sistema puntuación (crear)
├── results/                  # Resultados finales
└── discovery_input_example.xlsx  # Excel ejemplo

```

## INSTRUCCIONES PARA TRABAJAR

### AgentA (Frontend):
1. Abre terminal en Windows
2. `cd /home/runner/workspace/discovery_windows_test/AgentA_Frontend`
3. `claude`
4. En Claude: `edit MISION_FRONTEND.md`
5. Implementa todos los archivos listados

### AgentB (Backend):
1. Abre terminal en Windows  
2. `cd /home/runner/workspace/discovery_windows_test/AgentB_Backend`
3. `claude`
4. En Claude: `edit MISION_BACKEND.md`
5. Implementa todos los archivos listados

## COORDINACIÓN
- Frontend consume API de Backend
- Backend expone: `await discovery_engine.discover_content(topic_config)`
- Formato datos: DiscoveredItem con title, text, author, published_at, domain, relevance_score

## OBJETIVO FINAL
CLI funcional que procese Excel y genere outputs en múltiples formatos con descubrimiento exhaustivo.

**AMBOS AGENTES DEBEN TRABAJAR EN PARALELO HASTA COMPLETAR SUS MISIONES.**
