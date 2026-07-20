# 🦙 Ollama - Modelos de IA Locales (Instalado y Funcional)

**Estado**: ✅ INSTALADO Y FUNCIONAL
**Versión**: Ollama 0.32.1
**Fecha**: 2026-07-20

---

## 📦 Modelos Instalados

| Modelo | Tamaño | Uso recomendado | Estado |
|--------|--------|-----------------|--------|
| `phi3` | 2.2 GB | Chat rápido y ligero (3.8B) | ✅ Funcional |
| `llama3.1` | 4.9 GB | Propósito general (8B) | ✅ Funcional |
| `codellama` | 3.8 GB | Generación de código (7B) | ✅ Funcional |

**Total en disco**: ~11 GB

---

## 🚀 Cómo Usar

### Arrancar el servidor

En este entorno **systemd no está disponible**, por lo que el servidor no arranca
automáticamente. Usa el script incluido:

```bash
./scripts/start_ollama.sh          # Arranca el servidor
./scripts/start_ollama.sh --status # Verifica estado y lista modelos
```

O manualmente:
```bash
OLLAMA_HOST=127.0.0.1:11434 ollama serve > /tmp/ollama.log 2>&1 &
```

### Chat interactivo (CLI)
```bash
ollama run phi3
ollama run llama3.1
ollama run codellama
```

### Vía API REST
```bash
curl http://127.0.0.1:11434/api/generate -d '{
  "model": "llama3.1",
  "prompt": "Explica qué es una API REST en una frase",
  "stream": false
}'
```

### Vía Python
```python
import requests

def ask_ollama(prompt, model="llama3.1"):
    r = requests.post("http://127.0.0.1:11434/api/generate", json={
        "model": model,
        "prompt": prompt,
        "stream": False
    })
    return r.json()["response"]

print(ask_ollama("¿Qué es Python?", model="phi3"))
```

---

## ⚠️ Fix Importante Aplicado: Segmentation Fault en AVX512

### El problema
Al ejecutar cualquier modelo, `llama-server` crasheaba con:
```
general protection fault ... in libggml-cpu-sapphirerapids.so
Error: 500 Internal Server Error: llama-server process has terminated: signal: segmentation fault
```

### La causa
Este CPU es un **Intel Xeon virtualizado** que reporta soporte para AVX512
(incluyendo extensiones tipo Sapphire Rapids: AMX, AVX512-BF16). Ollama
auto-detecta esas capacidades y carga `libggml-cpu-sapphirerapids.so`, pero
**el hypervisor de la VM no soporta realmente esas instrucciones**, provocando
un "general protection fault".

### La solución
Se movieron las librerías CPU que usan AVX512 avanzado para forzar a Ollama a
usar el runner `haswell` (solo AVX2, totalmente compatible con la VM):

```bash
cd /usr/local/lib/ollama
mkdir -p ~/ollama-cpu-backup
for lib in sapphirerapids skylakex icelake cascadelake cooperlake cannonlake zen4; do
  mv "libggml-cpu-$lib.so" ~/ollama-cpu-backup/ 2>/dev/null
done
```

Librerías CPU que quedan activas (compatibles):
`alderlake`, `haswell` (AVX2), `ivybridge`, `sandybridge`, `sse42`, `x64`

> **Nota**: Si en el futuro reinstalas/actualizas Ollama, es posible que las
> librerías AVX512 vuelvan y el segfault reaparezca. Repite el fix de arriba.
> Las librerías respaldadas están en el scratchpad de la sesión y en
> `~/ollama-cpu-backup/`.

---

## 📊 Rendimiento (CPU, sin GPU)

- **Hardware**: Intel Xeon 4 cores, 16 GB RAM, sin GPU
- **Runner**: haswell (AVX2)
- **Velocidad aproximada**:
  - `phi3` (3.8B): ~3-6 seg respuestas cortas — el más rápido
  - `codellama` (7B): ~moderado
  - `llama3.1` (8B): ~moderado, el más capaz

> Sin GPU los modelos funcionan pero son más lentos que en la nube.
> Para prototipos rápidos usa `phi3`; para calidad usa `llama3.1`.

---

## 🔗 Integración con AI-Bridge

Ollama expone una API compatible que puede integrarse como un agente local
adicional en el sistema AI-Bridge (sin consumir API keys):

```python
# Ejemplo de agente local basado en Ollama
import requests

class OllamaAgent:
    def __init__(self, model="llama3.1", host="127.0.0.1:11434"):
        self.model = model
        self.url = f"http://{host}/api/generate"

    def generate(self, prompt: str) -> str:
        r = requests.post(self.url, json={
            "model": self.model,
            "prompt": prompt,
            "stream": False
        })
        return r.json().get("response", "")
```

También es compatible con la API de OpenAI en:
`http://127.0.0.1:11434/v1/chat/completions`

---

## 🛠️ Comandos Útiles

```bash
ollama list                    # Listar modelos instalados
ollama pull <modelo>           # Descargar un modelo nuevo
ollama rm <modelo>             # Eliminar un modelo
ollama ps                      # Ver modelos cargados en memoria
ollama run <modelo>            # Chat interactivo
```

### Modelos adicionales recomendados
```bash
ollama pull qwen2.5-coder:7b   # Excelente para código
ollama pull gemma2:2b          # Muy ligero de Google
ollama pull mistral            # Mistral 7B
ollama pull llama3.2:3b        # Llama pequeño y rápido
```
