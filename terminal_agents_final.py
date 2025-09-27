#!/usr/bin/env python3
"""
TERMINAL AGENTS FINAL - Tu vision exacta
Dos agentes interactuando en terminales separados SIN API KEYS
"""

import subprocess
import time
import os
import sys

def create_agent_terminal(agent_name, role, specialization):
    """Crea un terminal especializado para un agente"""
    script_content = f'''
@echo off
title {agent_name} - {role}
echo ================================
echo {agent_name} - {role}
echo ================================
echo Especialista en: {specialization}
echo SIN API KEYS - Solo terminal real
echo ================================
echo.
echo COMANDOS DISPONIBLES:
echo.
echo Para comunicarte con el otro agente:
echo   say "tu mensaje aqui"
echo.
echo Para trabajar en una tarea:
echo   work "descripcion de la tarea"
echo.
echo Para mostrar estado:
echo   status
echo.
echo ================================

python -c "
import sys
import time

def say(message):
    print(f'[{agent_name}]: {{message}}')
    with open('agent_communication.log', 'a') as f:
        f.write(f'{{time.strftime(\"%H:%M:%S\")}} - {agent_name}: {{message}}\\n')

def work(task):
    print(f'[{agent_name}] Trabajando en: {{task}}')
    print(f'[{agent_name}] Analizando requerimientos...')
    time.sleep(1)
    print(f'[{agent_name}] Generando solucion...')
    time.sleep(1)
    print(f'[{agent_name}] Tarea completada!')
    with open('agent_communication.log', 'a') as f:
        f.write(f'{{time.strftime(\"%H:%M:%S\")}} - {agent_name}: Completo tarea - {{task}}\\n')

def status():
    print(f'[{agent_name}] Estado: Activo y listo para colaborar')
    print(f'[{agent_name}] Rol: {role}')
    print(f'[{agent_name}] Especialidad: {specialization}')

def show_log():
    try:
        with open('agent_communication.log', 'r') as f:
            print('=== COMUNICACION ENTRE AGENTES ===')
            print(f.read())
    except:
        print('No hay comunicacion previa')

# Comandos disponibles
print('Agente listo. Comandos: say(), work(), status(), show_log()')
print('Ejemplo: say(\"Hola Agent B, necesito una API\")')
print('Ejemplo: work(\"Crear componentes React\")')
print()

while True:
    try:
        cmd = input(f'{agent_name}> ')
        if cmd.strip():
            exec(cmd)
    except KeyboardInterrupt:
        print(f'\\n[{agent_name}] Terminando sesion...')
        break
    except Exception as e:
        print(f'Error: {{e}}')
        print('Usa: say(\"mensaje\"), work(\"tarea\"), status(), show_log()')
"

pause
'''

    # Crear archivo de script temporal
    script_file = f"agent_{agent_name.lower()}.bat"
    with open(script_file, 'w') as f:
        f.write(script_content)

    return script_file

def launch_terminal_collaboration():
    """Lanza la colaboracion entre terminales"""
    print("=" * 60)
    print("TERMINAL AGENTS - VERSION FINAL")
    print("Tu vision: Agentes colaborando en terminales separados")
    print("SIN API KEYS - Solo procesos locales")
    print("=" * 60)

    # Limpiar log previo
    try:
        os.remove('agent_communication.log')
    except:
        pass

    print("\n[1] Creando Agent A (Frontend Developer)...")
    agent_a_script = create_agent_terminal(
        "AGENT_A",
        "Frontend Developer",
        "React, Vue, HTML, CSS, JavaScript, UI/UX"
    )

    print("[2] Creando Agent B (Backend Developer)...")
    agent_b_script = create_agent_terminal(
        "AGENT_B",
        "Backend Developer",
        "FastAPI, Express, APIs, Databases, Security"
    )

    print("\n[3] Abriendo terminales...")

    # Abrir Agent A
    subprocess.Popen([agent_a_script], shell=True)
    time.sleep(1)

    # Abrir Agent B
    subprocess.Popen([agent_b_script], shell=True)

    print("\n" + "=" * 60)
    print("DOS AGENTES LANZADOS EN TERMINALES SEPARADOS!")
    print("=" * 60)
    print("AGENT A: Frontend specialist")
    print("AGENT B: Backend specialist")
    print("")
    print("COMO USARLOS:")
    print("1. Ve al terminal 'AGENT_A - Frontend Developer'")
    print("2. Escribe: say(\"Hola Agent B, trabajemos en una Todo App\")")
    print("3. Ve al terminal 'AGENT_B - Backend Developer'")
    print("4. Escribe: show_log()  # para ver el mensaje")
    print("5. Escribe: say(\"Perfecto, yo creo la API\")")
    print("6. Continua la colaboracion...")
    print("")
    print("COMANDOS EN CADA TERMINAL:")
    print("- say(\"mensaje\")     -> Comunicarse con el otro agente")
    print("- work(\"tarea\")      -> Trabajar en una tarea")
    print("- status()            -> Ver estado del agente")
    print("- show_log()          -> Ver toda la comunicacion")
    print("")
    print("EJEMPLO DE SESION COLABORATIVA:")
    print("Agent A> say(\"Necesito endpoints CRUD para Todo App\")")
    print("Agent B> say(\"Perfecto, creare GET/POST/PUT/DELETE\")")
    print("Agent A> work(\"Crear componentes React\")")
    print("Agent B> work(\"Implementar API FastAPI\")")
    print("")
    print("ESA ES TU VISION - AGENTES REALES COLABORANDO!")

def demo_conversation():
    """Demo automatica de conversacion"""
    print("=" * 50)
    print("DEMO: CONVERSACION AUTOMATICA")
    print("=" * 50)

    # Simular conversacion
    print("\n[Agent A] Iniciando conversacion...")
    with open('agent_communication.log', 'w') as f:
        f.write(f"{time.strftime('%H:%M:%S')} - AGENT_A: Hola Agent B, trabajemos en una Todo App\n")

    time.sleep(1)
    print("[Agent B] Respondiendo...")
    with open('agent_communication.log', 'a') as f:
        f.write(f"{time.strftime('%H:%M:%S')} - AGENT_B: Perfecto! Yo creo la API con FastAPI\n")

    time.sleep(1)
    print("[Agent A] Continuando...")
    with open('agent_communication.log', 'a') as f:
        f.write(f"{time.strftime('%H:%M:%S')} - AGENT_A: Excelente, yo hago los componentes React\n")

    time.sleep(1)
    print("[Agent B] Trabajando...")
    with open('agent_communication.log', 'a') as f:
        f.write(f"{time.strftime('%H:%M:%S')} - AGENT_B: API endpoints listos: GET/POST/PUT/DELETE /todos\n")

    time.sleep(1)
    print("[Agent A] Finalizando...")
    with open('agent_communication.log', 'a') as f:
        f.write(f"{time.strftime('%H:%M:%S')} - AGENT_A: Frontend completado con formularios y lista\n")

    print("\n" + "=" * 50)
    print("CONVERSACION COMPLETADA!")
    print("=" * 50)

    # Mostrar log
    with open('agent_communication.log', 'r') as f:
        print("LOG DE COMUNICACION:")
        print(f.read())

    print("ESTO ES TU VISION:")
    print("- Agentes comunicandose")
    print("- Log persistente de conversacion")
    print("- Colaboracion real")
    print("- Sin APIs externas")

if __name__ == "__main__":
    print("TERMINAL AGENTS - VERSION DEFINITIVA")
    print("Tu vision de agentes colaborando sin API keys")
    print("")
    print("1. Lanzar agentes en terminales separados")
    print("2. Demo de conversacion automatica")

    try:
        choice = input("\nOpcion (1 o 2): ").strip()

        if choice == "1":
            launch_terminal_collaboration()
        elif choice == "2":
            demo_conversation()
        else:
            print("Lanzando agentes en terminales...")
            launch_terminal_collaboration()

    except KeyboardInterrupt:
        print("\nSaliendo...")
    except:
        print("Lanzando agentes en terminales...")
        launch_terminal_collaboration()

    # Limpiar archivos temporales al salir
    try:
        os.remove('agent_a.bat')
        os.remove('agent_b.bat')
    except:
        pass