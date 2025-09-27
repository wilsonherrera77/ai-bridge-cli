#!/usr/bin/env python3
"""
ORCHESTRATED AGENTS - Agentes que se comunican a través del orquestador
Version final que implementa tu vision completa
"""

import os
import time
import sys
from datetime import datetime

class OrchestatedAgent:
    """Agente que se comunica através del orquestador inteligente"""

    def __init__(self, agent_id, role, specialization):
        self.agent_id = agent_id
        self.role = role
        self.specialization = specialization
        self.communication_file = "agent_communication.txt"
        self.last_read = 0

    def send_message(self, message):
        """Envía mensaje que será procesado por el orquestador"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        with open(self.communication_file, "a") as f:
            f.write(f"{timestamp} - {self.agent_id}: {message}\n")
        print(f"[Enviado]: {message}")

    def work_on_task(self, task):
        """Trabaja en una tarea específica"""
        print(f"[{self.agent_id}] 🔧 Trabajando en: {task}")
        print(f"[{self.agent_id}] ⚙️ Analizando requerimientos...")
        time.sleep(1)

        if self.agent_id == "AGENT_A":  # Frontend
            print(f"[{self.agent_id}] 🎨 Diseñando interfaz...")
            time.sleep(1)
            print(f"[{self.agent_id}] ⚛️ Implementando componentes React...")
            time.sleep(1)
            print(f"[{self.agent_id}] 🎯 Frontend completado!")
        else:  # Backend
            print(f"[{self.agent_id}] 🗄️ Diseñando arquitectura...")
            time.sleep(1)
            print(f"[{self.agent_id}] 🔗 Creando endpoints API...")
            time.sleep(1)
            print(f"[{self.agent_id}] ✅ Backend completado!")

        # Notificar completación
        completion_msg = f"Completé tarea: {task}"
        self.send_message(completion_msg)

    def check_orchestrator_suggestions(self):
        """Revisa sugerencias del orquestador"""
        try:
            if not os.path.exists(self.communication_file):
                return

            with open(self.communication_file, "r") as f:
                lines = f.readlines()

            new_lines = lines[self.last_read:]
            self.last_read = len(lines)

            suggestions = []
            responses = []

            for line in new_lines:
                if f"ORCHESTRATOR_SUGGEST_{self.agent_id}" in line:
                    # Sugerencia de trabajo para este agente
                    if ": work " in line:
                        task = line.split(": work ", 1)[1].strip()
                        suggestions.append(("work", task))
                    elif ": say " in line:
                        message = line.split(": say ", 1)[1].strip()
                        suggestions.append(("say", message))

                elif "ORCHESTRATOR_SUGGEST_" in line and self.agent_id not in line:
                    # Respuesta sugerida del otro agente
                    if ": say " in line:
                        message = line.split(": say ", 1)[1].strip()
                        responses.append(message)

            # Mostrar sugerencias del orquestador
            if suggestions:
                print(f"\n🤖 SUGERENCIAS DEL ORQUESTADOR:")
                for i, (action, content) in enumerate(suggestions, 1):
                    if action == "work":
                        print(f"  {i}. Trabajar en: {content}")
                    else:
                        print(f"  {i}. Decir: {content}")

            # Mostrar respuestas del otro agente
            if responses:
                print(f"\n💬 RESPUESTAS DEL OTRO AGENTE:")
                for response in responses:
                    print(f"  • {response}")

            return suggestions

        except Exception as e:
            print(f"Error leyendo sugerencias: {e}")
            return []

    def auto_accept_suggestion(self, suggestions):
        """Auto-acepta la primera sugerencia inteligente"""
        if suggestions:
            action, content = suggestions[0]
            print(f"\n🚀 Auto-ejecutando sugerencia del orquestador...")

            if action == "work":
                self.work_on_task(content)
            elif action == "say":
                self.send_message(content)

            return True
        return False

    def run_agent(self, auto_mode=False):
        """Ejecuta el agente con interfaz interactiva"""
        print("=" * 60)
        print(f"{self.agent_id} - {self.role}")
        print("=" * 60)
        print(f"Especialista en: {self.specialization}")
        print("CONECTADO AL ORQUESTADOR INTELIGENTE")
        print("SIN API KEYS - Solo comunicación orquestada")
        print("=" * 60)
        print()
        print("COMANDOS MEJORADOS:")
        print("1. say [mensaje] - Enviar mensaje (será procesado por orquestador)")
        print("2. work [tarea] - Trabajar en tarea específica")
        print("3. check - Ver sugerencias del orquestador")
        print("4. auto - Ejecutar próxima sugerencia automáticamente")
        print("5. status - Ver estado")
        print("6. quit - Salir")
        print()

        if auto_mode:
            print("🤖 MODO AUTOMÁTICO ACTIVADO")
            print("El agente seguirá las sugerencias del orquestador automáticamente")
            print("-" * 50)

        while True:
            try:
                if auto_mode:
                    # Modo automático: revisar y ejecutar sugerencias
                    suggestions = self.check_orchestrator_suggestions()
                    if suggestions:
                        if self.auto_accept_suggestion(suggestions):
                            time.sleep(3)  # Pausa antes de la próxima acción
                    time.sleep(2)  # Revisar cada 2 segundos
                else:
                    # Modo manual
                    cmd = input(f"{self.agent_id}> ").strip()

                    if cmd.startswith("say "):
                        message = cmd[4:]
                        self.send_message(message)

                    elif cmd.startswith("work "):
                        task = cmd[5:]
                        self.work_on_task(task)

                    elif cmd == "check":
                        suggestions = self.check_orchestrator_suggestions()
                        if not suggestions:
                            print("No hay sugerencias nuevas del orquestrador")

                    elif cmd == "auto":
                        suggestions = self.check_orchestrator_suggestions()
                        if suggestions:
                            self.auto_accept_suggestion(suggestions)
                        else:
                            print("No hay sugerencias para ejecutar")

                    elif cmd == "status":
                        print(f"[{self.agent_id}] Estado: Activo y conectado al orquestador")
                        print(f"[{self.agent_id}] Rol: {self.role}")
                        print(f"[{self.agent_id}] Especialización: {self.specialization}")

                    elif cmd == "quit":
                        print(f"[{self.agent_id}] Desconectando del orquestador...")
                        break

                    else:
                        print("Comandos: say [mensaje], work [tarea], check, auto, status, quit")

            except KeyboardInterrupt:
                print(f"\n[{self.agent_id}] Sesión terminada")
                break
            except Exception as e:
                print(f"Error: {e}")

def main():
    print("ORCHESTRATED AGENTS - Agentes Inteligentes")
    print("Conectados a orquestador para comunicación avanzada")
    print()
    print("Opciones:")
    print("1. Agent A (Frontend) - Modo manual")
    print("2. Agent B (Backend) - Modo manual")
    print("3. Agent A (Frontend) - Modo automático")
    print("4. Agent B (Backend) - Modo automático")

    choice = input("\nSelecciona (1-4): ").strip()

    # Limpiar pantalla
    os.system('cls' if os.name == 'nt' else 'clear')

    if choice == "1":
        agent = OrchestatedAgent("AGENT_A", "Frontend Developer",
                                "React, Vue, HTML, CSS, JavaScript, UI/UX")
        agent.run_agent(auto_mode=False)

    elif choice == "2":
        agent = OrchestatedAgent("AGENT_B", "Backend Developer",
                                "FastAPI, Express, APIs, Databases, Security")
        agent.run_agent(auto_mode=False)

    elif choice == "3":
        agent = OrchestatedAgent("AGENT_A", "Frontend Developer",
                                "React, Vue, HTML, CSS, JavaScript, UI/UX")
        agent.run_agent(auto_mode=True)

    elif choice == "4":
        agent = OrchestatedAgent("AGENT_B", "Backend Developer",
                                "FastAPI, Express, APIs, Databases, Security")
        agent.run_agent(auto_mode=True)

    else:
        print("Opción inválida. Ejecutando Agent A en modo manual...")
        agent = OrchestatedAgent("AGENT_A", "Frontend Developer",
                                "React, Vue, HTML, CSS, JavaScript, UI/UX")
        agent.run_agent(auto_mode=False)

if __name__ == "__main__":
    main()