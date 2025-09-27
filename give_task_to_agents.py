#!/usr/bin/env python3
"""
INTERFAZ HUMANO → AGENTES AI
Permite dar tareas directamente a los agentes desde la línea de comandos
"""

import requests
import json
import sys

def give_task_to_agents():
    """Interfaz para dar tareas a los agentes"""
    print("=" * 60)
    print("AI-BRIDGE: INTERFAZ HUMANO → AGENTES")
    print("Dale tareas a tus agentes AI sin API keys")
    print("=" * 60)

    # Ejemplos de tareas predefinidas
    example_tasks = {
        "1": {
            "name": "Crear aplicación web simple",
            "objective": "Crear una aplicación web con frontend React y backend FastAPI para gestión de usuarios con registro, login y dashboard"
        },
        "2": {
            "name": "Sistema de blog",
            "objective": "Desarrollar un sistema de blog completo con posts, comentarios, categorías, frontend moderno y API REST"
        },
        "3": {
            "name": "E-commerce básico",
            "objective": "Crear una tienda online básica con catálogo de productos, carrito de compras, frontend React y backend con API"
        },
        "4": {
            "name": "Dashboard analytics",
            "objective": "Construir un dashboard de analytics con gráficos, métricas en tiempo real, frontend interactivo y API de datos"
        },
        "5": {
            "name": "Tarea personalizada",
            "objective": "custom"
        }
    }

    print("\nTAREAS DISPONIBLES:")
    for key, task in example_tasks.items():
        print(f"  {key}. {task['name']}")

    print("\n" + "=" * 40)
    choice = input("Selecciona una tarea (1-5): ").strip()

    if choice in example_tasks:
        task = example_tasks[choice]

        if task['objective'] == 'custom':
            print("\n🎯 TAREA PERSONALIZADA:")
            objective = input("Describe lo que quieres que hagan tus agentes: ").strip()
        else:
            objective = task['objective']
            print(f"\n🎯 TAREA SELECCIONADA: {task['name']}")
            print(f"Objetivo: {objective}")

        print(f"\n🚀 ENVIANDO TAREA A LOS AGENTES...")

        # Enviar tarea via API
        try:
            response = requests.post(
                "http://localhost:8000/api/orchestration/start",
                json={"objective": objective},
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                session_id = result.get("session_id")
                print(f"✅ TAREA ENVIADA EXITOSAMENTE!")
                print(f"   Session ID: {session_id}")
                print(f"   Status: {result.get('status')}")
                print(f"   Message: {result.get('message')}")

                print(f"\n📊 MONITOREO:")
                print(f"   Control Cabin: http://localhost:5002")
                print(f"   API Status: http://localhost:8000/api/orchestration/status")

                return session_id
            else:
                print(f"❌ ERROR: {response.status_code}")
                print(f"   Detalles: {response.text}")

                # Mostrar alternativas
                print(f"\n🔧 ALTERNATIVAS:")
                print(f"   1. Usar CLI Bridge directo")
                print(f"   2. Configurar agents manualmente")
                print(f"   3. Usar Python/Node como fallback")

                return None

        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return None
    else:
        print("❌ Selección inválida")
        return None

def monitor_task(session_id):
    """Monitorear el progreso de la tarea"""
    if not session_id:
        return

    print(f"\n🔍 MONITOREANDO TAREA...")
    try:
        response = requests.get("http://localhost:8000/api/orchestration/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"   Estado: {status.get('state', 'unknown')}")
            print(f"   Iteración: {status.get('current_iteration', 0)}")
            print(f"   Workspace: {status.get('workspace', 'N/A')}")

            if status.get('error_message'):
                print(f"   ⚠️ Info: {status['error_message']}")
        else:
            print(f"   Error obteniendo status: {response.status_code}")
    except Exception as e:
        print(f"   Error monitoreando: {e}")

def main():
    print("🤖 BIENVENIDO AL AI-BRIDGE")
    print("Interfaz para dirigir tu equipo de desarrollo AI")

    # Verificar que el sistema esté corriendo
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Sistema: {health['status']} (v{health['version']})")
        else:
            print("❌ Sistema no responde")
            return
    except Exception as e:
        print(f"❌ Error conectando al sistema: {e}")
        print("   Asegúrate de que AI-Bridge esté corriendo:")
        print("   python start_ai_bridge.py")
        return

    # Dar tarea a los agentes
    session_id = give_task_to_agents()

    # Monitorear progreso
    if session_id:
        monitor_task(session_id)

        print(f"\n🎯 PRÓXIMOS PASOS:")
        print(f"   1. Abre Control Cabin: http://localhost:5002")
        print(f"   2. Observa la colaboración en tiempo real")
        print(f"   3. Revisa el workspace cuando terminen")

if __name__ == "__main__":
    main()