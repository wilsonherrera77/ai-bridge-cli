#!/usr/bin/env python3
"""
INTELLIGENT ORCHESTRATOR - El cerebro que conecta los agentes
Procesa, analiza y orquesta la comunicacion inteligente entre terminales
"""

import os
import time
import json
import threading
from datetime import datetime
from pathlib import Path

class IntelligentOrchestrator:
    """Orquestador inteligente que conecta y dirige los agentes"""

    def __init__(self):
        self.communication_file = "agent_communication.txt"
        self.orchestrator_log = "orchestrator_decisions.txt"
        self.last_processed = 0
        self.running = True

        # Limpiar archivos previos
        for file in [self.communication_file, self.orchestrator_log]:
            if os.path.exists(file):
                os.remove(file)

        print("=" * 60)
        print("INTELLIGENT ORCHESTRATOR - INICIADO")
        print("Conectando agentes de forma inteligente...")
        print("SIN API KEYS - Solo logica local")
        print("=" * 60)

    def log_decision(self, decision):
        """Registra decisiones del orquestador"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        with open(self.orchestrator_log, "a") as f:
            f.write(f"{timestamp} - ORCHESTRATOR: {decision}\n")
        print(f"[ORCHESTRATOR] {decision}")

    def analyze_message(self, sender, message):
        """Analiza mensaje y determina respuesta inteligente"""
        message_lower = message.lower()

        # Detectar tipo de mensaje
        if any(word in message_lower for word in ["hola", "hello", "hi", "buenas"]):
            return "greeting"
        elif any(word in message_lower for word in ["necesito", "require", "need", "quiero"]):
            return "request"
        elif any(word in message_lower for word in ["api", "endpoint", "backend", "servidor"]):
            return "backend_task"
        elif any(word in message_lower for word in ["frontend", "react", "vue", "componente", "ui"]):
            return "frontend_task"
        elif any(word in message_lower for word in ["listo", "terminado", "completado", "done"]):
            return "completion"
        elif "?" in message:
            return "question"
        else:
            return "general"

    def generate_intelligent_response(self, message_type, sender, original_message):
        """Genera respuesta inteligente basada en el contexto"""

        if sender == "AGENT_A":  # Frontend pidiendo a Backend
            if message_type == "greeting":
                return "say Hola Agent A! Listo para trabajar en el backend"
            elif message_type == "request" or message_type == "backend_task":
                return "say Perfecto! Analizo los requerimientos y diseño la API"
            elif message_type == "question":
                return "say Déjame revisar y te confirmo los detalles técnicos"
            elif message_type == "completion":
                return "say Excelente! Ahora integro con el backend"
            else:
                return "say Entendido, procedo con la implementación backend"

        else:  # Backend respondiendo a Frontend
            if message_type == "greeting":
                return "say Hola Agent B! Empecemos con el frontend"
            elif message_type == "request" or message_type == "frontend_task":
                return "say Perfecto! Creo los componentes y la interfaz"
            elif message_type == "question":
                return "say Reviso la documentación y adapto el frontend"
            elif message_type == "completion":
                return "say Genial! Ahora conecto el frontend con tu API"
            else:
                return "say Entendido, continúo con el desarrollo frontend"

    def suggest_next_action(self, sender, message):
        """Sugiere próxima acción inteligente"""
        message_lower = message.lower()

        suggestions = []

        if "todo" in message_lower or "tarea" in message_lower:
            if sender == "AGENT_A":
                suggestions.append("work Crear componentes TodoList, TodoItem, AddTodo")
                suggestions.append("work Implementar estado con React hooks")
            else:
                suggestions.append("work Crear API endpoints GET/POST/PUT/DELETE /todos")
                suggestions.append("work Implementar validacion de datos")

        elif "api" in message_lower:
            if sender == "AGENT_A":
                suggestions.append("work Configurar cliente HTTP para consumir API")
                suggestions.append("work Implementar manejo de errores")
            else:
                suggestions.append("work Documentar endpoints con Swagger")
                suggestions.append("work Configurar CORS para frontend")

        elif "base" in message_lower or "datos" in message_lower:
            suggestions.append("work Diseñar esquema de base de datos")
            suggestions.append("work Implementar modelos de datos")

        return suggestions

    def process_communication(self):
        """Procesa comunicación y orquesta respuestas"""
        try:
            if not os.path.exists(self.communication_file):
                return

            with open(self.communication_file, "r") as f:
                lines = f.readlines()

            # Procesar solo mensajes nuevos
            new_messages = lines[self.last_processed:]
            self.last_processed = len(lines)

            for line in new_messages:
                if " - AGENT_" in line and ": " in line:
                    # Extraer información del mensaje
                    parts = line.strip().split(" - ", 1)
                    if len(parts) == 2:
                        timestamp = parts[0]
                        message_part = parts[1]

                        if ": " in message_part:
                            sender, message = message_part.split(": ", 1)

                            # Analizar mensaje
                            message_type = self.analyze_message(sender, message)

                            self.log_decision(f"Procesando {message_type} de {sender}: {message[:50]}...")

                            # Determinar agente receptor
                            recipient = "AGENT_B" if sender == "AGENT_A" else "AGENT_A"

                            # Generar respuesta inteligente
                            if not any(keyword in message.lower() for keyword in ["completé", "completed", "finished"]):
                                intelligent_response = self.generate_intelligent_response(message_type, sender, message)

                                # Escribir respuesta sugerida
                                suggestion_timestamp = datetime.now().strftime("%H:%M:%S")
                                with open(self.communication_file, "a") as f:
                                    f.write(f"{suggestion_timestamp} - ORCHESTRATOR_SUGGEST_{recipient}: {intelligent_response}\n")

                                self.log_decision(f"Sugiriendo a {recipient}: {intelligent_response}")

                                # Generar sugerencias de trabajo
                                work_suggestions = self.suggest_next_action(sender, message)
                                for suggestion in work_suggestions:
                                    with open(self.communication_file, "a") as f:
                                        f.write(f"{suggestion_timestamp} - ORCHESTRATOR_SUGGEST_{sender}: {suggestion}\n")
                                    self.log_decision(f"Sugiriendo trabajo a {sender}: {suggestion}")

        except Exception as e:
            self.log_decision(f"Error procesando: {e}")

    def monitor_and_orchestrate(self):
        """Monitorea continuamente y orquesta"""
        self.log_decision("Monitoreo inteligente iniciado")

        while self.running:
            try:
                self.process_communication()
                time.sleep(2)  # Revisar cada 2 segundos
            except KeyboardInterrupt:
                self.log_decision("Orquestación detenida por usuario")
                self.running = False
                break
            except Exception as e:
                self.log_decision(f"Error en monitoreo: {e}")
                time.sleep(5)

    def show_orchestrator_status(self):
        """Muestra estado del orquestador"""
        print("\n" + "=" * 50)
        print("ESTADO DEL ORCHESTRATOR")
        print("=" * 50)

        # Mostrar decisiones recientes
        try:
            with open(self.orchestrator_log, "r") as f:
                decisions = f.readlines()
                print("ÚLTIMAS DECISIONES:")
                for decision in decisions[-5:]:
                    print(f"  {decision.strip()}")
        except:
            print("No hay decisiones registradas")

        # Mostrar comunicación completa
        print("\nCOMUNICACIÓN COMPLETA:")
        try:
            with open(self.communication_file, "r") as f:
                messages = f.readlines()
                for msg in messages:
                    if "ORCHESTRATOR_SUGGEST" in msg:
                        print(f"  🤖 {msg.strip()}")
                    else:
                        print(f"  👤 {msg.strip()}")
        except:
            print("No hay comunicación registrada")

        print("=" * 50)

def main():
    print("INTELLIGENT ORCHESTRATOR")
    print("El cerebro que conecta tus agentes")
    print()
    print("Opciones:")
    print("1. Iniciar orquestación inteligente")
    print("2. Ver estado y decisiones")
    print("3. Solo mostrar comunicación")

    choice = input("\nSelecciona (1, 2, o 3): ").strip()

    orchestrator = IntelligentOrchestrator()

    if choice == "1":
        print("\n🤖 ORQUESTADOR INICIADO")
        print("Los agentes ahora tendrán comunicación inteligente!")
        print("Presiona Ctrl+C para detener")
        print("-" * 50)

        try:
            orchestrator.monitor_and_orchestrate()
        except KeyboardInterrupt:
            print("\n\nOrquestación finalizada")

    elif choice == "2":
        orchestrator.show_orchestrator_status()

    elif choice == "3":
        try:
            with open("agent_communication.txt", "r") as f:
                print("\n=== COMUNICACIÓN COMPLETA ===")
                print(f.read())
        except:
            print("No hay comunicación registrada")

    else:
        print("Iniciando orquestación por defecto...")
        orchestrator.monitor_and_orchestrate()

if __name__ == "__main__":
    main()