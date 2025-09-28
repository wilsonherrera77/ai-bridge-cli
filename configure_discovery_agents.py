#!/usr/bin/env python3
"""
Configurar agentes autónomos para motor de descubrimiento en tiempo real
Sistema de autonomía MÁXIMA - Los agentes persiguen el objetivo sin límites
"""

import requests
import json
import time
import sys
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BACKEND_URL = "http://localhost:8000"

def wait_for_backend():
    """Esperar que el backend esté disponible"""
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Backend está disponible")
                return True
        except requests.exceptions.RequestException:
            if attempt < max_attempts - 1:
                logger.info(f"⏳ Esperando backend... (intento {attempt + 1}/{max_attempts})")
                time.sleep(2)
            else:
                logger.error("❌ Backend no disponible después de esperar")
                return False
    return False

def start_orchestration():
    """Iniciar orquestación con objetivo del motor de descubrimiento"""
    
    discovery_objective = """
🎯 CONSTRUIR MOTOR DE DESCUBRIMIENTO EN TIEMPO REAL

OBJETIVO PRINCIPAL:
Crear un sistema avanzado que ingiera hojas Excel con temas/consultas, expanda búsquedas más allá de semillas, rastree con profundidad configurable, extraiga metadatos, canonice/deduplique y ejecute continuamente.

ESPECIFICACIONES TÉCNICAS:

📊 ENTRADA - HOJA EXCEL:
- Columnas: topic, query?, platform?, seed_url?, account?, lang?, region?, depth?, recency_days?
- Procesamiento robusto con validación y normalización

🔍 PROVIDERS MODULARES:
- Interfaz abstracta para enchufar nuevas fuentes
- Implementar: Búsqueda web general, RSS, Reddit, YouTube, X/Twitter
- Concurrencia configurable, retries, límites por dominio

🕷️ MOTOR DE CRAWLING:
- Profundidad configurable por topic
- Expansión más allá de semillas iniciales  
- Extraer: title, text, author, published_at, domain
- Sistema de normalización y limpieza de datos

🧹 CANONIZACIÓN Y DEDUPLICACIÓN:
- Algoritmos de similarity para evitar duplicados
- Persistencia entre rondas de ejecución
- Hash content-based + URL canonicalization

📊 SISTEMA DE SCORING:
- Relevancia (similarity con query/topic)
- Recencia (peso temporal configurable)
- Diversidad (evitar over-representation de dominios)

💻 CLI INTERFACE:
--excel [archivo]
--continuous [true/false]  
--interval [minutos]
--max-per-topic [número]
--max-crawl-per-domain [número]
--depth [niveles]
--output-format [jsonl/csv/sqlite/excel]
--output-destination [ruta]

📤 FORMATOS DE SALIDA:
- JSONL para streaming
- CSV para análisis 
- SQLite para queries
- Excel resumen ejecutivo
- Destinos configurables (local/remoto)

🔄 EJECUCIÓN CONTINUA:
- Scheduler configurable por intervalos
- Estado persistente entre ejecuciones
- Logs detallados y monitoreo

✅ CRITERIOS DE ACEPTACIÓN:
1. CLI funcional con todos los parámetros
2. Excel de ejemplo funcional 
3. Descubrimiento más allá de semillas
4. Cero duplicados entre rondas
5. Salidas estructuradas en todos los formatos
6. Logs claros y informativos
7. Pruebas para normalización/deduplicación/scoring

AUTONOMÍA: MÁXIMA
- Implementar solución COMPLETA y ROBUSTA
- Estándares enterprise-grade
- Código production-ready
- Documentación técnica exhaustiva
- Manejo de errores comprehensivo
"""

    config = {
        "autonomy_level": "MAX",  # AUTONOMÍA MÁXIMA
        "objective": discovery_objective,
        "workspace": "discovery_engine",
        "continuous_mode": True,
        "max_rounds": None,  # SIN LÍMITES
        "require_human_approval": False,
        "agents_config": {
            "frontend_cli": "claude",
            "backend_cli": "claude" 
        },
        "execution_mode": "autonomous",
        "completion_criteria": "objective_fully_achieved"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/orchestration/start",
            json=config,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            session_id = result.get('session_id')
            logger.info(f"🚀 ORQUESTACIÓN INICIADA - Sesión: {session_id}")
            logger.info("⚡ AUTONOMÍA MÁXIMA ACTIVADA")
            logger.info("🎯 Objetivo: Motor de Descubrimiento en Tiempo Real")
            logger.info("🤖 Los agentes trabajarán SIN LÍMITES hasta completar el objetivo")
            return session_id
        else:
            logger.error(f"❌ Error iniciando orquestación: {response.status_code}")
            logger.error(f"Respuesta: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error de conexión: {e}")
        return None

def monitor_session(session_id):
    """Monitorear progreso de la sesión"""
    logger.info(f"📊 Monitoreando sesión: {session_id}")
    
    while True:
        try:
            response = requests.get(f"{BACKEND_URL}/api/orchestration/status/{session_id}")
            
            if response.status_code == 200:
                status = response.json()
                state = status.get('state', 'unknown')
                phase = status.get('current_phase', 'unknown')
                
                logger.info(f"📈 Estado: {state} | Fase: {phase}")
                
                if state in ['completed', 'failed', 'cancelled']:
                    logger.info(f"🏁 Sesión terminada: {state}")
                    break
                    
            time.sleep(10)  # Check every 10 seconds
            
        except KeyboardInterrupt:
            logger.info("🛑 Monitoreo interrumpido por usuario")
            break
        except Exception as e:
            logger.error(f"❌ Error monitoreando: {e}")
            time.sleep(5)

def main():
    logger.info("🚀 INICIANDO SISTEMA DE AUTONOMÍA MÁXIMA")
    logger.info("🎯 Objetivo: Motor de Descubrimiento en Tiempo Real")
    
    # Esperar backend
    if not wait_for_backend():
        sys.exit(1)
    
    # Iniciar orquestación
    session_id = start_orchestration()
    if not session_id:
        sys.exit(1)
    
    # Monitorear progreso
    monitor_session(session_id)

if __name__ == "__main__":
    main()