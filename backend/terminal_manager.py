#!/usr/bin/env python3
"""
TerminalManager - Core CLI Process Management System
Manages real CLI processes for Claude and Codex without API keys.

Arquitectura CLI Real:
- Spawn real terminal processes (claude-cli, codex-cli, etc.)
- Communicate via stdin/stdout with existing paid memberships
- Zero API token consumption
- Real terminal orchestration
"""

import asyncio
import subprocess
import threading
import uuid
import logging
import json
import os
import signal
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class TerminalType(Enum):
    """Supported CLI terminal types"""
    CLAUDE_CLI = "claude_cli"
    CODEX_CLI = "codex_cli"  
    GPT_CLI = "gpt_cli"
    OPENAI_CLI = "openai_cli"
    CUSTOM_CLI = "custom_cli"

class ProcessStatus(Enum):
    """CLI process status"""
    STARTING = "starting"
    READY = "ready"
    ACTIVE = "active"
    WAITING = "waiting"
    ERROR = "error"
    STOPPED = "stopped"
    CRASHED = "crashed"

@dataclass
class TerminalConfig:
    """Configuration for CLI terminal process"""
    terminal_type: TerminalType
    command: List[str]  # CLI command to execute
    working_dir: Optional[str] = None
    env_vars: Dict[str, str] = None
    timeout: int = 300  # Process timeout in seconds
    retry_attempts: int = 3
    auto_restart: bool = True
    
    def __post_init__(self):
        if self.env_vars is None:
            self.env_vars = {}

@dataclass
class CLIProcess:
    """Represents a managed CLI process"""
    id: str
    config: TerminalConfig
    process: Optional[subprocess.Popen] = None
    status: ProcessStatus = ProcessStatus.STARTING
    created_at: datetime = None
    last_activity: datetime = None
    message_count: int = 0
    error_count: int = 0
    restart_count: int = 0
    output_buffer: List[str] = None
    error_buffer: List[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.output_buffer is None:
            self.output_buffer = []
        if self.error_buffer is None:
            self.error_buffer = []

class TerminalManager:
    """
    Central manager for real CLI terminal processes.
    
    Features:
    - Launch and manage Claude CLI and Codex CLI processes
    - Communicate via stdin/stdout (NO API keys)
    - Process health monitoring and auto-restart
    - Message queuing and response handling
    - Real-time terminal activity monitoring
    """
    
    def __init__(self):
        self.processes: Dict[str, CLIProcess] = {}
        self.message_queues: Dict[str, asyncio.Queue] = {}
        self.response_queues: Dict[str, asyncio.Queue] = {}
        self.running = False
        
        # Process monitoring
        self.monitor_task: Optional[asyncio.Task] = None
        self.communication_tasks: Dict[str, asyncio.Task] = {}
        
        # Default CLI configurations
        self.default_configs = {
            TerminalType.CLAUDE_CLI: TerminalConfig(
                terminal_type=TerminalType.CLAUDE_CLI,
                command=["claude", "chat"],  # Assuming claude-cli is installed
                env_vars={"CLAUDE_CLI_NO_API": "true"}  # Force CLI mode
            ),
            TerminalType.CODEX_CLI: TerminalConfig(
                terminal_type=TerminalType.CODEX_CLI,
                command=["codex", "chat"],  # Assuming codex-cli is installed
                env_vars={"CODEX_CLI_NO_API": "true"}  # Force CLI mode
            ),
            TerminalType.GPT_CLI: TerminalConfig(
                terminal_type=TerminalType.GPT_CLI, 
                command=["gpt", "chat"],  # Generic GPT CLI
                env_vars={"GPT_CLI_NO_API": "true"}
            )
        }
        
        logger.info("TerminalManager initialized - ZERO API key usage")
    
    async def start_terminal(self, terminal_type: TerminalType, custom_config: Optional[TerminalConfig] = None) -> str:
        """
        Start a CLI terminal process.
        
        Args:
            terminal_type: Type of CLI terminal to start
            custom_config: Optional custom configuration
            
        Returns:
            Process ID for tracking
        """
        try:
            # Generate process ID
            process_id = f"{terminal_type.value}_{uuid.uuid4().hex[:8]}"
            
            # Get configuration
            config = custom_config or self.default_configs.get(terminal_type)
            if not config:
                raise ValueError(f"No configuration available for {terminal_type}")
            
            logger.info(f"Starting CLI terminal: {process_id} - Command: {' '.join(config.command)}")
            
            # Setup environment
            env = os.environ.copy()
            env.update(config.env_vars)
            
            # Start process
            process = subprocess.Popen(
                config.command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered
                cwd=config.working_dir,
                env=env
            )
            
            # Create CLI process record
            cli_process = CLIProcess(
                id=process_id,
                config=config,
                process=process,
                status=ProcessStatus.STARTING
            )
            
            # Register process
            self.processes[process_id] = cli_process
            self.message_queues[process_id] = asyncio.Queue()
            self.response_queues[process_id] = asyncio.Queue()
            
            # Start communication handler
            self.communication_tasks[process_id] = asyncio.create_task(
                self._handle_process_communication(process_id)
            )
            
            # Wait for process to be ready
            await asyncio.sleep(2)  # Give process time to start
            cli_process.status = ProcessStatus.READY
            
            logger.info(f"CLI terminal started successfully: {process_id}")
            return process_id
            
        except Exception as e:
            logger.error(f"Failed to start CLI terminal {terminal_type}: {e}")
            raise
    
    async def send_message(self, process_id: str, message: str) -> str:
        """
        Send message to CLI process and wait for response.
        
        Args:
            process_id: Target process ID
            message: Message to send
            
        Returns:
            Response from CLI process
        """
        if process_id not in self.processes:
            raise ValueError(f"Process {process_id} not found")
        
        cli_process = self.processes[process_id]
        
        try:
            # Update activity timestamp
            cli_process.last_activity = datetime.now(timezone.utc)
            cli_process.message_count += 1
            cli_process.status = ProcessStatus.ACTIVE
            
            logger.info(f"Sending message to {process_id}: {message[:100]}...")
            
            # Send message to process stdin
            await self.message_queues[process_id].put(message)
            
            # Wait for response
            response = await asyncio.wait_for(
                self.response_queues[process_id].get(),
                timeout=cli_process.config.timeout
            )
            
            cli_process.status = ProcessStatus.READY
            logger.info(f"Received response from {process_id}: {response[:100]}...")
            
            return response
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout waiting for response from {process_id}")
            cli_process.error_count += 1
            cli_process.status = ProcessStatus.ERROR
            raise
        except Exception as e:
            logger.error(f"Error sending message to {process_id}: {e}")
            cli_process.error_count += 1
            cli_process.status = ProcessStatus.ERROR
            raise
    
    async def _handle_process_communication(self, process_id: str):
        """Handle stdin/stdout communication with CLI process"""
        cli_process = self.processes[process_id]
        process = cli_process.process
        
        try:
            # Create reader and writer tasks
            reader_task = asyncio.create_task(self._read_process_output(process_id))
            writer_task = asyncio.create_task(self._write_process_input(process_id))
            
            # Wait for either task to complete
            done, pending = await asyncio.wait(
                [reader_task, writer_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel pending tasks
            for task in pending:
                task.cancel()
                
        except Exception as e:
            logger.error(f"Communication error for {process_id}: {e}")
            cli_process.status = ProcessStatus.ERROR
    
    async def _read_process_output(self, process_id: str):
        """Read output from CLI process"""
        cli_process = self.processes[process_id]
        process = cli_process.process
        
        try:
            while True:
                # Read line from stdout
                line = await asyncio.get_event_loop().run_in_executor(
                    None, process.stdout.readline
                )
                
                if not line:  # Process ended
                    break
                
                line = line.strip()
                if line:
                    cli_process.output_buffer.append(line)
                    
                    # Put complete response in queue
                    await self.response_queues[process_id].put(line)
                    
        except Exception as e:
            logger.error(f"Error reading from {process_id}: {e}")
            cli_process.status = ProcessStatus.ERROR
    
    async def _write_process_input(self, process_id: str):
        """Write input to CLI process"""
        cli_process = self.processes[process_id]
        process = cli_process.process
        
        try:
            while True:
                # Wait for message to send
                message = await self.message_queues[process_id].get()
                
                # Write to process stdin
                process.stdin.write(message + "\n")
                process.stdin.flush()
                
        except Exception as e:
            logger.error(f"Error writing to {process_id}: {e}")
            cli_process.status = ProcessStatus.ERROR
    
    def get_process_status(self, process_id: str) -> Dict[str, Any]:
        """Get detailed status of CLI process"""
        if process_id not in self.processes:
            return {"error": "Process not found"}
        
        cli_process = self.processes[process_id]
        
        return {
            "id": cli_process.id,
            "type": cli_process.config.terminal_type.value,
            "status": cli_process.status.value,
            "created_at": cli_process.created_at.isoformat(),
            "last_activity": cli_process.last_activity.isoformat() if cli_process.last_activity else None,
            "message_count": cli_process.message_count,
            "error_count": cli_process.error_count,
            "restart_count": cli_process.restart_count,
            "command": " ".join(cli_process.config.command),
            "pid": cli_process.process.pid if cli_process.process else None,
            "is_running": cli_process.process.poll() is None if cli_process.process else False
        }
    
    def list_processes(self) -> List[Dict[str, Any]]:
        """List all managed CLI processes"""
        return [self.get_process_status(pid) for pid in self.processes.keys()]
    
    async def stop_terminal(self, process_id: str):
        """Stop a CLI terminal process"""
        if process_id not in self.processes:
            return
        
        cli_process = self.processes[process_id]
        
        try:
            # Cancel communication task
            if process_id in self.communication_tasks:
                self.communication_tasks[process_id].cancel()
                del self.communication_tasks[process_id]
            
            # Terminate process
            if cli_process.process:
                cli_process.process.terminate()
                
                # Wait for graceful shutdown
                try:
                    cli_process.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if needed
                    cli_process.process.kill()
            
            cli_process.status = ProcessStatus.STOPPED
            logger.info(f"CLI terminal stopped: {process_id}")
            
        except Exception as e:
            logger.error(f"Error stopping terminal {process_id}: {e}")
    
    async def shutdown(self):
        """Shutdown all CLI terminal processes"""
        logger.info("Shutting down all CLI terminals...")
        
        # Stop all processes
        for process_id in list(self.processes.keys()):
            await self.stop_terminal(process_id)
        
        self.running = False
        
        # Cancel monitor task
        if self.monitor_task:
            self.monitor_task.cancel()
        
        logger.info("TerminalManager shutdown complete - Zero API usage maintained")