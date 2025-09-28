# AGENTE FRONTEND - MOTOR DE DESCUBRIMIENTO

## TU MISIÓN
Implementar CLI completa y sistema de outputs para motor de descubrimiento.

## ARCHIVOS A CREAR EN ESTE DIRECTORIO:

### 1. discovery_cli.py (Principal)
```python
#!/usr/bin/env python3
import click
import pandas as pd
import json
from pathlib import Path

@click.command()
@click.option('--excel', required=True, help='Archivo Excel con temas/consultas')
@click.option('--continuous', is_flag=True, help='Ejecución continua')
@click.option('--interval', default=60, help='Intervalo en minutos')
@click.option('--max-per-topic', default=100, help='Máximo ítems por topic')
@click.option('--max-crawl-per-domain', default=10, help='Máximo crawl por dominio')
@click.option('--depth', default=3, help='Profundidad de crawling')
@click.option('--output-format', default='jsonl', help='Formato: jsonl,csv,sqlite,excel')
@click.option('--output-destination', default='../results/', help='Directorio salida')
def main(excel, continuous, interval, max_per_topic, max_crawl_per_domain, depth, output_format, output_destination):
    """Motor de Descubrimiento en Tiempo Real"""
    print(f"🚀 Iniciando motor de descubrimiento...")
    print(f"📊 Excel: {excel}")
    print(f"📁 Salida: {output_destination}")
    
    # TODO: Implementar lógica completa
    
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
        """Cargar y validar Excel con columnas requeridas"""
        try:
            self.df = pd.read_excel(self.excel_path)
            
            # Columnas requeridas y opcionales
            required = ['topic']
            optional = ['query', 'platform', 'seed_url', 'account', 'lang', 'region', 'depth', 'recency_days']
            
            # Validar columna requerida
            if 'topic' not in self.df.columns:
                raise ValueError("Columna 'topic' es requerida")
            
            print(f"✅ Excel cargado: {len(self.df)} filas")
            return True
            
        except Exception as e:
            print(f"❌ Error cargando Excel: {e}")
            return False
    
    def get_topics(self) -> List[Dict[str, Any]]:
        """Obtener lista de topics configurados"""
        if self.df is None:
            return []
        
        topics = []
        for _, row in self.df.iterrows():
            topic_config = {
                'topic': row.get('topic', ''),
                'query': row.get('query', ''),
                'platform': str(row.get('platform', 'web')).split(','),
                'seed_url': row.get('seed_url', ''),
                'account': row.get('account', ''),
                'lang': str(row.get('lang', 'en')).split(','),
                'region': str(row.get('region', 'US')).split(','),
                'depth': int(row.get('depth', 3)),
                'recency_days': int(row.get('recency_days', 30))
            }
            topics.append(topic_config)
        
        return topics
```

### 3. output_manager.py
```python
import json
import csv
import sqlite3
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

class OutputManager:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def save_jsonl(self, data: List[Dict], filename: str = "discovery_results.jsonl"):
        """Guardar en formato JSONL"""
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        print(f"✅ JSONL guardado: {filepath}")
    
    def save_csv(self, data: List[Dict], filename: str = "discovery_results.csv"):
        """Guardar en formato CSV"""
        if not data:
            return
        
        filepath = self.output_dir / filename
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False, encoding='utf-8')
        print(f"✅ CSV guardado: {filepath}")
    
    def save_sqlite(self, data: List[Dict], filename: str = "discovery_results.db"):
        """Guardar en SQLite"""
        if not data:
            return
        
        filepath = self.output_dir / filename
        df = pd.DataFrame(data)
        
        conn = sqlite3.connect(filepath)
        df.to_sql('discovery_results', conn, if_exists='replace', index=False)
        conn.close()
        print(f"✅ SQLite guardado: {filepath}")
    
    def save_excel_summary(self, data: List[Dict], filename: str = "discovery_summary.xlsx"):
        """Guardar resumen en Excel"""
        if not data:
            return
        
        filepath = self.output_dir / filename
        df = pd.DataFrame(data)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Resultados', index=False)
            
            # Crear hoja de resumen
            summary = {
                'Métrica': ['Total Items', 'Dominios Únicos', 'Promedio Relevancia'],
                'Valor': [len(data), len(set(item.get('domain', '') for item in data)), 
                         sum(item.get('relevance_score', 0) for item in data) / len(data) if data else 0]
            }
            pd.DataFrame(summary).to_excel(writer, sheet_name='Resumen', index=False)
        
        print(f"✅ Excel resumen guardado: {filepath}")
```

## COORDINACIÓN CON BACKEND
El backend te proporcionará datos en este formato:
```python
DiscoveredItem = {
    "title": "Título del contenido",
    "text": "Texto principal extraído", 
    "author": "Autor del contenido",
    "published_at": "2024-09-27T10:30:00Z",
    "domain": "ejemplo.com",
    "relevance_score": 0.85,
    "source_type": "web|reddit|youtube|twitter",
    "url": "URL original"
}
```

## SIGUIENTE PASO
1. Implementa discovery_cli.py completo
2. Crea excel_parser.py funcional
3. Implementa output_manager.py
4. Integra con backend a través de discovery_engine.py
5. Prueba con Excel de ejemplo

IMPORTANTE: Todos los archivos deben ser ejecutables y production-ready.
