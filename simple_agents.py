#!/usr/bin/env python3
"""
SIMPLE AGENTS - Version que funciona inmediatamente
Dos agentes comunicandose via archivos compartidos
"""

import os
import time
import sys
from datetime import datetime

def agent_a():
    """Agent A - Frontend Developer"""
    print("=" * 50)
    print("AGENT A - FRONTEND DEVELOPER")
    print("=" * 50)
    print("Especialista en: React, Vue, HTML, CSS, JavaScript")
    print("SIN API KEYS - Solo comunicacion local")
    print("=" * 50)
    print()
    print("COMANDOS:")
    print("1. say [mensaje] - Enviar mensaje a Agent B")
    print("2. work [tarea] - Trabajar en una tarea")
    print("3. check - Ver mensajes de Agent B")
    print("4. status - Ver estado")
    print("5. quit - Salir")
    print()

    while True:
        try:
            cmd = input("AGENT_A> ").strip()

            if cmd.startswith("say "):
                message = cmd[4:]
                timestamp = datetime.now().strftime("%H:%M:%S")
                with open("agent_communication.txt", "a") as f:
                    f.write(f"{timestamp} - AGENT_A: {message}\n")
                print(f"[Enviado a Agent B]: {message}")

            elif cmd.startswith("work "):
                task = cmd[5:]
                print(f"[AGENT_A] Trabajando en: {task}")
                print("[AGENT_A] Analizando requerimientos...")
                time.sleep(1)
                print("[AGENT_A] Diseñando componentes...")
                time.sleep(1)
                print("[AGENT_A] Implementando solucion frontend...")
                time.sleep(1)
                print("[AGENT_A] ✓ Tarea completada!")

                timestamp = datetime.now().strftime("%H:%M:%S")
                with open("agent_communication.txt", "a") as f:
                    f.write(f"{timestamp} - AGENT_A: Completé tarea - {task}\n")

            elif cmd == "check":
                print("\n=== COMUNICACION CON AGENT B ===")
                try:
                    with open("agent_communication.txt", "r") as f:
                        lines = f.readlines()
                        for line in lines:
                            if "AGENT_B:" in line:
                                print(line.strip())
                except FileNotFoundError:
                    print("No hay mensajes aún")
                print("=" * 35)

            elif cmd == "status":
                print("[AGENT_A] Estado: Activo y listo")
                print("[AGENT_A] Rol: Frontend Developer")
                print("[AGENT_A] Tecnologías: React, Vue, HTML, CSS, JS")

            elif cmd == "quit":
                print("[AGENT_A] Finalizando sesión...")
                break

            else:
                print("Comandos: say [mensaje], work [tarea], check, status, quit")

        except KeyboardInterrupt:
            print("\n[AGENT_A] Sesión terminada")
            break
        except Exception as e:
            print(f"Error: {e}")

def agent_b():
    """Agent B - Backend Developer"""
    print("=" * 50)
    print("AGENT B - BACKEND DEVELOPER")
    print("=" * 50)
    print("Especialista en: FastAPI, Express, APIs, Databases")
    print("SIN API KEYS - Solo comunicacion local")
    print("=" * 50)
    print()
    print("COMANDOS:")
    print("1. say [mensaje] - Enviar mensaje a Agent A")
    print("2. work [tarea] - Trabajar en una tarea")
    print("3. check - Ver mensajes de Agent A")
    print("4. status - Ver estado")
    print("5. quit - Salir")
    print()

    while True:
        try:
            cmd = input("AGENT_B> ").strip()

            if cmd.startswith("say "):
                message = cmd[4:]
                timestamp = datetime.now().strftime("%H:%M:%S")
                with open("agent_communication.txt", "a") as f:
                    f.write(f"{timestamp} - AGENT_B: {message}\n")
                print(f"[Enviado a Agent A]: {message}")

            elif cmd.startswith("work "):
                task = cmd[5:]
                print(f"[AGENT_B] Trabajando en: {task}")
                print("[AGENT_B] Diseñando arquitectura...")
                time.sleep(1)
                print("[AGENT_B] Implementando API endpoints...")
                time.sleep(1)
                print("[AGENT_B] Configurando base de datos...")
                time.sleep(1)
                print("[AGENT_B] ✓ Tarea completada!")

                timestamp = datetime.now().strftime("%H:%M:%S")
                with open("agent_communication.txt", "a") as f:
                    f.write(f"{timestamp} - AGENT_B: Completé tarea - {task}\n")

            elif cmd == "check":
                print("\n=== COMUNICACION CON AGENT A ===")
                try:
                    with open("agent_communication.txt", "r") as f:
                        lines = f.readlines()
                        for line in lines:
                            if "AGENT_A:" in line:
                                print(line.strip())
                except FileNotFoundError:
                    print("No hay mensajes aún")
                print("=" * 35)

            elif cmd == "status":
                print("[AGENT_B] Estado: Activo y listo")
                print("[AGENT_B] Rol: Backend Developer")
                print("[AGENT_B] Tecnologías: FastAPI, Express, APIs, DBs")

            elif cmd == "quit":
                print("[AGENT_B] Finalizando sesión...")
                break

            else:
                print("Comandos: say [mensaje], work [tarea], check, status, quit")

        except KeyboardInterrupt:
            print("\n[AGENT_B] Sesión terminada")
            break
        except Exception as e:
            print(f"Error: {e}")

def show_full_log():
    """Mostrar todo el log de comunicacion"""
    print("\n" + "=" * 60)
    print("LOG COMPLETO DE COMUNICACION ENTRE AGENTES")
    print("=" * 60)
    try:
        with open("agent_communication.txt", "r") as f:
            print(f.read())
    except FileNotFoundError:
        print("No hay comunicación registrada aún")
    print("=" * 60)

if __name__ == "__main__":
    print("SIMPLE AGENTS - Comunicación Directa")
    print("Tu visión: Agentes comunicándose sin API keys")
    print()
    print("Opciones:")
    print("1. Ejecutar como Agent A (Frontend)")
    print("2. Ejecutar como Agent B (Backend)")
    print("3. Ver log completo de comunicación")

    choice = input("\nSelecciona (1, 2, o 3): ").strip()

    # Limpiar pantalla
    os.system('cls' if os.name == 'nt' else 'clear')

    if choice == "1":
        agent_a()
    elif choice == "2":
        agent_b()
    elif choice == "3":
        show_full_log()
    else:
        print("Opción inválida")

    print("\n¡Gracias por usar Simple Agents!")