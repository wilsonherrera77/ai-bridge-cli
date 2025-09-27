
@echo off
title AGENT_B - Backend Developer
echo ================================
echo AGENT_B - Backend Developer
echo ================================
echo Especialista en: FastAPI, Express, APIs, Databases, Security
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
    print(f'[AGENT_B]: {message}')
    with open('agent_communication.log', 'a') as f:
        f.write(f'{time.strftime("%H:%M:%S")} - AGENT_B: {message}\n')

def work(task):
    print(f'[AGENT_B] Trabajando en: {task}')
    print(f'[AGENT_B] Analizando requerimientos...')
    time.sleep(1)
    print(f'[AGENT_B] Generando solucion...')
    time.sleep(1)
    print(f'[AGENT_B] Tarea completada!')
    with open('agent_communication.log', 'a') as f:
        f.write(f'{time.strftime("%H:%M:%S")} - AGENT_B: Completo tarea - {task}\n')

def status():
    print(f'[AGENT_B] Estado: Activo y listo para colaborar')
    print(f'[AGENT_B] Rol: Backend Developer')
    print(f'[AGENT_B] Especialidad: FastAPI, Express, APIs, Databases, Security')

def show_log():
    try:
        with open('agent_communication.log', 'r') as f:
            print('=== COMUNICACION ENTRE AGENTES ===')
            print(f.read())
    except:
        print('No hay comunicacion previa')

# Comandos disponibles
print('Agente listo. Comandos: say(), work(), status(), show_log()')
print('Ejemplo: say("Hola Agent B, necesito una API")')
print('Ejemplo: work("Crear componentes React")')
print()

while True:
    try:
        cmd = input(f'AGENT_B> ')
        if cmd.strip():
            exec(cmd)
    except KeyboardInterrupt:
        print(f'\n[AGENT_B] Terminando sesion...')
        break
    except Exception as e:
        print(f'Error: {e}')
        print('Usa: say("mensaje"), work("tarea"), status(), show_log()')
"

pause
