#!/usr/bin/env python3
"""
Fix setup Windows - Crear estructura manualmente si hay problemas
"""

import os
import json
from pathlib import Path
from datetime import datetime

def create_structure_manually(base_dir: str):
    """Crear estructura manualmente"""
    
    print(f"🔧 CREANDO ESTRUCTURA MANUALMENTE EN: {base_dir}")
    
    base_path = Path(base_dir)
    base_path.mkdir(parents=True, exist_ok=True)
    
    # Crear directorios
    agent_a_dir = base_path / "AgentA_Frontend"
    agent_b_dir = base_path / "AgentB_Backend" 
    results_dir = base_path / "results"
    
    agent_a_dir.mkdir(exist_ok=True)
    agent_b_dir.mkdir(exist_ok=True)
    results_dir.mkdir(exist_ok=True)
    
    print(f"✅ Directorios creados:")
    print(f"   📁 {agent_a_dir}")
    print(f"   📁 {agent_b_dir}")
    print(f"   📁 {results_dir}")
    
    # Crear misión Frontend
    frontend_mission = """# AGENTE FRONTEND - MOTOR DE DESCUBRIMIENTO

## TU MISIÓN
Implementar CLI completa y sistema de outputs para motor de descubrimiento.

## ARCHIVOS A CREAR:

### 1. discovery_cli.py (PRINCIPAL)
```python
import click
import pandas as pd
import json
import asyncio
from pathlib import Path

@click.command()
@click.option('--excel', required=True, help='Archivo Excel con temas/consultas')
@click.option('--continuous', is_flag=True, help='Ejecución continua')
@click.option('--interval', default=60, help='Intervalo en minutos')
@click.option('--max-per-topic', default=100, help='Máximo ítems por topic')
@click.option('--output-format', default='jsonl', help='Formato: jsonl,csv,sqlite,excel')
@click.option('--output-destination', default='../results/', help='Directorio salida')
def main(excel, continuous, interval, max_per_topic, output_format, output_destination):
    \"\"\"Motor de Descubrimiento en Tiempo Real\"\"\"
    print(f"🚀 MOTOR DE DESCUBRIMIENTO INICIADO")
    print(f"📊 Excel: {excel}")
    print(f"📁 Salida: {output_destination}")
    print(f"🔄 Continuo: {continuous}")
    
    # Cargar Excel
    try:
        df = pd.read_excel(excel)
        print(f"✅ Excel cargado: {len(df)} topics")
        
        for _, row in df.iterrows():
            topic = row.get('topic', '')
            query = row.get('query', topic)
            print(f"🔍 Procesando: {topic}")
            
            # Aquí integrar con el backend
            # results = await backend_engine.discover_content(topic_config)
            
        print(f"✅ Procesamiento completado")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
```

### 2. excel_parser.py
```python
import pandas as pd
from typing import Dict, List, Any

class ExcelParser:
    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self.df = None
    
    def load_and_validate(self) -> bool:
        try:
            self.df = pd.read_excel(self.excel_path)
            
            if 'topic' not in self.df.columns:
                raise ValueError("Columna 'topic' es requerida")
            
            print(f"✅ Excel cargado: {len(self.df)} filas")
            return True
            
        except Exception as e:
            print(f"❌ Error cargando Excel: {e}")
            return False
    
    def get_topics(self) -> List[Dict[str, Any]]:
        if self.df is None:
            return []
        
        topics = []
        for _, row in self.df.iterrows():
            topic_config = {
                'topic': row.get('topic', ''),
                'query': row.get('query', ''),
                'platform': str(row.get('platform', 'web')).split(','),
                'depth': int(row.get('depth', 3)),
                'recency_days': int(row.get('recency_days', 30))
            }
            topics.append(topic_config)
        
        return topics
```

### 3. output_manager.py
```python
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

class OutputManager:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def save_jsonl(self, data: List[Dict], filename: str = "discovery_results.jsonl"):
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\\n')
        print(f"✅ JSONL guardado: {filepath}")
    
    def save_csv(self, data: List[Dict], filename: str = "discovery_results.csv"):
        if not data:
            return
        
        filepath = self.output_dir / filename
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False, encoding='utf-8')
        print(f"✅ CSV guardado: {filepath}")
```

## SIGUIENTE PASO:
1. Crea estos archivos en este directorio
2. Implementa discovery_cli.py completo
3. Integra con backend para datos reales
"""
    
    # Crear misión Backend
    backend_mission = """# AGENTE BACKEND - MOTOR DE DESCUBRIMIENTO

## TU MISIÓN
Implementar motor de crawling y providers para descubrimiento exhaustivo.

## ARCHIVOS A CREAR:

### 1. discovery_engine.py (PRINCIPAL)
```python
import asyncio
import aiohttp
from typing import List, Dict, Any

class DiscoveryEngine:
    def __init__(self):
        self.providers = {}
    
    async def discover_content(self, topic_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        print(f"🔍 Descubriendo: {topic_config['topic']}")
        
        # Simular resultados por ahora
        results = [
            {
                "title": f"Research on {topic_config['topic']}",
                "text": f"Latest findings about {topic_config['topic']} showing promising results...",
                "author": "Research Team",
                "published_at": "2024-09-27T10:30:00Z",
                "domain": "research.example.com",
                "relevance_score": 0.85,
                "source_type": "web",
                "url": f"https://example.com/{topic_config['topic'].lower()}"
            },
            {
                "title": f"{topic_config['topic']} Implementation Guide",
                "text": f"Comprehensive guide for implementing {topic_config['topic']} solutions...",
                "author": "Tech Expert",
                "published_at": "2024-09-27T09:15:00Z", 
                "domain": "tech.example.org",
                "relevance_score": 0.78,
                "source_type": "web",
                "url": f"https://tech.example.org/guides/{topic_config['topic'].lower()}"
            }
        ]
        
        print(f"✅ Encontrados: {len(results)} resultados")
        return results

if __name__ == "__main__":
    engine = DiscoveryEngine()
    test_config = {
        'topic': 'Inteligencia Artificial',
        'query': 'AI machine learning 2024',
        'platform': ['web'],
        'depth': 2
    }
    
    async def test():
        results = await engine.discover_content(test_config)
        for result in results:
            print(f"📄 {result['title']}")
    
    asyncio.run(test())
```

### 2. web_provider.py
```python
import aiohttp
import asyncio
from typing import List, Dict, Any

class WebProvider:
    def __init__(self):
        self.name = "web"
    
    async def search(self, query: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        print(f"🌐 WebProvider buscando: {query}")
        
        # Resultados simulados realistas
        results = [
            {
                "title": f"Advanced {query} Research 2024",
                "url": f"https://research.example.com/{query.replace(' ', '-').lower()}",
                "domain": "research.example.com",
                "snippet": f"Latest developments in {query} showing promising results...",
                "source_type": "web"
            }
        ]
        
        return results
```

## SIGUIENTE PASO:
1. Crea estos archivos en este directorio
2. Implementa discovery_engine.py completo
3. Agrega providers reales (Reddit, YouTube, etc.)
"""
    
    # Guardar misiones
    with open(agent_a_dir / "MISION_FRONTEND.md", 'w', encoding='utf-8') as f:
        f.write(frontend_mission)
    
    with open(agent_b_dir / "MISION_BACKEND.md", 'w', encoding='utf-8') as f:
        f.write(backend_mission)
    
    # Crear Excel de ejemplo simple (sin openpyxl)
    excel_data = [
        ["topic", "query", "platform", "depth", "recency_days"],
        ["Inteligencia Artificial", "AI machine learning 2024", "web,reddit", 3, 30],
        ["Blockchain Technology", "cryptocurrency DeFi blockchain", "web", 2, 15],
        ["Quantum Computing", "quantum computers qubits IBM", "web,youtube", 4, 60]
    ]
    
    # Guardar como CSV primero
    csv_path = base_path / "discovery_input_example.csv"
    with open(csv_path, 'w', encoding='utf-8') as f:
        for row in excel_data:
            f.write(','.join(str(x) for x in row) + '\n')
    
    print(f"✅ CSV ejemplo creado: {csv_path}")
    
    # Crear README
    readme_content = f"""# MOTOR DE DESCUBRIMIENTO - CONFIGURADO

## ESTRUCTURA CREADA:
```
{base_path.name}/
├── AgentA_Frontend/          # CLI, parsing, outputs
│   └── MISION_FRONTEND.md   # Tu misión completa
├── AgentB_Backend/           # Providers, crawling, scoring  
│   └── MISION_BACKEND.md    # Tu misión completa
├── results/                  # Resultados finales
└── discovery_input_example.csv  # Datos ejemplo
```

## PRÓXIMOS PASOS:

### Para AgentA (Frontend):
1. `cd {agent_a_dir}`
2. `claude`
3. En Claude: `edit MISION_FRONTEND.md`
4. Implementar discovery_cli.py siguiendo la misión

### Para AgentB (Backend):
1. `cd {agent_b_dir}`  
2. `claude`
3. En Claude: `edit MISION_BACKEND.md`
4. Implementar discovery_engine.py siguiendo la misión

## TEST RÁPIDO:
```cmd
cd {agent_a_dir}
python discovery_cli.py --excel ../discovery_input_example.csv --output-destination ../results/
```

¡ESTRUCTURA LISTA PARA TRABAJAR!
"""
    
    with open(base_path / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"\n✅ ESTRUCTURA COMPLETA CREADA:")
    print(f"📁 Base: {base_path}")
    print(f"🎨 Frontend: {agent_a_dir}")
    print(f"🔧 Backend: {agent_b_dir}")
    print(f"📊 Datos: {csv_path}")
    print(f"📖 README: {base_path / 'README.md'}")
    
    return {
        'base_dir': base_path,
        'agent_a_dir': agent_a_dir,
        'agent_b_dir': agent_b_dir,
        'csv_path': csv_path
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Uso: python fix_setup_windows.py <directorio_destino>")
        sys.exit(1)
    
    target_dir = sys.argv[1]
    create_structure_manually(target_dir)
    print("\n🚀 ¡LISTO PARA TRABAJAR CON LOS AGENTES!")