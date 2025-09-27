# AI-Bridge CLI System

## Overview

AI-Bridge is an autonomous AI development system that orchestrates collaboration between specialized AI agents to complete software development tasks. The system eliminates API key dependencies by using local CLI tools (Claude CLI, OpenAI CLI) with existing paid memberships. It features a FastAPI backend for orchestration and a React frontend for real-time monitoring and control.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Architecture Pattern
The system follows a **CLI-first orchestration pattern** where real terminal processes communicate through a centralized message bus without consuming API tokens. The architecture consists of three main layers:

**Agent Layer**: Specialized AI agents (Frontend/Backend) that run as real CLI processes
**Orchestration Layer**: Central coordination engine that manages agent communication and workflow
**Interface Layer**: Web-based control cabin for monitoring and human interaction

### Backend Architecture (FastAPI)
- **Main Server** (`main.py`): FastAPI application providing REST endpoints and WebSocket connections
- **Agent System** (`agents.py`): AgentA (Frontend specialist) and AgentB (Backend specialist) classes
- **Orchestrator** (`orchestrator.py`): Core coordination engine managing agent lifecycle and task distribution
- **Communication Bus** (`communication.py`): Centralized messaging system for inter-agent communication
- **CLI Bridge** (`real_cli_bridge.py`): Interface layer for real CLI process communication
- **Terminal Management** (`terminal_manager.py`): Process lifecycle management for CLI tools
- **Workflow Engine** (`workflow.py`): Automated workflow cycles (Planning → Implementation → Review)

### Frontend Architecture (React + Vite)
- **Control Cabin Interface**: Real-time dashboard for monitoring agent activity
- **WebSocket Integration**: Live communication with backend orchestration system
- **Agent Monitoring**: Visual panels showing agent status, conversations, and progress
- **Configuration Management**: Runtime configuration of orchestration parameters

### Communication Architecture
The system uses a **hybrid communication model**:
- **MessageBus**: Structured message routing between agents with type safety and validation
- **CLI Process Communication**: Direct stdin/stdout communication with real terminal processes
- **WebSocket Streaming**: Real-time frontend updates and human interaction
- **File-based Persistence**: Session state, conversation history, and workflow tracking

### Data Storage Strategy
- **Session-based Storage**: Each orchestration session creates isolated workspace and state files
- **Conversation Logging**: Complete message history with evidence capture for audit trails
- **Workflow Persistence**: State machines persisted to JSON for recovery and analysis
- **Configuration Management**: Runtime configuration through JSON files with hot-reload capability

### Process Management
- **Terminal Orchestration**: Real CLI processes managed through subprocess with proper lifecycle handling
- **Health Monitoring**: Process health checks, crash detection, and automatic restart capabilities
- **Resource Management**: Memory and CPU monitoring for CLI processes using psutil
- **Error Recovery**: Graceful error handling with fallback strategies and process isolation

### Security and Isolation
- **No API Key Storage**: System operates entirely through local CLI tools with user's existing memberships
- **Process Isolation**: Each agent runs in isolated subprocess with controlled communication channels
- **Workspace Sandboxing**: File operations contained within session-specific workspaces
- **Configuration Validation**: Input validation and sanitization for all user-provided configuration

## External Dependencies

### Core Runtime Dependencies
- **FastAPI**: Web framework for orchestration API and WebSocket communication
- **Uvicorn**: ASGI server for FastAPI application
- **Pydantic**: Data validation and serialization for API models
- **WebSockets**: Real-time communication library for frontend connectivity
- **psutil**: System process monitoring and resource management

### Frontend Dependencies
- **React 19**: Frontend framework with modern hooks and concurrent features
- **Vite**: Build tool and development server with hot module replacement
- **Tailwind CSS**: Utility-first CSS framework for responsive UI design
- **Lucide React**: Icon library for consistent UI elements
- **Socket.IO Client**: WebSocket client for real-time backend communication

### CLI Tool Dependencies
- **Claude CLI**: Anthropic's command-line interface (requires paid membership)
- **OpenAI CLI**: OpenAI's command-line interface (requires paid membership)
- **Python 3.8+**: Runtime environment for backend orchestration system
- **Node.js 16+**: Runtime environment for frontend development and build processes

### Development and Build Tools
- **ESLint**: Code linting for JavaScript/React codebase
- **PostCSS**: CSS processing pipeline with Tailwind integration
- **Autoprefixer**: CSS vendor prefix automation
- **Python subprocess**: Built-in library for CLI process management

### System Requirements
- **Operating System**: Cross-platform support (Windows/macOS/Linux)
- **Terminal Emulator**: Required for CLI tool interaction
- **File System**: Read/write access for workspace and session management
- **Network**: Local network access for WebSocket communication between frontend and backend