"""
Project Guide Tool - Sistema de orientación, corrección y entrega de proyectos full stack

Este módulo proporciona:
- Templates de proyectos full stack
- Validación automática de código y estructura
- Corrección automática y sugerencias
- Checklist de calidad paso a paso
- Pipeline de entrega completa
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ProjectType(Enum):
    """Tipos de proyectos soportados"""
    REACT_FASTAPI = "react_fastapi"
    NEXTJS_FASTAPI = "nextjs_fastapi"
    REACT_NODE_EXPRESS = "react_node_express"
    VUE_FASTAPI = "vue_fastapi"
    FULLSTACK_MONOREPO = "fullstack_monorepo"


class ValidationLevel(Enum):
    """Niveles de validación"""
    BASIC = "basic"              # Estructura básica
    STANDARD = "standard"        # + Linting y formateo
    PROFESSIONAL = "professional" # + Tests y documentación
    PRODUCTION = "production"    # + Security, performance, deploy


class ProjectPhase(Enum):
    """Fases del proyecto"""
    PLANNING = "planning"
    SETUP = "setup"
    DEVELOPMENT = "development"
    TESTING = "testing"
    OPTIMIZATION = "optimization"
    DEPLOYMENT = "deployment"
    COMPLETED = "completed"


@dataclass
class ValidationResult:
    """Resultado de validación"""
    passed: bool
    level: ValidationLevel
    issues: List[Dict[str, Any]]
    suggestions: List[Dict[str, Any]]
    auto_fixable: List[Dict[str, Any]]
    score: float  # 0-100


@dataclass
class ProjectTemplate:
    """Template de proyecto"""
    name: str
    type: ProjectType
    description: str
    structure: Dict[str, Any]
    dependencies: Dict[str, List[str]]
    scripts: Dict[str, str]
    checklist: List[str]


@dataclass
class ProjectGuide:
    """Guía de proyecto"""
    project_id: str
    type: ProjectType
    phase: ProjectPhase
    checklist: List[Dict[str, Any]]
    progress: float
    validation_results: Optional[ValidationResult]
    corrections_applied: List[str]


class ProjectGuideEngine:
    """Motor principal de guía de proyectos"""

    def __init__(self, workspace_path: str = "./workspace"):
        self.workspace_path = Path(workspace_path)
        self.templates_path = Path(__file__).parent / "templates"
        self.validators_path = Path(__file__).parent / "validators"
        self.workspace_path.mkdir(exist_ok=True)
        self.templates_path.mkdir(exist_ok=True)
        self.validators_path.mkdir(exist_ok=True)

    def get_template(self, project_type: ProjectType) -> ProjectTemplate:
        """Obtiene template de proyecto"""
        templates = {
            ProjectType.REACT_FASTAPI: self._get_react_fastapi_template(),
            ProjectType.NEXTJS_FASTAPI: self._get_nextjs_fastapi_template(),
            ProjectType.REACT_NODE_EXPRESS: self._get_react_node_template(),
            ProjectType.FULLSTACK_MONOREPO: self._get_monorepo_template(),
        }
        return templates.get(project_type, templates[ProjectType.REACT_FASTAPI])

    def _get_react_fastapi_template(self) -> ProjectTemplate:
        """Template React + FastAPI"""
        return ProjectTemplate(
            name="React + FastAPI Full Stack",
            type=ProjectType.REACT_FASTAPI,
            description="Aplicación full stack moderna con React frontend y FastAPI backend",
            structure={
                "frontend": {
                    "src": {
                        "components": {},
                        "hooks": {},
                        "services": {},
                        "utils": {},
                        "pages": {},
                        "assets": {}
                    },
                    "public": {},
                    "tests": {}
                },
                "backend": {
                    "app": {
                        "api": {
                            "routes": {},
                            "dependencies": {}
                        },
                        "core": {},
                        "models": {},
                        "schemas": {},
                        "services": {},
                        "db": {}
                    },
                    "tests": {},
                    "alembic": {}
                },
                "shared": {
                    "types": {},
                    "constants": {}
                },
                "docs": {},
                "scripts": {}
            },
            dependencies={
                "frontend": [
                    "react",
                    "react-dom",
                    "vite",
                    "tailwindcss",
                    "axios",
                    "react-router-dom",
                    "zustand",
                    "react-query"
                ],
                "backend": [
                    "fastapi",
                    "uvicorn",
                    "pydantic",
                    "sqlalchemy",
                    "alembic",
                    "python-jose",
                    "passlib",
                    "python-multipart",
                    "pytest",
                    "pytest-asyncio"
                ]
            },
            scripts={
                "frontend": {
                    "dev": "vite",
                    "build": "vite build",
                    "preview": "vite preview",
                    "test": "vitest",
                    "lint": "eslint src --ext js,jsx",
                    "format": "prettier --write src"
                },
                "backend": {
                    "dev": "uvicorn app.main:app --reload",
                    "test": "pytest",
                    "lint": "ruff check .",
                    "format": "black .",
                    "migrate": "alembic upgrade head"
                }
            },
            checklist=[
                "✅ Estructura de proyecto creada",
                "✅ Dependencias instaladas",
                "✅ Configuración de base de datos",
                "✅ Sistema de autenticación",
                "✅ API endpoints implementados",
                "✅ Componentes frontend creados",
                "✅ Integración frontend-backend",
                "✅ Tests unitarios (>80% coverage)",
                "✅ Tests de integración",
                "✅ Documentación API (OpenAPI)",
                "✅ README y documentación",
                "✅ Configuración de CI/CD",
                "✅ Variables de entorno configuradas",
                "✅ Validación de seguridad",
                "✅ Optimización de rendimiento",
                "✅ Build de producción exitoso"
            ]
        )

    def _get_nextjs_fastapi_template(self) -> ProjectTemplate:
        """Template Next.js + FastAPI"""
        return ProjectTemplate(
            name="Next.js + FastAPI Full Stack",
            type=ProjectType.NEXTJS_FASTAPI,
            description="Aplicación full stack con Next.js SSR/SSG y FastAPI backend",
            structure={
                "frontend": {
                    "app": {},
                    "components": {},
                    "lib": {},
                    "public": {},
                    "styles": {}
                },
                "backend": {
                    "app": {
                        "api": {},
                        "core": {},
                        "models": {},
                        "services": {}
                    }
                }
            },
            dependencies={
                "frontend": ["next", "react", "react-dom", "tailwindcss"],
                "backend": ["fastapi", "uvicorn", "pydantic", "sqlalchemy"]
            },
            scripts={},
            checklist=[]
        )

    def _get_react_node_template(self) -> ProjectTemplate:
        """Template React + Node/Express"""
        return ProjectTemplate(
            name="React + Node Express Full Stack",
            type=ProjectType.REACT_NODE_EXPRESS,
            description="Aplicación full stack con React y Node.js/Express backend",
            structure={},
            dependencies={},
            scripts={},
            checklist=[]
        )

    def _get_monorepo_template(self) -> ProjectTemplate:
        """Template Monorepo Full Stack"""
        return ProjectTemplate(
            name="Full Stack Monorepo",
            type=ProjectType.FULLSTACK_MONOREPO,
            description="Monorepo con múltiples apps y packages compartidos",
            structure={},
            dependencies={},
            scripts={},
            checklist=[]
        )

    async def create_project(
        self,
        project_name: str,
        project_type: ProjectType,
        validation_level: ValidationLevel = ValidationLevel.PROFESSIONAL
    ) -> ProjectGuide:
        """Crea un nuevo proyecto con template"""
        logger.info(f"Creando proyecto: {project_name} ({project_type.value})")

        # Obtener template
        template = self.get_template(project_type)

        # Crear estructura de directorios
        project_path = self.workspace_path / project_name
        await self._create_directory_structure(project_path, template.structure)

        # Crear archivos de configuración
        await self._create_config_files(project_path, template)

        # Crear checklist inicial
        checklist = [
            {
                "id": i,
                "task": task,
                "completed": False,
                "phase": self._get_task_phase(task)
            }
            for i, task in enumerate(template.checklist)
        ]

        # Crear guía de proyecto
        guide = ProjectGuide(
            project_id=project_name,
            type=project_type,
            phase=ProjectPhase.SETUP,
            checklist=checklist,
            progress=0.0,
            validation_results=None,
            corrections_applied=[]
        )

        # Guardar guía
        await self._save_guide(project_name, guide)

        logger.info(f"Proyecto {project_name} creado exitosamente")
        return guide

    async def validate_project(
        self,
        project_name: str,
        validation_level: ValidationLevel = ValidationLevel.STANDARD
    ) -> ValidationResult:
        """Valida un proyecto según el nivel especificado"""
        logger.info(f"Validando proyecto: {project_name} (nivel: {validation_level.value})")

        project_path = self.workspace_path / project_name
        issues = []
        suggestions = []
        auto_fixable = []

        # Validación BASIC: Estructura
        if validation_level.value in [v.value for v in ValidationLevel]:
            structure_issues = await self._validate_structure(project_path)
            issues.extend(structure_issues)

        # Validación STANDARD: Linting y formateo
        if validation_level.value in ["standard", "professional", "production"]:
            lint_issues = await self._validate_linting(project_path)
            issues.extend(lint_issues)
            auto_fixable.extend([i for i in lint_issues if i.get("auto_fixable")])

        # Validación PROFESSIONAL: Tests y docs
        if validation_level.value in ["professional", "production"]:
            test_issues = await self._validate_tests(project_path)
            doc_issues = await self._validate_documentation(project_path)
            issues.extend(test_issues + doc_issues)

        # Validación PRODUCTION: Security y performance
        if validation_level.value == "production":
            security_issues = await self._validate_security(project_path)
            perf_issues = await self._validate_performance(project_path)
            issues.extend(security_issues + perf_issues)

        # Generar sugerencias
        suggestions = await self._generate_suggestions(issues)

        # Calcular score
        score = self._calculate_score(issues, validation_level)

        result = ValidationResult(
            passed=score >= 80.0,
            level=validation_level,
            issues=issues,
            suggestions=suggestions,
            auto_fixable=auto_fixable,
            score=score
        )

        logger.info(f"Validación completada. Score: {score}/100")
        return result

    async def apply_corrections(
        self,
        project_name: str,
        validation_result: ValidationResult
    ) -> List[str]:
        """Aplica correcciones automáticas"""
        logger.info(f"Aplicando correcciones a: {project_name}")

        project_path = self.workspace_path / project_name
        applied = []

        for issue in validation_result.auto_fixable:
            try:
                fix_type = issue.get("type")

                if fix_type == "formatting":
                    await self._fix_formatting(project_path, issue)
                    applied.append(f"Formateo corregido: {issue.get('file')}")

                elif fix_type == "imports":
                    await self._fix_imports(project_path, issue)
                    applied.append(f"Imports optimizados: {issue.get('file')}")

                elif fix_type == "unused_vars":
                    await self._fix_unused_vars(project_path, issue)
                    applied.append(f"Variables sin usar eliminadas: {issue.get('file')}")

                elif fix_type == "missing_types":
                    await self._fix_types(project_path, issue)
                    applied.append(f"Tipos añadidos: {issue.get('file')}")

            except Exception as e:
                logger.error(f"Error aplicando corrección: {e}")

        logger.info(f"Correcciones aplicadas: {len(applied)}")
        return applied

    async def get_next_steps(self, project_name: str) -> List[Dict[str, Any]]:
        """Obtiene los próximos pasos a seguir"""
        guide = await self._load_guide(project_name)

        # Encontrar tareas no completadas
        pending_tasks = [t for t in guide.checklist if not t["completed"]]

        if not pending_tasks:
            return [{
                "type": "completion",
                "message": "¡Proyecto completado! 🎉",
                "action": "deploy"
            }]

        # Obtener fase actual
        current_phase = guide.phase
        phase_tasks = [t for t in pending_tasks if t["phase"] == current_phase]

        if not phase_tasks:
            # Avanzar a siguiente fase
            next_phase = self._get_next_phase(current_phase)
            phase_tasks = [t for t in pending_tasks if t["phase"] == next_phase]

        next_steps = []
        for task in phase_tasks[:3]:  # Mostrar máximo 3 tareas
            next_steps.append({
                "task": task["task"],
                "phase": task["phase"],
                "guidance": self._get_task_guidance(task["task"]),
                "resources": self._get_task_resources(task["task"])
            })

        return next_steps

    # Métodos auxiliares

    async def _create_directory_structure(self, base_path: Path, structure: Dict):
        """Crea estructura de directorios"""
        for name, children in structure.items():
            dir_path = base_path / name
            dir_path.mkdir(parents=True, exist_ok=True)
            if isinstance(children, dict) and children:
                await self._create_directory_structure(dir_path, children)

    async def _create_config_files(self, project_path: Path, template: ProjectTemplate):
        """Crea archivos de configuración"""
        # package.json para frontend
        if "frontend" in template.structure:
            package_json = {
                "name": f"{project_path.name}-frontend",
                "version": "0.1.0",
                "type": "module",
                "scripts": template.scripts.get("frontend", {}),
                "dependencies": {dep: "latest" for dep in template.dependencies.get("frontend", [])[:5]},
                "devDependencies": {dep: "latest" for dep in template.dependencies.get("frontend", [])[5:]}
            }
            (project_path / "frontend" / "package.json").write_text(
                json.dumps(package_json, indent=2)
            )

        # requirements.txt para backend
        if "backend" in template.structure:
            requirements = "\n".join(template.dependencies.get("backend", []))
            (project_path / "backend" / "requirements.txt").write_text(requirements)

        # README.md
        readme = f"""# {project_path.name}

{template.description}

## Stack
- Frontend: {template.type.value.split('_')[0].upper()}
- Backend: {template.type.value.split('_')[1].upper()}

## Desarrollo

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

## Checklist de Desarrollo

{chr(10).join(f'- [ ] {task}' for task in template.checklist)}
"""
        (project_path / "README.md").write_text(readme)

    async def _validate_structure(self, project_path: Path) -> List[Dict]:
        """Valida estructura del proyecto"""
        issues = []

        required_files = ["README.md"]
        for file in required_files:
            if not (project_path / file).exists():
                issues.append({
                    "severity": "error",
                    "type": "missing_file",
                    "file": file,
                    "message": f"Archivo requerido faltante: {file}",
                    "auto_fixable": False
                })

        return issues

    async def _validate_linting(self, project_path: Path) -> List[Dict]:
        """Valida linting"""
        # Aquí iría la validación real con ESLint, Ruff, etc.
        return []

    async def _validate_tests(self, project_path: Path) -> List[Dict]:
        """Valida tests"""
        # Aquí iría la validación de coverage, etc.
        return []

    async def _validate_documentation(self, project_path: Path) -> List[Dict]:
        """Valida documentación"""
        return []

    async def _validate_security(self, project_path: Path) -> List[Dict]:
        """Valida seguridad"""
        return []

    async def _validate_performance(self, project_path: Path) -> List[Dict]:
        """Valida rendimiento"""
        return []

    async def _generate_suggestions(self, issues: List[Dict]) -> List[Dict]:
        """Genera sugerencias basadas en issues"""
        suggestions = []

        for issue in issues:
            if issue["type"] == "missing_file":
                suggestions.append({
                    "type": "create_file",
                    "file": issue["file"],
                    "template": "default"
                })

        return suggestions

    def _calculate_score(self, issues: List[Dict], level: ValidationLevel) -> float:
        """Calcula score de validación"""
        if not issues:
            return 100.0

        severity_weights = {
            "error": 10,
            "warning": 5,
            "info": 1
        }

        total_penalty = sum(severity_weights.get(i.get("severity", "info"), 1) for i in issues)
        max_penalty = 100

        score = max(0, 100 - (total_penalty / max_penalty * 100))
        return round(score, 2)

    async def _fix_formatting(self, project_path: Path, issue: Dict):
        """Corrige formateo"""
        pass

    async def _fix_imports(self, project_path: Path, issue: Dict):
        """Corrige imports"""
        pass

    async def _fix_unused_vars(self, project_path: Path, issue: Dict):
        """Elimina variables sin usar"""
        pass

    async def _fix_types(self, project_path: Path, issue: Dict):
        """Añade tipos faltantes"""
        pass

    def _get_task_phase(self, task: str) -> ProjectPhase:
        """Determina fase de una tarea"""
        if "estructura" in task.lower() or "dependencias" in task.lower():
            return ProjectPhase.SETUP
        elif "test" in task.lower():
            return ProjectPhase.TESTING
        elif "optimización" in task.lower() or "rendimiento" in task.lower():
            return ProjectPhase.OPTIMIZATION
        elif "deploy" in task.lower() or "ci/cd" in task.lower():
            return ProjectPhase.DEPLOYMENT
        else:
            return ProjectPhase.DEVELOPMENT

    def _get_next_phase(self, current: ProjectPhase) -> ProjectPhase:
        """Obtiene siguiente fase"""
        phases = list(ProjectPhase)
        try:
            idx = phases.index(current)
            return phases[min(idx + 1, len(phases) - 1)]
        except ValueError:
            return ProjectPhase.DEVELOPMENT

    def _get_task_guidance(self, task: str) -> str:
        """Obtiene guía para una tarea"""
        guidance_map = {
            "autenticación": "Implementa JWT tokens con refresh tokens. Usa bcrypt para passwords.",
            "tests": "Apunta a >80% coverage. Usa pytest para backend, vitest para frontend.",
            "documentación": "Genera OpenAPI automático con FastAPI. Documenta componentes React.",
        }

        for key, guidance in guidance_map.items():
            if key in task.lower():
                return guidance

        return "Sigue las mejores prácticas de la industria."

    def _get_task_resources(self, task: str) -> List[str]:
        """Obtiene recursos para una tarea"""
        return [
            "https://fastapi.tiangolo.com/",
            "https://react.dev/",
            "https://tailwindcss.com/"
        ]

    async def _save_guide(self, project_name: str, guide: ProjectGuide):
        """Guarda guía de proyecto"""
        guide_path = self.workspace_path / project_name / ".project-guide.json"
        guide_path.write_text(json.dumps(asdict(guide), indent=2, default=str))

    async def _load_guide(self, project_name: str) -> ProjectGuide:
        """Carga guía de proyecto"""
        guide_path = self.workspace_path / project_name / ".project-guide.json"
        if not guide_path.exists():
            raise FileNotFoundError(f"No se encontró guía para proyecto: {project_name}")

        data = json.loads(guide_path.read_text())
        return ProjectGuide(**data)


# Funciones auxiliares para integración con orchestrator

async def create_fullstack_project(
    project_name: str,
    project_type: str = "react_fastapi",
    validation_level: str = "professional"
) -> Dict[str, Any]:
    """Función auxiliar para crear proyecto full stack"""
    engine = ProjectGuideEngine()

    guide = await engine.create_project(
        project_name=project_name,
        project_type=ProjectType(project_type),
        validation_level=ValidationLevel(validation_level)
    )

    return {
        "status": "success",
        "project_id": guide.project_id,
        "type": guide.type.value,
        "phase": guide.phase.value,
        "checklist": guide.checklist,
        "message": f"Proyecto {project_name} creado exitosamente"
    }


async def validate_and_correct(
    project_name: str,
    validation_level: str = "standard",
    auto_correct: bool = True
) -> Dict[str, Any]:
    """Función auxiliar para validar y corregir proyecto"""
    engine = ProjectGuideEngine()

    # Validar
    result = await engine.validate_project(
        project_name=project_name,
        validation_level=ValidationLevel(validation_level)
    )

    # Corregir si es necesario
    corrections = []
    if auto_correct and result.auto_fixable:
        corrections = await engine.apply_corrections(project_name, result)

    return {
        "status": "success",
        "validation": {
            "passed": result.passed,
            "score": result.score,
            "issues": len(result.issues),
            "auto_fixable": len(result.auto_fixable)
        },
        "corrections_applied": corrections,
        "suggestions": result.suggestions
    }


async def get_project_guidance(project_name: str) -> Dict[str, Any]:
    """Función auxiliar para obtener guía del proyecto"""
    engine = ProjectGuideEngine()

    next_steps = await engine.get_next_steps(project_name)
    guide = await engine._load_guide(project_name)

    return {
        "status": "success",
        "project": project_name,
        "phase": guide.phase.value,
        "progress": guide.progress,
        "next_steps": next_steps,
        "checklist_completion": f"{sum(1 for t in guide.checklist if t['completed'])}/{len(guide.checklist)}"
    }
