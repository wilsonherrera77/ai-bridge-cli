#!/usr/bin/env python3
"""
Inter-Agent Communication System for AI-Bridge

Provides structured messaging pipeline for autonomous agent collaboration:
- MessageBus for centralized message routing
- Message types for different communication patterns
- Conversation logging and persistence
- Message validation and error handling
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Configure logging
logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Types of messages in the communication system"""
    TASK = "task"                           # Task assignment
    RESPONSE = "response"                   # Task response  
    COORDINATION = "coordination"           # Cross-agent coordination
    CROSS_COMMUNICATION = "cross_communication"  # Agent-to-agent direct communication
    IMPLEMENTATION = "implementation"       # Implementation work updates
    REVIEW = "review"                      # Review and validation requests
    CONFLICT_RESOLUTION = "conflict_resolution"  # Conflict resolution instructions
    STATUS_UPDATE = "status_update"        # Status updates
    ERROR = "error"                        # Error notifications
    SYSTEM = "system"                      # System messages
    HEARTBEAT = "heartbeat"                # Keep-alive messages
    # New types for autonomous communication
    AUTONOMOUS_REQUEST = "autonomous_request"      # Agent requesting work from other agent
    AUTONOMOUS_RESPONSE = "autonomous_response"    # Agent completing work and reporting back
    CONTEXT_ENRICHED = "context_enriched"          # Message with enhanced context
    HANDOFF = "handoff"                            # Control handoff between agents
    PROGRESS_UPDATE = "progress_update"            # Progress tracking updates

class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

@dataclass 
class Message:
    """Structured message for inter-agent communication"""
    type: MessageType
    sender: str
    recipient: str 
    content: str
    session_id: str
    id: str = None
    timestamp: datetime = None
    priority: MessagePriority = MessagePriority.NORMAL
    metadata: Dict[str, Any] = None
    reply_to: Optional[str] = None
    requires_response: bool = False
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ConversationThread:
    """A conversation thread between agents"""
    id: str
    participants: List[str]
    session_id: str
    created_at: datetime
    messages: List[Message]
    is_active: bool = True
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class AgentRole(Enum):
    """Agent roles for message transformation"""
    FRONTEND = "frontend"
    BACKEND = "backend"
    ORCHESTRATOR = "orchestrator"

class MessageTransformationTemplate:
    """Template for transforming messages between agent roles"""
    
    def __init__(self, from_role: AgentRole, to_role: AgentRole, template: str, context_fields: List[str]):
        self.from_role = from_role
        self.to_role = to_role
        self.template = template
        self.context_fields = context_fields

class MessageTransformationEngine:
    """
    Advanced engine for transforming agent outputs into contextual inputs for other agents.
    
    Features:
    - Role-aware message transformation
    - Context enrichment with project state
    - Template-based message formatting
    - Smart field extraction and mapping
    """
    
    def __init__(self):
        self.templates = {}
        self._initialize_default_templates()
        
        # Context providers for enrichment
        self.context_providers = {}
        
        logger.info("MessageTransformationEngine initialized")
    
    def _initialize_default_templates(self):
        """Initialize default message transformation templates"""
        
        # Frontend → Backend templates
        self.add_template(
            AgentRole.FRONTEND, 
            AgentRole.BACKEND,
            "frontend_to_backend_api_request",
            """
BACKEND IMPLEMENTATION REQUEST:

**Context**: The frontend agent needs {functionality} implemented on the backend.

**Specific Requirements**:
{requirements}

**Technical Details**:
- Implement {endpoint_type} endpoints: {endpoints}
- Add data validation for: {validation_fields}
- Include authentication/authorization: {auth_required}
- Database operations needed: {db_operations}
- Return format: {response_format}

**Project Context**:
- Current backend architecture: {backend_stack}
- Database schema: {db_schema}
- Authentication system: {auth_system}
- API standards: {api_standards}

**Expected Deliverables**:
1. API endpoint implementation
2. Data models/schemas
3. Input validation
4. Error handling
5. Documentation of endpoints

**Integration Notes**:
{integration_notes}

Please implement the backend components and provide the API specification for frontend integration.
            """,
            ["functionality", "requirements", "endpoints", "validation_fields", "auth_required", "db_operations", "response_format", "backend_stack", "db_schema", "auth_system", "api_standards", "integration_notes"]
        )
        
        # Backend → Frontend templates
        self.add_template(
            AgentRole.BACKEND,
            AgentRole.FRONTEND,
            "backend_to_frontend_api_ready",
            """
FRONTEND INTEGRATION REQUEST:

**Backend Implementation Complete**: {implementation_summary}

**Available APIs**:
{api_endpoints}

**Authentication Requirements**:
{auth_details}

**Frontend Integration Tasks**:
1. Create UI components for: {ui_components}
2. Implement API client methods: {api_methods}
3. Add form validation for: {form_fields}
4. Handle authentication flow: {auth_flow}
5. Implement error handling for: {error_scenarios}

**API Details**:
{api_documentation}

**Sample Usage**:
{code_examples}

**State Management**:
- Global state updates needed: {state_updates}
- Local component state: {local_state}
- Cache management: {cache_strategy}

**UI/UX Requirements**:
- Loading states for: {loading_states}
- Error messages for: {error_messages}
- Success feedback for: {success_feedback}

**Testing Requirements**:
{testing_requirements}

Please integrate these APIs into the frontend and create the necessary user interface components.
            """,
            ["implementation_summary", "api_endpoints", "auth_details", "ui_components", "api_methods", "form_fields", "auth_flow", "error_scenarios", "api_documentation", "code_examples", "state_updates", "local_state", "cache_strategy", "loading_states", "error_messages", "success_feedback", "testing_requirements"]
        )
        
        # Orchestrator → Agent templates
        self.add_template(
            AgentRole.ORCHESTRATOR,
            AgentRole.FRONTEND,
            "orchestrator_to_frontend_task",
            """
FRONTEND DEVELOPMENT TASK:

**Project Objective**: {project_objective}

**Your Specific Role**: {agent_role}

**Task Assignment**:
{task_description}

**Current Project State**:
{project_state}

**Collaboration Context**:
- Backend agent status: {backend_status}
- Previously completed work: {completed_work}
- Dependencies: {dependencies}
- Next expected handoff: {next_handoff}

**Technical Requirements**:
{technical_requirements}

**Success Criteria**:
{success_criteria}

**Resources Available**:
{resources}

Please proceed with the frontend implementation and coordinate with the backend agent as needed.
            """,
            ["project_objective", "agent_role", "task_description", "project_state", "backend_status", "completed_work", "dependencies", "next_handoff", "technical_requirements", "success_criteria", "resources"]
        )
        
        self.add_template(
            AgentRole.ORCHESTRATOR,
            AgentRole.BACKEND,
            "orchestrator_to_backend_task",
            """
BACKEND DEVELOPMENT TASK:

**Project Objective**: {project_objective}

**Your Specific Role**: {agent_role}

**Task Assignment**:
{task_description}

**Current Project State**:
{project_state}

**Collaboration Context**:
- Frontend agent status: {frontend_status}
- Previously completed work: {completed_work}
- Dependencies: {dependencies}
- Next expected handoff: {next_handoff}

**Technical Requirements**:
{technical_requirements}

**Success Criteria**:
{success_criteria}

**Resources Available**:
{resources}

Please proceed with the backend implementation and coordinate with the frontend agent as needed.
            """,
            ["project_objective", "agent_role", "task_description", "project_state", "frontend_status", "completed_work", "dependencies", "next_handoff", "technical_requirements", "success_criteria", "resources"]
        )
    
    def add_template(self, from_role: AgentRole, to_role: AgentRole, template_id: str, template: str, context_fields: List[str]):
        """Add a message transformation template"""
        key = f"{from_role.value}_to_{to_role.value}_{template_id}"
        self.templates[key] = MessageTransformationTemplate(from_role, to_role, template, context_fields)
        logger.debug(f"Added transformation template: {key}")
    
    def add_context_provider(self, name: str, provider_func: Callable):
        """Add a context provider function"""
        self.context_providers[name] = provider_func
        logger.debug(f"Added context provider: {name}")
    
    async def transform_message(self, message: Message, from_role: AgentRole, to_role: AgentRole, 
                               template_id: str, context: Dict[str, Any] = None) -> Message:
        """
        Transform a message from one agent role to another using templates and context enrichment.
        
        Args:
            message: Original message to transform
            from_role: Source agent role
            to_role: Target agent role  
            template_id: Template identifier to use
            context: Additional context for transformation
            
        Returns:
            Transformed message with enriched context
        """
        try:
            # Get template
            template_key = f"{from_role.value}_to_{to_role.value}_{template_id}"
            if template_key not in self.templates:
                logger.warning(f"Template not found: {template_key}")
                return message
            
            template = self.templates[template_key]
            
            # Extract content from original message
            original_content = message.content
            
            # Enrich context
            enriched_context = await self._enrich_context(message, from_role, to_role, context or {})
            
            # Apply template transformation with robust field mapping
            safe_context = self._ensure_template_fields(enriched_context, template.context_fields, message)
            transformed_content = template.template.format(**safe_context)
            
            # Create transformed message
            transformed_message = Message(
                type=MessageType.CONTEXT_ENRICHED,
                sender=message.sender,
                recipient=message.recipient,
                content=transformed_content,
                session_id=message.session_id,
                priority=message.priority,
                metadata={
                    **message.metadata,
                    "transformation": {
                        "from_role": from_role.value,
                        "to_role": to_role.value,
                        "template_id": template_id,
                        "original_content": original_content,
                        "enriched_fields": list(enriched_context.keys())
                    }
                },
                reply_to=message.id
            )
            
            logger.info(f"Message transformed using template {template_key}")
            return transformed_message
            
        except Exception as e:
            logger.error(f"Message transformation failed: {e}")
            return message
    
    async def _enrich_context(self, message: Message, from_role: AgentRole, to_role: AgentRole, 
                             base_context: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich message context with project state and agent-specific information"""
        try:
            enriched = base_context.copy()
            
            # Add basic message context
            enriched.update({
                "original_message": message.content,
                "from_agent": from_role.value,
                "to_agent": to_role.value,
                "timestamp": message.timestamp.isoformat(),
                "session_id": message.session_id
            })
            
            # Apply context providers
            for name, provider in self.context_providers.items():
                try:
                    provider_context = await provider(message, from_role, to_role)
                    if isinstance(provider_context, dict):
                        enriched.update(provider_context)
                except Exception as e:
                    logger.warning(f"Context provider {name} failed: {e}")
            
            # Set default values for missing template fields
            enriched = self._set_default_values(enriched)
            
            return enriched
            
        except Exception as e:
            logger.error(f"Context enrichment failed: {e}")
            return base_context
    
    def _set_default_values(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Set default values for common template fields"""
        defaults = {
            "functionality": "requested functionality",
            "requirements": "to be determined",
            "endpoints": "to be specified",
            "validation_fields": "to be determined",
            "auth_required": "to be determined",
            "db_operations": "to be specified",
            "response_format": "JSON",
            "backend_stack": "to be determined",
            "db_schema": "to be defined",
            "auth_system": "to be implemented",
            "api_standards": "RESTful APIs",
            "integration_notes": "standard integration patterns",
            "endpoint_type": "RESTful endpoints",
            "endpoints": "API endpoints to be defined",
            "implementation_summary": "implementation completed",
            "api_endpoints": "endpoints available",
            "auth_details": "authentication configured",
            "ui_components": "to be created",
            "api_methods": "to be implemented",
            "form_fields": "to be defined",
            "auth_flow": "standard authentication flow",
            "error_scenarios": "standard error handling",
            "api_documentation": "documentation available",
            "code_examples": "examples provided",
            "state_updates": "to be determined",
            "local_state": "component-specific state",
            "cache_strategy": "standard caching",
            "loading_states": "loading indicators",
            "error_messages": "user-friendly errors",
            "success_feedback": "success notifications",
            "testing_requirements": "standard testing",
            "project_objective": "project development",
            "agent_role": "specialized development role",
            "task_description": "development task",
            "project_state": "in progress",
            "backend_status": "active",
            "frontend_status": "active",
            "completed_work": "previous work completed",
            "dependencies": "no blocking dependencies",
            "next_handoff": "coordinate with other agent",
            "technical_requirements": "standard requirements",
            "success_criteria": "functional implementation",
            "resources": "development resources available"
        }
        
        for key, default_value in defaults.items():
            if key not in context:
                context[key] = default_value
        
        return context
    
    def _ensure_template_fields(self, context: Dict[str, Any], required_fields: List[str], message: Message) -> Dict[str, Any]:
        """Ensure all required template fields are present with intelligent extraction and fallbacks"""
        safe_context = context.copy()
        
        # Extract data from message content and metadata
        content_lower = message.content.lower()
        metadata = message.metadata or {}
        
        for field in required_fields:
            if field not in safe_context or not safe_context[field]:
                # Try to extract field value from message content or metadata
                extracted_value = self._extract_field_from_content(field, message.content, metadata)
                if extracted_value:
                    safe_context[field] = extracted_value
                else:
                    # Use intelligent default based on field name and context
                    safe_context[field] = self._get_intelligent_default(field, message, context)
        
        return safe_context
    
    def _extract_field_from_content(self, field: str, content: str, metadata: Dict[str, Any]) -> Optional[str]:
        """Extract field value from message content or metadata"""
        # Check metadata first
        if field in metadata:
            return str(metadata[field])
        
        content_lower = content.lower()
        
        # Field-specific extraction logic
        if field == "functionality":
            if "api" in content_lower:
                return "API implementation"
            elif "frontend" in content_lower or "ui" in content_lower:
                return "Frontend interface"
            elif "backend" in content_lower:
                return "Backend service"
            elif "database" in content_lower:
                return "Database operations"
        
        elif field == "requirements":
            if "create" in content_lower:
                return "Create new components"
            elif "update" in content_lower or "modify" in content_lower:
                return "Update existing functionality"
            elif "implement" in content_lower:
                return "Implementation requirements"
        
        elif field == "api_endpoints":
            if "endpoint" in content_lower or "api" in content_lower:
                return "RESTful API endpoints"
            elif "route" in content_lower:
                return "Application routes"
        
        elif field == "auth_required":
            if "auth" in content_lower or "login" in content_lower:
                return "Yes - authentication required"
            else:
                return "To be determined based on requirements"
        
        return None
    
    def _get_intelligent_default(self, field: str, message: Message, context: Dict[str, Any]) -> str:
        """Get intelligent default value based on field, message, and context"""
        # Use message metadata for more context
        sender_role = context.get("from_agent", "unknown")
        
        # Role-specific defaults
        if sender_role == "frontend":
            if field == "functionality":
                return "Frontend user interface development"
            elif field == "requirements":
                return "User interface components and interactions"
            elif field == "api_endpoints":
                return "Client-side API consumption endpoints"
        
        elif sender_role == "backend":
            if field == "functionality":
                return "Backend service implementation"
            elif field == "requirements":
                return "Server-side logic and data management"
            elif field == "api_endpoints":
                return "Server API endpoints and services"
        
        # Fallback to general defaults
        return self._set_default_values({}).get(field, f"[{field} to be determined]")

class ConversationStateManager:
    """
    Manages conversation state, turn management, and automatic handoffs between agents.
    
    Features:
    - Turn-based conversation control
    - Progress tracking and completion detection
    - Conflict resolution
    - Automatic handoff decisions
    - Conversation memory and context preservation
    """
    
    def __init__(self):
        self.active_conversations = {}
        self.turn_history = {}
        self.progress_tracking = {}
        self.handoff_rules = []
        
        # Initialize default handoff rules
        self._initialize_handoff_rules()
        
        logger.info("ConversationStateManager initialized")
    
    def _initialize_handoff_rules(self):
        """Initialize default rules for automatic handoffs"""
        self.handoff_rules = [
            {
                "trigger": "api_implementation_complete",
                "condition": lambda msg: "implementation completed" in msg.content.lower() and "api" in msg.content.lower(),
                "from_role": AgentRole.BACKEND,
                "to_role": AgentRole.FRONTEND,
                "message_type": MessageType.HANDOFF
            },
            {
                "trigger": "frontend_integration_request",
                "condition": lambda msg: any(word in msg.content.lower() for word in ["need api", "backend for", "implement endpoint"]),
                "from_role": AgentRole.FRONTEND,
                "to_role": AgentRole.BACKEND,
                "message_type": MessageType.HANDOFF
            },
            {
                "trigger": "ui_components_complete",
                "condition": lambda msg: "ui completed" in msg.content.lower() or "components ready" in msg.content.lower(),
                "from_role": AgentRole.FRONTEND,
                "to_role": AgentRole.BACKEND,
                "message_type": MessageType.HANDOFF
            },
            {
                "trigger": "review_request",
                "condition": lambda msg: any(word in msg.content.lower() for word in ["review", "check", "validate"]),
                "from_role": AgentRole.FRONTEND,
                "to_role": AgentRole.BACKEND,
                "message_type": MessageType.REVIEW
            }
        ]
    
    async def manage_conversation_turn(self, message: Message, current_agent: AgentRole) -> Dict[str, Any]:
        """
        Manage conversation turns and determine next actions.
        
        Returns:
            Dictionary with turn management decisions
        """
        try:
            conversation_id = f"{message.session_id}_{message.sender}_{message.recipient}"
            
            # DETAILED STATE MANAGEMENT LOGGING
            logger.info(f"🌐 GLOBAL STATE MANAGEMENT: Processing message {message.id} for conversation {conversation_id}")
            logger.info(f"🔄 STATE UPDATE: Current agent={current_agent.value}, Session={message.session_id}")
            
            # Initialize conversation state if needed
            if conversation_id not in self.active_conversations:
                logger.info(f"🆕 NEW CONVERSATION STATE: Initializing global state for {conversation_id}")
                self.active_conversations[conversation_id] = {
                    "current_turn": current_agent,
                    "turn_count": 0,
                    "last_activity": datetime.now(timezone.utc),
                    "progress_markers": [],
                    "blocked": False,
                    "completion_status": "in_progress"
                }
            
            conversation = self.active_conversations[conversation_id]
            old_turn_count = conversation["turn_count"]
            conversation["turn_count"] += 1
            conversation["last_activity"] = datetime.now(timezone.utc)
            
            # LOG GLOBAL STATE UPDATE
            logger.info(f"📈 GLOBAL STATE UPDATED: Conversation {conversation_id}")
            logger.info(f"   Turn count: {old_turn_count} → {conversation['turn_count']}")
            logger.info(f"   Current agent: {current_agent.value}")
            logger.info(f"   Progress markers: {len(conversation['progress_markers'])}")
            logger.info(f"   Status: {conversation['completion_status']}")
            
            # Check for handoff conditions WITH DETAILED LOGGING
            logger.info(f"🔄 EVALUATING HANDOFF CONDITIONS for {message.id}...")
            handoff_decision = await self._evaluate_handoff(message, current_agent)
            
            if handoff_decision.get("required"):
                logger.info(f"🚀 AUTOMATIC HANDOFF TRIGGERED: {handoff_decision.get('reason')} from {current_agent.value} to {handoff_decision.get('next_agent')}")
            else:
                logger.info(f"ℹ️  No handoff required for current message")
            
            # Update progress tracking WITH STATE LOGGING
            logger.info(f"📉 UPDATING PROGRESS TRACKING for conversation {conversation_id}...")
            progress_update = await self._track_progress(message, conversation_id)
            
            # Check for completion or blocking conditions
            completion_check = await self._check_completion(message, conversation_id)
            
            # LOG COMPREHENSIVE STATE UPDATE
            final_state = {
                "conversation_id": conversation_id,
                "current_turn": current_agent.value,
                "turn_count": conversation["turn_count"],
                "handoff_required": handoff_decision["required"],
                "next_agent": handoff_decision.get("next_agent"),
                "handoff_reason": handoff_decision.get("reason"),
                "progress_status": progress_update,
                "completion_status": completion_check,
                "recommended_action": self._get_recommended_action(handoff_decision, progress_update, completion_check)
            }
            
            logger.info(f"🌐 GLOBAL STATE FINAL UPDATE: ConversationState updated with comprehensive context")
            logger.info(f"   📊 State Summary: {final_state['recommended_action']} | Handoff: {final_state['handoff_required']} | Turn: {final_state['turn_count']}")
            
            return final_state
            
        except Exception as e:
            logger.error(f"Turn management failed: {e}")
            return {"error": str(e)}
    
    async def evaluate_handoff(self, message: Message) -> Dict[str, Any]:
        """Public method to evaluate handoff need - determines current agent from message"""
        try:
            # Determine current agent from message sender
            current_agent = self._determine_agent_role_from_message(message)
            if not current_agent:
                return {"required": False, "reason": "could not determine current agent role"}
            
            # Call internal evaluation method
            return await self._evaluate_handoff(message, current_agent)
            
        except Exception as e:
            logger.error(f"Public handoff evaluation failed: {e}")
            return {"required": False, "error": str(e)}
    
    def _determine_agent_role_from_message(self, message: Message) -> Optional[AgentRole]:
        """Determine agent role from message sender identifier"""
        sender_lower = message.sender.lower()
        
        if "frontend" in sender_lower or "ui" in sender_lower:
            return AgentRole.FRONTEND
        elif "backend" in sender_lower or "api" in sender_lower:
            return AgentRole.BACKEND
        elif "orchestrator" in sender_lower or "manager" in sender_lower:
            return AgentRole.ORCHESTRATOR
        
        # Try to infer from message metadata
        if message.metadata and "agent_role" in message.metadata:
            role_str = message.metadata["agent_role"]
            try:
                return AgentRole(role_str)
            except ValueError:
                pass
        
        return None
    
    async def _evaluate_handoff(self, message: Message, current_agent: AgentRole) -> Dict[str, Any]:
        """Evaluate if a handoff should occur based on message content and rules"""
        try:
            for rule in self.handoff_rules:
                if rule["from_role"] == current_agent and rule["condition"](message):
                    return {
                        "required": True,
                        "next_agent": rule["to_role"].value,
                        "reason": rule["trigger"],
                        "message_type": rule["message_type"].value
                    }
            
            return {"required": False}
            
        except Exception as e:
            logger.error(f"Handoff evaluation failed: {e}")
            return {"required": False, "error": str(e)}
    
    async def _track_progress(self, message: Message, conversation_id: str) -> Dict[str, Any]:
        """Track progress markers in the conversation"""
        try:
            if conversation_id not in self.progress_tracking:
                self.progress_tracking[conversation_id] = {
                    "markers": [],
                    "completion_percentage": 0,
                    "blocked_items": [],
                    "completed_items": []
                }
            
            progress = self.progress_tracking[conversation_id]
            
            # Detect progress markers
            content_lower = message.content.lower()
            
            # Completion markers
            completion_keywords = ["completed", "finished", "done", "implemented", "ready"]
            if any(keyword in content_lower for keyword in completion_keywords):
                progress["completed_items"].append({
                    "timestamp": message.timestamp.isoformat(),
                    "description": message.content[:100] + "..." if len(message.content) > 100 else message.content,
                    "agent": message.sender
                })
            
            # Blocking markers
            blocking_keywords = ["blocked", "cannot", "error", "failed", "issue"]
            if any(keyword in content_lower for keyword in blocking_keywords):
                progress["blocked_items"].append({
                    "timestamp": message.timestamp.isoformat(),
                    "description": message.content[:100] + "..." if len(message.content) > 100 else message.content,
                    "agent": message.sender
                })
            
            # Calculate completion percentage (simple heuristic)
            total_items = len(progress["completed_items"]) + len(progress["blocked_items"])
            if total_items > 0:
                progress["completion_percentage"] = (len(progress["completed_items"]) / total_items) * 100
            
            return progress
            
        except Exception as e:
            logger.error(f"Progress tracking failed: {e}")
            return {}
    
    async def _check_completion(self, message: Message, conversation_id: str) -> str:
        """Check if the conversation/task should be considered complete"""
        try:
            content_lower = message.content.lower()
            
            # Strong completion indicators
            strong_completion = ["task completed", "project finished", "implementation done", "all requirements met"]
            if any(phrase in content_lower for phrase in strong_completion):
                return "completed"
            
            # Partial completion indicators  
            partial_completion = ["phase completed", "milestone reached", "ready for next"]
            if any(phrase in content_lower for phrase in partial_completion):
                return "partial_complete"
            
            # Error/blocking indicators
            blocking_indicators = ["cannot proceed", "blocked", "error encountered", "failed to"]
            if any(phrase in content_lower for phrase in blocking_indicators):
                return "blocked"
            
            return "in_progress"
            
        except Exception as e:
            logger.error(f"Completion check failed: {e}")
            return "unknown"
    
    def _get_recommended_action(self, handoff_decision: Dict[str, Any], progress_update: Dict[str, Any], 
                               completion_status: str) -> str:
        """Get recommended next action based on conversation state"""
        if completion_status == "completed":
            return "finalize_conversation"
        elif completion_status == "blocked":
            return "resolve_blocking_issue"
        elif handoff_decision.get("required"):
            return f"handoff_to_{handoff_decision.get('next_agent')}"
        elif len(progress_update.get("completed_items", [])) > 0:
            return "continue_with_next_task"
        else:
            return "continue_current_work"

class MessageBus:
    """
    CENTRALIZED message bus - ÚNICO propietario de MessageTransformationEngine y ConversationStateManager.
    
    ARQUITECTURA CENTRALIZADA:
    - ÚNICO propietario de MessageTransformationEngine (NO duplicar en agents)
    - ÚNICO propietario de ConversationStateManager (NO duplicar en agents)
    - Agents se REGISTRAN con MessageBus para proveer contexto
    - Pipeline centralizado: Agent A → MessageBus (transformation) → Agent B
    - State management global observa TODA la conversación
    - Handoffs automáticos basados en estado global CENTRALIZADO
    
    Features:
    - Intelligent message routing and transformation
    - Automatic context enrichment and role-aware messaging
    - Turn management and handoff coordination
    - Conversation state tracking and progress monitoring
    - Event-driven message handling with autonomous decision making
    - Advanced logging and conversation persistence
    """
    
    def __init__(self, persistence_dir: Optional[Path] = None):
        self.persistence_dir = persistence_dir or Path("conversations")
        self.persistence_dir.mkdir(exist_ok=True)
        
        # CENTRALISED OWNERSHIP - ÚNICO propietario de estos engines
        self.transformation_engine = MessageTransformationEngine()
        self.state_manager = ConversationStateManager()
        
        # Agent registration system - agents se registran aquí
        self.registered_agents = {}
        self.agent_context_providers = {}
        
        # In-memory message storage
        self.messages: List[Message] = []
        self.conversations: Dict[str, ConversationThread] = {}
        
        # Message handlers
        self.message_handlers: Dict[str, List[Callable]] = {}
        
        # Event system for real-time updates
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Message queues for different recipients
        self.message_queues: Dict[str, asyncio.Queue] = {}
        
        # Autonomous communication settings
        self.auto_transform = True
        self.auto_handoff = True
        self.context_enrichment = True
        
        # Agent role mapping
        self.agent_roles = {
            "agent_frontend": AgentRole.FRONTEND,
            "agent_backend": AgentRole.BACKEND,
            "orchestrator": AgentRole.ORCHESTRATOR
        }
        
        # Statistics
        self.stats = {
            "total_messages": 0,
            "messages_by_type": {},
            "active_conversations": 0,
            "transformations": 0,
            "handoffs": 0,
            "errors": 0
        }
        
        logger.info("CENTRALIZED MessageBus initialized - ÚNICO propietario de transformation y state management")
    
    # AGENT REGISTRATION METHODS - Para centralizar todo en MessageBus
    
    def register_agent(self, agent_id: str, agent_role: AgentRole, context_provider: Callable) -> bool:
        """
        Registra un agent con el MessageBus central.
        
        Args:
            agent_id: Identificador único del agent
            agent_role: Rol del agent (FRONTEND, BACKEND, etc.)
            context_provider: Función que provee contexto específico del agent
            
        Returns:
            bool: True si se registró exitosamente
        """
        try:
            # Registrar agent
            self.registered_agents[agent_id] = {
                "role": agent_role,
                "registered_at": datetime.now(timezone.utc).isoformat(),
                "active": True
            }
            
            # Registrar context provider con el transformation engine CENTRALIZADO
            provider_name = f"agent_{agent_id}_context"
            self.transformation_engine.add_context_provider(provider_name, context_provider)
            self.agent_context_providers[agent_id] = context_provider
            
            logger.info(f"Agent {agent_id} ({agent_role.value}) registered with centralized MessageBus")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register agent {agent_id}: {e}")
            return False
    
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Desregistra un agent del MessageBus central.
        
        Args:
            agent_id: Identificador del agent a desregistrar
            
        Returns:
            bool: True si se desregistró exitosamente
        """
        try:
            if agent_id in self.registered_agents:
                # Mark as inactive
                self.registered_agents[agent_id]["active"] = False
                
                # Remove context provider
                if agent_id in self.agent_context_providers:
                    del self.agent_context_providers[agent_id]
                
                logger.info(f"Agent {agent_id} unregistered from centralized MessageBus")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to unregister agent {agent_id}: {e}")
            return False
    
    def get_registered_agents(self) -> Dict[str, Any]:
        """
        Obtiene la lista de agents registrados.
        
        Returns:
            Dict con información de agents registrados
        """
        return self.registered_agents.copy()
    
    async def transform_message_centralized(self, message: Message, from_role: AgentRole, to_role: AgentRole, 
                                          template_id: str, additional_context: Dict[str, Any] = None) -> Message:
        """
        Transforma mensaje usando el transformation engine CENTRALIZADO.
        
        Args:
            message: Mensaje original
            from_role: Rol del agent emisor
            to_role: Rol del agent receptor
            template_id: ID del template a usar
            additional_context: Contexto adicional
            
        Returns:
            Mensaje transformado con contexto enriquecido
        """
        try:
            # Enriquecer contexto usando providers registrados de TODOS los agents
            enriched_context = additional_context or {}
            
            # Agregar contexto de todos los agents registrados activos
            for agent_id, provider in self.agent_context_providers.items():
                if self.registered_agents.get(agent_id, {}).get("active"):
                    try:
                        agent_context = await provider(message, from_role, to_role)
                        if isinstance(agent_context, dict):
                            # Prefix keys con agent_id para evitar conflictos
                            for key, value in agent_context.items():
                                prefixed_key = f"{agent_id}_{key}"
                                enriched_context[prefixed_key] = value
                    except Exception as e:
                        logger.warning(f"Context provider for agent {agent_id} failed: {e}")
            
            # Usar el transformation engine CENTRALIZADO
            transformed_message = await self.transformation_engine.transform_message(
                message, from_role, to_role, template_id, enriched_context
            )
            
            logger.info(f"Message {message.id} transformed using CENTRALIZED transformation engine")
            return transformed_message
            
        except Exception as e:
            logger.error(f"Centralized message transformation failed: {e}")
            return message
    
    async def manage_conversation_state_centralized(self, message: Message, current_agent: AgentRole) -> Dict[str, Any]:
        """
        Maneja el estado de conversación usando el state manager CENTRALIZADO.
        
        Args:
            message: Mensaje actual
            current_agent: Agent actualmente activo
            
        Returns:
            Dict con decisiones de turn management
        """
        try:
            # Usar el state manager CENTRALIZADO que observa TODA la conversación
            turn_decision = await self.state_manager.manage_conversation_turn(message, current_agent)
            
            logger.info(f"Conversation state managed centrally for message {message.id}")
            return turn_decision
            
        except Exception as e:
            logger.error(f"Centralized conversation state management failed: {e}")
            return {"action": "continue", "error": str(e)}
    
    async def send_message(self, message: Message) -> bool:
        """
        Send a message through the bus with validation, transformation, and routing.
        
        Args:
            message: The message to send
            
        Returns:
            bool: True if message was sent successfully
        """
        try:
            # LOG DETAILED INPUT MESSAGE
            logger.info(f"🔥 TRANSFORMATION PIPELINE STARTING for message {message.id}")
            logger.info(f"📥 INPUT MESSAGE: Sender={message.sender}, Recipient={message.recipient}, Type={message.type.value}")
            logger.info(f"📝 INPUT CONTENT (raw): {message.content[:200]}{'...' if len(message.content) > 200 else ''}")
            
            # Validate message
            if not await self._validate_message(message):
                logger.error(f"❌ Message validation failed: {message.id}")
                return False
            
            # Apply CENTRALIZED transformation using registered agents' context
            transformed_message = message
            transformation_occurred = False
            
            if self.auto_transform:
                logger.info(f"🔄 APPLYING CENTRALIZED TRANSFORMATION for {message.id}...")
                transformed_message = await self._apply_centralized_transformation(message)
                
                # DETAILED TRANSFORMATION LOGGING
                if transformed_message != message:
                    transformation_occurred = True
                    self.stats["transformations"] += 1
                    
                    # LOG TRANSFORMATION DETAILS
                    logger.info(f"✅ TRANSFORMATION SUCCESSFUL for message {message.id}")
                    logger.info(f"📤 OUTPUT CONTENT (transformed): {transformed_message.content[:300]}{'...' if len(transformed_message.content) > 300 else ''}")
                    logger.info(f"🔍 TRANSFORMATION METADATA: {transformed_message.metadata.get('transformation', {})}")
                    
                    # EXPLICIT BEFORE/AFTER COMPARISON
                    logger.info(f"🔀 TRANSFORMATION EVIDENCE:")
                    logger.info(f"   Input (raw): '{message.content[:100]}{'...' if len(message.content) > 100 else ''}'")
                    logger.info(f"   Output (transformed): '{transformed_message.content[:100]}{'...' if len(transformed_message.content) > 100 else ''}'")
                    
                else:
                    logger.info(f"ℹ️  No transformation applied to message {message.id} (no matching template or criteria)")
            
            # Add to message history (transformed version)
            self.messages.append(transformed_message)
            self.stats["total_messages"] += 1
            self.stats["messages_by_type"][transformed_message.type.value] = (
                self.stats["messages_by_type"].get(transformed_message.type.value, 0) + 1
            )
            
            # Add to appropriate conversation thread WITH STATE MANAGEMENT LOGGING
            logger.info(f"📋 UPDATING CONVERSATION STATE for message {transformed_message.id}...")
            await self._add_to_conversation(transformed_message)
            
            # DETAILED STATE MANAGEMENT LOGGING
            sender_role = self._get_registered_agent_role(transformed_message.sender)
            if sender_role:
                state_decision = await self.manage_conversation_state_centralized(transformed_message, sender_role)
                logger.info(f"🌐 GLOBAL STATE UPDATED: Action={state_decision.get('action', 'unknown')}, Decision={state_decision}")
            
            # Check for automatic handoff decision WITH DETAILED LOGGING
            if self.auto_handoff:
                logger.info(f"🔄 CHECKING AUTOMATIC HANDOFF for message {transformed_message.id}...")
                await self._check_automatic_handoff(transformed_message)
            
            # Route message to recipient(s)
            await self._route_message(transformed_message)
            
            # Trigger event handlers
            await self._trigger_event("message_sent", transformed_message)
            
            # Persist message
            await self._persist_message(transformed_message)
            
            # FINAL SUCCESS LOG WITH SUMMARY
            logger.info(f"🎉 MESSAGE PIPELINE COMPLETED: {transformed_message.id}")
            logger.info(f"📊 Pipeline Summary: Transformed={transformation_occurred}, From={transformed_message.sender}, To={transformed_message.recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message {message.id}: {e}")
            self.stats["errors"] += 1
            return False
    
    async def _apply_centralized_transformation(self, message: Message) -> Message:
        """
        Apply CENTRALIZED transformation using registered agents' context.
        
        ARQUITECTURA CENTRALIZADA:
        - Usa el transformation engine CENTRALIZADO
        - Enriquece contexto de TODOS los agents registrados
        - Pipeline: Agent → MessageBus (transformation) → Agent
        """
        try:
            # DETAILED TRANSFORMATION PROCESS LOGGING
            logger.info(f"🔄 STARTING CENTRALIZED TRANSFORMATION for message {message.id}")
            
            # Determine sender and recipient roles from registered agents
            sender_role = self._get_registered_agent_role(message.sender)
            recipient_role = self._get_registered_agent_role(message.recipient)
            
            logger.info(f"🎭 ROLES DETERMINED: {message.sender} ({sender_role.value if sender_role else 'unknown'}) → {message.recipient} ({recipient_role.value if recipient_role else 'unknown'})")
            
            if not sender_role or not recipient_role:
                logger.warning(f"⚠️  Could not determine registered agent roles: {message.sender} -> {message.recipient}")
                return message
            
            # Determine appropriate template based on message type and content
            template_id = self._determine_template_id(message, sender_role, recipient_role)
            
            logger.info(f"📋 TEMPLATE SELECTED: {template_id if template_id else 'none'}")
            
            if not template_id:
                logger.info(f"ℹ️  No appropriate template found for message {message.id} - returning original message")
                return message
            
            # LOG BEFORE TRANSFORMATION
            logger.info(f"📥 BEFORE TRANSFORMATION:")
            logger.info(f"   Content: '{message.content[:150]}{'...' if len(message.content) > 150 else ''}'")
            logger.info(f"   Type: {message.type.value}")
            logger.info(f"   Metadata: {message.metadata}")
            
            # Apply CENTRALIZED transformation using enriched context from ALL registered agents
            transformed_message = await self.transform_message_centralized(
                message, sender_role, recipient_role, template_id, {"auto_generated": True, "centralized_pipeline": True}
            )
            
            # LOG AFTER TRANSFORMATION
            logger.info(f"📤 AFTER TRANSFORMATION:")
            logger.info(f"   Content: '{transformed_message.content[:150]}{'...' if len(transformed_message.content) > 150 else ''}'")
            logger.info(f"   Type: {transformed_message.type.value}")
            logger.info(f"   New Metadata: {transformed_message.metadata}")
            
            # EXPLICIT TRANSFORMATION EVIDENCE
            logger.info(f"✅ TRANSFORMATION EVIDENCE: Message transformed from [{message.content[:50]}...] to [{transformed_message.content[:50]}...]")
            logger.info(f"🔧 Template {template_id} successfully applied: {message.sender} → {message.recipient}")
            
            return transformed_message
            
        except Exception as e:
            logger.error(f"❌ CENTRALIZED transformation failed for message {message.id}: {e}")
            return message
    
    def _get_registered_agent_role(self, agent_identifier: str) -> Optional[AgentRole]:
        """Get role from registered agents (CENTRALIZED lookup)"""
        # Check in registered agents first (authoritative source)
        for agent_id, agent_info in self.registered_agents.items():
            if agent_id == agent_identifier or agent_identifier.endswith(agent_id):
                return agent_info.get("role")
        
        # Fallback to original method for compatibility
        return self._get_agent_role(agent_identifier)
    
    def _get_agent_role(self, agent_identifier: str) -> Optional[AgentRole]:
        """Get agent role from identifier"""
        # Direct mapping from configured roles
        if agent_identifier in self.agent_roles:
            return self.agent_roles[agent_identifier]
        
        # Try to infer from identifier name
        identifier_lower = agent_identifier.lower()
        if "frontend" in identifier_lower or "ui" in identifier_lower:
            return AgentRole.FRONTEND
        elif "backend" in identifier_lower or "api" in identifier_lower:
            return AgentRole.BACKEND
        elif "orchestrator" in identifier_lower or "manager" in identifier_lower:
            return AgentRole.ORCHESTRATOR
        
        return None
    
    def _determine_template_id(self, message: Message, sender_role: AgentRole, recipient_role: AgentRole) -> Optional[str]:
        """Determine appropriate template ID based on message context"""
        content_lower = message.content.lower()
        
        # Frontend to Backend transformations
        if sender_role == AgentRole.FRONTEND and recipient_role == AgentRole.BACKEND:
            if "api" in content_lower or "endpoint" in content_lower or "implement" in content_lower:
                return "frontend_to_backend_api_request"
        
        # Backend to Frontend transformations  
        elif sender_role == AgentRole.BACKEND and recipient_role == AgentRole.FRONTEND:
            if "complete" in content_lower or "ready" in content_lower or "implemented" in content_lower:
                return "backend_to_frontend_api_ready"
        
        # Orchestrator to Agent transformations
        elif sender_role == AgentRole.ORCHESTRATOR:
            if recipient_role == AgentRole.FRONTEND:
                return "orchestrator_to_frontend_task"
            elif recipient_role == AgentRole.BACKEND:
                return "orchestrator_to_backend_task"
        
        return None
    
    async def _check_automatic_handoff(self, message: Message):
        """Check if automatic handoff should occur based on message content"""
        try:
            # Use state manager to evaluate handoff need
            decision = await self.state_manager.evaluate_handoff(message)
            
            if decision.get("required", False):
                next_agent = decision.get("next_agent")
                handoff_reason = decision.get("reason", "automatic handoff")
                
                # Create handoff message
                handoff_message = Message(
                    type=MessageType.HANDOFF,
                    sender="system",
                    recipient=next_agent,
                    content=f"Automatic handoff initiated: {handoff_reason}",
                    session_id=message.session_id,
                    metadata={
                        "handoff_reason": handoff_reason,
                        "original_message_id": message.id,
                        "handoff_source": message.sender
                    }
                )
                
                # Send handoff message (without transformation to avoid recursion)
                original_auto_transform = self.auto_transform
                self.auto_transform = False
                await self.send_message(handoff_message)
                self.auto_transform = original_auto_transform
                
                self.stats["handoffs"] += 1
                logger.info(f"Automatic handoff executed from {message.sender} to {next_agent}")
                
        except Exception as e:
            logger.error(f"Automatic handoff check failed: {e}")
    
    async def _validate_message(self, message: Message) -> bool:
        """Validate message structure and content"""
        try:
            # Check required fields
            if not all([message.type, message.sender, message.recipient, message.content, message.session_id]):
                return False
            
            # Check message type
            if not isinstance(message.type, MessageType):
                return False
            
            # Check content length (prevent extremely large messages)
            if len(message.content) > 50000:  # 50KB limit
                logger.warning(f"Message content too large: {len(message.content)} chars")
                return False
            
            # Check for circular references (sender == recipient for non-system messages)
            if message.sender == message.recipient and message.type != MessageType.SYSTEM:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Message validation error: {e}")
            return False
    
    async def _add_to_conversation(self, message: Message):
        """Add message to appropriate conversation thread"""
        try:
            # Find existing conversation or create new one
            conversation_id = self._get_conversation_id(message.sender, message.recipient, message.session_id)
            
            if conversation_id not in self.conversations:
                # Create new conversation
                participants = list(set([message.sender, message.recipient]))
                self.conversations[conversation_id] = ConversationThread(
                    id=conversation_id,
                    participants=participants,
                    session_id=message.session_id,
                    created_at=datetime.now(timezone.utc),
                    messages=[]
                )
                self.stats["active_conversations"] += 1
            
            # Add message to conversation
            self.conversations[conversation_id].messages.append(message)
            
        except Exception as e:
            logger.error(f"Error adding message to conversation: {e}")
    
    def _get_conversation_id(self, sender: str, recipient: str, session_id: str) -> str:
        """Generate conversation ID for a sender-recipient pair"""
        # Create deterministic conversation ID
        participants = sorted([sender, recipient])
        return f"{session_id}_{participants[0]}_{participants[1]}"
    
    async def _route_message(self, message: Message):
        """Route message to appropriate recipient queue"""
        try:
            # Handle broadcast messages
            if message.recipient == "both" or message.recipient == "all":
                # Route to all active agents
                for queue_name in self.message_queues:
                    if queue_name.startswith("agent_"):
                        await self._add_to_queue(queue_name, message)
            else:
                # Route to specific recipient
                await self._add_to_queue(message.recipient, message)
                
        except Exception as e:
            logger.error(f"Message routing error: {e}")
    
    async def _add_to_queue(self, recipient: str, message: Message):
        """Add message to recipient's queue"""
        try:
            # Create queue if it doesn't exist
            if recipient not in self.message_queues:
                self.message_queues[recipient] = asyncio.Queue()
            
            # Add message to queue
            await self.message_queues[recipient].put(message)
            
        except Exception as e:
            logger.error(f"Error adding message to queue {recipient}: {e}")
    
    async def receive_message(self, recipient: str, timeout: Optional[float] = None) -> Optional[Message]:
        """
        Receive a message from the recipient's queue.
        
        Args:
            recipient: The recipient identifier
            timeout: Optional timeout in seconds
            
        Returns:
            Message or None if timeout
        """
        try:
            # Create queue if it doesn't exist
            if recipient not in self.message_queues:
                self.message_queues[recipient] = asyncio.Queue()
            
            # Get message from queue
            if timeout:
                message = await asyncio.wait_for(
                    self.message_queues[recipient].get(),
                    timeout=timeout
                )
            else:
                message = await self.message_queues[recipient].get()
            
            logger.info(f"Message received by {recipient}: {message.id}")
            return message
            
        except asyncio.TimeoutError:
            logger.debug(f"Message receive timeout for {recipient}")
            return None
        except Exception as e:
            logger.error(f"Error receiving message for {recipient}: {e}")
            return None
    
    async def get_conversation(self, conversation_id: str) -> Optional[ConversationThread]:
        """Get conversation thread by ID"""
        return self.conversations.get(conversation_id)
    
    async def get_conversation_between(self, sender: str, recipient: str, session_id: str) -> Optional[ConversationThread]:
        """Get conversation between two participants"""
        conversation_id = self._get_conversation_id(sender, recipient, session_id)
        return await self.get_conversation(conversation_id)
    
    async def get_recent_messages(self, count: int = 10, session_id: Optional[str] = None) -> List[Message]:
        """Get recent messages, optionally filtered by session"""
        try:
            messages = self.messages
            
            if session_id:
                messages = [msg for msg in messages if msg.session_id == session_id]
            
            # Sort by timestamp and return most recent
            messages.sort(key=lambda x: x.timestamp, reverse=True)
            return messages[:count]
            
        except Exception as e:
            logger.error(f"Error getting recent messages: {e}")
            return []
    
    async def get_message_count(self, session_id: Optional[str] = None) -> int:
        """Get total message count, optionally filtered by session"""
        if session_id:
            return len([msg for msg in self.messages if msg.session_id == session_id])
        return len(self.messages)
    
    async def register_message_handler(self, message_type: str, handler: Callable):
        """Register a handler for specific message types"""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
    
    async def register_event_handler(self, event_type: str, handler: Callable):
        """Register a handler for system events"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def _trigger_event(self, event_type: str, data: Any):
        """Trigger event handlers"""
        try:
            if event_type in self.event_handlers:
                for handler in self.event_handlers[event_type]:
                    await handler(data)
        except Exception as e:
            logger.error(f"Error triggering event {event_type}: {e}")
    
    async def _persist_message(self, message: Message):
        """Persist message to disk"""
        try:
            # Create session directory
            session_dir = self.persistence_dir / message.session_id
            session_dir.mkdir(exist_ok=True)
            
            # Save message to session log
            message_log = session_dir / "messages.jsonl"
            message_data = asdict(message)
            message_data['timestamp'] = message.timestamp.isoformat()
            message_data['type'] = message.type.value
            message_data['priority'] = message.priority.value
            
            with open(message_log, 'a') as f:
                f.write(json.dumps(message_data) + '\n')
                
        except Exception as e:
            logger.error(f"Error persisting message: {e}")
    
    async def load_conversation_history(self, session_id: str) -> List[Message]:
        """Load conversation history from disk"""
        try:
            session_dir = self.persistence_dir / session_id
            message_log = session_dir / "messages.jsonl"
            
            if not message_log.exists():
                return []
            
            messages = []
            with open(message_log, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        message = Message(
                            type=MessageType(data['type']),
                            sender=data['sender'],
                            recipient=data['recipient'],
                            content=data['content'],
                            session_id=data['session_id'],
                            id=data['id'],
                            timestamp=datetime.fromisoformat(data['timestamp']),
                            priority=MessagePriority(data['priority']),
                            metadata=data.get('metadata', {}),
                            reply_to=data.get('reply_to'),
                            requires_response=data.get('requires_response', False)
                        )
                        messages.append(message)
                    except Exception as e:
                        logger.warning(f"Error parsing message line: {e}")
            
            logger.info(f"Loaded {len(messages)} messages for session {session_id}")
            return messages
            
        except Exception as e:
            logger.error(f"Error loading conversation history: {e}")
            return []
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get communication statistics"""
        return {
            **self.stats,
            "active_queues": len(self.message_queues),
            "conversation_count": len(self.conversations)
        }
    
    async def clear_session_data(self, session_id: str):
        """Clear all data for a specific session"""
        try:
            # Remove messages
            self.messages = [msg for msg in self.messages if msg.session_id != session_id]
            
            # Remove conversations
            to_remove = [conv_id for conv_id, conv in self.conversations.items() 
                        if conv.session_id == session_id]
            for conv_id in to_remove:
                del self.conversations[conv_id]
            
            logger.info(f"Cleared data for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error clearing session data: {e}")
    
    async def shutdown(self):
        """Graceful shutdown of message bus"""
        try:
            # Close all queues
            for queue in self.message_queues.values():
                while not queue.empty():
                    try:
                        queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break
            
            self.message_queues.clear()
            
            # Clear handlers
            self.message_handlers.clear()
            self.event_handlers.clear()
            
            logger.info("MessageBus shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during MessageBus shutdown: {e}")


# Utility functions
async def create_system_message(content: str, session_id: str, recipient: str = "all") -> Message:
    """Create a system message"""
    return Message(
        type=MessageType.SYSTEM,
        sender="system",
        recipient=recipient,
        content=content,
        session_id=session_id,
        priority=MessagePriority.HIGH
    )

async def create_task_message(content: str, sender: str, recipient: str, session_id: str) -> Message:
    """Create a task assignment message"""
    return Message(
        type=MessageType.TASK,
        sender=sender,
        recipient=recipient,
        content=content,
        session_id=session_id,
        requires_response=True
    )

async def create_coordination_message(content: str, session_id: str) -> Message:
    """Create a coordination message for both agents"""
    return Message(
        type=MessageType.COORDINATION,
        sender="orchestrator",
        recipient="both",
        content=content,
        session_id=session_id,
        priority=MessagePriority.HIGH
    )

class MessageLogger:
    """Enhanced logging for message conversations"""
    
    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(exist_ok=True)
    
    async def log_conversation(self, conversation: ConversationThread):
        """Log a complete conversation thread"""
        try:
            log_file = self.log_dir / f"conversation_{conversation.id}.md"
            
            with open(log_file, 'w') as f:
                f.write(f"# Conversation: {conversation.id}\n\n")
                f.write(f"**Participants:** {', '.join(conversation.participants)}\n")
                f.write(f"**Session:** {conversation.session_id}\n")
                f.write(f"**Created:** {conversation.created_at.isoformat()}\n")
                f.write(f"**Messages:** {len(conversation.messages)}\n\n")
                
                f.write("## Messages\n\n")
                
                for msg in conversation.messages:
                    f.write(f"### {msg.timestamp.strftime('%H:%M:%S')} - {msg.sender} → {msg.recipient}\n")
                    f.write(f"**Type:** {msg.type.value}\n")
                    if msg.priority != MessagePriority.NORMAL:
                        f.write(f"**Priority:** {msg.priority.value}\n")
                    f.write(f"\n{msg.content}\n\n")
                    f.write("---\n\n")
            
            logger.info(f"Conversation logged: {log_file}")
            
        except Exception as e:
            logger.error(f"Error logging conversation: {e}")