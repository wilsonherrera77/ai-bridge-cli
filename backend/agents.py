#!/usr/bin/env python3
"""
AI Agent Classes for CLI-Based Orchestration System

AgentA: Frontend specialist using Claude CLI (real terminal process)
AgentB: Backend specialist using Codex/GPT CLI (real terminal process)

Each agent communicates via stdin/stdout with real CLI processes.
ZERO API key usage - uses existing paid CLI memberships exclusively.
"""

import asyncio
import json
import os
import sys
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Real CLI Bridge Integration - NO API KEYS
# Real CLI process communication using actual terminals
from real_cli_bridge import RealCLIBridge, CLIType, real_cli_bridge
from terminal_manager import TerminalManager, TerminalType, ProcessStatus
from cli_orchestrator import CLIOrchestrator
from process_communicator import ProcessCommunicator
from terminal_monitor import TerminalMonitor

# Import communication system
from communication import Message, MessageType, AgentRole as CommAgentRole, MessageTransformationEngine, ConversationStateManager

# Configure logging
logger = logging.getLogger(__name__)

class AgentRole(Enum):
    """Agent specialization roles"""
    FRONTEND = "frontend"
    BACKEND = "backend"
    FULLSTACK = "fullstack"

class AgentStatus(Enum):
    """Agent operational status"""
    IDLE = "idle"
    INITIALIZING = "initializing" 
    ACTIVE = "active"
    THINKING = "thinking"
    WORKING = "working"
    READY = "ready"
    COMPLETED = "completed"
    PAUSED = "paused"
    ERROR = "error"
    STOPPED = "stopped"

@dataclass
class AgentMemory:
    """Persistent memory structure for agents"""
    agent_id: str
    role: AgentRole
    session_id: str
    context: Dict[str, Any]
    conversation_history: List[Dict[str, Any]]
    decisions_made: List[Dict[str, Any]]
    files_created: List[str]
    current_focus: Optional[str] = None
    last_output: Optional[str] = None
    error_log: List[str] = None
    
    def __post_init__(self):
        if self.error_log is None:
            self.error_log = []

@dataclass
class AgentConfig:
    """Configuration for CLI-based agent behavior"""
    cli_command: List[str] = None  # CLI command to execute
    working_directory: str = "workspace"
    timeout_seconds: int = 120
    max_retries: int = 3
    enable_reflection: bool = True
    save_memory: bool = True
    memory_limit: int = 1000  # Max conversation history entries
    auto_restart: bool = True  # Auto-restart CLI process if it crashes
    
    def __post_init__(self):
        if self.cli_command is None:
            self.cli_command = []

class BaseAgent(ABC):
    """
    Enhanced abstract base class for AI agents with real CLI communication capabilities.

    Features:
    - Real CLI process management and communication
    - Smart context processing for incoming messages
    - Output formatting for target agent communication
    - Integration with message transformation engine
    - Automatic handoff decision making
    - Enhanced conversation memory and state management
    """
    
    def __init__(self, role: AgentRole, config: Optional[AgentConfig] = None):
        self.role = role
        self.config = config or AgentConfig()
        self.agent_id = str(uuid.uuid4())
        self.status = AgentStatus.IDLE
        self.memory: Optional[AgentMemory] = None
        self.memory_file: Optional[Path] = None
        
        # NO crear engines duplicados - se registrarán con MessageBus central
        # ARQUITECTURA CENTRALIZADA: MessageBus es el ÚNICO propietario
        self.message_bus = None  # Se inyectará durante initialize()
        self.is_registered_with_messagebus = False
        
        # Communication role mapping
        self.comm_role = self._map_to_comm_role()
        
        # Context processors
        self.context_enrichers = {}
        self.output_formatters = {}
        
        # Setup logging for this agent
        self.logger = logging.getLogger(f"agent_{self.role.value}")
        
        # NO inicializar capabilities duplicadas - se usará registration pattern
    
    def _map_to_comm_role(self) -> CommAgentRole:
        """Map agent role to communication role"""
        role_mapping = {
            AgentRole.FRONTEND: CommAgentRole.FRONTEND,
            AgentRole.BACKEND: CommAgentRole.BACKEND,
            AgentRole.FULLSTACK: CommAgentRole.FRONTEND  # Default to frontend
        }
        return role_mapping.get(self.role, CommAgentRole.FRONTEND)
    
    def register_with_messagebus(self, message_bus) -> bool:
        """
        Registra este agent con el MessageBus centralizado.
        
        Args:
            message_bus: El MessageBus central donde registrarse
            
        Returns:
            bool: True si se registró exitosamente
        """
        try:
            self.message_bus = message_bus
            
            # Registrar con el MessageBus central usando el context provider
            success = self.message_bus.register_agent(
                agent_id=f"agent_{self.role.value}",
                agent_role=self.comm_role,
                context_provider=self._provide_agent_context
            )
            
            if success:
                self.is_registered_with_messagebus = True
                self._setup_output_formatters()
                logger.info(f"Agent {self.role.value} registered with centralized MessageBus")
            else:
                logger.error(f"Failed to register agent {self.role.value} with MessageBus")
            
            return success
            
        except Exception as e:
            logger.error(f"Registration with MessageBus failed for agent {self.role.value}: {e}")
            return False
    
    def _setup_output_formatters(self):
        """Setup output formatters for different message types"""
        self.output_formatters = {
            "api_request": self._format_api_request_output,
            "implementation_complete": self._format_implementation_complete_output,
            "status_update": self._format_status_update_output,
            "error_report": self._format_error_report_output
        }
    
    async def _provide_agent_context(self, message: Message, from_role: CommAgentRole, to_role: CommAgentRole) -> Dict[str, Any]:
        """Provide agent-specific context for message transformation"""
        try:
            context = {
                "agent_id": self.agent_id,
                "agent_role": self.role.value,
                "agent_status": self.status.value,
                "current_focus": self.memory.current_focus if self.memory else "general development",
                "recent_decisions": len(self.memory.decisions_made) if self.memory else 0,
                "files_created": len(self.memory.files_created) if self.memory else 0,
                "specialization": self._get_specialization_context()
            }
            
            # Add recent work summary
            if self.memory and self.memory.last_output:
                context["recent_output"] = self.memory.last_output[:200] + "..." if len(self.memory.last_output) > 200 else self.memory.last_output
            
            # Add role-specific context
            if self.role == AgentRole.FRONTEND:
                context.update({
                    "frontend_frameworks": "React, Vue, Angular",
                    "ui_specialties": "responsive design, user experience, accessibility",
                    "integration_expertise": "API consumption, state management, routing"
                })
            elif self.role == AgentRole.BACKEND:
                context.update({
                    "backend_frameworks": "FastAPI, Express, Django",
                    "api_specialties": "RESTful APIs, authentication, data validation",
                    "database_expertise": "SQL, NoSQL, ORM integration"
                })
            
            return context
            
        except Exception as e:
            self.logger.warning(f"Failed to provide agent context: {e}")
            return {"agent_role": self.role.value}
    
    def _get_specialization_context(self) -> str:
        """Get specialization description for this agent"""
        specializations = {
            AgentRole.FRONTEND: "Frontend development, UI/UX design, user interaction, responsive layouts",
            AgentRole.BACKEND: "Backend development, API design, database management, server architecture",
            AgentRole.FULLSTACK: "Full-stack development, end-to-end application architecture"
        }
        return specializations.get(self.role, "General development")
    
    def _format_api_request_output(self, content: str) -> str:
        """Format output when requesting API implementation from backend"""
        return f"""
API IMPLEMENTATION REQUEST:

{content}

EXPECTED BACKEND DELIVERABLES:
- API endpoint implementation
- Request/response schemas
- Authentication integration
- Error handling
- API documentation

FRONTEND INTEGRATION REQUIREMENTS:
- Clear endpoint specifications
- Sample request/response examples
- Authentication flow details
- Error handling patterns
"""
    
    def _format_implementation_complete_output(self, content: str) -> str:
        """Format output when implementation is complete"""
        return f"""
IMPLEMENTATION COMPLETED:

{content}

HANDOFF DETAILS:
- Implementation is ready for integration
- All requirements have been addressed
- Testing has been completed
- Documentation is available

NEXT STEPS FOR COLLABORATING AGENT:
- Review implementation
- Integrate with existing codebase
- Test integration points
- Provide feedback or proceed with next phase
"""
    
    def _format_status_update_output(self, content: str) -> str:
        """Format status update output"""
        return f"""
STATUS UPDATE:

{content}

CURRENT STATE:
- Agent: {self.role.value}
- Status: {self.status.value}
- Progress: In progress
- Ready for: Next task or collaboration

COLLABORATION CONTEXT:
- Available for handoff
- Monitoring for incoming requests
- Ready to assist with integration
"""
    
    def _format_error_report_output(self, content: str) -> str:
        """Format error report output"""
        return f"""
ERROR REPORT:

{content}

BLOCKING ISSUES:
- Error encountered in current task
- Requires intervention or assistance
- May need alternative approach

REQUESTED SUPPORT:
- Review error details
- Suggest alternative solutions
- Provide guidance on next steps
- Consider task reassignment if needed
"""
        
    async def initialize(self, context: Dict[str, Any]) -> bool:
        """Initialize agent with session context"""
        try:
            self.status = AgentStatus.INITIALIZING
            
            # Create memory structure
            self.memory = AgentMemory(
                agent_id=self.agent_id,
                role=self.role,
                session_id=context.get("session_id", "unknown"),
                context=context,
                conversation_history=[],
                decisions_made=[],
                files_created=[]
            )
            
            # Setup memory persistence
            if context.get("workspace"):
                workspace = Path(context["workspace"])
                workspace.mkdir(parents=True, exist_ok=True)
                self.memory_file = workspace / f"agent_{self.role.value}_memory.json"
            
            # Initialize CLI process
            await self._initialize_cli_process()
            
            # Set initial context
            initial_context = await self._create_initial_context(context)
            self.memory.conversation_history.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": "system_context",
                "content": initial_context
            })
            
            await self._save_memory()
            self.status = AgentStatus.ACTIVE
            
            self.logger.info(f"Agent {self.role.value} initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Agent {self.role.value} initialization failed: {e}")
            self.status = AgentStatus.ERROR
            if self.memory:
                self.memory.error_log.append(f"Initialization error: {e}")
            return False
    
    @abstractmethod
    async def _initialize_cli_process(self):
        """Initialize the CLI process for this agent"""
        # Will be implemented by subclasses to start their specific CLI processes
        pass
    
    @abstractmethod
    async def _create_initial_context(self, context: Dict[str, Any]) -> str:
        """Create the initial system context for the agent"""
        pass
    
    @abstractmethod
    async def _communicate_with_cli(self, message: str, **kwargs) -> str:
        """Communicate with CLI process via stdin/stdout"""
        # Will be implemented by subclasses to communicate with their specific CLI processes
        pass
    
    async def process_message(self, message: Message) -> Message:
        """Process incoming message and generate response"""
        try:
            self.status = AgentStatus.THINKING
            
            # Add message to conversation history
            self.memory.conversation_history.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": "incoming",
                "sender": message.sender,
                "content": message.content,
                "message_type": message.type.value
            })
            
            # Prepare message for CLI communication
            cli_message = await self._prepare_message_for_cli(message)
            
            # Communicate with CLI process
            self.status = AgentStatus.WORKING
            response_content = await self._communicate_with_cli(cli_message)
            
            # Process and store response
            self.memory.last_output = response_content
            self.memory.conversation_history.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": "outgoing",
                "content": response_content
            })
            
            # Extract any decisions or actions from the response
            await self._extract_decisions_and_actions(response_content)
            
            # Save memory
            await self._save_memory()
            
            self.status = AgentStatus.READY
            
            # Create response message
            response = Message(
                type=MessageType.RESPONSE,
                sender=f"agent_{self.role.value}",
                recipient=message.sender,
                content=response_content,
                session_id=message.session_id,
                metadata={
                    "agent_role": self.role.value,
                    "processing_time": datetime.now(timezone.utc).isoformat()
                }
            )
            
            self.logger.info(f"Agent {self.role.value} processed message successfully")
            return response
            
        except Exception as e:
            self.logger.error(f"Agent {self.role.value} message processing failed: {e}")
            self.status = AgentStatus.ERROR
            if self.memory:
                self.memory.error_log.append(f"Message processing error: {e}")
            
            # Return error message
            return Message(
                type=MessageType.ERROR,
                sender=f"agent_{self.role.value}",
                recipient=message.sender,
                content=f"Error processing message: {e}",
                session_id=message.session_id
            )
    
    async def _prepare_conversation_for_api(self, current_message: Message) -> List[Dict[str, Any]]:
        """Prepare conversation history for API call"""
        messages = []
        
        # Add system context if available
        if self.memory.conversation_history:
            first_msg = self.memory.conversation_history[0]
            if first_msg.get("type") == "system_context":
                messages.append({
                    "role": "system",
                    "content": first_msg["content"]
                })
        
        # Add recent conversation history (limit to avoid token overflow)
        recent_history = self.memory.conversation_history[-20:] if len(self.memory.conversation_history) > 20 else self.memory.conversation_history
        
        for entry in recent_history:
            if entry.get("type") == "incoming":
                messages.append({
                    "role": "user", 
                    "content": entry["content"]
                })
            elif entry.get("type") == "outgoing":
                messages.append({
                    "role": "assistant",
                    "content": entry["content"]
                })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": current_message.content
        })
        
        return messages
    
    async def _extract_decisions_and_actions(self, response_content: str):
        """Extract decisions and file creation actions from agent response"""
        try:
            # Look for decision indicators
            decision_keywords = ["decided", "choosing", "will implement", "approach"]
            for keyword in decision_keywords:
                if keyword in response_content.lower():
                    self.memory.decisions_made.append({
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "content": response_content,
                        "type": "automatic_extraction"
                    })
                    break
            
            # Look for file creation mentions
            file_keywords = ["created file", "saving to", "writing file", "generated"]
            for keyword in file_keywords:
                if keyword in response_content.lower():
                    # This is a simplified extraction - could be enhanced with regex
                    self.memory.files_created.append(f"File mentioned at {datetime.now(timezone.utc).isoformat()}")
                    break
                    
        except Exception as e:
            self.logger.warning(f"Error extracting decisions and actions: {e}")
    
    async def _save_memory(self):
        """Save agent memory to disk"""
        if not self.memory_file or not self.config.save_memory:
            return
        
        try:
            # Limit conversation history size
            if len(self.memory.conversation_history) > self.config.memory_limit:
                self.memory.conversation_history = self.memory.conversation_history[-self.config.memory_limit:]
            
            memory_data = asdict(self.memory)
            memory_data['role'] = self.memory.role.value
            
            with open(self.memory_file, 'w') as f:
                json.dump(memory_data, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Failed to save memory: {e}")
    
    async def get_status(self) -> AgentStatus:
        """Get current agent status"""
        return self.status
    
    async def get_latest_output(self) -> str:
        """Get the latest output from the agent"""
        return self.memory.last_output if self.memory and self.memory.last_output else ""
    
    async def pause(self):
        """Pause the agent"""
        self.status = AgentStatus.PAUSED
        await self._save_memory()
    
    async def resume(self):
        """Resume the agent"""
        if self.status == AgentStatus.PAUSED:
            self.status = AgentStatus.ACTIVE
    
    async def stop(self):
        """Stop the agent"""
        self.status = AgentStatus.STOPPED
        await self._save_memory()
    
    async def cleanup(self):
        """Clean up agent resources"""
        self.status = AgentStatus.COMPLETED
        await self._save_memory()


class AgentA(BaseAgent):
    """
    Frontend specialist agent using Claude CLI process.
    Specializes in UI/UX, React, Vue, Angular, styling, and user experience.
    ZERO API key usage - communicates with real Claude CLI terminal.
    """
    
    def __init__(self, role: AgentRole = AgentRole.FRONTEND, config: Optional[AgentConfig] = None):
        super().__init__(role, config)
        
        # CLI process management
        self.terminal_manager = None  # Will be injected during initialization
        self.cli_process_id: Optional[str] = None
        self.process_communicator = ProcessCommunicator()
        
        # CLI configuration
        if not config:
            config = AgentConfig()
        if not config.cli_command:
            config.cli_command = ["claude", "chat"]  # Default Claude CLI command
        
        self.config = config
        
        self.logger.info("AgentA (Frontend) initialized for CLI communication - NO API keys")
    
    async def _initialize_cli_process(self):
        """Initialize Claude CLI process - NO API KEYS"""
        try:
            if not self.terminal_manager:
                # Create our own terminal manager if not injected
                from terminal_manager import TerminalManager, TerminalType
                self.terminal_manager = TerminalManager()
            
            # Start Claude CLI process
            self.cli_process_id = await self.terminal_manager.start_terminal(
                TerminalType.CLAUDE_CLI
            )
            
            # Wait for CLI to be ready
            await asyncio.sleep(3)
            
            self.logger.info(f"Claude CLI process initialized: {self.cli_process_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Claude CLI process: {e}")
            raise ValueError(f"Claude CLI initialization failed: {e}")
    
    async def _create_initial_context(self, context: Dict[str, Any]) -> str:
        """Create initial system context for frontend specialist"""
        return f"""FRONTEND DEVELOPMENT SPECIALIST

ROLE & SPECIALIZATION:
- Frontend development expert (React, Vue, Angular, vanilla JS)
- UI/UX design and user experience optimization
- CSS/SCSS styling and responsive design
- Modern web technologies and best practices
- Component architecture and state management

CURRENT OBJECTIVE: {context.get('objective', 'No objective specified')}

COLLABORATION CONTEXT:
- Work autonomously with Backend Specialist
- Integrate seamlessly with backend APIs
- Communicate implementation decisions clearly
- Ask questions when you need backend specifications
- Focus on user experience and frontend best practices

WORKSPACE: {context.get('workspace', 'workspace')}
SESSION: {context.get('session_id', 'unknown')}

INSTRUCTIONS:
1. Analyze objectives and plan frontend implementation
2. Create modular, maintainable frontend code
3. Consider responsive design and accessibility
4. Coordinate for API requirements and data flow
5. Document decisions and provide clear progress updates
6. Generate production-ready code with proper error handling

Provide thoughtful analysis, implementation plans, and working code. Be autonomous but collaborative.
"""
    
    async def _communicate_with_cli(self, message: str, **kwargs) -> str:
        """Communicate with Claude CLI process - NO API KEYS"""
        try:
            if not self.cli_process_id:
                raise ValueError("Claude CLI process not initialized")
            
            self.logger.info(f"Sending message to Claude CLI: {message[:100]}...")
            
            # Send message to Claude CLI process via TerminalManager
            response = await self.terminal_manager.send_message(
                self.cli_process_id,
                message
            )
            
            self.logger.info(f"Received response from Claude CLI: {response[:100]}...")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Claude CLI communication failed: {e}")
            raise ValueError(f"CLI communication error: {e}")


class AgentB(BaseAgent):
    """
    Backend specialist agent using Codex/GPT CLI process.
    Specializes in APIs, databases, server architecture, and security.
    ZERO API key usage - communicates with real Codex/GPT CLI terminal.
    """
    
    def __init__(self, role: AgentRole = AgentRole.BACKEND, config: Optional[AgentConfig] = None):
        super().__init__(role, config)
        
        # CLI process management
        self.terminal_manager = None  # Will be injected during initialization
        self.cli_process_id: Optional[str] = None
        self.process_communicator = ProcessCommunicator()
        
        # CLI configuration
        if not config:
            config = AgentConfig()
        if not config.cli_command:
            config.cli_command = ["codex", "chat"]  # Default Codex CLI command
        
        self.config = config
        
        self.logger.info("AgentB (Backend) initialized for CLI communication - NO API keys")
    
    async def _initialize_cli_process(self):
        """Initialize Codex/GPT CLI process - NO API KEYS"""
        try:
            if not self.terminal_manager:
                # Create our own terminal manager if not injected
                from terminal_manager import TerminalManager, TerminalType
                self.terminal_manager = TerminalManager()
            
            # Start Codex CLI process
            self.cli_process_id = await self.terminal_manager.start_terminal(
                TerminalType.CODEX_CLI
            )
            
            # Wait for CLI to be ready
            await asyncio.sleep(3)
            
            self.logger.info(f"Codex CLI process initialized: {self.cli_process_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Codex CLI process: {e}")
            raise ValueError(f"Codex CLI initialization failed: {e}")
    
    async def _create_initial_context(self, context: Dict[str, Any]) -> str:
        """Create initial system context for backend specialist"""
        return f"""BACKEND DEVELOPMENT SPECIALIST

ROLE & SPECIALIZATION:
- Backend development expert (Python, Node.js, FastAPI, Express)
- Database design and optimization (SQL, NoSQL)
- API design and RESTful services
- Server architecture and deployment
- Security, authentication, and authorization
- Performance optimization and scalability

CURRENT OBJECTIVE: {context.get('objective', 'No objective specified')}

COLLABORATION CONTEXT:
- Work autonomously with Frontend Specialist
- Design APIs that support frontend requirements seamlessly
- Provide clear API documentation and data schemas
- Consider security and performance implications
- Communicate architecture decisions and constraints clearly

WORKSPACE: {context.get('workspace', 'workspace')}
SESSION: {context.get('session_id', 'unknown')}

INSTRUCTIONS:
1. Analyze objectives and plan backend architecture
2. Design scalable, secure backend solutions
3. Create clear APIs with proper validation and error handling
4. Coordinate for frontend data requirements
5. Implement proper security measures and best practices
6. Provide thorough documentation and testing guidance

Provide detailed architecture analysis, implementation plans, and production-ready code. Be autonomous but collaborative.
"""
    
    async def _communicate_with_cli(self, message: str, **kwargs) -> str:
        """Communicate with Codex/GPT CLI process - NO API KEYS"""
        try:
            if not self.cli_process_id:
                raise ValueError("Codex CLI process not initialized")
            
            self.logger.info(f"Sending message to Codex CLI: {message[:100]}...")
            
            # Send message to Codex CLI process via TerminalManager
            response = await self.terminal_manager.send_message(
                self.cli_process_id,
                message
            )
            
            self.logger.info(f"Received response from Codex CLI: {response[:100]}...")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Codex CLI communication failed: {e}")
            raise ValueError(f"CLI communication error: {e}")


# Utility functions for agent management
async def create_agent_pair(session_id: str, workspace: str, objective: str) -> Tuple[AgentA, AgentB]:
    """Create and initialize a pair of agents for collaboration"""
    try:
        # Create agents
        agent_a = AgentA()
        agent_b = AgentB()
        
        # Prepare context
        context = {
            "session_id": session_id,
            "workspace": workspace,
            "objective": objective
        }
        
        # Initialize both agents
        await asyncio.gather(
            agent_a.initialize(context),
            agent_b.initialize(context)
        )
        
        logger.info(f"Agent pair created for session {session_id}")
        return agent_a, agent_b
        
    except Exception as e:
        logger.error(f"Failed to create agent pair: {e}")
        raise

async def load_agent_from_memory(memory_file: Path, agent_type: str) -> Union[AgentA, AgentB]:
    """Load agent from saved memory file"""
    try:
        with open(memory_file, 'r') as f:
            memory_data = json.load(f)
        
        # Create appropriate agent
        if agent_type.lower() == 'frontend' or memory_data.get('role') == 'frontend':
            agent = AgentA()
        elif agent_type.lower() == 'backend' or memory_data.get('role') == 'backend':
            agent = AgentB()
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        # Restore memory
        agent.memory = AgentMemory(
            agent_id=memory_data['agent_id'],
            role=AgentRole(memory_data['role']),
            session_id=memory_data['session_id'],
            context=memory_data['context'],
            conversation_history=memory_data['conversation_history'],
            decisions_made=memory_data['decisions_made'],
            files_created=memory_data['files_created'],
            current_focus=memory_data.get('current_focus'),
            last_output=memory_data.get('last_output'),
            error_log=memory_data.get('error_log', [])
        )
        
        agent.memory_file = memory_file
        agent.status = AgentStatus.ACTIVE
        
        # Reinitialize CLI process
        await agent._initialize_cli_process()
        
        logger.info(f"Agent {agent_type} loaded from memory")
        return agent
        
    except Exception as e:
        logger.error(f"Failed to load agent from memory: {e}")
        raise