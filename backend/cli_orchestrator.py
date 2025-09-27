#!/usr/bin/env python3
"""
CLIOrchestrator - Coordination Engine for CLI Terminal Communication
Orchestrates communication between Claude CLI and Codex CLI processes.

Arquitectura sin API Keys:
- Coordina intercambio de mensajes entre terminales CLI reales
- Transforma contexto entre Claude CLI y Codex CLI
- Mantiene flujo conversacional autónomo
- Gestiona handoffs y decisiones de routing
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from terminal_manager import TerminalManager, TerminalType, ProcessStatus
from communication import Message, MessageType, AgentRole

logger = logging.getLogger(__name__)

class OrchestrationMode(Enum):
    """Orchestration operation modes"""
    AUTONOMOUS = "autonomous"        # Fully autonomous agent interaction
    GUIDED = "guided"               # Human-guided interaction
    ALTERNATING = "alternating"     # Strict alternating between agents
    COLLABORATIVE = "collaborative"  # Smart collaborative mode

class ConversationPhase(Enum):
    """Conversation phases in CLI orchestration"""
    INITIALIZATION = "initialization"
    PLANNING = "planning"
    IMPLEMENTATION = "implementation"
    REVIEW = "review"
    REFINEMENT = "refinement"
    COMPLETION = "completion"
    ERROR_HANDLING = "error_handling"

@dataclass
class OrchestrationSession:
    """Active orchestration session between CLI terminals"""
    id: str
    objective: str
    claude_process_id: str
    codex_process_id: str
    mode: OrchestrationMode
    current_phase: ConversationPhase
    created_at: datetime
    message_history: List[Dict[str, Any]]
    current_focus: str
    iteration_count: int = 0
    max_iterations: int = 50
    completion_criteria: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.completion_criteria is None:
            self.completion_criteria = {}

class CLIOrchestrator:
    """
    High-level orchestration engine for CLI terminal communication.
    
    Features:
    - Launch Claude CLI and Codex CLI terminals
    - Coordinate autonomous conversation flow
    - Transform messages between different CLI contexts
    - Manage conversation phases and handoffs
    - Monitor progress toward objective completion
    - Zero API key usage - pure CLI orchestration
    """
    
    def __init__(self, terminal_manager: TerminalManager):
        self.terminal_manager = terminal_manager
        self.active_sessions: Dict[str, OrchestrationSession] = {}
        
        # Context transformation templates
        self.context_transformers = self._initialize_context_transformers()
        
        # Completion detection patterns
        self.completion_patterns = [
            "task completed successfully",
            "implementation finished",
            "project ready for deployment",
            "objective achieved",
            "no further changes needed"
        ]
        
        logger.info("CLIOrchestrator initialized for real terminal coordination")
    
    def _initialize_context_transformers(self) -> Dict[str, str]:
        """Initialize context transformation templates for CLI communication"""
        return {
            "claude_to_codex": """
BACKEND IMPLEMENTATION REQUEST:

**Context**: The frontend specialist (Claude CLI) has completed their analysis and needs backend support.

**Frontend Requirements**:
{frontend_output}

**Implementation Needed**:
- API endpoints: {endpoints}
- Data models: {models} 
- Authentication: {auth}
- Database operations: {database}

**Technical Specifications**:
{technical_specs}

Please implement the backend components to support these frontend requirements.
""",
            
            "codex_to_claude": """
FRONTEND INTEGRATION TASK:

**Context**: The backend specialist (Codex CLI) has implemented the backend components.

**Backend Implementation**:
{backend_output}

**Integration Required**:
- Connect to APIs: {api_endpoints}
- Handle data flow: {data_flow}
- Implement UI components: {ui_components}
- Add error handling: {error_handling}

**Technical Details**:
{technical_details}

Please integrate these backend components into the frontend.
""",
            
            "planning_phase": """
PROJECT PLANNING PHASE

**Objective**: {objective}

**Your Role**: {agent_role}

Please analyze the project requirements and provide:
1. Technical approach for your specialization
2. Key components you'll need to implement
3. Dependencies on the other agent
4. Estimated complexity and timeline
5. Any potential challenges or blockers

Focus on your expertise area and identify collaboration points.
""",
            
            "review_phase": """
REVIEW AND FEEDBACK PHASE

**Context**: Project implementation in progress.

**Current Implementation**:
{current_work}

**Your Task**:
1. Review the implementation for your area of expertise
2. Identify any issues or improvements needed
3. Suggest specific changes or enhancements
4. Verify integration points are working correctly
5. Assess if project objectives are being met

Provide constructive feedback and specific action items.
"""
        }
    
    async def start_orchestration(self, objective: str, mode: OrchestrationMode = OrchestrationMode.AUTONOMOUS) -> str:
        """
        Start a new CLI orchestration session.
        
        Args:
            objective: Project objective to accomplish
            mode: Orchestration mode
            
        Returns:
            Session ID for tracking
        """
        try:
            session_id = str(uuid.uuid4())
            
            logger.info(f"Starting CLI orchestration session: {session_id}")
            logger.info(f"Objective: {objective}")
            logger.info(f"Mode: {mode.value}")
            
            # Launch CLI terminals
            claude_process = await self.terminal_manager.start_terminal(TerminalType.CLAUDE_CLI)
            codex_process = await self.terminal_manager.start_terminal(TerminalType.CODEX_CLI)
            
            logger.info(f"Claude CLI process: {claude_process}")
            logger.info(f"Codex CLI process: {codex_process}")
            
            # Create orchestration session
            session = OrchestrationSession(
                id=session_id,
                objective=objective,
                claude_process_id=claude_process,
                codex_process_id=codex_process,
                mode=mode,
                current_phase=ConversationPhase.INITIALIZATION,
                created_at=datetime.now(timezone.utc),
                message_history=[],
                current_focus=objective
            )
            
            self.active_sessions[session_id] = session
            
            # Start orchestration loop
            asyncio.create_task(self._orchestration_loop(session_id))
            
            logger.info(f"CLI orchestration started successfully: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to start CLI orchestration: {e}")
            raise
    
    async def _orchestration_loop(self, session_id: str):
        """Main orchestration loop for autonomous CLI communication"""
        session = self.active_sessions[session_id]
        
        try:
            logger.info(f"Starting orchestration loop for session: {session_id}")
            
            # Initialize both agents with the objective
            await self._initialize_agents(session)
            
            # Main conversation loop
            while session.iteration_count < session.max_iterations:
                session.iteration_count += 1
                
                logger.info(f"Orchestration iteration {session.iteration_count} - Phase: {session.current_phase.value}")
                
                # Execute current phase
                if session.current_phase == ConversationPhase.INITIALIZATION:
                    await self._handle_initialization_phase(session)
                elif session.current_phase == ConversationPhase.PLANNING:
                    await self._handle_planning_phase(session)
                elif session.current_phase == ConversationPhase.IMPLEMENTATION:
                    await self._handle_implementation_phase(session)
                elif session.current_phase == ConversationPhase.REVIEW:
                    await self._handle_review_phase(session)
                elif session.current_phase == ConversationPhase.REFINEMENT:
                    await self._handle_refinement_phase(session)
                elif session.current_phase == ConversationPhase.COMPLETION:
                    logger.info(f"Session {session_id} completed successfully!")
                    break
                elif session.current_phase == ConversationPhase.ERROR_HANDLING:
                    await self._handle_error_recovery(session)
                
                # Check for completion
                if await self._check_completion_criteria(session):
                    session.current_phase = ConversationPhase.COMPLETION
                    continue
                
                # Short delay between iterations
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error in orchestration loop {session_id}: {e}")
            session.current_phase = ConversationPhase.ERROR_HANDLING
    
    async def _initialize_agents(self, session: OrchestrationSession):
        """Initialize both CLI agents with the project objective"""
        logger.info("Initializing CLI agents with project objective")
        
        # Initialize Claude CLI (Frontend specialist)
        claude_prompt = self.context_transformers["planning_phase"].format(
            objective=session.objective,
            agent_role="Frontend Specialist - Focus on UI, UX, and client-side implementation"
        )
        
        claude_response = await self.terminal_manager.send_message(
            session.claude_process_id, 
            claude_prompt
        )
        
        # Log Claude's initial response
        session.message_history.append({
            "agent": "claude_cli",
            "type": "initialization",
            "message": claude_prompt,
            "response": claude_response,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Initialize Codex CLI (Backend specialist)
        codex_prompt = self.context_transformers["planning_phase"].format(
            objective=session.objective,
            agent_role="Backend Specialist - Focus on APIs, databases, and server-side logic"
        )
        
        codex_response = await self.terminal_manager.send_message(
            session.codex_process_id,
            codex_prompt
        )
        
        # Log Codex's initial response
        session.message_history.append({
            "agent": "codex_cli",
            "type": "initialization", 
            "message": codex_prompt,
            "response": codex_response,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Move to planning phase
        session.current_phase = ConversationPhase.PLANNING
        logger.info("CLI agents initialized, moving to planning phase")
    
    async def _handle_planning_phase(self, session: OrchestrationSession):
        """Handle collaborative planning phase"""
        logger.info("Executing planning phase")
        
        # Get both agents to create their implementation plans
        # This creates a collaborative planning session via CLI
        
        planning_prompt = f"""
COLLABORATIVE PLANNING SESSION

**Project Objective**: {session.objective}

Based on the initial analysis, please provide:
1. Detailed implementation plan for your specialty
2. Interfaces/APIs needed from the other specialist
3. Data flow and integration points
4. Timeline and dependencies

Make this concrete and actionable.
"""
        
        # Get Claude's frontend plan
        claude_plan = await self.terminal_manager.send_message(
            session.claude_process_id,
            planning_prompt + "\n\n**Your Role**: Frontend Implementation"
        )
        
        # Get Codex's backend plan  
        codex_plan = await self.terminal_manager.send_message(
            session.codex_process_id,
            planning_prompt + "\n\n**Your Role**: Backend Implementation"
        )
        
        # Record planning outputs
        session.message_history.extend([
            {
                "agent": "claude_cli",
                "type": "planning",
                "message": planning_prompt,
                "response": claude_plan,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            {
                "agent": "codex_cli", 
                "type": "planning",
                "message": planning_prompt,
                "response": codex_plan,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        ])
        
        # Move to implementation
        session.current_phase = ConversationPhase.IMPLEMENTATION
        logger.info("Planning phase completed, moving to implementation")
    
    async def _handle_implementation_phase(self, session: OrchestrationSession):
        """Handle collaborative implementation phase"""
        logger.info("Executing implementation phase")
        
        # Alternating implementation with cross-communication
        # Start with backend implementation
        
        backend_task = f"""
BACKEND IMPLEMENTATION TASK

**Project**: {session.objective}

**Context**: Based on the planning phase, implement the backend components.

**Required**:
1. Set up project structure
2. Implement core APIs and endpoints
3. Set up database models if needed
4. Create authentication/authorization
5. Prepare frontend integration points

Focus on creating a working backend that the frontend can integrate with.
"""
        
        backend_result = await self.terminal_manager.send_message(
            session.codex_process_id,
            backend_task
        )
        
        # Now frontend implementation based on backend
        frontend_task = self.context_transformers["codex_to_claude"].format(
            backend_output=backend_result,
            api_endpoints="from backend implementation",
            data_flow="as defined in backend",
            ui_components="based on project requirements",
            error_handling="for API integration",
            technical_details=backend_result[:500]  # Summary of backend work
        )
        
        frontend_result = await self.terminal_manager.send_message(
            session.claude_process_id,
            frontend_task
        )
        
        # Record implementation work
        session.message_history.extend([
            {
                "agent": "codex_cli",
                "type": "implementation",
                "message": backend_task,
                "response": backend_result,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            {
                "agent": "claude_cli",
                "type": "implementation",
                "message": frontend_task, 
                "response": frontend_result,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        ])
        
        # Move to review phase
        session.current_phase = ConversationPhase.REVIEW
        logger.info("Implementation phase completed, moving to review")
    
    async def _handle_review_phase(self, session: OrchestrationSession):
        """Handle cross-review and validation phase"""
        logger.info("Executing review phase")
        
        # Get recent implementation work for review
        recent_work = session.message_history[-2:]  # Last 2 messages
        work_summary = "\n\n".join([
            f"**{msg['agent']}**: {msg['response'][:300]}..."
            for msg in recent_work
        ])
        
        review_prompt = self.context_transformers["review_phase"].format(
            current_work=work_summary
        )
        
        # Claude reviews backend work
        claude_review = await self.terminal_manager.send_message(
            session.claude_process_id,
            review_prompt + "\n\n**Focus**: Review backend implementation for frontend integration"
        )
        
        # Codex reviews frontend work
        codex_review = await self.terminal_manager.send_message(
            session.codex_process_id,
            review_prompt + "\n\n**Focus**: Review frontend implementation for backend compatibility"
        )
        
        # Record review results
        session.message_history.extend([
            {
                "agent": "claude_cli",
                "type": "review",
                "message": review_prompt,
                "response": claude_review,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            {
                "agent": "codex_cli",
                "type": "review", 
                "message": review_prompt,
                "response": codex_review,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        ])
        
        # Determine next phase based on review
        needs_refinement = any(
            pattern in review.lower()
            for review in [claude_review, codex_review]
            for pattern in ["needs improvement", "issues found", "not working"]
        )
        
        if needs_refinement:
            session.current_phase = ConversationPhase.REFINEMENT
            logger.info("Review identified issues, moving to refinement")
        else:
            session.current_phase = ConversationPhase.COMPLETION  
            logger.info("Review passed, moving toward completion")
    
    async def _handle_refinement_phase(self, session: OrchestrationSession):
        """Handle refinement and improvement phase"""
        logger.info("Executing refinement phase")
        
        # Address issues identified in review
        refinement_task = f"""
REFINEMENT TASK

**Project**: {session.objective}

**Context**: Review phase identified areas for improvement.

**Your Task**:
1. Address any issues mentioned in the review
2. Improve integration between frontend and backend
3. Fix any bugs or problems identified
4. Enhance functionality to better meet the objective
5. Test and verify your improvements work

Focus on creating a polished, working solution.
"""
        
        # Both agents refine their work
        claude_refinement = await self.terminal_manager.send_message(
            session.claude_process_id,
            refinement_task + "\n\n**Focus**: Frontend improvements and integration"
        )
        
        codex_refinement = await self.terminal_manager.send_message(
            session.codex_process_id,
            refinement_task + "\n\n**Focus**: Backend improvements and stability"
        )
        
        # Record refinement work
        session.message_history.extend([
            {
                "agent": "claude_cli",
                "type": "refinement",
                "message": refinement_task,
                "response": claude_refinement,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            {
                "agent": "codex_cli",
                "type": "refinement",
                "message": refinement_task,
                "response": codex_refinement,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        ])
        
        # Go back to review to validate improvements
        session.current_phase = ConversationPhase.REVIEW
        logger.info("Refinement completed, returning to review phase")
    
    async def _handle_error_recovery(self, session: OrchestrationSession):
        """Handle error recovery and process restart if needed"""
        logger.info("Executing error recovery")
        
        # Check process health
        claude_status = self.terminal_manager.get_process_status(session.claude_process_id)
        codex_status = self.terminal_manager.get_process_status(session.codex_process_id)
        
        # Restart failed processes
        if claude_status.get("status") == "error":
            logger.info("Restarting Claude CLI process")
            await self.terminal_manager.stop_terminal(session.claude_process_id)
            session.claude_process_id = await self.terminal_manager.start_terminal(TerminalType.CLAUDE_CLI)
        
        if codex_status.get("status") == "error":
            logger.info("Restarting Codex CLI process")
            await self.terminal_manager.stop_terminal(session.codex_process_id)
            session.codex_process_id = await self.terminal_manager.start_terminal(TerminalType.CODEX_CLI)
        
        # Return to previous phase
        session.current_phase = ConversationPhase.IMPLEMENTATION
        logger.info("Error recovery completed, resuming implementation")
    
    async def _check_completion_criteria(self, session: OrchestrationSession) -> bool:
        """Check if the project objective has been completed"""
        
        # Check recent messages for completion indicators
        recent_messages = session.message_history[-4:] if len(session.message_history) >= 4 else session.message_history
        
        for message in recent_messages:
            response_lower = message["response"].lower()
            for pattern in self.completion_patterns:
                if pattern in response_lower:
                    logger.info(f"Completion pattern detected: {pattern}")
                    return True
        
        # Additional completion checks
        if session.iteration_count >= session.max_iterations:
            logger.info("Maximum iterations reached, marking as complete")
            return True
        
        return False
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get detailed status of orchestration session"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        
        # Get process statuses
        claude_status = self.terminal_manager.get_process_status(session.claude_process_id)
        codex_status = self.terminal_manager.get_process_status(session.codex_process_id)
        
        return {
            "session_id": session.id,
            "objective": session.objective,
            "mode": session.mode.value,
            "current_phase": session.current_phase.value,
            "iteration_count": session.iteration_count,
            "max_iterations": session.max_iterations,
            "created_at": session.created_at.isoformat(),
            "message_count": len(session.message_history),
            "claude_cli": claude_status,
            "codex_cli": codex_status,
            "current_focus": session.current_focus
        }
    
    async def stop_session(self, session_id: str):
        """Stop an orchestration session and cleanup resources"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        
        # Stop CLI processes
        await self.terminal_manager.stop_terminal(session.claude_process_id)
        await self.terminal_manager.stop_terminal(session.codex_process_id)
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        
        logger.info(f"CLI orchestration session stopped: {session_id}")