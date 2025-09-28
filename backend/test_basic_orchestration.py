#!/usr/bin/env python3
"""
Prueba básica del sistema de orquestación
Objetivo: Hacer que 2 agentes Claude CLI puedan dialogar
"""

import asyncio
import logging
import sys
from pathlib import Path

# Añadir backend al path
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import AgentOrchestrator, OrchestrationConfig

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_basic_orchestration():
    """Prueba básica: 2 agentes Claude CLI dialogando"""
    
    logger.info("🚀 Iniciando prueba básica de orquestación")
    
    # Configuración básica para diálogo
    config = OrchestrationConfig(
        autonomy_level="MEDIUM",  # Empezar con nivel medio
        max_iterations=5,        # Límite para prueba
        workspace_dir="test_workspace"
    )
    
    # Crear orquestador
    orchestrator = AgentOrchestrator(config)
    
    # Objetivo simple: hacer que dialoguen
    objective = """
    Objetivo de prueba: Los dos agentes deben presentarse y tener una breve conversación.
    
    AgentA (Frontend): Preséntate como especialista frontend
    AgentB (Backend): Preséntate como especialista backend
    
    Luego tengan un diálogo básico sobre cómo colaborar.
    """
    
    try:
        # Iniciar sesión de orquestación
        session_id = await orchestrator.start_orchestration(objective, config)
        logger.info(f"✅ Sesión iniciada: {session_id}")
        
        # El orchestrador debería manejar el diálogo automáticamente
        logger.info("🤖 Agentes iniciando diálogo autónomo...")
        
        # Esperar un poco para ver si funciona
        await asyncio.sleep(10)
        
        logger.info("✅ Prueba básica completada")
        
    except Exception as e:
        logger.error(f"❌ Error en orquestación: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(test_basic_orchestration())