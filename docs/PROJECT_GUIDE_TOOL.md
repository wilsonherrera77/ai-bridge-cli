# 🚀 Project Guide Tool - Guía Full Stack Completa

## Descripción

**Project Guide Tool** es un sistema completo de orientación, corrección y entrega de proyectos full stack integrado en AI-Bridge CLI. Esta herramienta proporciona:

- ✅ **Templates profesionales** de proyectos full stack
- ✅ **Validación automática** de código y estructura
- ✅ **Corrección automática** de issues comunes
- ✅ **Guía paso a paso** para completar proyectos
- ✅ **Checklist de calidad** con mejores prácticas
- ✅ **Integración con agentes AI** para desarrollo autónomo

---

## 📋 Características Principales

### 1. Templates de Proyectos

Cuatro templates completos listos para usar:

#### React + FastAPI (Recomendado)
- **Frontend**: React 19, Vite, TailwindCSS, Zustand, React Query
- **Backend**: FastAPI, SQLAlchemy, Alembic, Pydantic
- **Features**: Auth JWT, API REST, WebSocket, Tests
- **Uso ideal**: Apps web modernas, dashboards, SaaS

#### Next.js + FastAPI
- **Frontend**: Next.js 14, Server Components, App Router
- **Backend**: FastAPI, SQLAlchemy
- **Features**: SSR/SSG, SEO optimizado, API routes
- **Uso ideal**: Landing pages, e-commerce, blogs

#### React + Node/Express
- **Frontend**: React, Vite
- **Backend**: Node.js, Express, MongoDB
- **Features**: Auth, REST API, Socket.io
- **Uso ideal**: Chat apps, tiempo real, CRUD tradicional

#### Full Stack Monorepo
- **Stack**: Turborepo, múltiples apps, shared packages
- **Features**: Code sharing, unified build, scalable
- **Uso ideal**: Empresas, múltiples productos, equipos grandes

---

### 2. Niveles de Validación

#### Basic
- ✅ Estructura de archivos correcta
- ✅ Archivos de configuración presentes
- ✅ Dependencies instaladas

#### Standard (Recomendado)
- ✅ Todo lo de Basic
- ✅ Linting sin errores (ESLint, Ruff)
- ✅ Formateo consistente (Prettier, Black)
- ✅ Imports optimizados

#### Professional
- ✅ Todo lo de Standard
- ✅ Tests unitarios (>80% coverage)
- ✅ Tests de integración
- ✅ Documentación completa (README, API docs)
- ✅ Types/schemas definidos

#### Production
- ✅ Todo lo de Professional
- ✅ Security audit (dependencias, vulnerabilidades)
- ✅ Performance optimization (bundle size, lazy loading)
- ✅ CI/CD configurado
- ✅ Environment variables securizadas
- ✅ Build de producción exitoso

---

## 🎯 Cómo Usar

### Opción 1: Interfaz Web (Recomendado)

1. **Iniciar AI-Bridge**
```bash
cd ai-bridge-cli
python start_ai_bridge.py
```

2. **Abrir Control Cabin**
- Navega a: `http://localhost:5002`
- Click en tab "Project Guide" en el header

3. **Crear Proyecto**
- Ingresa nombre del proyecto (ej: "mi-app-increible")
- Selecciona template (ej: "React + FastAPI")
- Selecciona nivel de validación (recomendado: "Professional")
- Click en "Crear Proyecto"

4. **Ver Progreso**
- Ve a tab "Mis Proyectos"
- Click en "Guía" para ver próximos pasos
- Click en "Validar" para validar código

5. **Seguir Guía**
- En tab "Guía" verás los próximos 3 pasos
- Cada paso incluye:
  - Descripción de la tarea
  - Fase del proyecto
  - Orientación técnica
  - Recursos útiles

### Opción 2: API REST

#### Crear Proyecto

```bash
curl -X POST http://localhost:8000/api/project/create \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "mi-app",
    "project_type": "react_fastapi",
    "validation_level": "professional"
  }'
```

**Respuesta:**
```json
{
  "status": "success",
  "project_id": "mi-app",
  "type": "react_fastapi",
  "phase": "setup",
  "checklist": [
    {"id": 0, "task": "✅ Estructura de proyecto creada", "completed": false},
    ...
  ],
  "message": "Proyecto mi-app creado exitosamente"
}
```

#### Validar Proyecto

```bash
curl -X POST http://localhost:8000/api/project/validate \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "mi-app",
    "validation_level": "standard",
    "auto_correct": true
  }'
```

**Respuesta:**
```json
{
  "status": "success",
  "validation": {
    "passed": true,
    "score": 92.5,
    "issues": 3,
    "auto_fixable": 2
  },
  "corrections_applied": [
    "Formateo corregido: src/App.jsx",
    "Imports optimizados: backend/main.py"
  ],
  "suggestions": [...]
}
```

#### Obtener Guía

```bash
curl -X POST http://localhost:8000/api/project/guidance \
  -H "Content-Type: application/json" \
  -d '{"project_name": "mi-app"}'
```

**Respuesta:**
```json
{
  "status": "success",
  "project": "mi-app",
  "phase": "development",
  "progress": 45.0,
  "next_steps": [
    {
      "task": "✅ Sistema de autenticación",
      "phase": "development",
      "guidance": "Implementa JWT tokens con refresh tokens...",
      "resources": ["https://fastapi.tiangolo.com/..."]
    }
  ],
  "checklist_completion": "7/16"
}
```

#### Listar Templates

```bash
curl http://localhost:8000/api/project/templates
```

#### Listar Proyectos

```bash
curl http://localhost:8000/api/project/list
```

---

## 📊 Estructura de Proyecto Creado

Cuando creas un proyecto, se genera esta estructura:

```
workspace/
└── mi-app/
    ├── .project-guide.json       # Estado de la guía
    ├── README.md                  # Documentación generada
    ├── frontend/
    │   ├── src/
    │   │   ├── components/        # Componentes React
    │   │   ├── hooks/             # Custom hooks
    │   │   ├── services/          # API clients
    │   │   ├── utils/             # Utilidades
    │   │   ├── pages/             # Pages/Routes
    │   │   └── assets/            # Static assets
    │   ├── public/
    │   ├── tests/
    │   ├── package.json           # Generado con deps
    │   ├── vite.config.js
    │   └── tailwind.config.js
    ├── backend/
    │   ├── app/
    │   │   ├── api/
    │   │   │   ├── routes/        # Endpoints
    │   │   │   └── dependencies/  # DI
    │   │   ├── core/              # Config
    │   │   ├── models/            # DB models
    │   │   ├── schemas/           # Pydantic schemas
    │   │   ├── services/          # Business logic
    │   │   └── db/                # Database
    │   ├── tests/
    │   ├── alembic/               # Migrations
    │   └── requirements.txt       # Generado con deps
    ├── shared/
    │   ├── types/                 # TypeScript/Python types
    │   └── constants/             # Constantes compartidas
    ├── docs/                      # Documentación
    └── scripts/                   # Build/deploy scripts
```

---

## 🔄 Ciclo de Trabajo

### Fase 1: Planning (Planificación)
- Definir requisitos
- Diseñar arquitectura
- Planear API endpoints
- Diseñar UI/UX

### Fase 2: Setup (Configuración)
- Estructura de proyecto creada ✅ (automático)
- Dependencias instaladas
- Base de datos configurada
- Variables de entorno setup

### Fase 3: Development (Desarrollo)
- Implementar autenticación
- Crear API endpoints
- Desarrollar componentes frontend
- Integrar frontend-backend

### Fase 4: Testing (Pruebas)
- Tests unitarios (>80% coverage)
- Tests de integración
- Tests E2E
- Manual QA

### Fase 5: Optimization (Optimización)
- Code review
- Performance tuning
- Security hardening
- Bundle optimization

### Fase 6: Deployment (Despliegue)
- CI/CD setup
- Environment configs
- Build de producción
- Deploy a staging/production

### Fase 7: Completed (Completado)
- 🎉 Proyecto listo para usar
- Documentación completa
- Tests pasando
- Production ready

---

## 🤖 Integración con Agentes AI

El Project Guide Tool se integra perfectamente con los agentes AI de AI-Bridge:

### Workflow Automático

1. **Usuario crea proyecto** vía Project Guide Tool
2. **AgentA (Frontend)** recibe instrucción de crear componentes
3. **AgentB (Backend)** recibe instrucción de crear API
4. **Project Guide valida** el código automáticamente
5. **Correcciones automáticas** se aplican
6. **Guía actualizada** con próximos pasos
7. **Agentes continúan** hasta completar proyecto

### Ejemplo de Integración

```python
from orchestrator import AgentOrchestrator
from project_guide import ProjectGuideEngine

# Crear proyecto
engine = ProjectGuideEngine()
guide = await engine.create_project("mi-app", "react_fastapi")

# Iniciar orquestador con objetivo del proyecto
orchestrator = AgentOrchestrator(config)
await orchestrator.start_session(
    goal=f"Implementar {guide.checklist[guide.progress].task}",
    workspace="workspace/mi-app"
)

# Después de implementación, validar
result = await engine.validate_project("mi-app")

# Si hay errores, los agentes los corrigen
if not result.passed:
    await orchestrator.send_correction_request(result.issues)

# Obtener siguiente tarea
next_steps = await engine.get_next_steps("mi-app")
```

---

## ⚙️ Configuración Avanzada

### Personalizar Templates

Edita `backend/project_guide.py` para agregar templates custom:

```python
def _get_custom_template(self) -> ProjectTemplate:
    return ProjectTemplate(
        name="Mi Template Custom",
        type=ProjectType.CUSTOM,
        description="Template personalizado",
        structure={
            "mi-estructura": {
                "personalizada": {}
            }
        },
        dependencies={
            "frontend": ["react", "mi-lib-custom"],
            "backend": ["fastapi", "mi-backend-lib"]
        },
        scripts={...},
        checklist=[...]
    )
```

### Agregar Validadores Custom

```python
async def _validate_custom(self, project_path: Path) -> List[Dict]:
    issues = []

    # Tu lógica de validación
    if not (project_path / "mi-archivo-importante.txt").exists():
        issues.append({
            "severity": "error",
            "type": "missing_file",
            "file": "mi-archivo-importante.txt",
            "message": "Archivo crítico faltante",
            "auto_fixable": False
        })

    return issues
```

### Agregar Correctores Custom

```python
async def _fix_custom(self, project_path: Path, issue: Dict):
    if issue["type"] == "custom_issue":
        # Tu lógica de corrección
        file_path = project_path / issue["file"]
        # ... aplicar fix
```

---

## 📈 Mejores Prácticas

### 1. Usar Nivel Professional para Producción
- Asegura calidad de código
- Tests automáticos
- Documentación completa

### 2. Validar Frecuentemente
- Después de cada feature
- Antes de commits importantes
- Antes de merge a main

### 3. Seguir la Guía Paso a Paso
- No saltarse pasos
- Completar checklist en orden
- Validar antes de avanzar

### 4. Aprovechar Auto-corrección
- `auto_correct: true` ahorra tiempo
- Revisa los cambios aplicados
- Aprende de las correcciones

### 5. Integrar con CI/CD
- Validación automática en PRs
- Score mínimo requerido
- Deploy solo si validación pasa

---

## 🐛 Troubleshooting

### Error: "Project Guide Tool not available"

**Solución:**
```bash
# Verificar que project_guide.py existe
ls backend/project_guide.py

# Reiniciar servidor
python backend/main.py
```

### Error: "Project not found"

**Solución:**
```bash
# Verificar que el proyecto existe
ls workspace/mi-app/.project-guide.json

# Crear proyecto si no existe
curl -X POST http://localhost:8000/api/project/create ...
```

### Score bajo en validación

**Solución:**
1. Revisar `validation.issues` para ver problemas
2. Aplicar correcciones automáticas: `auto_correct: true`
3. Revisar `suggestions` para mejoras manuales
4. Ejecutar linters manualmente:
```bash
# Frontend
cd frontend && npm run lint && npm run format

# Backend
cd backend && ruff check . && black .
```

### Guía no se actualiza

**Solución:**
```bash
# Recargar guía
curl -X POST http://localhost:8000/api/project/guidance \
  -d '{"project_name": "mi-app"}'

# O en la UI: Click en "Actualizar"
```

---

## 🎓 Ejemplos Completos

### Ejemplo 1: Crear y Validar Proyecto

```python
import asyncio
from project_guide import create_fullstack_project, validate_and_correct

async def main():
    # Crear proyecto
    result = await create_fullstack_project(
        project_name="todo-app",
        project_type="react_fastapi",
        validation_level="professional"
    )
    print(f"✅ Proyecto creado: {result['project_id']}")

    # ... implementar features ...

    # Validar
    validation = await validate_and_correct(
        project_name="todo-app",
        validation_level="professional",
        auto_correct=True
    )

    if validation['validation']['passed']:
        print(f"✅ Validación exitosa! Score: {validation['validation']['score']}")
    else:
        print(f"⚠️ Issues encontrados: {validation['validation']['issues']}")
        print(f"Correcciones aplicadas: {len(validation['corrections_applied'])}")

asyncio.run(main())
```

### Ejemplo 2: Workflow con Agentes

```python
from orchestrator import AgentOrchestrator
from project_guide import ProjectGuideEngine
import asyncio

async def develop_with_guide():
    engine = ProjectGuideEngine()
    orchestrator = AgentOrchestrator()

    # Crear proyecto
    guide = await engine.create_project("ecommerce-app", "react_fastapi")

    # Para cada tarea en checklist
    for task in guide.checklist:
        if task["completed"]:
            continue

        print(f"📋 Tarea: {task['task']}")

        # Agentes implementan la tarea
        await orchestrator.start_session(
            goal=task["task"],
            workspace=f"workspace/{guide.project_id}"
        )

        # Esperar a que agentes terminen
        while orchestrator.state == "running":
            await asyncio.sleep(5)

        # Validar implementación
        result = await engine.validate_project(guide.project_id)

        if result.passed:
            task["completed"] = True
            print(f"✅ Tarea completada! Score: {result.score}")
        else:
            print(f"⚠️ Requiere correcciones")
            # Aplicar correcciones
            await engine.apply_corrections(guide.project_id, result)

asyncio.run(develop_with_guide())
```

---

## 🚀 Próximas Mejoras

- [ ] Soporte para más frameworks (Vue, Angular, Svelte)
- [ ] Templates especializados (E-commerce, CMS, Chat)
- [ ] Validación de performance con Lighthouse
- [ ] Integración con GitHub Actions
- [ ] Deployment automático a Vercel/Railway
- [ ] AI Code Review con GPT-4
- [ ] Generación automática de tests
- [ ] Dashboard de métricas de calidad

---

## 📚 Recursos Adicionales

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [Vite Docs](https://vitejs.dev/)
- [TailwindCSS Docs](https://tailwindcss.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)

---

## 🤝 Contribuir

¿Tienes ideas para mejorar Project Guide Tool?

1. Fork el repositorio
2. Crea una branch: `git checkout -b feature/mi-mejora`
3. Commit cambios: `git commit -m 'Agregar mi mejora'`
4. Push: `git push origin feature/mi-mejora`
5. Abre un Pull Request

---

## 📄 Licencia

MIT License - Usa libremente en tus proyectos!

---

**¡Feliz desarrollo full stack! 🚀**
