#!/usr/bin/env python3
"""
Enhanced Evidence Capture System for AI-Bridge Closed-Loop Communication

Captures complete evidence of A→B→A cycles including:
- Raw message payloads
- Transformed message payloads  
- Delivery confirmations
- Processing evidence from recipient agents
- Response generation tracking
- Complete conversation transcripts
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Configure evidence logger
evidence_logger = logging.getLogger("evidence_capture")

class EvidenceType(Enum):
    """Types of evidence captured"""
    RAW_MESSAGE = "raw_message"
    TRANSFORMED_MESSAGE = "transformed_message"
    DELIVERY_CONFIRMATION = "delivery_confirmation"
    PROCESSING_START = "processing_start"
    PROCESSING_COMPLETE = "processing_complete" 
    RESPONSE_GENERATED = "response_generated"
    HANDOFF_TRIGGERED = "handoff_triggered"
    CYCLE_COMPLETE = "cycle_complete"

@dataclass
class EvidenceRecord:
    """Individual evidence record"""
    id: str
    type: EvidenceType
    timestamp: datetime
    session_id: str
    agent_id: str
    message_id: str
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ConversationCycleEvidence:
    """Complete evidence for one A→B→A cycle"""
    cycle_id: str
    session_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    participants: List[str] = None
    evidence_records: List[EvidenceRecord] = None
    transcript: List[Dict[str, Any]] = None
    is_complete: bool = False
    
    def __post_init__(self):
        if self.participants is None:
            self.participants = []
        if self.evidence_records is None:
            self.evidence_records = []
        if self.transcript is None:
            self.transcript = []

class EnhancedEvidenceCapture:
    """
    Enhanced evidence capture system for complete closed-loop documentation.
    
    Captures and documents:
    - Original raw messages
    - Complete payload transformations
    - Delivery confirmations with exact payloads received
    - Agent processing evidence and understanding
    - Response generation with causality tracking
    - Complete A→B→A cycle documentation
    """
    
    def __init__(self, evidence_dir: str = "evidence"):
        self.evidence_dir = Path(evidence_dir)
        self.evidence_dir.mkdir(exist_ok=True)
        
        # Active conversation cycles being tracked
        self.active_cycles: Dict[str, ConversationCycleEvidence] = {}
        
        # Evidence storage
        self.evidence_records: List[EvidenceRecord] = []
        
        # Session tracking
        self.session_cycles: Dict[str, List[str]] = {}
        
        evidence_logger.info("Enhanced Evidence Capture System initialized")
    
    async def start_conversation_cycle(self, session_id: str, participants: List[str]) -> str:
        """Start tracking a new conversation cycle"""
        cycle_id = str(uuid.uuid4())
        
        cycle_evidence = ConversationCycleEvidence(
            cycle_id=cycle_id,
            session_id=session_id,
            started_at=datetime.now(timezone.utc),
            participants=participants
        )
        
        self.active_cycles[cycle_id] = cycle_evidence
        
        if session_id not in self.session_cycles:
            self.session_cycles[session_id] = []
        self.session_cycles[session_id].append(cycle_id)
        
        evidence_logger.info(f"Started conversation cycle {cycle_id} for session {session_id}")
        return cycle_id
    
    async def capture_raw_message(self, cycle_id: str, message_id: str, sender: str, 
                                  recipient: str, content: str, message_type: str) -> str:
        """Capture original raw message before transformation"""
        evidence_id = str(uuid.uuid4())
        
        evidence = EvidenceRecord(
            id=evidence_id,
            type=EvidenceType.RAW_MESSAGE,
            timestamp=datetime.now(timezone.utc),
            session_id=self.active_cycles[cycle_id].session_id,
            agent_id=sender,
            message_id=message_id,
            payload={
                "raw_content": content,
                "sender": sender,
                "recipient": recipient,
                "message_type": message_type,
                "content_length": len(content),
                "content_preview": content[:100] + "..." if len(content) > 100 else content
            },
            metadata={
                "capture_stage": "before_transformation",
                "cycle_id": cycle_id
            }
        )
        
        self.evidence_records.append(evidence)
        self.active_cycles[cycle_id].evidence_records.append(evidence)
        
        # Add to transcript
        self.active_cycles[cycle_id].transcript.append({
            "step": len(self.active_cycles[cycle_id].transcript) + 1,
            "stage": "RAW_MESSAGE",
            "timestamp": evidence.timestamp.isoformat(),
            "sender": sender,
            "recipient": recipient,
            "content": content,
            "evidence_id": evidence_id
        })
        
        evidence_logger.info(f"Captured raw message {message_id} from {sender} to {recipient}")
        return evidence_id
    
    async def capture_transformed_message(self, cycle_id: str, message_id: str, 
                                          original_content: str, transformed_content: str,
                                          transformation_template: str, context_used: Dict[str, Any],
                                          sender: str, recipient: str) -> str:
        """Capture complete payload transformation details"""
        evidence_id = str(uuid.uuid4())
        
        evidence = EvidenceRecord(
            id=evidence_id,
            type=EvidenceType.TRANSFORMED_MESSAGE,
            timestamp=datetime.now(timezone.utc),
            session_id=self.active_cycles[cycle_id].session_id,
            agent_id=sender,
            message_id=message_id,
            payload={
                "original_content": original_content,
                "transformed_content": transformed_content,
                "transformation_template": transformation_template,
                "context_used": context_used,
                "sender": sender,
                "recipient": recipient,
                "transformation_size_change": len(transformed_content) - len(original_content),
                "exactly_what_recipient_receives": transformed_content
            },
            metadata={
                "capture_stage": "after_transformation",
                "cycle_id": cycle_id,
                "template_applied": transformation_template
            }
        )
        
        self.evidence_records.append(evidence)
        self.active_cycles[cycle_id].evidence_records.append(evidence)
        
        # Add to transcript
        self.active_cycles[cycle_id].transcript.append({
            "step": len(self.active_cycles[cycle_id].transcript) + 1,
            "stage": "TRANSFORMATION",
            "timestamp": evidence.timestamp.isoformat(),
            "original_message": original_content,
            "transformed_message": transformed_content,
            "template_used": transformation_template,
            "context_applied": context_used,
            "exactly_what_recipient_receives": transformed_content,
            "evidence_id": evidence_id
        })
        
        evidence_logger.info(f"Captured transformation for message {message_id}: {len(original_content)} → {len(transformed_content)} chars")
        return evidence_id
    
    async def capture_delivery_confirmation(self, cycle_id: str, message_id: str,
                                            recipient: str, delivered_content: str) -> str:
        """Capture confirmation that message was delivered to recipient with exact payload"""
        evidence_id = str(uuid.uuid4())
        
        evidence = EvidenceRecord(
            id=evidence_id,
            type=EvidenceType.DELIVERY_CONFIRMATION,
            timestamp=datetime.now(timezone.utc),
            session_id=self.active_cycles[cycle_id].session_id,
            agent_id=recipient,
            message_id=message_id,
            payload={
                "recipient": recipient,
                "delivered_content": delivered_content,
                "delivered_at": datetime.now(timezone.utc).isoformat(),
                "content_length": len(delivered_content),
                "delivery_confirmed": True
            },
            metadata={
                "capture_stage": "delivery_confirmed",
                "cycle_id": cycle_id
            }
        )
        
        self.evidence_records.append(evidence)
        self.active_cycles[cycle_id].evidence_records.append(evidence)
        
        # Add to transcript
        self.active_cycles[cycle_id].transcript.append({
            "step": len(self.active_cycles[cycle_id].transcript) + 1,
            "stage": "DELIVERY_CONFIRMED",
            "timestamp": evidence.timestamp.isoformat(),
            "recipient": recipient,
            "delivered_content": delivered_content,
            "confirmation": "Message successfully delivered to recipient",
            "evidence_id": evidence_id
        })
        
        evidence_logger.info(f"Captured delivery confirmation for message {message_id} to {recipient}")
        return evidence_id
    
    async def capture_processing_start(self, cycle_id: str, message_id: str, 
                                       agent_id: str, received_content: str) -> str:
        """Capture when agent starts processing received message"""
        evidence_id = str(uuid.uuid4())
        
        evidence = EvidenceRecord(
            id=evidence_id,
            type=EvidenceType.PROCESSING_START,
            timestamp=datetime.now(timezone.utc),
            session_id=self.active_cycles[cycle_id].session_id,
            agent_id=agent_id,
            message_id=message_id,
            payload={
                "agent_id": agent_id,
                "received_content": received_content,
                "processing_started_at": datetime.now(timezone.utc).isoformat(),
                "content_length": len(received_content)
            },
            metadata={
                "capture_stage": "processing_started",
                "cycle_id": cycle_id
            }
        )
        
        self.evidence_records.append(evidence)
        self.active_cycles[cycle_id].evidence_records.append(evidence)
        
        # Add to transcript
        self.active_cycles[cycle_id].transcript.append({
            "step": len(self.active_cycles[cycle_id].transcript) + 1,
            "stage": "PROCESSING_STARTED",
            "timestamp": evidence.timestamp.isoformat(),
            "agent": agent_id,
            "status": "Agent began processing received message",
            "received_content": received_content,
            "evidence_id": evidence_id
        })
        
        evidence_logger.info(f"Captured processing start for message {message_id} by agent {agent_id}")
        return evidence_id
    
    async def capture_processing_complete(self, cycle_id: str, message_id: str,
                                          agent_id: str, understanding_evidence: str,
                                          actions_taken: List[str]) -> str:
        """Capture evidence that agent understood and acted on the message"""
        evidence_id = str(uuid.uuid4())
        
        evidence = EvidenceRecord(
            id=evidence_id,
            type=EvidenceType.PROCESSING_COMPLETE,
            timestamp=datetime.now(timezone.utc),
            session_id=self.active_cycles[cycle_id].session_id,
            agent_id=agent_id,
            message_id=message_id,
            payload={
                "agent_id": agent_id,
                "understanding_evidence": understanding_evidence,
                "actions_taken": actions_taken,
                "processing_completed_at": datetime.now(timezone.utc).isoformat(),
                "demonstrates_understanding": True
            },
            metadata={
                "capture_stage": "processing_completed",
                "cycle_id": cycle_id,
                "understanding_confirmed": True
            }
        )
        
        self.evidence_records.append(evidence)
        self.active_cycles[cycle_id].evidence_records.append(evidence)
        
        # Add to transcript
        self.active_cycles[cycle_id].transcript.append({
            "step": len(self.active_cycles[cycle_id].transcript) + 1,
            "stage": "PROCESSING_COMPLETED",
            "timestamp": evidence.timestamp.isoformat(),
            "agent": agent_id,
            "status": "Agent completed processing and demonstrated understanding",
            "understanding_evidence": understanding_evidence,
            "actions_taken": actions_taken,
            "evidence_id": evidence_id
        })
        
        evidence_logger.info(f"Captured processing completion for message {message_id} by agent {agent_id}")
        return evidence_id
    
    async def capture_response_generated(self, cycle_id: str, original_message_id: str,
                                         response_message_id: str, agent_id: str,
                                         response_content: str, causality_evidence: str) -> str:
        """Capture response generated as direct result of processed message"""
        evidence_id = str(uuid.uuid4())
        
        evidence = EvidenceRecord(
            id=evidence_id,
            type=EvidenceType.RESPONSE_GENERATED,
            timestamp=datetime.now(timezone.utc),
            session_id=self.active_cycles[cycle_id].session_id,
            agent_id=agent_id,
            message_id=response_message_id,
            payload={
                "agent_id": agent_id,
                "original_message_id": original_message_id,
                "response_message_id": response_message_id,
                "response_content": response_content,
                "causality_evidence": causality_evidence,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "is_direct_response": True
            },
            metadata={
                "capture_stage": "response_generated",
                "cycle_id": cycle_id,
                "causal_link_confirmed": True,
                "original_message_id": original_message_id
            }
        )
        
        self.evidence_records.append(evidence)
        self.active_cycles[cycle_id].evidence_records.append(evidence)
        
        # Add to transcript
        self.active_cycles[cycle_id].transcript.append({
            "step": len(self.active_cycles[cycle_id].transcript) + 1,
            "stage": "RESPONSE_GENERATED",
            "timestamp": evidence.timestamp.isoformat(),
            "agent": agent_id,
            "status": "Agent generated response based on processed message",
            "response_content": response_content,
            "causality_evidence": causality_evidence,
            "original_message_id": original_message_id,
            "evidence_id": evidence_id
        })
        
        evidence_logger.info(f"Captured response generation for original message {original_message_id}")
        return evidence_id
    
    async def capture_handoff_triggered(self, cycle_id: str, message_id: str,
                                        from_agent: str, to_agent: str, reason: str) -> str:
        """Capture automatic handoff between agents"""
        evidence_id = str(uuid.uuid4())
        
        evidence = EvidenceRecord(
            id=evidence_id,
            type=EvidenceType.HANDOFF_TRIGGERED,
            timestamp=datetime.now(timezone.utc),
            session_id=self.active_cycles[cycle_id].session_id,
            agent_id=from_agent,
            message_id=message_id,
            payload={
                "from_agent": from_agent,
                "to_agent": to_agent,
                "handoff_reason": reason,
                "triggered_at": datetime.now(timezone.utc).isoformat(),
                "automatic_handoff": True
            },
            metadata={
                "capture_stage": "handoff_triggered",
                "cycle_id": cycle_id,
                "handoff_direction": f"{from_agent}→{to_agent}"
            }
        )
        
        self.evidence_records.append(evidence)
        self.active_cycles[cycle_id].evidence_records.append(evidence)
        
        # Add to transcript
        self.active_cycles[cycle_id].transcript.append({
            "step": len(self.active_cycles[cycle_id].transcript) + 1,
            "stage": "HANDOFF_TRIGGERED",
            "timestamp": evidence.timestamp.isoformat(),
            "from_agent": from_agent,
            "to_agent": to_agent,
            "status": "Automatic handoff triggered",
            "reason": reason,
            "evidence_id": evidence_id
        })
        
        evidence_logger.info(f"Captured handoff from {from_agent} to {to_agent}: {reason}")
        return evidence_id
    
    async def complete_conversation_cycle(self, cycle_id: str) -> ConversationCycleEvidence:
        """Mark conversation cycle as complete and generate final evidence"""
        if cycle_id not in self.active_cycles:
            raise ValueError(f"Cycle {cycle_id} not found")
        
        cycle = self.active_cycles[cycle_id]
        cycle.completed_at = datetime.now(timezone.utc)
        cycle.is_complete = True
        
        # Capture cycle completion evidence
        evidence_id = str(uuid.uuid4())
        evidence = EvidenceRecord(
            id=evidence_id,
            type=EvidenceType.CYCLE_COMPLETE,
            timestamp=datetime.now(timezone.utc),
            session_id=cycle.session_id,
            agent_id="system",
            message_id="cycle_complete",
            payload={
                "cycle_id": cycle_id,
                "completed_at": cycle.completed_at.isoformat(),
                "total_evidence_records": len(cycle.evidence_records),
                "transcript_steps": len(cycle.transcript),
                "participants": cycle.participants,
                "duration_seconds": (cycle.completed_at - cycle.started_at).total_seconds()
            },
            metadata={
                "capture_stage": "cycle_completed",
                "cycle_id": cycle_id,
                "complete_evidence": True
            }
        )
        
        self.evidence_records.append(evidence)
        cycle.evidence_records.append(evidence)
        
        # Add final transcript entry
        cycle.transcript.append({
            "step": len(cycle.transcript) + 1,
            "stage": "CYCLE_COMPLETE",
            "timestamp": evidence.timestamp.isoformat(),
            "status": "Complete A→B→A cycle documented",
            "summary": f"Captured {len(cycle.evidence_records)} evidence records",
            "evidence_id": evidence_id
        })
        
        # Save to file
        await self._save_cycle_evidence(cycle)
        
        evidence_logger.info(f"Completed conversation cycle {cycle_id} with {len(cycle.evidence_records)} evidence records")
        return cycle
    
    async def _save_cycle_evidence(self, cycle: ConversationCycleEvidence):
        """Save cycle evidence to file"""
        try:
            cycle_file = self.evidence_dir / f"cycle_{cycle.cycle_id}.json"
            
            # Convert to serializable format
            cycle_data = {
                "cycle_id": cycle.cycle_id,
                "session_id": cycle.session_id,
                "started_at": cycle.started_at.isoformat(),
                "completed_at": cycle.completed_at.isoformat() if cycle.completed_at else None,
                "participants": cycle.participants,
                "is_complete": cycle.is_complete,
                "evidence_records": [
                    {
                        "id": record.id,
                        "type": record.type.value,
                        "timestamp": record.timestamp.isoformat(),
                        "session_id": record.session_id,
                        "agent_id": record.agent_id,
                        "message_id": record.message_id,
                        "payload": record.payload,
                        "metadata": record.metadata
                    }
                    for record in cycle.evidence_records
                ],
                "transcript": cycle.transcript
            }
            
            with open(cycle_file, 'w') as f:
                json.dump(cycle_data, f, indent=2)
            
            evidence_logger.info(f"Saved cycle evidence to {cycle_file}")
            
        except Exception as e:
            evidence_logger.error(f"Failed to save cycle evidence: {e}")
    
    async def get_cycle_evidence(self, cycle_id: str) -> Optional[ConversationCycleEvidence]:
        """Get evidence for a specific cycle"""
        return self.active_cycles.get(cycle_id)
    
    async def get_complete_transcript(self, cycle_id: str) -> List[Dict[str, Any]]:
        """Get complete transcript for a cycle"""
        if cycle_id in self.active_cycles:
            return self.active_cycles[cycle_id].transcript
        return []
    
    async def generate_evidence_summary(self, cycle_id: str) -> Dict[str, Any]:
        """Generate comprehensive evidence summary for architect review"""
        if cycle_id not in self.active_cycles:
            return {"error": f"Cycle {cycle_id} not found"}
        
        cycle = self.active_cycles[cycle_id]
        
        # Extract key evidence
        raw_messages = [r for r in cycle.evidence_records if r.type == EvidenceType.RAW_MESSAGE]
        transformations = [r for r in cycle.evidence_records if r.type == EvidenceType.TRANSFORMED_MESSAGE]
        deliveries = [r for r in cycle.evidence_records if r.type == EvidenceType.DELIVERY_CONFIRMATION]
        processing = [r for r in cycle.evidence_records if r.type == EvidenceType.PROCESSING_COMPLETE]
        responses = [r for r in cycle.evidence_records if r.type == EvidenceType.RESPONSE_GENERATED]
        handoffs = [r for r in cycle.evidence_records if r.type == EvidenceType.HANDOFF_TRIGGERED]
        
        summary = {
            "cycle_id": cycle_id,
            "complete_evidence_captured": cycle.is_complete,
            "evidence_summary": {
                "raw_messages_captured": len(raw_messages),
                "transformations_documented": len(transformations),
                "deliveries_confirmed": len(deliveries),
                "processing_evidence": len(processing),
                "responses_generated": len(responses),
                "handoffs_triggered": len(handoffs)
            },
            "payload_evidence": {
                "raw_payloads": [r.payload["raw_content"] for r in raw_messages],
                "transformed_payloads": [r.payload["exactly_what_recipient_receives"] for r in transformations],
                "delivery_confirmations": [r.payload["delivered_content"] for r in deliveries]
            },
            "consumption_evidence": [r.payload["understanding_evidence"] for r in processing],
            "response_causality": [
                {
                    "original_message": r.payload["original_message_id"],
                    "response_content": r.payload["response_content"],
                    "causality_evidence": r.payload["causality_evidence"]
                }
                for r in responses
            ],
            "complete_transcript": cycle.transcript,
            "autonomous_collaboration_evidence": len(handoffs) > 0 and len(responses) > 0
        }
        
        return summary