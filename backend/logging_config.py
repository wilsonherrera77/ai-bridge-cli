#!/usr/bin/env python3
"""
Structured Logging Configuration for AI-Bridge Orchestration System

Provides centralized logging configuration with:
- Structured JSON logging with timestamps and context
- Session-specific log files
- Multiple log levels and handlers
- Performance and audit logging
- Real-time log streaming
"""

import logging
import logging.config
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
import uuid

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def format(self, record):
        # Create base log entry
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add session context if available
        if hasattr(record, 'session_id'):
            log_entry["session_id"] = record.session_id
        
        if hasattr(record, 'agent_id'):
            log_entry["agent_id"] = record.agent_id
            
        if hasattr(record, 'workflow_id'):
            log_entry["workflow_id"] = record.workflow_id
            
        if hasattr(record, 'message_id'):
            log_entry["message_id"] = record.message_id
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add any extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'exc_info', 'exc_text', 'stack_info']:
                if not key.startswith('_'):
                    log_entry[key] = value
        
        return json.dumps(log_entry, default=str)

class OrchestrationLoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that adds orchestration context to log records"""
    
    def __init__(self, logger, extra=None):
        super().__init__(logger, extra or {})
    
    def process(self, msg, kwargs):
        # Add context to the log record
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        
        kwargs['extra'].update(self.extra)
        return msg, kwargs

def setup_logging(
    log_dir: str = "logs",
    log_level: str = "INFO",
    session_id: Optional[str] = None,
    enable_console: bool = True,
    enable_file: bool = True,
    enable_json: bool = True
) -> Dict[str, logging.Logger]:
    """
    Setup structured logging for the orchestration system.
    
    Args:
        log_dir: Directory for log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        session_id: Optional session ID for session-specific logging
        enable_console: Enable console logging
        enable_file: Enable file logging
        enable_json: Enable JSON formatted logging
        
    Returns:
        Dictionary of configured loggers
    """
    
    # Create log directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Create session-specific directory if session_id provided
    if session_id:
        session_log_path = log_path / session_id
        session_log_path.mkdir(exist_ok=True)
    else:
        session_log_path = log_path
    
    # Configure handlers
    handlers = {}
    formatters = {}
    
    # Console handler
    if enable_console:
        handlers['console'] = {
            'class': 'logging.StreamHandler',
            'level': log_level,
            'formatter': 'simple',
            'stream': 'ext://sys.stdout'
        }
        
        formatters['simple'] = {
            'format': '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    
    # File handlers
    if enable_file:
        # Main application log
        handlers['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': log_level,
            'formatter': 'simple' if not enable_json else 'structured',
            'filename': str(session_log_path / 'orchestration.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
        
        # Error log
        handlers['error_file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'simple' if not enable_json else 'structured',
            'filename': str(session_log_path / 'errors.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 3
        }
        
        # Agent-specific logs
        handlers['agent_file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'structured' if enable_json else 'simple',
            'filename': str(session_log_path / 'agents.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
        
        # Communication logs
        handlers['communication_file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'structured' if enable_json else 'simple',
            'filename': str(session_log_path / 'communication.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
        
        # Workflow logs
        handlers['workflow_file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'structured' if enable_json else 'simple',
            'filename': str(session_log_path / 'workflow.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
    
    # JSON formatter for structured logging
    if enable_json:
        formatters['structured'] = {
            '()': StructuredFormatter
        }
    
    # Logger configuration
    logger_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': formatters,
        'handlers': handlers,
        'loggers': {
            # Root orchestrator logger
            'orchestrator': {
                'level': log_level,
                'handlers': ['console', 'file', 'error_file'] if enable_file else ['console'],
                'propagate': False
            },
            # Agent loggers
            'agents': {
                'level': log_level,
                'handlers': ['console', 'agent_file', 'error_file'] if enable_file else ['console'],
                'propagate': False
            },
            'agent_a': {
                'level': log_level,
                'handlers': ['agent_file', 'error_file'] if enable_file else ['console'],
                'propagate': False
            },
            'agent_b': {
                'level': log_level,
                'handlers': ['agent_file', 'error_file'] if enable_file else ['console'],
                'propagate': False
            },
            # Communication logger
            'communication': {
                'level': log_level,
                'handlers': ['communication_file', 'error_file'] if enable_file else ['console'],
                'propagate': False
            },
            # Workflow logger
            'workflow': {
                'level': log_level,
                'handlers': ['workflow_file', 'error_file'] if enable_file else ['console'],
                'propagate': False
            },
            # FastAPI logger
            'uvicorn': {
                'level': log_level,
                'handlers': ['console', 'file'] if enable_file else ['console'],
                'propagate': False
            },
            'uvicorn.access': {
                'level': log_level,
                'handlers': ['console', 'file'] if enable_file else ['console'],
                'propagate': False
            }
        },
        'root': {
            'level': log_level,
            'handlers': ['console', 'file', 'error_file'] if enable_file else ['console']
        }
    }
    
    # Apply configuration
    logging.config.dictConfig(logger_config)
    
    # Create logger instances
    loggers = {
        'orchestrator': logging.getLogger('orchestrator'),
        'agents': logging.getLogger('agents'),
        'agent_a': logging.getLogger('agent_a'),
        'agent_b': logging.getLogger('agent_b'),
        'communication': logging.getLogger('communication'),
        'workflow': logging.getLogger('workflow'),
        'root': logging.getLogger()
    }
    
    # Add session context if provided
    if session_id:
        for name, logger in loggers.items():
            loggers[name] = OrchestrationLoggerAdapter(logger, {'session_id': session_id})
    
    return loggers

def get_session_logger(session_id: str, component: str = 'orchestrator') -> logging.Logger:
    """Get a logger for a specific orchestration session and component"""
    logger = logging.getLogger(f"{component}.{session_id}")
    return OrchestrationLoggerAdapter(logger, {'session_id': session_id})

def log_orchestration_event(
    logger: logging.Logger,
    event_type: str,
    message: str,
    level: str = 'INFO',
    **kwargs
):
    """Log a structured orchestration event"""
    log_level = getattr(logging, level.upper())
    
    extra = {
        'event_type': event_type,
        'event_id': str(uuid.uuid4()),
        **kwargs
    }
    
    logger.log(log_level, message, extra=extra)

def log_agent_action(
    logger: logging.Logger,
    agent_id: str,
    action: str,
    message: str,
    level: str = 'INFO',
    **kwargs
):
    """Log an agent action with context"""
    log_level = getattr(logging, level.upper())
    
    extra = {
        'agent_id': agent_id,
        'action': action,
        'action_id': str(uuid.uuid4()),
        **kwargs
    }
    
    logger.log(log_level, message, extra=extra)

def log_message_event(
    logger: logging.Logger,
    message_id: str,
    sender: str,
    recipient: str,
    message_type: str,
    content_length: int,
    level: str = 'INFO',
    **kwargs
):
    """Log a message communication event"""
    log_level = getattr(logging, level.upper())
    
    extra = {
        'message_id': message_id,
        'sender': sender,
        'recipient': recipient,
        'message_type': message_type,
        'content_length': content_length,
        **kwargs
    }
    
    logger.log(log_level, f"Message {message_type} from {sender} to {recipient}", extra=extra)

def log_workflow_transition(
    logger: logging.Logger,
    workflow_id: str,
    from_phase: str,
    to_phase: str,
    message: str = None,
    level: str = 'INFO',
    **kwargs
):
    """Log a workflow phase transition"""
    log_level = getattr(logging, level.upper())
    
    extra = {
        'workflow_id': workflow_id,
        'from_phase': from_phase,
        'to_phase': to_phase,
        'transition_id': str(uuid.uuid4()),
        **kwargs
    }
    
    log_message = message or f"Workflow transition: {from_phase} → {to_phase}"
    logger.log(log_level, log_message, extra=extra)

# Performance logging utilities
class PerformanceTimer:
    """Context manager for timing operations"""
    
    def __init__(self, logger: logging.Logger, operation: str, **context):
        self.logger = logger
        self.operation = operation
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now(timezone.utc)
        log_orchestration_event(
            self.logger,
            'performance_start',
            f"Starting {self.operation}",
            level='DEBUG',
            operation=self.operation,
            **self.context
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = datetime.now(timezone.utc)
        duration = (end_time - self.start_time).total_seconds()
        
        level = 'ERROR' if exc_type else 'DEBUG'
        message = f"Completed {self.operation} in {duration:.3f}s"
        
        if exc_type:
            message += f" with error: {exc_val}"
        
        log_orchestration_event(
            self.logger,
            'performance_end',
            message,
            level=level,
            operation=self.operation,
            duration_seconds=duration,
            success=exc_type is None,
            **self.context
        )

def configure_orchestration_logging(session_id: Optional[str] = None) -> Dict[str, logging.Logger]:
    """Configure logging for a new orchestration session"""
    return setup_logging(
        log_dir="logs",
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        session_id=session_id,
        enable_console=True,
        enable_file=True,
        enable_json=True
    )