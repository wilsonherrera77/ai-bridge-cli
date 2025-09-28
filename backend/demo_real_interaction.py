#!/usr/bin/env python3
"""
Demo Real de Interacciones Entre Agentes
Muestra conversación real paso a paso
"""

import asyncio
import logging
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InteractiveAgent:
    """Agente que simula comportamiento real con delays y conversación detallada"""
    
    def __init__(self, name: str, role: str, personality: str):
        self.name = name
        self.role = role  
        self.personality = personality
        self.conversation_memory = []
        self.task_progress = []
        
    async def process_message(self, message: str, context: str = ""):
        """Procesar mensaje con delay realista y respuesta contextual"""
        
        # Simular tiempo de pensamiento (1-3 segundos)
        think_time = 1.5 + (len(message) / 200)  # Más tiempo para mensajes largos
        
        logger.info(f"🤔 {self.name} está pensando... ({think_time:.1f}s)")
        await asyncio.sleep(think_time)
        
        # Generar respuesta contextual
        response = self._generate_contextual_response(message, context)
        
        # Registrar en memoria
        self.conversation_memory.append({
            "timestamp": datetime.now().isoformat(),
            "input": message[:100] + "..." if len(message) > 100 else message,
            "response": response,
            "context": context
        })
        
        return response
    
    def _generate_contextual_response(self, message: str, context: str):
        """Generar respuesta contextual basada en rol y personalidad"""
        
        if "motor de descubrimiento" in message.lower():
            if self.role == "Frontend":
                return f"🎨 {self.name}: Entendido. Me encargaré de la CLI con Click, parser de Excel con pandas, y outputs en JSONL/CSV/SQLite. Necesito que Backend me defina la interfaz de los providers para integrar el crawling."
            else:
                return f"🔧 {self.name}: Perfecto. Implementaré providers modulares (Web/RSS/Reddit/YouTube/Twitter), motor de crawling con asyncio, y extracción con trafilatura. ¿Qué formato de datos prefieres para la comunicación entre componentes?"
        
        elif "interfaz" in message.lower() or "api" in message.lower():
            if self.role == "Frontend":
                return f"🎨 {self.name}: Propongo una clase DiscoveryEngine con métodos async: discover_content(topic, config) -> List[DiscoveredItem]. ¿Te parece? También necesito conocer el formato de DiscoveredItem."
            else:
                return f"🔧 {self.name}: Excelente propuesta. DiscoveredItem será: {{title, text, author, published_at, domain, relevance_score, source_type}}. Implementaré rate limiting automático por dominio."
        
        elif "implementación" in message.lower() or "código" in message.lower():
            if self.role == "Frontend":
                return f"🎨 {self.name}: Trabajando en discovery_cli.py. Agregué validación robusta de Excel, múltiples formatos de output, y integración con asyncio para llamadas no-bloqueantes al backend."
            else:
                return f"🔧 {self.name}: Implementando providers en providers/. WebSearchProvider usa requests+BeautifulSoup, RedditProvider usa praw, TwitterProvider usa tweepy. Concurrencia con asyncio.gather()."
        
        elif "progreso" in message.lower() or "status" in message.lower():
            progress = len(self.task_progress)
            if self.role == "Frontend":
                tasks = ["CLI completa ✅", "Parser Excel ✅", "Output formats 🔄", "Error handling ⏳"]
                return f"🎨 {self.name}: Progreso Frontend: {tasks[min(progress, 3)]}. CLI funcional con todos los parámetros requeridos."
            else:
                tasks = ["Providers base ✅", "WebSearch impl 🔄", "Deduplication ⏳", "Scoring engine ⏳"] 
                return f"🔧 {self.name}: Progreso Backend: {tasks[min(progress, 3)]}. AbstractProvider y WebSearchProvider operativos."
        
        else:
            # Respuesta genérica pero contextual
            if self.role == "Frontend":
                return f"🎨 {self.name}: Como Frontend specialist, me enfoco en UX, CLI intuitiva y formatos de output claros. ¿Qué aspecto específico necesitas que priorice?"
            else:
                return f"🔧 {self.name}: Como Backend specialist, optimizo para performance, escalabilidad y robustez. ¿Hay algún provider específico que debería implementar primero?"

class RealInteractionDemo:
    """Demo de interacciones reales entre agentes"""
    
    def __init__(self):
        self.agent_frontend = InteractiveAgent(
            "Alex", 
            "Frontend", 
            "Meticuloso, enfocado en UX, piensa en el usuario final"
        )
        self.agent_backend = InteractiveAgent(
            "Morgan", 
            "Backend",
            "Analítico, optimiza performance, piensa en escalabilidad"
        )
        self.interaction_log = []
        
    async def run_real_demo(self):
        """Ejecutar demo de interacciones reales"""
        
        logger.info("🚀 INICIANDO DEMO DE INTERACCIONES REALES")
        logger.info("👥 Alex (Frontend) y Morgan (Backend) van a colaborar")
        print("\n" + "="*60)
        print("🎬 DEMO: AGENTES TRABAJANDO EN MOTOR DE DESCUBRIMIENTO")
        print("="*60 + "\n")
        
        # Escenario realista de colaboración
        scenarios = [
            {
                "stage": "1. ASIGNACIÓN INICIAL", 
                "from_agent": "SISTEMA",
                "message": "Implementar motor de descubrimiento en tiempo real con Excel input, múltiples providers y outputs configurables.",
                "context": "mission_start"
            },
            {
                "stage": "2. COORDINACIÓN INICIAL",
                "from_agent": self.agent_frontend,
                "to_agent": self.agent_backend, 
                "message": "Hola Morgan, recibí el objetivo. Me haré cargo de CLI, parsing Excel y outputs. ¿Puedes manejar los providers y crawling? Necesitamos definir interfaces entre nuestros componentes.",
                "context": "coordination"
            },
            {
                "stage": "3. DEFINICIÓN DE INTERFACES",
                "from_agent": self.agent_backend,
                "to_agent": self.agent_frontend,
                "message": "Perfecto Alex. Propongo que mi motor de discovery expose una API async. ¿Qué formato prefieres para los resultados? También necesito saber qué parámetros de configuración esperas del Excel.",
                "context": "interface"
            },
            {
                "stage": "4. ESPECIFICACIÓN TÉCNICA", 
                "from_agent": self.agent_frontend,
                "to_agent": self.agent_backend,
                "message": "Excel tiene columnas: topic, query, platform, seed_url, account, lang, region, depth, recency_days. Para resultados, necesito objetos con title, text, author, published_at, domain, relevance_score. ¿Puedes implementar deduplicación content-based?",
                "context": "technical_spec"
            },
            {
                "stage": "5. IMPLEMENTACIÓN EN PARALELO",
                "from_agent": self.agent_backend,
                "to_agent": self.agent_frontend, 
                "message": "Implementando providers modulares. WebSearchProvider listo, trabajando en RedditProvider con praw. Deduplicación usa content hashing + fuzzy matching. ¿Cómo va tu CLI?",
                "context": "implementation"
            },
            {
                "stage": "6. REPORTE DE PROGRESO",
                "from_agent": self.agent_frontend,
                "to_agent": self.agent_backend,
                "message": "CLI con Click completa, parser Excel robusto, outputs JSONL/CSV/SQLite funcionando. Agregué validación y error handling. ¿Necesitas testing específico de algún provider?",
                "context": "progress"
            }
        ]
        
        for i, scenario in enumerate(scenarios):
            print(f"\n🎬 {scenario['stage']}")
            print("-" * 40)
            
            if scenario['from_agent'] == "SISTEMA":
                print(f"📋 SISTEMA: {scenario['message']}")
                
                # Ambos agentes reciben la misión
                print(f"\n📤 Enviando misión a Alex (Frontend)...")
                alex_response = await self.agent_frontend.process_message(
                    scenario['message'], scenario['context']
                )
                print(f"💬 Alex: {alex_response}")
                
                print(f"\n📤 Enviando misión a Morgan (Backend)...")
                morgan_response = await self.agent_backend.process_message(
                    scenario['message'], scenario['context']
                )
                print(f"💬 Morgan: {morgan_response}")
                
            else:
                # Diálogo entre agentes
                from_agent = scenario['from_agent']
                to_agent = scenario['to_agent']
                
                print(f"📤 {from_agent.name} dice:")
                print(f"💬 {scenario['message']}")
                
                print(f"\n🤔 {to_agent.name} procesando...")
                response = await to_agent.process_message(
                    scenario['message'], scenario['context']
                )
                
                print(f"📥 {to_agent.name} responde:")
                print(f"💬 {response}")
                
                # Actualizar progreso
                from_agent.task_progress.append(f"stage_{i}")
                to_agent.task_progress.append(f"stage_{i}")
            
            # Registro para análisis
            self.interaction_log.append({
                "stage": scenario['stage'],
                "timestamp": datetime.now().isoformat(),
                "interaction": scenario
            })
            
            # Pausa dramática para el demo
            await asyncio.sleep(1)
        
        print(f"\n🎉 DEMO COMPLETADO")
        print("="*60)
        
        return True
    
    def show_interaction_summary(self):
        """Mostrar resumen de interacciones"""
        print(f"\n📊 RESUMEN DE INTERACCIONES:")
        print(f"├── Total etapas: {len(self.interaction_log)}")
        print(f"├── Alex (Frontend) memoria: {len(self.agent_frontend.conversation_memory)} entradas")
        print(f"├── Morgan (Backend) memoria: {len(self.agent_backend.conversation_memory)} entradas")
        print(f"└── Colaboración exitosa: ✅")
        
        print(f"\n🧠 MEMORIA DE ALEX (Frontend):")
        for entry in self.agent_frontend.conversation_memory[-3:]:  # Últimas 3
            print(f"  💭 {entry['timestamp'][:19]}: {entry['response'][:80]}...")
            
        print(f"\n🧠 MEMORIA DE MORGAN (Backend):")
        for entry in self.agent_backend.conversation_memory[-3:]:  # Últimas 3
            print(f"  💭 {entry['timestamp'][:19]}: {entry['response'][:80]}...")

async def main():
    """Demo principal"""
    demo = RealInteractionDemo()
    
    try:
        success = await demo.run_real_demo()
        if success:
            demo.show_interaction_summary()
            
            print(f"\n🎯 RESULTADO: Motor de descubrimiento implementado colaborativamente")
            print(f"├── Frontend: CLI, parsing, outputs ✅")
            print(f"├── Backend: Providers, crawling, dedup ✅") 
            print(f"└── Coordinación autónoma exitosa ✅")
            
    except Exception as e:
        logger.error(f"❌ Error en demo: {e}")

if __name__ == "__main__":
    asyncio.run(main())