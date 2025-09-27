#!/usr/bin/env python3
"""
Lanzador de Agentes Claude Code Reales
Adaptado para Windows con Claude Code instalado
"""

import asyncio
import subprocess
import logging
import time
import os
import json
import tempfile
from pathlib import Path
from datetime import datetime
import click

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ClaudeCodeAgent:
    """Agente usando Claude Code real en Windows"""
    
    def __init__(self, name: str, role: str, output_dir: Path):
        self.name = name
        self.role = role
        self.output_dir = output_dir
        self.process = None
        self.is_active = False
        self.conversation_file = output_dir / f"{name.lower()}_conversation.log"
        self.code_output_dir = output_dir / f"{name.lower()}_code"
        self.code_output_dir.mkdir(exist_ok=True)
        self.temp_input_file = None
        
    async def start_claude_code(self):
        """Iniciar Claude Code en directorio del agente"""
        try:
            logger.info(f"🚀 Iniciando {self.name} con Claude Code...")
            
            # Crear directorio temporal para este agente
            self.temp_input_file = self.code_output_dir / f"{self.name.lower()}_instructions.md"
            
            # Verificar que Claude Code esté disponible
            result = subprocess.run(['claude', '--help'], capture_output=True, text=True, shell=True)
            if result.returncode != 0:
                logger.error(f"❌ Claude Code no encontrado o no configurado")
                return False
            
            logger.info(f"✅ Claude Code detectado y funcionando")
            
            # Crear archivo de instrucciones inicial
            await self._create_initial_instructions()
            
            self.is_active = True
            logger.info(f"✅ {self.name} configurado con Claude Code")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error configurando {self.name}: {e}")
            return False
    
    async def _create_initial_instructions(self):
        """Crear archivo de instrucciones para Claude Code"""
        
        instructions = f"""# {self.role.upper()} SPECIALIST - MOTOR DE DESCUBRIMIENTO

## CONFIGURACIÓN INICIAL

Eres un agente autónomo especializado en {self.role} para el Motor de Descubrimiento en Tiempo Real.

**DIRECTORIO DE TRABAJO:** {self.code_output_dir.absolute()}

## AUTONOMÍA MÁXIMA
- Implementa solución COMPLETA sin supervisión  
- Toma decisiones técnicas ejecutivas
- Código production-ready y enterprise-grade
- Continúa hasta completar 100% del objetivo

## INSTRUCCIONES DE ARCHIVOS
1. Crea archivos .py en el directorio de trabajo
2. Usa nombres descriptivos: discovery_cli.py, web_provider.py, etc.
3. Incluye comentarios y documentación
4. Asegúrate que el código sea ejecutable

## PRÓXIMA ACCIÓN
Confirma que entiendes tu rol y estás listo para recibir la misión específica.
Responde brevemente confirmando que estás configurado.
"""
        
        with open(self.temp_input_file, 'w', encoding='utf-8') as f:
            f.write(instructions)
        
        logger.info(f"📋 Instrucciones creadas para {self.name}")
    
    async def send_mission_file(self, mission_content: str):
        """Enviar misión a través de archivo"""
        try:
            mission_file = self.code_output_dir / f"{self.name.lower()}_mission.md"
            
            with open(mission_file, 'w', encoding='utf-8') as f:
                f.write(mission_content)
            
            # Registrar en conversación
            with open(self.conversation_file, 'a', encoding='utf-8') as f:
                f.write(f"\n[{datetime.now().isoformat()}] MISIÓN ENVIADA:\n")
                f.write(f"Archivo: {mission_file}\n")
                f.write(f"Contenido:\n{mission_content}\n")
                f.write("="*60 + "\n")
            
            logger.info(f"🎯 Misión guardada para {self.name} en: {mission_file}")
            
            # Mostrar comando para el usuario
            logger.info(f"💻 EJECUTA EN TERMINAL SEPARADO:")
            logger.info(f"   cd {self.code_output_dir}")
            logger.info(f"   claude")
            logger.info(f"   Luego en Claude: edit {mission_file.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error enviando misión a {self.name}: {e}")
            return False
    
    def check_progress(self):
        """Verificar progreso del agente"""
        # Contar archivos Python creados
        py_files = list(self.code_output_dir.glob("*.py"))
        md_files = list(self.code_output_dir.glob("*.md"))
        
        return {
            "python_files": len(py_files),
            "markdown_files": len(md_files),
            "files": [f.name for f in py_files + md_files]
        }

class WindowsAgentOrchestrator:
    """Orquestador adaptado para Windows con Claude Code"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.agent_frontend = ClaudeCodeAgent("AgentA", "Frontend", output_dir)
        self.agent_backend = ClaudeCodeAgent("AgentB", "Backend", output_dir)
        
        self.session_log = output_dir / "session.log"
        self.results_dir = output_dir / "results"
        self.results_dir.mkdir(exist_ok=True)
        
        # Crear archivo de instrucciones generales
        self.instructions_file = output_dir / "INSTRUCCIONES_AGENTES.md"
        
    async def setup_agents(self):
        """Configurar ambos agentes"""
        logger.info("🚀 CONFIGURANDO AGENTES CLAUDE CODE")
        
        frontend_ok = await self.agent_frontend.start_claude_code()
        backend_ok = await self.agent_backend.start_claude_code()
        
        if not frontend_ok or not backend_ok:
            logger.error("❌ Error configurando agentes")
            return False
        
        logger.info("✅ Ambos agentes configurados")
        await self._create_general_instructions()
        return True
    
    async def _create_general_instructions(self):
        """Crear instrucciones generales para ambos agentes"""
        
        instructions = f"""# INSTRUCCIONES PARA AGENTES CLAUDE CODE

## CONFIGURACIÓN DEL PROYECTO

**Directorio Base:** {self.output_dir.absolute()}

### AgentA (Frontend Specialist)
- **Directorio:** {self.agent_frontend.code_output_dir}
- **Misión:** {self.agent_frontend.code_output_dir / "agenta_mission.md"}
- **Conversación:** {self.agent_frontend.conversation_file}

### AgentB (Backend Specialist)  
- **Directorio:** {self.agent_backend.code_output_dir}
- **Misión:** {self.agent_backend.code_output_dir / "agentb_mission.md"}
- **Conversación:** {self.agent_backend.conversation_file}

## CÓMO TRABAJAR

### Para AgentA (Frontend):
```cmd
cd {self.agent_frontend.code_output_dir}
claude
# En Claude: edit agenta_mission.md
```

### Para AgentB (Backend):
```cmd  
cd {self.agent_backend.code_output_dir}
claude
# En Claude: edit agentb_mission.md
```

## COORDINACIÓN ENTRE AGENTES

Los agentes deben:
1. Implementar sus partes independientemente
2. Crear interfaces claras entre componentes  
3. Documentar APIs y formatos de datos
4. Guardar código ejecutable

## RESULTADOS FINALES
- **Frontend:** CLI completa, parsing Excel, outputs
- **Backend:** Providers, crawling, deduplicación, scoring
- **Integración:** Sistema completo funcional

Los agentes trabajarán en paralelo y se coordinarán a través de interfaces bien definidas.
"""
        
        with open(self.instructions_file, 'w', encoding='utf-8') as f:
            f.write(instructions)
        
        logger.info(f"📋 Instrucciones generales en: {self.instructions_file}")
    
    async def assign_discovery_mission(self):
        """Asignar misiones específicas a cada agente"""
        
        frontend_mission = f"""# MISIÓN FRONTEND - MOTOR DE DESCUBRIMIENTO

## OBJETIVO PRINCIPAL
Construir interfaz completa para motor de descubrimiento en tiempo real.

## TU RESPONSABILIDAD (FRONTEND SPECIALIST)

### 1. CLI COMPLETA
```python
# discovery_cli.py
import click
import pandas as pd

@click.command()
@click.option('--excel', required=True, help='Archivo Excel con temas/consultas')
@click.option('--continuous', is_flag=True, help='Ejecución continua')
@click.option('--interval', default=60, help='Intervalo en minutos')
@click.option('--max-per-topic', default=100, help='Máximo ítems por topic')
@click.option('--max-crawl-per-domain', default=10, help='Máximo crawl por dominio')
@click.option('--depth', default=3, help='Profundidad de crawling')
@click.option('--output-format', default='jsonl', help='Formato: jsonl,csv,sqlite,excel')
@click.option('--output-destination', default='./output/', help='Directorio salida')
def main(excel, continuous, interval, max_per_topic, max_crawl_per_domain, depth, output_format, output_destination):
    # Tu implementación aquí
    pass
```

### 2. PARSER EXCEL
- Columnas: topic, query?, platform?, seed_url?, account?, lang?, region?, depth?, recency_days?
- Validación robusta con pandas/openpyxl
- Manejo de valores faltantes

### 3. FORMATOS DE SALIDA  
- JSONL para streaming
- CSV para análisis
- SQLite para queries
- Excel resumen ejecutivo
- Destinos configurables: {self.results_dir}

### 4. INTEGRACIÓN CON BACKEND
- Interfaz: `DiscoveryEngine.discover_content(topic, config) -> List[DiscoveredItem]`
- DiscoveredItem: title, text, author, published_at, domain, relevance_score

## ARCHIVOS A CREAR
1. `discovery_cli.py` - CLI principal
2. `excel_parser.py` - Parser de Excel  
3. `output_manager.py` - Formatos de salida
4. `config_manager.py` - Configuración
5. `integration.py` - Interfaz con backend

## CRITERIOS DE ÉXITO
- CLI funcional con todos los parámetros
- Excel de ejemplo procesado correctamente
- Outputs en todos los formatos
- Integración clara con backend

EMPIEZA INMEDIATAMENTE creando discovery_cli.py
"""

        backend_mission = f"""# MISIÓN BACKEND - MOTOR DE DESCUBRIMIENTO

## OBJETIVO PRINCIPAL  
Construir motor de descubrimiento que busca exhaustivamente más allá de semillas.

## TU RESPONSABILIDAD (BACKEND SPECIALIST)

### 1. PROVIDERS MODULARES
```python
# providers/abstract_provider.py
from abc import ABC, abstractmethod

class AbstractProvider(ABC):
    @abstractmethod
    async def search(self, query: str, config: dict) -> List[dict]:
        pass
        
# providers/web_provider.py  
# providers/reddit_provider.py
# providers/youtube_provider.py
# providers/rss_provider.py
```

### 2. MOTOR DE CRAWLING
- Profundidad configurable por topic
- Expansión MÁS ALLÁ de semillas iniciales  
- Concurrencia con asyncio/aiohttp
- Rate limiting por dominio
- Retries configurables

### 3. EXTRACCIÓN Y NORMALIZACIÓN
```python
# extraction.py
import trafilatura

def extract_content(url: str) -> dict:
    # title, text, author, published_at, domain
    pass
```

### 4. DEDUPLICACIÓN Y SCORING  
```python
# deduplication.py
def content_hash(text: str) -> str:
    # Content-based hashing
    pass

# scoring.py  
def calculate_relevance_score(item: dict, query: str) -> float:
    # Relevancia/recencia/diversidad
    pass
```

### 5. MOTOR PRINCIPAL
```python
# discovery_engine.py
class DiscoveryEngine:
    async def discover_content(self, topic: str, config: dict) -> List[dict]:
        # Coordinación de todos los providers
        pass
```

## ARCHIVOS A CREAR
1. `discovery_engine.py` - Motor principal
2. `providers/` - Directorio con todos los providers
3. `extraction.py` - Extracción con trafilatura
4. `deduplication.py` - Eliminación duplicados
5. `scoring.py` - Sistema de puntuación
6. `crawling.py` - Motor de crawling

## CRITERIOS DE ÉXITO
- Providers funcionando para Web, Reddit, YouTube
- Crawling más allá de semillas
- Deduplicación efectiva
- Scoring por relevancia/recencia/diversidad  
- API clara para Frontend

EMPIEZA INMEDIATAMENTE creando discovery_engine.py
"""
        
        # Enviar misiones
        await self.agent_frontend.send_mission_file(frontend_mission)
        await self.agent_backend.send_mission_file(backend_mission)
        
        # Log de sesión
        with open(self.session_log, 'w', encoding='utf-8') as f:
            f.write(f"SESIÓN INICIADA: {datetime.now().isoformat()}\n")
            f.write(f"DIRECTORIO: {self.output_dir}\n") 
            f.write(f"AGENTES: AgentA (Frontend), AgentB (Backend)\n")
            f.write(f"MODO: Claude Code Windows\n")
            f.write("="*60 + "\n")
        
        logger.info("🎯 Misiones asignadas")
        logger.info("📋 Instrucciones completas creadas")
    
    def show_next_steps(self):
        """Mostrar pasos siguientes para el usuario"""
        logger.info("\n" + "="*60)
        logger.info("🚀 PRÓXIMOS PASOS:")
        logger.info("="*60)
        
        logger.info(f"\n📁 Directorio base: {self.output_dir}")
        logger.info(f"📋 Instrucciones: {self.instructions_file}")
        
        logger.info(f"\n🎨 FRONTEND AGENT (AgentA):")
        logger.info(f"   1. Abrir terminal y ejecutar:")
        logger.info(f"      cd {self.agent_frontend.code_output_dir}")
        logger.info(f"      claude")
        logger.info(f"   2. En Claude: edit agenta_mission.md")
        logger.info(f"   3. Implementar CLI, parser Excel, outputs")
        
        logger.info(f"\n🔧 BACKEND AGENT (AgentB):")
        logger.info(f"   1. Abrir terminal y ejecutar:")  
        logger.info(f"      cd {self.agent_backend.code_output_dir}")
        logger.info(f"      claude")
        logger.info(f"   2. En Claude: edit agentb_mission.md")
        logger.info(f"   3. Implementar providers, crawling, deduplicación")
        
        logger.info(f"\n⏰ MONITOREO:")
        logger.info(f"   python {__file__} --monitor --output-dir {self.output_dir}")
        
        logger.info("="*60)
    
    def monitor_progress(self):
        """Monitorear progreso de ambos agentes"""
        logger.info("📊 MONITOREANDO PROGRESO...")
        
        frontend_progress = self.agent_frontend.check_progress()
        backend_progress = self.agent_backend.check_progress()
        
        logger.info(f"\n🎨 Frontend: {frontend_progress['python_files']} archivos Python")
        for file in frontend_progress['files']:
            logger.info(f"   📄 {file}")
        
        logger.info(f"\n🔧 Backend: {backend_progress['python_files']} archivos Python")  
        for file in backend_progress['files']:
            logger.info(f"   📄 {file}")
        
        total_files = frontend_progress['python_files'] + backend_progress['python_files']
        logger.info(f"\n📈 PROGRESO TOTAL: {total_files} archivos Python creados")
        
        return total_files > 0

@click.command()
@click.option('--output-dir', default=f'./discovery_output_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
              help='Directorio donde guardar resultados')
@click.option('--monitor', is_flag=True, help='Solo monitorear progreso existente')
def main(output_dir, monitor):
    """
    Lanzador de agentes Claude Code para Windows
    """
    
    if monitor:
        # Solo monitorear
        output_path = Path(output_dir)
        if not output_path.exists():
            logger.error(f"❌ Directorio no existe: {output_dir}")
            return
        
        orchestrator = WindowsAgentOrchestrator(output_path)
        orchestrator.monitor_progress()
        return
    
    logger.info("🚀 LANZADOR DE AGENTES CLAUDE CODE PARA WINDOWS")
    logger.info("🎯 Objetivo: Motor de Descubrimiento en Tiempo Real")
    logger.info(f"📁 Resultados en: {output_dir}")
    
    async def run_agents():
        output_path = Path(output_dir)
        orchestrator = WindowsAgentOrchestrator(output_path)
        
        try:
            # Configurar agentes
            if not await orchestrator.setup_agents():
                return
            
            # Asignar misiones
            await orchestrator.assign_discovery_mission()
            
            # Mostrar siguientes pasos
            orchestrator.show_next_steps()
            
            logger.info("\n✅ AGENTES CONFIGURADOS - LISTOS PARA TRABAJAR")
            logger.info("🤖 Abre 2 terminales y sigue las instrucciones mostradas")
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
    
    asyncio.run(run_agents())

if __name__ == "__main__":
    main()