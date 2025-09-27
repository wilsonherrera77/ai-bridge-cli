#!/usr/bin/env python3
"""
Lanzador de Agentes Claude CLI Reales
Sistema para que 2 agentes Claude trabajen autónomamente en motor de descubrimiento
"""

import asyncio
import subprocess
import logging
import time
import os
import json
from pathlib import Path
from datetime import datetime
import click

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealClaudeAgent:
    """Agente Claude CLI real con comunicación bidireccional"""
    
    def __init__(self, name: str, role: str, output_dir: Path):
        self.name = name
        self.role = role
        self.output_dir = output_dir
        self.process: subprocess.Popen = None
        self.is_active = False
        self.conversation_file = output_dir / f"{name.lower()}_conversation.log"
        self.code_output_dir = output_dir / f"{name.lower()}_code"
        self.code_output_dir.mkdir(exist_ok=True)
        
    async def start_claude_cli(self):
        """Iniciar proceso Claude CLI real"""
        try:
            logger.info(f"🚀 Iniciando {self.name} con Claude CLI real...")
            
            # Verificar que Claude CLI esté disponible
            result = subprocess.run(['claude', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"❌ Claude CLI no encontrado. Instala con: npm install -g @anthropic-ai/claude-cli")
                return False
            
            logger.info(f"✅ Claude CLI detectado: {result.stdout.strip()}")
            
            # Iniciar Claude CLI interactivo
            self.process = subprocess.Popen(
                ['claude', 'chat', '--interactive'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.is_active = True
            logger.info(f"✅ {self.name} Claude CLI iniciado (PID: {self.process.pid})")
            
            # Enviar configuración inicial
            await self._send_initial_setup()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error iniciando {self.name}: {e}")
            return False
    
    async def _send_initial_setup(self):
        """Enviar configuración inicial al agente"""
        
        setup_message = f"""
🎯 AGENTE {self.role.upper()} SPECIALIST - CONFIGURACIÓN INICIAL

Eres un agente autónomo especializado en {self.role} para el Motor de Descubrimiento en Tiempo Real.

IMPORTANTE: Todos tus archivos de código deben guardarse en: {self.code_output_dir}

AUTONOMÍA: MÁXIMA
- Implementa solución COMPLETA sin supervisión
- Toma decisiones técnicas ejecutivas
- Código production-ready y enterprise-grade
- Continúa hasta completar 100% del objetivo

INSTRUCCIONES DE GUARDADO:
1. Crea archivos .py en {self.code_output_dir}/
2. Usa nombres descriptivos: discovery_cli.py, web_provider.py, etc.
3. Incluye comentarios y documentación
4. Asegúrate que el código sea ejecutable

Confirma que entiendes tu rol y el directorio de trabajo.
"""
        
        await self._send_message(setup_message)
    
    async def _send_message(self, message: str):
        """Enviar mensaje al agente Claude"""
        if self.is_active and self.process:
            try:
                self.process.stdin.write(message + '\n\n')
                self.process.stdin.flush()
                
                # Registrar en archivo de conversación
                with open(self.conversation_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n[{datetime.now().isoformat()}] ENVIADO:\n{message}\n{'='*60}\n")
                
                logger.info(f"📤 {self.name}: Mensaje enviado")
                
            except Exception as e:
                logger.error(f"❌ {self.name}: Error enviando mensaje: {e}")
    
    async def send_mission(self, mission: str):
        """Enviar misión específica al agente"""
        logger.info(f"🎯 Enviando misión a {self.name}...")
        await self._send_message(mission)
    
    async def read_output(self):
        """Leer output del agente (no bloqueante)"""
        if self.is_active and self.process:
            try:
                # Verificar si hay output disponible
                output = []
                while True:
                    line = self.process.stdout.readline()
                    if not line:
                        break
                    output.append(line.strip())
                    
                    # Registrar en archivo de conversación
                    with open(self.conversation_file, 'a', encoding='utf-8') as f:
                        f.write(f"[{datetime.now().isoformat()}] RECIBIDO: {line}")
                
                if output:
                    logger.info(f"📥 {self.name}: {len(output)} líneas recibidas")
                    
                return output
                
            except Exception as e:
                logger.error(f"❌ {self.name}: Error leyendo output: {e}")
                return []
    
    def stop(self):
        """Detener agente"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                logger.info(f"🛑 {self.name} detenido")
            except:
                self.process.kill()
                logger.info(f"🛑 {self.name} terminado forzosamente")
            finally:
                self.is_active = False

class RealAgentOrchestrator:
    """Orquestador para agentes Claude CLI reales"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.agent_frontend = RealClaudeAgent("AgentA", "Frontend", output_dir)
        self.agent_backend = RealClaudeAgent("AgentB", "Backend", output_dir)
        
        self.session_log = output_dir / "session.log"
        self.results_dir = output_dir / "results"
        self.results_dir.mkdir(exist_ok=True)
        
    async def setup_agents(self):
        """Configurar ambos agentes Claude CLI"""
        logger.info("🚀 CONFIGURANDO AGENTES CLAUDE CLI REALES")
        
        # Intentar iniciar ambos agentes
        frontend_ok = await self.agent_frontend.start_claude_cli()
        backend_ok = await self.agent_backend.start_claude_cli()
        
        if not frontend_ok or not backend_ok:
            logger.error("❌ No se pudieron iniciar los agentes Claude CLI")
            logger.info("💡 Asegúrate de tener Claude CLI instalado: npm install -g @anthropic-ai/claude-cli")
            logger.info("💡 Y autenticado: claude auth")
            return False
        
        logger.info("✅ Ambos agentes Claude CLI iniciados exitosamente")
        return True
    
    async def assign_discovery_mission(self):
        """Asignar misión específica del motor de descubrimiento"""
        
        frontend_mission = f"""
🎯 MISIÓN CRÍTICA: MOTOR DE DESCUBRIMIENTO - FRONTEND SPECIALIST

OBJETIVO PRINCIPAL:
Construir motor de descubrimiento en tiempo real que ingiera Excel con temas/consultas,
busque exhaustivamente, extraiga metadatos, deduplique y ejecute continuamente.

TU RESPONSABILIDAD ESPECÍFICA (FRONTEND):

1. CLI COMPLETA:
   - Usar Click para parámetros: --excel, --continuous, --interval, --max-per-topic, --max-crawl-per-domain, --depth
   - Validación robusta de Excel con columnas: topic, query?, platform?, seed_url?, account?, lang?, region?, depth?, recency_days?
   - Manejo de errores y help detallado

2. FORMATOS DE SALIDA CONFIGURABLES:
   - JSONL para streaming 
   - CSV para análisis
   - SQLite para queries
   - Excel resumen ejecutivo
   - Usuario configura destino: {self.results_dir}

3. PARSING Y VALIDACIÓN:
   - Parser robusto con pandas/openpyxl
   - Validación de columnas y datos
   - Configuración por filas del Excel

4. COORDINACIÓN CON BACKEND:
   - Define interfaz clara para recibir resultados de crawling
   - Especifica formato DiscoveredItem esperado
   - Integra con motor de backend

DIRECTORIO DE TRABAJO: {self.agent_frontend.code_output_dir}
RESULTADOS EN: {self.results_dir}

INSTRUCCIONES ESPECÍFICAS:
- Crea discovery_cli.py como archivo principal
- Implementa clases: ExcelParser, OutputManager, CLIInterface
- Código debe ser ejecutable directamente
- Incluye ejemplo de uso en comentarios

EMPIEZA INMEDIATAMENTE. Coordina con Backend para interfaces.
"""

        backend_mission = f"""
🎯 MISIÓN CRÍTICA: MOTOR DE DESCUBRIMIENTO - BACKEND SPECIALIST

OBJETIVO PRINCIPAL:
Construir motor de descubrimiento en tiempo real que ingiera Excel con temas/consultas,
busque exhaustivamente, extraiga metadatos, deduplique y ejecute continuamente.

TU RESPONSABILIDAD ESPECÍFICA (BACKEND):

1. PROVIDERS MODULARES:
   - AbstractProvider interface base
   - WebSearchProvider (requests + BeautifulSoup/trafilatura)
   - RSSProvider (feedparser)
   - RedditProvider (praw)
   - YouTubeProvider (youtube-dl/yt-dlp)
   - TwitterProvider (tweepy si es posible)

2. MOTOR DE CRAWLING:
   - Profundidad configurable por topic
   - Expansión MÁS ALLÁ de semillas iniciales
   - Concurrencia con asyncio/aiohttp
   - Rate limiting y retries por dominio
   - Límites configurables --max-crawl-per-domain

3. EXTRACCIÓN Y NORMALIZACIÓN:
   - Usar trafilatura para texto principal
   - Extraer metadatos: title, text, author, published_at, domain
   - Limpieza y normalización de datos
   - Manejo robusto de errores

4. DEDUPLICACIÓN Y SCORING:
   - Content-based hashing para duplicados
   - Fuzzy matching para similarity
   - Scoring por relevancia/recencia/diversidad
   - Persistencia entre rondas

5. COORDINACIÓN CON FRONTEND:
   - Define API clara: discover_content(topic, config) -> List[DiscoveredItem]
   - Formato DiscoveredItem: title, text, author, published_at, domain, relevance_score
   - Integración asyncio para no bloquear

DIRECTORIO DE TRABAJO: {self.agent_backend.code_output_dir}

INSTRUCCIONES ESPECÍFICAS:
- Crea discovery_engine.py como motor principal
- Implementa providers/ directory con cada provider
- Incluye deduplication.py y scoring.py
- Código debe ser importable por Frontend

EMPIEZA INMEDIATAMENTE. Coordina con Frontend para interfaces.
"""
        
        # Enviar misiones a ambos agentes
        await self.agent_frontend.send_mission(frontend_mission)
        await self.agent_backend.send_mission(backend_mission)
        
        # Log de sesión
        with open(self.session_log, 'w', encoding='utf-8') as f:
            f.write(f"SESIÓN INICIADA: {datetime.now().isoformat()}\n")
            f.write(f"DIRECTORIO DE SALIDA: {self.output_dir}\n")
            f.write(f"AGENTES: AgentA (Frontend), AgentB (Backend)\n")
            f.write(f"MISIÓN: Motor de Descubrimiento en Tiempo Real\n")
            f.write("="*60 + "\n")
        
        logger.info("🎯 Misiones asignadas a ambos agentes")
        logger.info("⚡ AUTONOMÍA MÁXIMA ACTIVADA")
        
    async def monitor_agents(self, duration_minutes: int = 30):
        """Monitorear agentes trabajando"""
        logger.info(f"📊 Monitoreando agentes por {duration_minutes} minutos...")
        logger.info(f"📁 Archivos se guardan en: {self.output_dir}")
        logger.info(f"💬 Conversaciones en: {self.agent_frontend.conversation_file} y {self.agent_backend.conversation_file}")
        logger.info(f"💻 Código en: {self.agent_frontend.code_output_dir} y {self.agent_backend.code_output_dir}")
        
        end_time = time.time() + (duration_minutes * 60)
        
        while time.time() < end_time:
            if not (self.agent_frontend.is_active and self.agent_backend.is_active):
                logger.warning("⚠️ Uno o ambos agentes se desconectaron")
                break
            
            # Leer outputs periódicamente
            frontend_output = await self.agent_frontend.read_output()
            backend_output = await self.agent_backend.read_output()
            
            if frontend_output:
                logger.info(f"📥 Frontend: Nueva actividad ({len(frontend_output)} líneas)")
            
            if backend_output:
                logger.info(f"📥 Backend: Nueva actividad ({len(backend_output)} líneas)")
            
            # Verificar archivos creados
            frontend_files = list(self.agent_frontend.code_output_dir.glob("*.py"))
            backend_files = list(self.agent_backend.code_output_dir.glob("*.py"))
            
            if frontend_files or backend_files:
                logger.info(f"📁 Archivos creados - Frontend: {len(frontend_files)}, Backend: {len(backend_files)}")
            
            await asyncio.sleep(30)  # Check every 30 seconds
        
        logger.info("⏰ Tiempo de monitoreo completado")
        
    def show_results_summary(self):
        """Mostrar resumen de resultados"""
        logger.info("📊 RESUMEN DE RESULTADOS:")
        logger.info("="*50)
        
        # Archivos creados por frontend
        frontend_files = list(self.agent_frontend.code_output_dir.glob("*"))
        logger.info(f"🎨 Frontend creó {len(frontend_files)} archivos:")
        for file in frontend_files:
            logger.info(f"  📄 {file.name}")
        
        # Archivos creados por backend
        backend_files = list(self.agent_backend.code_output_dir.glob("*"))
        logger.info(f"🔧 Backend creó {len(backend_files)} archivos:")
        for file in backend_files:
            logger.info(f"  📄 {file.name}")
        
        # Conversaciones
        if self.agent_frontend.conversation_file.exists():
            size = self.agent_frontend.conversation_file.stat().st_size
            logger.info(f"💬 Conversación Frontend: {size} bytes")
        
        if self.agent_backend.conversation_file.exists():
            size = self.agent_backend.conversation_file.stat().st_size
            logger.info(f"💬 Conversación Backend: {size} bytes")
        
        logger.info(f"📁 Todos los resultados en: {self.output_dir}")
        
    def cleanup(self):
        """Limpiar agentes"""
        logger.info("🧹 Limpiando agentes...")
        self.agent_frontend.stop()
        self.agent_backend.stop()

@click.command()
@click.option('--output-dir', default=f'./discovery_output_{datetime.now().strftime("%Y%m%d_%H%M%S")}', 
              help='Directorio donde guardar todos los resultados')
@click.option('--duration', default=30, help='Duración del monitoreo en minutos')
@click.option('--auto-start', is_flag=True, help='Iniciar automáticamente sin confirmación')
def main(output_dir, duration, auto_start):
    """
    Lanzar 2 agentes Claude CLI reales para implementar motor de descubrimiento
    """
    
    logger.info("🚀 LANZADOR DE AGENTES CLAUDE CLI REALES")
    logger.info("🎯 Objetivo: Motor de Descubrimiento en Tiempo Real")
    logger.info(f"📁 Resultados se guardarán en: {output_dir}")
    
    if not auto_start:
        response = input(f"\n¿Continuar con agentes Claude CLI reales? (y/N): ")
        if response.lower() != 'y':
            logger.info("❌ Operación cancelada")
            return
    
    async def run_real_agents():
        output_path = Path(output_dir)
        orchestrator = RealAgentOrchestrator(output_path)
        
        try:
            # Configurar agentes
            if not await orchestrator.setup_agents():
                return
            
            # Asignar misión
            await orchestrator.assign_discovery_mission()
            
            logger.info("🤖 AGENTES TRABAJANDO AUTÓNOMAMENTE")
            logger.info("🔄 Implementando motor de descubrimiento sin supervisión")
            logger.info(f"⏰ Monitoreo por {duration} minutos")
            logger.info("⏹️  Presiona Ctrl+C para detener antes")
            
            # Monitorear trabajo
            await orchestrator.monitor_agents(duration)
            
            # Mostrar resultados
            orchestrator.show_results_summary()
            
            logger.info("✅ AGENTES CLAUDE CLI COMPLETARON SU TRABAJO")
            
        except KeyboardInterrupt:
            logger.info("🛑 Detenido por usuario")
        except Exception as e:
            logger.error(f"❌ Error: {e}")
        finally:
            orchestrator.cleanup()
    
    asyncio.run(run_real_agents())

if __name__ == "__main__":
    main()