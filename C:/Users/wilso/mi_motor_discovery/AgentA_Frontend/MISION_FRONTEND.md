# AGENTE FRONTEND - MOTOR DE DESCUBRIMIENTO

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
    """Motor de Descubrimiento en Tiempo Real"""
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
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
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
