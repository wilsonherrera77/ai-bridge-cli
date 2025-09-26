#!/usr/bin/env python3
"""
Workflow Engine for AI-Bridge Orchestration System

Manages automatic workflow cycles:
- Planning → Implementation → Review → Iteration
- Task completion detection 
- Conflict resolution and blocker handling
- Intelligent completion criteria
- Workflow state persistence
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Configure logging
logger = logging.getLogger(__name__)

class WorkflowPhase(Enum):
    """Workflow execution phases"""
    INITIALIZATION = "initialization"
    PLANNING = "planning"
    IMPLEMENTATION = "implementation"
    REVIEW = "review"
    ITERATION = "iteration"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class WorkflowState(Enum):
    """Overall workflow state"""
    IDLE = "idle"
    RUNNING = "running"
    WAITING = "waiting"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class TaskStatus(Enum):
    """Individual task status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"

@dataclass
class WorkflowTask:
    """Individual task within a workflow"""
    id: str
    name: str
    description: str
    assigned_agent: str
    dependencies: List[str]
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class WorkflowPhaseInfo:
    """Information about a workflow phase"""
    phase: WorkflowPhase
    started_at: datetime
    completed_at: Optional[datetime] = None
    tasks: List[WorkflowTask] = None
    output: Optional[str] = None
    success: bool = False
    
    def __post_init__(self):
        if self.tasks is None:
            self.tasks = []

@dataclass
class WorkflowExecution:
    """Complete workflow execution state"""
    id: str
    objective: str
    workspace_path: Path
    state: WorkflowState
    current_phase: WorkflowPhase
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    phases: Dict[WorkflowPhase, WorkflowPhaseInfo] = None
    all_tasks: List[WorkflowTask] = None
    iteration_count: int = 0
    max_iterations: int = 10
    completion_criteria: Dict[str, Any] = None
    error_log: List[str] = None
    
    def __post_init__(self):
        if self.phases is None:
            self.phases = {}
        if self.all_tasks is None:
            self.all_tasks = []
        if self.completion_criteria is None:
            self.completion_criteria = {}
        if self.error_log is None:
            self.error_log = []

class WorkflowEngine:
    """
    Workflow engine that manages automatic collaboration cycles.
    
    Features:
    - Phase-based workflow execution
    - Task dependency management
    - Completion criteria detection
    - Conflict and blocker resolution
    - Workflow state persistence
    - Performance metrics and reporting
    """
    
    def __init__(self, persistence_dir: Optional[Path] = None):
        self.persistence_dir = persistence_dir or Path("workflows")
        self.persistence_dir.mkdir(exist_ok=True)
        
        self.current_workflow: Optional[WorkflowExecution] = None
        self.workflow_templates: Dict[str, Dict] = {}
        
        # Performance tracking
        self.metrics = {
            "workflows_started": 0,
            "workflows_completed": 0,
            "workflows_failed": 0,
            "average_completion_time": 0.0,
            "total_tasks_executed": 0
        }
        
        # Load default workflow templates
        self._load_default_templates()
        
        logger.info("WorkflowEngine initialized")
    
    def _load_default_templates(self):
        """Load default workflow templates for common scenarios"""
        
        # Full-stack development workflow
        self.workflow_templates["fullstack_development"] = {
            "phases": {
                "planning": [
                    {
                        "name": "analyze_requirements",
                        "description": "Analyze project requirements and create specification",
                        "assigned_agent": "both",
                        "dependencies": []
                    },
                    {
                        "name": "frontend_planning",
                        "description": "Create frontend architecture and component plan",
                        "assigned_agent": "agent_a",
                        "dependencies": ["analyze_requirements"]
                    },
                    {
                        "name": "backend_planning", 
                        "description": "Design backend architecture and API specification",
                        "assigned_agent": "agent_b",
                        "dependencies": ["analyze_requirements"]
                    },
                    {
                        "name": "integration_planning",
                        "description": "Plan frontend-backend integration points",
                        "assigned_agent": "both",
                        "dependencies": ["frontend_planning", "backend_planning"]
                    }
                ],
                "implementation": [
                    {
                        "name": "backend_foundation",
                        "description": "Implement core backend services and APIs",
                        "assigned_agent": "agent_b",
                        "dependencies": []
                    },
                    {
                        "name": "frontend_foundation",
                        "description": "Create frontend foundation and routing",
                        "assigned_agent": "agent_a", 
                        "dependencies": []
                    },
                    {
                        "name": "api_integration",
                        "description": "Connect frontend to backend APIs",
                        "assigned_agent": "both",
                        "dependencies": ["backend_foundation", "frontend_foundation"]
                    },
                    {
                        "name": "feature_implementation",
                        "description": "Implement core features and functionality",
                        "assigned_agent": "both",
                        "dependencies": ["api_integration"]
                    }
                ],
                "review": [
                    {
                        "name": "code_review",
                        "description": "Review code quality and architecture",
                        "assigned_agent": "both",
                        "dependencies": []
                    },
                    {
                        "name": "integration_testing",
                        "description": "Test frontend-backend integration",
                        "assigned_agent": "both",
                        "dependencies": ["code_review"]
                    },
                    {
                        "name": "user_experience_review",
                        "description": "Review user experience and interface",
                        "assigned_agent": "agent_a",
                        "dependencies": ["integration_testing"]
                    }
                ]
            },
            "completion_criteria": {
                "required_files": ["package.json", "requirements.txt"],
                "required_directories": ["frontend", "backend"],
                "functional_tests": True,
                "documentation": True
            }
        }
        
        # Frontend-only workflow
        self.workflow_templates["frontend_development"] = {
            "phases": {
                "planning": [
                    {
                        "name": "ui_ux_planning",
                        "description": "Design user interface and experience",
                        "assigned_agent": "agent_a",
                        "dependencies": []
                    },
                    {
                        "name": "component_architecture",
                        "description": "Plan component structure and state management",
                        "assigned_agent": "agent_a",
                        "dependencies": ["ui_ux_planning"]
                    }
                ],
                "implementation": [
                    {
                        "name": "setup_project",
                        "description": "Setup frontend project structure and dependencies",
                        "assigned_agent": "agent_a",
                        "dependencies": []
                    },
                    {
                        "name": "implement_components",
                        "description": "Implement UI components and functionality",
                        "assigned_agent": "agent_a",
                        "dependencies": ["setup_project"]
                    },
                    {
                        "name": "styling_responsive",
                        "description": "Implement styling and responsive design",
                        "assigned_agent": "agent_a",
                        "dependencies": ["implement_components"]
                    }
                ],
                "review": [
                    {
                        "name": "ui_review",
                        "description": "Review user interface and usability",
                        "assigned_agent": "agent_a",
                        "dependencies": []
                    }
                ]
            }
        }
    
    async def start_workflow(self, objective: str, workspace_path: Path, template: str = "fullstack_development") -> str:
        """
        Start a new workflow execution.
        
        Args:
            objective: The project objective
            workspace_path: Workspace directory
            template: Workflow template to use
            
        Returns:
            Workflow ID
        """
        try:
            workflow_id = str(uuid.uuid4())
            
            # Create workflow execution
            self.current_workflow = WorkflowExecution(
                id=workflow_id,
                objective=objective,
                workspace_path=workspace_path,
                state=WorkflowState.IDLE,
                current_phase=WorkflowPhase.INITIALIZATION,
                created_at=datetime.now(timezone.utc)
            )
            
            # Generate tasks from template
            if template in self.workflow_templates:
                await self._generate_tasks_from_template(template)
            else:
                await self._generate_dynamic_tasks(objective)
            
            # Set completion criteria
            await self._set_completion_criteria(objective, template)
            
            # Start workflow
            self.current_workflow.state = WorkflowState.RUNNING
            self.current_workflow.started_at = datetime.now(timezone.utc)
            self.current_workflow.current_phase = WorkflowPhase.PLANNING
            
            # Create initial phase
            self.current_workflow.phases[WorkflowPhase.PLANNING] = WorkflowPhaseInfo(
                phase=WorkflowPhase.PLANNING,
                started_at=datetime.now(timezone.utc)
            )
            
            await self._save_workflow_state()
            
            self.metrics["workflows_started"] += 1
            logger.info(f"Workflow started: {workflow_id} with objective: {objective}")
            
            return workflow_id
            
        except Exception as e:
            logger.error(f"Failed to start workflow: {e}")
            if self.current_workflow:
                self.current_workflow.state = WorkflowState.FAILED
                self.current_workflow.error_log.append(f"Startup error: {e}")
            raise
    
    async def _generate_tasks_from_template(self, template: str):
        """Generate workflow tasks from a template"""
        try:
            template_data = self.workflow_templates[template]
            
            for phase_name, phase_tasks in template_data["phases"].items():
                phase = WorkflowPhase(phase_name)
                
                if phase not in self.current_workflow.phases:
                    self.current_workflow.phases[phase] = WorkflowPhaseInfo(
                        phase=phase,
                        started_at=datetime.now(timezone.utc)
                    )
                
                for task_data in phase_tasks:
                    task = WorkflowTask(
                        id=str(uuid.uuid4()),
                        name=task_data["name"],
                        description=task_data["description"],
                        assigned_agent=task_data["assigned_agent"],
                        dependencies=task_data["dependencies"],
                        status=TaskStatus.PENDING,
                        created_at=datetime.now(timezone.utc)
                    )
                    
                    self.current_workflow.all_tasks.append(task)
                    self.current_workflow.phases[phase].tasks.append(task)
            
            logger.info(f"Generated {len(self.current_workflow.all_tasks)} tasks from template {template}")
            
        except Exception as e:
            logger.error(f"Error generating tasks from template: {e}")
            raise
    
    async def _generate_dynamic_tasks(self, objective: str):
        """Generate workflow tasks dynamically based on objective analysis"""
        try:
            # Simple dynamic task generation based on keywords in objective
            objective_lower = objective.lower()
            
            planning_tasks = []
            implementation_tasks = []
            review_tasks = []
            
            # Determine if it's frontend, backend, or fullstack
            is_frontend = any(keyword in objective_lower for keyword in ["ui", "frontend", "interface", "website", "app"])
            is_backend = any(keyword in objective_lower for keyword in ["api", "backend", "server", "database"])
            is_fullstack = is_frontend and is_backend
            
            # Generate planning tasks
            planning_tasks.append(WorkflowTask(
                id=str(uuid.uuid4()),
                name="analyze_objective",
                description=f"Analyze the objective: {objective}",
                assigned_agent="both",
                dependencies=[],
                status=TaskStatus.PENDING,
                created_at=datetime.now(timezone.utc)
            ))
            
            if is_frontend or is_fullstack:
                planning_tasks.append(WorkflowTask(
                    id=str(uuid.uuid4()),
                    name="frontend_planning",
                    description="Plan frontend architecture and user interface",
                    assigned_agent="agent_a",
                    dependencies=["analyze_objective"],
                    status=TaskStatus.PENDING,
                    created_at=datetime.now(timezone.utc)
                ))
            
            if is_backend or is_fullstack:
                planning_tasks.append(WorkflowTask(
                    id=str(uuid.uuid4()),
                    name="backend_planning",
                    description="Plan backend architecture and services",
                    assigned_agent="agent_b", 
                    dependencies=["analyze_objective"],
                    status=TaskStatus.PENDING,
                    created_at=datetime.now(timezone.utc)
                ))
            
            # Generate implementation tasks
            if is_frontend or is_fullstack:
                implementation_tasks.append(WorkflowTask(
                    id=str(uuid.uuid4()),
                    name="implement_frontend",
                    description="Implement frontend solution",
                    assigned_agent="agent_a",
                    dependencies=[],
                    status=TaskStatus.PENDING,
                    created_at=datetime.now(timezone.utc)
                ))
            
            if is_backend or is_fullstack:
                implementation_tasks.append(WorkflowTask(
                    id=str(uuid.uuid4()),
                    name="implement_backend",
                    description="Implement backend solution",
                    assigned_agent="agent_b",
                    dependencies=[],
                    status=TaskStatus.PENDING,
                    created_at=datetime.now(timezone.utc)
                ))
            
            # Generate review tasks
            review_tasks.append(WorkflowTask(
                id=str(uuid.uuid4()),
                name="solution_review",
                description="Review complete solution for quality and completeness",
                assigned_agent="both",
                dependencies=[],
                status=TaskStatus.PENDING,
                created_at=datetime.now(timezone.utc)
            ))
            
            # Add tasks to workflow phases
            phases_data = {
                WorkflowPhase.PLANNING: planning_tasks,
                WorkflowPhase.IMPLEMENTATION: implementation_tasks,
                WorkflowPhase.REVIEW: review_tasks
            }
            
            for phase, tasks in phases_data.items():
                self.current_workflow.phases[phase] = WorkflowPhaseInfo(
                    phase=phase,
                    started_at=datetime.now(timezone.utc),
                    tasks=tasks
                )
                self.current_workflow.all_tasks.extend(tasks)
            
            logger.info(f"Generated {len(self.current_workflow.all_tasks)} dynamic tasks")
            
        except Exception as e:
            logger.error(f"Error generating dynamic tasks: {e}")
            raise
    
    async def _set_completion_criteria(self, objective: str, template: str):
        """Set intelligent completion criteria based on objective and template"""
        try:
            criteria = {
                "workspace_has_files": True,
                "min_file_count": 3,
                "required_file_patterns": [],
                "all_tasks_completed": True,
                "no_critical_errors": True,
                "agents_report_completion": True
            }
            
            # Add template-specific criteria
            if template in self.workflow_templates:
                template_criteria = self.workflow_templates[template].get("completion_criteria", {})
                criteria.update(template_criteria)
            
            # Add objective-specific criteria
            objective_lower = objective.lower()
            if "website" in objective_lower or "web app" in objective_lower:
                criteria["required_file_patterns"].extend(["*.html", "*.css", "*.js"])
            if "api" in objective_lower:
                criteria["required_file_patterns"].extend(["*.py", "requirements.txt"])
            
            self.current_workflow.completion_criteria = criteria
            logger.info(f"Set completion criteria: {criteria}")
            
        except Exception as e:
            logger.error(f"Error setting completion criteria: {e}")
    
    async def advance_phase(self, next_phase: WorkflowPhase) -> bool:
        """
        Advance workflow to the next phase.
        
        Args:
            next_phase: The phase to advance to
            
        Returns:
            bool: True if phase was advanced successfully
        """
        try:
            if not self.current_workflow:
                return False
            
            # Complete current phase
            current_phase_info = self.current_workflow.phases.get(self.current_workflow.current_phase)
            if current_phase_info and not current_phase_info.completed_at:
                current_phase_info.completed_at = datetime.now(timezone.utc)
                current_phase_info.success = True
            
            # Update workflow state
            self.current_workflow.current_phase = next_phase
            
            # Create new phase if it doesn't exist
            if next_phase not in self.current_workflow.phases:
                self.current_workflow.phases[next_phase] = WorkflowPhaseInfo(
                    phase=next_phase,
                    started_at=datetime.now(timezone.utc)
                )
            else:
                # Reset phase start time if re-entering
                self.current_workflow.phases[next_phase].started_at = datetime.now(timezone.utc)
            
            # Handle specific phase transitions
            if next_phase == WorkflowPhase.COMPLETED:
                await self._complete_workflow()
            elif next_phase == WorkflowPhase.ITERATION:
                self.current_workflow.iteration_count += 1
                # After iteration, go back to implementation
                if self.current_workflow.iteration_count < self.current_workflow.max_iterations:
                    next_phase = WorkflowPhase.IMPLEMENTATION
                    self.current_workflow.current_phase = next_phase
                else:
                    # Max iterations reached, force completion
                    await self._complete_workflow()
            
            await self._save_workflow_state()
            
            logger.info(f"Advanced workflow to phase: {next_phase.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error advancing workflow phase: {e}")
            return False
    
    async def _complete_workflow(self):
        """Complete the current workflow"""
        try:
            self.current_workflow.state = WorkflowState.COMPLETED
            self.current_workflow.completed_at = datetime.now(timezone.utc)
            
            # Mark all remaining tasks as completed or skipped
            for task in self.current_workflow.all_tasks:
                if task.status == TaskStatus.PENDING:
                    task.status = TaskStatus.SKIPPED
                elif task.status == TaskStatus.IN_PROGRESS:
                    task.status = TaskStatus.COMPLETED
                    task.completed_at = datetime.now(timezone.utc)
            
            # Update metrics
            self.metrics["workflows_completed"] += 1
            if self.current_workflow.started_at:
                completion_time = (self.current_workflow.completed_at - self.current_workflow.started_at).total_seconds()
                self._update_average_completion_time(completion_time)
            
            await self._generate_workflow_report()
            
            logger.info(f"Workflow completed: {self.current_workflow.id}")
            
        except Exception as e:
            logger.error(f"Error completing workflow: {e}")
    
    def _update_average_completion_time(self, completion_time: float):
        """Update the average completion time metric"""
        completed_count = self.metrics["workflows_completed"]
        if completed_count == 1:
            self.metrics["average_completion_time"] = completion_time
        else:
            current_avg = self.metrics["average_completion_time"]
            self.metrics["average_completion_time"] = ((current_avg * (completed_count - 1)) + completion_time) / completed_count
    
    async def check_completion_criteria(self) -> Tuple[bool, List[str]]:
        """
        Check if workflow completion criteria are met.
        
        Returns:
            Tuple of (is_complete, missing_criteria)
        """
        try:
            if not self.current_workflow:
                return False, ["No active workflow"]
            
            criteria = self.current_workflow.completion_criteria
            missing = []
            
            # Check workspace has files
            if criteria.get("workspace_has_files", False):
                if not any(self.current_workflow.workspace_path.iterdir()):
                    missing.append("Workspace is empty")
            
            # Check minimum file count
            min_files = criteria.get("min_file_count", 0)
            if min_files > 0:
                file_count = len(list(self.current_workflow.workspace_path.rglob("*")))
                if file_count < min_files:
                    missing.append(f"Need at least {min_files} files, found {file_count}")
            
            # Check required file patterns
            required_patterns = criteria.get("required_file_patterns", [])
            for pattern in required_patterns:
                if not list(self.current_workflow.workspace_path.rglob(pattern)):
                    missing.append(f"Missing files matching pattern: {pattern}")
            
            # Check all tasks completed
            if criteria.get("all_tasks_completed", False):
                incomplete_tasks = [task for task in self.current_workflow.all_tasks 
                                 if task.status not in [TaskStatus.COMPLETED, TaskStatus.SKIPPED]]
                if incomplete_tasks:
                    missing.append(f"{len(incomplete_tasks)} tasks not completed")
            
            # Check no critical errors
            if criteria.get("no_critical_errors", False):
                if self.current_workflow.error_log:
                    missing.append(f"{len(self.current_workflow.error_log)} errors logged")
            
            is_complete = len(missing) == 0
            return is_complete, missing
            
        except Exception as e:
            logger.error(f"Error checking completion criteria: {e}")
            return False, [f"Error checking criteria: {e}"]
    
    async def get_state(self) -> Optional[WorkflowExecution]:
        """Get current workflow state"""
        return self.current_workflow
    
    async def is_completed(self) -> bool:
        """Check if current workflow is completed"""
        if not self.current_workflow:
            return False
        return self.current_workflow.state == WorkflowState.COMPLETED
    
    async def get_current_tasks(self) -> List[WorkflowTask]:
        """Get tasks for the current phase"""
        if not self.current_workflow or self.current_workflow.current_phase not in self.current_workflow.phases:
            return []
        
        return self.current_workflow.phases[self.current_workflow.current_phase].tasks
    
    async def update_task_status(self, task_id: str, status: TaskStatus, output: Optional[str] = None, error: Optional[str] = None) -> bool:
        """Update status of a specific task"""
        try:
            for task in self.current_workflow.all_tasks:
                if task.id == task_id:
                    task.status = status
                    if status == TaskStatus.IN_PROGRESS and not task.started_at:
                        task.started_at = datetime.now(timezone.utc)
                    elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                        task.completed_at = datetime.now(timezone.utc)
                    
                    if output:
                        task.output = output
                    if error:
                        task.error_message = error
                    
                    await self._save_workflow_state()
                    self.metrics["total_tasks_executed"] += 1
                    
                    logger.info(f"Task {task_id} status updated to {status.value}")
                    return True
            
            logger.warning(f"Task {task_id} not found")
            return False
            
        except Exception as e:
            logger.error(f"Error updating task status: {e}")
            return False
    
    async def detect_blockers(self) -> List[Dict[str, Any]]:
        """Detect workflow blockers and issues"""
        try:
            blockers = []
            
            if not self.current_workflow:
                return blockers
            
            # Check for stuck tasks
            now = datetime.now(timezone.utc)
            for task in self.current_workflow.all_tasks:
                if task.status == TaskStatus.IN_PROGRESS and task.started_at:
                    duration = (now - task.started_at).total_seconds()
                    if duration > 300:  # 5 minutes
                        blockers.append({
                            "type": "stuck_task",
                            "task_id": task.id,
                            "task_name": task.name,
                            "duration": duration
                        })
            
            # Check for failed dependencies
            for task in self.current_workflow.all_tasks:
                if task.status == TaskStatus.PENDING:
                    for dep_name in task.dependencies:
                        dep_task = next((t for t in self.current_workflow.all_tasks if t.name == dep_name), None)
                        if dep_task and dep_task.status == TaskStatus.FAILED:
                            blockers.append({
                                "type": "failed_dependency",
                                "task_id": task.id,
                                "task_name": task.name,
                                "failed_dependency": dep_name
                            })
            
            # Check for long-running phases
            current_phase_info = self.current_workflow.phases.get(self.current_workflow.current_phase)
            if current_phase_info and not current_phase_info.completed_at:
                phase_duration = (now - current_phase_info.started_at).total_seconds()
                if phase_duration > 1800:  # 30 minutes
                    blockers.append({
                        "type": "long_running_phase",
                        "phase": self.current_workflow.current_phase.value,
                        "duration": phase_duration
                    })
            
            return blockers
            
        except Exception as e:
            logger.error(f"Error detecting blockers: {e}")
            return []
    
    async def pause_workflow(self) -> bool:
        """Pause the current workflow"""
        try:
            if self.current_workflow and self.current_workflow.state == WorkflowState.RUNNING:
                self.current_workflow.state = WorkflowState.PAUSED
                await self._save_workflow_state()
                logger.info(f"Workflow paused: {self.current_workflow.id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error pausing workflow: {e}")
            return False
    
    async def resume_workflow(self) -> bool:
        """Resume a paused workflow"""
        try:
            if self.current_workflow and self.current_workflow.state == WorkflowState.PAUSED:
                self.current_workflow.state = WorkflowState.RUNNING
                await self._save_workflow_state()
                logger.info(f"Workflow resumed: {self.current_workflow.id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error resuming workflow: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop the current workflow"""
        try:
            if self.current_workflow:
                self.current_workflow.state = WorkflowState.FAILED
                self.current_workflow.completed_at = datetime.now(timezone.utc)
                await self._save_workflow_state()
                logger.info(f"Workflow stopped: {self.current_workflow.id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error stopping workflow: {e}")
            return False
    
    async def _save_workflow_state(self):
        """Save workflow state to disk"""
        try:
            if not self.current_workflow:
                return
            
            workflow_file = self.persistence_dir / f"workflow_{self.current_workflow.id}.json"
            
            # Convert to serializable format
            workflow_data = asdict(self.current_workflow)
            workflow_data['workspace_path'] = str(self.current_workflow.workspace_path)
            workflow_data['state'] = self.current_workflow.state.value
            workflow_data['current_phase'] = self.current_workflow.current_phase.value
            workflow_data['created_at'] = self.current_workflow.created_at.isoformat()
            if self.current_workflow.started_at:
                workflow_data['started_at'] = self.current_workflow.started_at.isoformat()
            if self.current_workflow.completed_at:
                workflow_data['completed_at'] = self.current_workflow.completed_at.isoformat()
            
            # Convert phases
            phases_data = {}
            for phase, phase_info in self.current_workflow.phases.items():
                phase_data = asdict(phase_info)
                phase_data['phase'] = phase.value
                phase_data['started_at'] = phase_info.started_at.isoformat()
                if phase_info.completed_at:
                    phase_data['completed_at'] = phase_info.completed_at.isoformat()
                
                # Convert tasks
                tasks_data = []
                for task in phase_info.tasks:
                    task_data = asdict(task)
                    task_data['status'] = task.status.value
                    task_data['created_at'] = task.created_at.isoformat()
                    if task.started_at:
                        task_data['started_at'] = task.started_at.isoformat()
                    if task.completed_at:
                        task_data['completed_at'] = task.completed_at.isoformat()
                    tasks_data.append(task_data)
                
                phase_data['tasks'] = tasks_data
                phases_data[phase.value] = phase_data
            
            workflow_data['phases'] = phases_data
            
            # Convert all_tasks
            all_tasks_data = []
            for task in self.current_workflow.all_tasks:
                task_data = asdict(task)
                task_data['status'] = task.status.value
                task_data['created_at'] = task.created_at.isoformat()
                if task.started_at:
                    task_data['started_at'] = task.started_at.isoformat()
                if task.completed_at:
                    task_data['completed_at'] = task.completed_at.isoformat()
                all_tasks_data.append(task_data)
            
            workflow_data['all_tasks'] = all_tasks_data
            
            with open(workflow_file, 'w') as f:
                json.dump(workflow_data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Error saving workflow state: {e}")
    
    async def _generate_workflow_report(self):
        """Generate a comprehensive workflow report"""
        try:
            if not self.current_workflow:
                return
            
            report = {
                "workflow_id": self.current_workflow.id,
                "objective": self.current_workflow.objective,
                "state": self.current_workflow.state.value,
                "duration": None,
                "iteration_count": self.current_workflow.iteration_count,
                "phases_completed": len([p for p in self.current_workflow.phases.values() if p.completed_at]),
                "total_phases": len(self.current_workflow.phases),
                "tasks_completed": len([t for t in self.current_workflow.all_tasks if t.status == TaskStatus.COMPLETED]),
                "tasks_failed": len([t for t in self.current_workflow.all_tasks if t.status == TaskStatus.FAILED]),
                "total_tasks": len(self.current_workflow.all_tasks),
                "errors": self.current_workflow.error_log,
                "workspace_files": []
            }
            
            # Calculate duration
            if self.current_workflow.started_at and self.current_workflow.completed_at:
                duration = self.current_workflow.completed_at - self.current_workflow.started_at
                report["duration"] = duration.total_seconds()
            
            # List workspace files
            try:
                if self.current_workflow.workspace_path.exists():
                    for file_path in self.current_workflow.workspace_path.rglob("*"):
                        if file_path.is_file():
                            report["workspace_files"].append(str(file_path.relative_to(self.current_workflow.workspace_path)))
            except Exception:
                pass
            
            # Save report
            report_file = self.persistence_dir / f"report_{self.current_workflow.id}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Workflow report generated: {report_file}")
            
        except Exception as e:
            logger.error(f"Error generating workflow report: {e}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get workflow engine performance metrics"""
        return {
            **self.metrics,
            "current_workflow_id": self.current_workflow.id if self.current_workflow else None,
            "current_workflow_state": self.current_workflow.state.value if self.current_workflow else None,
            "current_phase": self.current_workflow.current_phase.value if self.current_workflow else None
        }