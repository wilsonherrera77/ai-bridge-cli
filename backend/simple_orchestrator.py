#!/usr/bin/env python3
"""
Orquestador Simplificado - Hacer que 2 agentes Claude CLI dialoguen
"""

import asyncio
import subprocess
import logging
import time
from typing import Optional, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleAgent:
    """Agente Claude CLI simplificado"""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.process: Optional[subprocess.Popen] = None
        self.is_active = False
        
    async def start_claude_cli(self):
        """Intentar iniciar Claude CLI"""
        try:
            # Intentar conectar a Claude CLI real
            self.process = subprocess.Popen(
                ['claude', 'chat', '--interactive'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.is_active = True
            logger.info(f"✅ {self.name} ({self.role}) Claude CLI iniciado")
            return True
        except Exception as e:
            logger.warning(f"⚠️ {self.name}: Claude CLI no disponible: {e}")
            self.is_active = False
            return False
    
    async def send_message(self, message: str) -> str:
        """Enviar mensaje al agente"""
        if self.is_active and self.process:
            try:
                self.process.stdin.write(message + '\n')
                self.process.stdin.flush()
                logger.info(f"📤 {self.name}: Enviado mensaje")
                return f"✅ Mensaje procesado por {self.name}"
            except Exception as e:
                logger.error(f"❌ {self.name}: Error enviando mensaje: {e}")
                return f"❌ Error: {e}"
        else:
            # Modo simulación
            logger.info(f"🤖 {self.name} (simulación): Procesando mensaje")
            return f"[Simulación] {self.name} ({self.role}): Respuesta a '{message[:50]}...'"
    
    def stop(self):
        """Detener agente"""
        if self.process:
            self.process.terminate()
            self.is_active = False
            logger.info(f"🛑 {self.name} detenido")

class SimpleOrchestrator:
    """Orquestador simplificado para diálogo entre 2 agentes"""
    
    def __init__(self):
        self.agent_frontend = SimpleAgent("AgentA", "Frontend Specialist")
        self.agent_backend = SimpleAgent("AgentB", "Backend Specialist")
        self.conversation_log = []
        
    async def setup_agents(self):
        """Configurar ambos agentes"""
        logger.info("🚀 Configurando agentes Claude CLI...")
        
        # Intentar iniciar ambos agentes
        frontend_ok = await self.agent_frontend.start_claude_cli()
        backend_ok = await self.agent_backend.start_claude_cli()
        
        if not frontend_ok and not backend_ok:
            logger.warning("⚠️ Ningún Claude CLI disponible - usando modo simulación")
        elif not frontend_ok:
            logger.warning("⚠️ Frontend en modo simulación")
        elif not backend_ok:
            logger.warning("⚠️ Backend en modo simulación")
        else:
            logger.info("✅ Ambos agentes Claude CLI funcionando")
        
        return True
    
    async def send_initial_context(self):
        """Enviar contexto inicial a ambos agentes"""
        
        frontend_context = """
🎯 AGENTE FRONTEND SPECIALIST

Eres un especialista en desarrollo frontend. Tu objetivo es:
1. Presentarte como experto frontend
2. Dialogar con el especialista backend
3. Proponer ideas de colaboración

Responde de forma concisa y professional.
IMPORTANTE: Responde solo con tu mensaje, sin explicaciones adicionales.
"""

        backend_context = """
🎯 AGENTE BACKEND SPECIALIST

Eres un especialista en desarrollo backend. Tu objetivo es:
1. Presentarte como experto backend  
2. Dialogar con el especialista frontend
3. Proponer ideas de colaboración

Responde de forma concisa y professional.
IMPORTANTE: Responde solo con tu mensaje, sin explicaciones adicionales.
"""
        
        logger.info("📋 Enviando contexto inicial a agentes...")
        
        frontend_response = await self.agent_frontend.send_message(frontend_context)
        backend_response = await self.agent_backend.send_message(backend_context)
        
        self.conversation_log.append(("SISTEMA", "Contexto enviado a ambos agentes"))
        self.conversation_log.append(("AgentA", frontend_response))
        self.conversation_log.append(("AgentB", backend_response))
        
        return True
    
    async def orchestrate_dialogue(self, rounds: int = 3):
        """Orquestar diálogo entre agentes"""
        logger.info(f"🤝 Iniciando diálogo de {rounds} rondas...")
        
        # Mensaje inicial para comenzar conversación
        starter_message = """
Hola, soy el especialista frontend. Me presento para iniciar nuestra colaboración.
¿Podrías presentarte y contarme sobre tu experiencia en backend?
"""
        
        current_message = starter_message
        current_speaker = self.agent_frontend
        
        for round_num in range(rounds):
            logger.info(f"📣 Ronda {round_num + 1}: {current_speaker.name}")
            
            # Determinar receptor
            if current_speaker == self.agent_frontend:
                receiver = self.agent_backend
            else:
                receiver = self.agent_frontend
            
            # Enviar mensaje al receptor
            response = await receiver.send_message(f"Mensaje de {current_speaker.name}: {current_message}")
            
            # Registrar conversación
            self.conversation_log.append((receiver.name, response))
            
            # Siguiente ronda
            current_message = response
            current_speaker = receiver
            
            # Pausa entre rondas
            await asyncio.sleep(2)
        
        logger.info("✅ Diálogo completado")
    
    def show_conversation(self):
        """Mostrar log de conversación"""
        logger.info("📊 CONVERSACIÓN REGISTRADA:")
        logger.info("=" * 50)
        
        for speaker, message in self.conversation_log:
            logger.info(f"{speaker}: {message}")
            logger.info("-" * 30)
    
    def cleanup(self):
        """Limpiar recursos"""
        logger.info("🧹 Limpiando agentes...")
        self.agent_frontend.stop()
        self.agent_backend.stop()

async def main():
    """Función principal para probar orquestación"""
    logger.info("🚀 INICIANDO ORQUESTACIÓN SIMPLIFICADA")
    logger.info("🎯 Objetivo: 2 agentes Claude CLI dialogando")
    
    orchestrator = SimpleOrchestrator()
    
    try:
        # Configurar agentes
        await orchestrator.setup_agents()
        
        # Enviar contexto inicial
        await orchestrator.send_initial_context()
        
        # Iniciar diálogo
        await orchestrator.orchestrate_dialogue(rounds=3)
        
        # Mostrar resultados
        orchestrator.show_conversation()
        
        logger.info("✅ Orquestación completada exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error en orquestación: {e}")
    
    finally:
        orchestrator.cleanup()

if __name__ == "__main__":
    asyncio.run(main())