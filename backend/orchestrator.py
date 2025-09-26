#!/usr/bin/env python3
"""
AI-Bridge Core Orchestration Engine
Central brain that converts human objectives into autonomous collaboration between specialized AI agents.

Architecture:
- AgentOrchestrator: Manages agent lifecycle and coordination
- AgentA: Frontend specialist (Claude API)
- AgentB: Backend specialist (OpenAI GPT-5 API) 
- Communication pipeline with structured messaging
- Workflow engine with automatic cycles
"""

import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Import agent classes and communication system
from agents import AgentA, AgentB, AgentRole, AgentStatus
from communication import MessageBus, Message, MessageType
from workflow import WorkflowEngine, WorkflowState, WorkflowPhase

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OrchestrationState(Enum):
    """Orchestration lifecycle states"""
    IDLE = "idle"
    INITIALIZING = "initializing" 
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"

@dataclass
class OrchestrationConfig:
    """Configuration for orchestration session"""
    max_iterations: int = 50
    timeout_minutes: int = 60
    auto_approve: bool = True
    logging_level: str = "INFO"
    workspace_dir: str = "workspace"
    save_conversations: bool = True
    enable_reflection: bool = True
    conflict_resolution: str = "agent_a_priority"  # or "agent_b_priority", "human_intervention"

@dataclass
class OrchestrationSession:
    """Represents an active orchestration session"""
    id: str
    objective: str
    config: OrchestrationConfig
    state: OrchestrationState
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    current_iteration: int = 0
    agents_status: Dict[str, AgentStatus] = None
    workspace_path: Path = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.agents_status is None:
            self.agents_status = {"agent_a": AgentStatus.IDLE, "agent_b": AgentStatus.IDLE}
        if self.workspace_path is None:
            self.workspace_path = Path(self.config.workspace_dir) / f"session_{self.id}"

class AgentOrchestrator:
    """
    Central orchestration engine that manages autonomous collaboration between specialized AI agents.
    
    Responsibilities:
    - Manage agent lifecycle (start, pause, stop)
    - Coordinate bidirectional communication flow
    - Monitor workflow progress and completion criteria
    - Handle conflicts and error recovery
    - Maintain global project state
    """
    
    def __init__(self, config: Optional[OrchestrationConfig] = None):
        self.config = config or OrchestrationConfig()
        self.session: Optional[OrchestrationSession] = None
        self.message_bus = MessageBus()
        self.workflow_engine = WorkflowEngine()
        
        # Initialize agents
        self.agent_a = AgentA(role=AgentRole.FRONTEND)
        self.agent_b = AgentB(role=AgentRole.BACKEND)
        
        # Session storage
        self.sessions_dir = Path("sessions")
        self.sessions_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        logger.info("AgentOrchestrator initialized")
    
    def _setup_logging(self):
        """Configure structured logging with timestamps and context"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create session-specific handler
        if self.session:
            session_log = log_dir / f"orchestration_{self.session.id}.log"
            handler = logging.FileHandler(session_log)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - [%(levelname)s] - SESSION:%(session_id)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
    
    async def start_orchestration(self, objective: str, config: Optional[OrchestrationConfig] = None) -> str:
        """
        Start a new orchestration session with the given objective.
        
        Args:
            objective: Human-readable goal for the agent collaboration
            config: Optional configuration overrides
            
        Returns:
            Session ID for tracking
        """
        try:
            # Create new session
            session_config = config or self.config
            session_id = str(uuid.uuid4())
            
            self.session = OrchestrationSession(
                id=session_id,
                objective=objective,
                config=session_config,
                state=OrchestrationState.INITIALIZING,
                created_at=datetime.now(timezone.utc)
            )
            
            # Setup workspace
            self.session.workspace_path.mkdir(parents=True, exist_ok=True)
            
            # Save session
            await self._save_session()
            
            logger.info(f"Starting orchestration session {session_id} with objective: {objective}")
            
            # Initialize agents with context
            await self._initialize_agents()
            
            # Start workflow engine
            await self.workflow_engine.start_workflow(objective, self.session.workspace_path)
            
            # Begin orchestration loop
            self.session.state = OrchestrationState.RUNNING
            self.session.started_at = datetime.now(timezone.utc)
            await self._save_session()
            
            # Run the main orchestration loop in background
            asyncio.create_task(self._orchestration_loop())
            
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to start orchestration: {e}")
            if self.session:
                self.session.state = OrchestrationState.FAILED
                self.session.error_message = str(e)
                await self._save_session()
            raise
    
    async def _initialize_agents(self):
        """Initialize both agents with session context and roles"""
        try:
            # Validate environment first
            await self._validate_environment()
            
            # Setup Agent A (Frontend specialist with Claude) usando ARQUITECTURA CENTRALIZADA
            agent_a_context = {
                "role": "frontend_specialist",
                "objective": self.session.objective,
                "workspace": str(self.session.workspace_path),
                "session_id": self.session.id,
                "specialization": "Frontend development, UI/UX, React, Vue, Angular, styling, user experience"
            }
            
            logger.info("Initializing Agent A (Frontend specialist) with CENTRALIZED architecture...")
            agent_a_success = await self.agent_a.initialize(agent_a_context)
            if not agent_a_success:
                self.session.agents_status["agent_a"] = AgentStatus.ERROR
                raise RuntimeError("Agent A (Frontend) initialization failed - check API keys and configuration")
            
            # REGISTRAR Agent A con MessageBus CENTRALIZADO
            logger.info("Registering Agent A with centralized MessageBus...")
            agent_a_registered = self.agent_a.register_with_messagebus(self.message_bus)
            if not agent_a_registered:
                self.session.agents_status["agent_a"] = AgentStatus.ERROR
                raise RuntimeError("Agent A failed to register with centralized MessageBus")
            
            self.session.agents_status["agent_a"] = AgentStatus.ACTIVE
            logger.info("Agent A initialized and registered with centralized MessageBus")
            
            # Setup Agent B (Backend specialist with GPT-5) usando ARQUITECTURA CENTRALIZADA
            agent_b_context = {
                "role": "backend_specialist", 
                "objective": self.session.objective,
                "workspace": str(self.session.workspace_path),
                "session_id": self.session.id,
                "specialization": "Backend development, APIs, databases, server architecture, security"
            }
            
            logger.info("Initializing Agent B (Backend specialist) with CENTRALIZED architecture...")
            agent_b_success = await self.agent_b.initialize(agent_b_context)
            if not agent_b_success:
                self.session.agents_status["agent_b"] = AgentStatus.ERROR
                raise RuntimeError("Agent B (Backend) initialization failed - check API keys and configuration")
            
            # REGISTRAR Agent B con MessageBus CENTRALIZADO
            logger.info("Registering Agent B with centralized MessageBus...")
            agent_b_registered = self.agent_b.register_with_messagebus(self.message_bus)
            if not agent_b_registered:
                self.session.agents_status["agent_b"] = AgentStatus.ERROR
                raise RuntimeError("Agent B failed to register with centralized MessageBus")
            
            self.session.agents_status["agent_b"] = AgentStatus.ACTIVE
            logger.info("Agent B initialized and registered with centralized MessageBus")
            
            logger.info("Both agents initialized successfully")
            
        except Exception as e:
            logger.error(f"Agent initialization failed: {e}")
            # Set both agents to error state if initialization fails
            self.session.agents_status["agent_a"] = AgentStatus.ERROR
            self.session.agents_status["agent_b"] = AgentStatus.ERROR
            raise
    
    async def _validate_environment(self):
        """Validate that required environment variables and API keys are present"""
        missing_keys = []
        
        # Check for Anthropic API key (for Agent A)
        if not os.environ.get('ANTHROPIC_API_KEY'):
            missing_keys.append('ANTHROPIC_API_KEY')
            
        # Check for OpenAI API key (for Agent B)  
        if not os.environ.get('OPENAI_API_KEY'):
            missing_keys.append('OPENAI_API_KEY')
            
        if missing_keys:
            error_msg = f"Missing required API keys: {', '.join(missing_keys)}. Set these environment variables before starting orchestration."
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        logger.info("Environment validation passed - all required API keys are present")
    
    async def _orchestration_loop(self):
        """
        Main orchestration loop that coordinates agent collaboration.
        
        Flow: Planning → Implementation → Review → Iteration
        """
        try:
            while (self.session.state == OrchestrationState.RUNNING and 
                   self.session.current_iteration < self.config.max_iterations):
                
                self.session.current_iteration += 1
                logger.info(f"Orchestration iteration {self.session.current_iteration}")
                
                # Defensive check: verify session and workflow state
                if not self.session:
                    logger.error("Session is None, cannot continue orchestration")
                    break
                
                if not self.workflow_engine:
                    logger.error("Workflow engine is None, cannot continue orchestration")
                    self.session.state = OrchestrationState.FAILED
                    self.session.error_message = "Workflow engine is not available"
                    break
                
                # Check workflow state with error handling
                try:
                    workflow_state = await self.workflow_engine.get_state()
                    if not workflow_state:
                        logger.error("Workflow state is None, stopping orchestration")
                        self.session.state = OrchestrationState.FAILED
                        self.session.error_message = "Unable to get workflow state"
                        break
                    
                    # Defensive check: ensure current_phase exists
                    if not hasattr(workflow_state, 'current_phase'):
                        logger.error("Workflow state has no current_phase attribute")
                        self.session.state = OrchestrationState.FAILED
                        self.session.error_message = "Invalid workflow state structure"
                        break
                        
                except Exception as e:
                    logger.error(f"Failed to get workflow state: {e}")
                    self.session.state = OrchestrationState.FAILED
                    self.session.error_message = f"Workflow state error: {e}"
                    break
                
                # Verify agents are still active
                if (self.session.agents_status.get("agent_a") == AgentStatus.ERROR or 
                    self.session.agents_status.get("agent_b") == AgentStatus.ERROR):
                    logger.error("One or more agents are in ERROR state, stopping orchestration")
                    self.session.state = OrchestrationState.FAILED
                    self.session.error_message = "Agent failure detected during orchestration"
                    break
                
                # Process current workflow phase with error handling
                try:
                    if workflow_state.current_phase == WorkflowPhase.PLANNING:
                        await self._planning_phase()
                    elif workflow_state.current_phase == WorkflowPhase.IMPLEMENTATION:
                        await self._implementation_phase()
                    elif workflow_state.current_phase == WorkflowPhase.REVIEW:
                        await self._review_phase()
                    elif workflow_state.current_phase == WorkflowPhase.COMPLETED:
                        await self._complete_orchestration()
                        break
                    else:
                        logger.warning(f"Unknown workflow phase: {workflow_state.current_phase}")
                        
                except Exception as e:
                    logger.error(f"Error in orchestration phase {workflow_state.current_phase}: {e}")
                    self.session.state = OrchestrationState.FAILED
                    self.session.error_message = f"Phase execution error: {e}"
                    break
                
                # Check for completion criteria
                try:
                    if await self._check_completion_criteria():
                        await self._complete_orchestration()
                        break
                except Exception as e:
                    logger.error(f"Error checking completion criteria: {e}")
                    # Continue execution, this is not fatal
                
                # Check for conflicts or blocks
                try:
                    if await self._detect_conflicts():
                        await self._resolve_conflicts()
                except Exception as e:
                    logger.error(f"Error in conflict detection/resolution: {e}")
                    # Continue execution, this is not fatal
                
                # Save session state
                try:
                    await self._save_session()
                except Exception as e:
                    logger.error(f"Failed to save session state: {e}")
                    # Continue execution, but log the error
                
                # Brief pause between iterations
                await asyncio.sleep(1)
            
            # Handle max iterations reached
            if self.session.current_iteration >= self.config.max_iterations:
                logger.warning("Max iterations reached, stopping orchestration")
                self.session.state = OrchestrationState.COMPLETED
                self.session.error_message = "Max iterations reached"
                
        except Exception as e:
            logger.error(f"Orchestration loop failed: {e}")
            self.session.state = OrchestrationState.FAILED
            self.session.error_message = str(e)
        finally:
            await self._save_session()
    
    async def _planning_phase(self):
        """Coordinate planning between agents"""
        logger.info("Entering planning phase")
        
        # Agent A creates frontend plan
        frontend_plan_msg = Message(
            type=MessageType.TASK,
            sender="orchestrator",
            recipient="agent_a",
            content=f"Create a detailed frontend implementation plan for: {self.session.objective}",
            session_id=self.session.id
        )
        
        await self.message_bus.send_message(frontend_plan_msg)
        frontend_plan = await self.agent_a.process_message(frontend_plan_msg)
        
        # Agent B creates backend plan  
        backend_plan_msg = Message(
            type=MessageType.TASK,
            sender="orchestrator", 
            recipient="agent_b",
            content=f"Create a detailed backend implementation plan for: {self.session.objective}. Consider frontend plan: {frontend_plan.content}",
            session_id=self.session.id
        )
        
        await self.message_bus.send_message(backend_plan_msg)
        backend_plan = await self.agent_b.process_message(backend_plan_msg)
        
        # Coordinate plans
        coordination_msg = Message(
            type=MessageType.COORDINATION,
            sender="orchestrator",
            recipient="both",
            content=f"Coordinate your plans. Frontend: {frontend_plan.content}. Backend: {backend_plan.content}",
            session_id=self.session.id
        )
        
        await self.message_bus.send_message(coordination_msg)
        
        # Advance workflow
        await self.workflow_engine.advance_phase(WorkflowPhase.IMPLEMENTATION)
    
    async def _implementation_phase(self):
        """Coordinate implementation work between agents"""
        logger.info("Entering implementation phase")
        
        # Both agents work in parallel with cross-communication
        implementation_tasks = []
        
        # Agent A implements frontend
        frontend_task = asyncio.create_task(
            self._agent_implementation_cycle(self.agent_a, "frontend")
        )
        implementation_tasks.append(frontend_task)
        
        # Agent B implements backend
        backend_task = asyncio.create_task(
            self._agent_implementation_cycle(self.agent_b, "backend")
        )
        implementation_tasks.append(backend_task)
        
        # Wait for both to complete current cycle
        await asyncio.gather(*implementation_tasks)
        
        # Cross-agent communication
        await self._facilitate_cross_communication()
        
        # Advance to review if both agents report completion
        if await self._check_implementation_completion():
            await self.workflow_engine.advance_phase(WorkflowPhase.REVIEW)
    
    async def _agent_implementation_cycle(self, agent: Union[AgentA, AgentB], domain: str):
        """Run implementation cycle for a specific agent"""
        try:
            implementation_msg = Message(
                type=MessageType.IMPLEMENTATION,
                sender="orchestrator",
                recipient=f"agent_{'a' if domain == 'frontend' else 'b'}",
                content=f"Implement your {domain} solution. Report progress and any blockers.",
                session_id=self.session.id
            )
            
            await self.message_bus.send_message(implementation_msg)
            response = await agent.process_message(implementation_msg)
            
            # Log agent response
            logger.info(f"Agent {domain} implementation response: {response.content[:200]}...")
            
        except Exception as e:
            logger.error(f"Agent {domain} implementation cycle failed: {e}")
    
    async def _facilitate_cross_communication(self):
        """Enable agents to communicate and coordinate their work"""
        try:
            # Get latest outputs from both agents
            agent_a_output = await self.agent_a.get_latest_output()
            agent_b_output = await self.agent_b.get_latest_output()
            
            # Send Agent A's output to Agent B
            cross_msg_a_to_b = Message(
                type=MessageType.CROSS_COMMUNICATION,
                sender="agent_a",
                recipient="agent_b", 
                content=f"Frontend update: {agent_a_output}",
                session_id=self.session.id
            )
            
            await self.message_bus.send_message(cross_msg_a_to_b)
            await self.agent_b.process_message(cross_msg_a_to_b)
            
            # Send Agent B's output to Agent A
            cross_msg_b_to_a = Message(
                type=MessageType.CROSS_COMMUNICATION,
                sender="agent_b",
                recipient="agent_a",
                content=f"Backend update: {agent_b_output}",
                session_id=self.session.id
            )
            
            await self.message_bus.send_message(cross_msg_b_to_a)
            await self.agent_a.process_message(cross_msg_b_to_a)
            
            logger.info("Cross-agent communication completed")
            
        except Exception as e:
            logger.error(f"Cross-communication failed: {e}")
    
    async def _review_phase(self):
        """Coordinate review and validation of the implementation"""
        logger.info("Entering review phase")
        
        # Both agents review the complete solution
        review_msg = Message(
            type=MessageType.REVIEW,
            sender="orchestrator",
            recipient="both",
            content="Review the complete solution. Check integration points, identify issues, and suggest improvements.",
            session_id=self.session.id
        )
        
        await self.message_bus.send_message(review_msg)
        
        # Get reviews from both agents
        agent_a_review = await self.agent_a.process_message(review_msg)
        agent_b_review = await self.agent_b.process_message(review_msg)
        
        # Analyze reviews for completion or needed iterations
        if await self._analyze_reviews(agent_a_review, agent_b_review):
            await self.workflow_engine.advance_phase(WorkflowPhase.COMPLETED)
        else:
            # Need more iterations
            await self.workflow_engine.advance_phase(WorkflowPhase.IMPLEMENTATION)
    
    async def _check_completion_criteria(self) -> bool:
        """Check if the orchestration objective has been met"""
        try:
            # Check workspace for deliverables
            if not self.session.workspace_path.exists():
                return False
            
            # Basic file structure checks
            has_files = any(self.session.workspace_path.iterdir())
            
            # Check agent status
            both_agents_completed = (
                self.session.agents_status.get("agent_a") == AgentStatus.COMPLETED and
                self.session.agents_status.get("agent_b") == AgentStatus.COMPLETED
            )
            
            # Check workflow completion
            workflow_completed = await self.workflow_engine.is_completed()
            
            return has_files and (both_agents_completed or workflow_completed)
            
        except Exception as e:
            logger.error(f"Error checking completion criteria: {e}")
            return False
    
    async def _detect_conflicts(self) -> bool:
        """Detect conflicts or blockers between agents"""
        try:
            # Check for agent errors
            agent_a_status = await self.agent_a.get_status()
            agent_b_status = await self.agent_b.get_status()
            
            if agent_a_status == AgentStatus.ERROR or agent_b_status == AgentStatus.ERROR:
                return True
            
            # Check message bus for conflict indicators
            recent_messages = await self.message_bus.get_recent_messages(10)
            conflict_keywords = ["error", "conflict", "blocked", "failed", "cannot"]
            
            for msg in recent_messages:
                if any(keyword in msg.content.lower() for keyword in conflict_keywords):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting conflicts: {e}")
            return False
    
    async def _resolve_conflicts(self):
        """Resolve conflicts between agents using configured strategy"""
        logger.info("Resolving conflicts between agents")
        
        if self.config.conflict_resolution == "agent_a_priority":
            # Agent A decision takes priority
            resolution_msg = Message(
                type=MessageType.CONFLICT_RESOLUTION,
                sender="orchestrator",
                recipient="agent_b",
                content="Conflict detected. Agent A's approach will be prioritized. Please adapt your implementation.",
                session_id=self.session.id
            )
            await self.agent_b.process_message(resolution_msg)
            
        elif self.config.conflict_resolution == "agent_b_priority":
            # Agent B decision takes priority  
            resolution_msg = Message(
                type=MessageType.CONFLICT_RESOLUTION,
                sender="orchestrator",
                recipient="agent_a", 
                content="Conflict detected. Agent B's approach will be prioritized. Please adapt your implementation.",
                session_id=self.session.id
            )
            await self.agent_a.process_message(resolution_msg)
        
        # Reset both agents to active status
        self.session.agents_status["agent_a"] = AgentStatus.ACTIVE
        self.session.agents_status["agent_b"] = AgentStatus.ACTIVE
    
    async def _analyze_reviews(self, review_a: Message, review_b: Message) -> bool:
        """Analyze agent reviews to determine if solution is complete"""
        # Simple keyword analysis for completion indicators
        completion_keywords = ["complete", "finished", "done", "ready", "success"]
        issue_keywords = ["issue", "problem", "bug", "error", "fix"]
        
        a_complete = any(keyword in review_a.content.lower() for keyword in completion_keywords)
        b_complete = any(keyword in review_b.content.lower() for keyword in completion_keywords)
        
        a_issues = any(keyword in review_a.content.lower() for keyword in issue_keywords)
        b_issues = any(keyword in review_b.content.lower() for keyword in issue_keywords)
        
        # Both agents indicate completion and no major issues
        return a_complete and b_complete and not (a_issues or b_issues)
    
    async def _check_implementation_completion(self) -> bool:
        """Check if both agents have completed their implementation tasks"""
        agent_a_status = await self.agent_a.get_status()
        agent_b_status = await self.agent_b.get_status()
        
        return (agent_a_status in [AgentStatus.COMPLETED, AgentStatus.READY] and
                agent_b_status in [AgentStatus.COMPLETED, AgentStatus.READY])
    
    async def _complete_orchestration(self):
        """Complete the orchestration session"""
        logger.info("Completing orchestration session")
        
        self.session.state = OrchestrationState.COMPLETED
        self.session.completed_at = datetime.now(timezone.utc)
        self.session.agents_status["agent_a"] = AgentStatus.COMPLETED
        self.session.agents_status["agent_b"] = AgentStatus.COMPLETED
        
        # Generate final report
        await self._generate_final_report()
        
        # Clean up agents
        await self.agent_a.cleanup()
        await self.agent_b.cleanup()
        
        logger.info(f"Orchestration session {self.session.id} completed successfully")
    
    async def _generate_final_report(self):
        """Generate final report of the orchestration session"""
        try:
            report = {
                "session_id": self.session.id,
                "objective": self.session.objective,
                "status": self.session.state.value,
                "created_at": self.session.created_at.isoformat(),
                "completed_at": self.session.completed_at.isoformat() if self.session.completed_at else None,
                "iterations": self.session.current_iteration,
                "workspace": str(self.session.workspace_path),
                "agents_final_status": self.session.agents_status,
                "message_count": await self.message_bus.get_message_count(),
                "deliverables": await self._list_deliverables()
            }
            
            report_path = self.session.workspace_path / "orchestration_report.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Final report generated: {report_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate final report: {e}")
    
    async def _list_deliverables(self) -> List[str]:
        """List all files created during the orchestration"""
        try:
            deliverables = []
            if self.session.workspace_path.exists():
                for file_path in self.session.workspace_path.rglob("*"):
                    if file_path.is_file():
                        deliverables.append(str(file_path.relative_to(self.session.workspace_path)))
            return deliverables
        except Exception as e:
            logger.error(f"Error listing deliverables: {e}")
            return []
    
    async def _save_session(self):
        """Save session state to disk"""
        try:
            session_file = self.sessions_dir / f"session_{self.session.id}.json"
            session_data = asdict(self.session)
            session_data['created_at'] = self.session.created_at.isoformat()
            if self.session.started_at:
                session_data['started_at'] = self.session.started_at.isoformat()
            if self.session.completed_at:
                session_data['completed_at'] = self.session.completed_at.isoformat()
            session_data['workspace_path'] = str(self.session.workspace_path)
            session_data['state'] = self.session.state.value
            
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
    
    async def pause_orchestration(self) -> bool:
        """Pause the current orchestration session"""
        if not self.session or self.session.state != OrchestrationState.RUNNING:
            return False
        
        try:
            self.session.state = OrchestrationState.PAUSED
            await self.agent_a.pause()
            await self.agent_b.pause()
            await self._save_session()
            logger.info(f"Orchestration session {self.session.id} paused")
            return True
        except Exception as e:
            logger.error(f"Failed to pause orchestration: {e}")
            return False
    
    async def resume_orchestration(self) -> bool:
        """Resume a paused orchestration session"""
        if not self.session or self.session.state != OrchestrationState.PAUSED:
            return False
        
        try:
            self.session.state = OrchestrationState.RUNNING
            await self.agent_a.resume()
            await self.agent_b.resume()
            await self._save_session()
            
            # Continue orchestration loop
            asyncio.create_task(self._orchestration_loop())
            
            logger.info(f"Orchestration session {self.session.id} resumed")
            return True
        except Exception as e:
            logger.error(f"Failed to resume orchestration: {e}")
            return False
    
    async def stop_orchestration(self) -> bool:
        """Stop the current orchestration session"""
        if not self.session:
            return False
        
        try:
            self.session.state = OrchestrationState.STOPPED
            await self.agent_a.stop()
            await self.agent_b.stop()
            await self.workflow_engine.stop()
            await self._save_session()
            logger.info(f"Orchestration session {self.session.id} stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop orchestration: {e}")
            return False
    
    async def get_session_status(self) -> Optional[Dict[str, Any]]:
        """Get current session status"""
        if not self.session:
            return None
        
        return {
            "session_id": self.session.id,
            "objective": self.session.objective,
            "state": self.session.state.value,
            "current_iteration": self.session.current_iteration,
            "agents_status": self.session.agents_status,
            "created_at": self.session.created_at.isoformat(),
            "started_at": self.session.started_at.isoformat() if self.session.started_at else None,
            "workspace": str(self.session.workspace_path),
            "error_message": self.session.error_message
        }
    
    async def load_session(self, session_id: str) -> bool:
        """Load an existing session from disk"""
        try:
            session_file = self.sessions_dir / f"session_{session_id}.json"
            if not session_file.exists():
                return False
            
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            # Reconstruct session object
            self.session = OrchestrationSession(
                id=session_data['id'],
                objective=session_data['objective'],
                config=OrchestrationConfig(**session_data['config']),
                state=OrchestrationState(session_data['state']),
                created_at=datetime.fromisoformat(session_data['created_at']),
                started_at=datetime.fromisoformat(session_data['started_at']) if session_data.get('started_at') else None,
                completed_at=datetime.fromisoformat(session_data['completed_at']) if session_data.get('completed_at') else None,
                current_iteration=session_data['current_iteration'],
                agents_status=session_data['agents_status'],
                workspace_path=Path(session_data['workspace_path']),
                error_message=session_data.get('error_message')
            )
            
            logger.info(f"Session {session_id} loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")
            return False