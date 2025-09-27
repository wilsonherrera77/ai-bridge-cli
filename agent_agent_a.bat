
@echo off
title AGENT_A - Frontend Developer
echo ================================
echo AGENT_A - Frontend Developer
echo ================================
echo Especialista en: React, Vue, HTML, CSS, JavaScript, UI/UX
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
    print(f'[AGENT_A]: {message}')
    with open('agent_communication.log', 'a') as f:
        f.write(f'{time.strftime("%H:%M:%S")} - AGENT_A: {message}\n')

def work(task):
    print(f'[AGENT_A] Trabajando en: {task}')
    print(f'[AGENT_A] Analizando requerimientos...')
    time.sleep(1)
    print(f'[AGENT_A] Generando solucion...')
    time.sleep(1)
    print(f'[AGENT_A] Tarea completada!')
    with open('agent_communication.log', 'a') as f:
        f.write(f'{time.strftime("%H:%M:%S")} - AGENT_A: Completo tarea - {task}\n')

def status():
    print(f'[AGENT_A] Estado: Activo y listo para colaborar')
    print(f'[AGENT_A] Rol: Frontend Developer')
    print(f'[AGENT_A] Especialidad: React, Vue, HTML, CSS, JavaScript, UI/UX')

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
        cmd = input(f'AGENT_A> ')
        if cmd.strip():
            exec(cmd)
    except KeyboardInterrupt:
        print(f'\n[AGENT_A] Terminando sesion...')
        break
    except Exception as e:
        print(f'Error: {e}')
        print('Usa: say("mensaje"), work("tarea"), status(), show_log()')
"

pause
