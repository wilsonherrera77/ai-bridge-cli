#!/usr/bin/env python3
"""
Real CLI Bridge - Bridge for actual CLI communication
Enables REAL communication between CLI tools like Claude CLI, GPT CLI, etc.
WITHOUT API keys - uses existing CLI memberships.
"""

import asyncio
import subprocess
import logging
import json
import os
import sys
import signal
import threading
import queue
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

class CLIType(Enum):
    """Real CLI types available on system"""
    CLAUDE_CLI = "claude"  # claude-cli if installed
    OPENAI_CLI = "openai"  # openai CLI
    PYTHON_REPL = "python"  # Python REPL as agent
    NODE_REPL = "node"     # Node.js REPL as agent
    BASH_SHELL = "bash"    # Bash shell as agent
    POWERSHELL = "powershell"  # PowerShell as agent

@dataclass
class CLIConfig:
    """Configuration for real CLI process"""
    command: List[str]
    working_dir: str
    env_vars: Dict[str, str]
    startup_commands: List[str]
    prompt_pattern: str
    timeout: int = 30

class RealCLIProcess:
    """Manages a real CLI subprocess with bidirectional communication"""

    def __init__(self, cli_type: CLIType, config: CLIConfig):
        self.cli_type = cli_type
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        self.error_queue = queue.Queue()
        self.is_running = False
        self.last_response = ""

    async def start(self) -> bool:
        """Start the CLI process"""
        try:
            # Prepare environment
            env = os.environ.copy()
            env.update(self.config.env_vars)

            # Start process
            self.process = subprocess.Popen(
                self.config.command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.config.working_dir,
                env=env,
                bufsize=0,  # Unbuffered for real-time communication
                universal_newlines=True
            )

            self.is_running = True

            # Start communication threads
            threading.Thread(target=self._read_output, daemon=True).start()
            threading.Thread(target=self._read_errors, daemon=True).start()

            # Send startup commands
            for cmd in self.config.startup_commands:
                await self._send_command(cmd)
                await asyncio.sleep(0.5)

            logger.info(f"Started {self.cli_type.value} CLI process: PID {self.process.pid}")
            return True

        except Exception as e:
            logger.error(f"Failed to start {self.cli_type.value}: {e}")
            self.is_running = False
            return False

    def _read_output(self):
        """Read stdout in separate thread"""
        while self.is_running and self.process:
            try:
                line = self.process.stdout.readline()
                if line:
                    self.output_queue.put(line.strip())
                elif self.process.poll() is not None:
                    break
            except Exception as e:
                logger.error(f"Error reading output: {e}")
                break

    def _read_errors(self):
        """Read stderr in separate thread"""
        while self.is_running and self.process:
            try:
                line = self.process.stderr.readline()
                if line:
                    self.error_queue.put(line.strip())
                elif self.process.poll() is not None:
                    break
            except Exception as e:
                logger.error(f"Error reading stderr: {e}")
                break

    async def _send_command(self, command: str):
        """Send command to CLI process"""
        if self.process and self.process.stdin:
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()

    async def send_message(self, message: str) -> str:
        """Send message and wait for response"""
        if not self.is_running:
            return "ERROR: CLI process not running"

        # Clear previous output
        while not self.output_queue.empty():
            self.output_queue.get_nowait()

        # Send message
        await self._send_command(message)

        # Wait for response
        response_lines = []
        start_time = time.time()

        while time.time() - start_time < self.config.timeout:
            try:
                # Get output with timeout
                line = self.output_queue.get(timeout=1.0)
                response_lines.append(line)

                # Check if we have a complete response
                if self._is_response_complete(response_lines):
                    break

            except queue.Empty:
                # Check if there are any error messages
                if not self.error_queue.empty():
                    error = self.error_queue.get_nowait()
                    response_lines.append(f"ERROR: {error}")
                continue

        response = "\n".join(response_lines)
        self.last_response = response
        return response

    def _is_response_complete(self, lines: List[str]) -> bool:
        """Check if response is complete based on CLI type"""
        if not lines:
            return False

        last_line = lines[-1].lower()

        # Different completion patterns for different CLIs
        if self.cli_type == CLIType.PYTHON_REPL:
            return last_line.startswith(">>> ") or last_line.startswith("... ")
        elif self.cli_type == CLIType.NODE_REPL:
            return last_line.startswith("> ") or "undefined" in last_line
        elif self.cli_type in [CLIType.BASH_SHELL, CLIType.POWERSHELL]:
            return "$" in last_line or ">" in last_line
        else:
            # For other CLIs, wait for a pause in output
            return len(lines) > 2 and not any("loading" in line.lower() for line in lines[-3:])

    def get_status(self) -> Dict[str, Any]:
        """Get process status"""
        return {
            "cli_type": self.cli_type.value,
            "is_running": self.is_running,
            "pid": self.process.pid if self.process else None,
            "last_response_preview": self.last_response[:100] + "..." if len(self.last_response) > 100 else self.last_response
        }

    async def stop(self):
        """Stop the CLI process"""
        self.is_running = False
        if self.process:
            self.process.terminate()
            await asyncio.sleep(1)
            if self.process.poll() is None:
                self.process.kill()
        logger.info(f"Stopped {self.cli_type.value} CLI process")

class RealCLIBridge:
    """
    Bridge that enables real communication between CLI processes.
    Each agent runs in its own terminal/CLI and they communicate through this bridge.
    """

    def __init__(self):
        self.agents: Dict[str, RealCLIProcess] = {}
        self.conversation_log = []
        self.is_active = False

        # Initialize CLI configurations
        self.cli_configs = self._initialize_cli_configs()

        logger.info("RealCLIBridge initialized - Ready for real CLI communication")

    def _initialize_cli_configs(self) -> Dict[CLIType, CLIConfig]:
        """Initialize configurations for different CLI types"""

        configs = {}

        # Python REPL configuration (always available)
        configs[CLIType.PYTHON_REPL] = CLIConfig(
            command=[sys.executable, "-i"],
            working_dir=os.getcwd(),
            env_vars={"PYTHONUNBUFFERED": "1"},
            startup_commands=[
                "import os, json, requests, time",
                "print('Python Agent Ready')"
            ],
            prompt_pattern=">>> ",
            timeout=30
        )

        # Node.js REPL configuration (if available)
        configs[CLIType.NODE_REPL] = CLIConfig(
            command=["node", "--interactive"],
            working_dir=os.getcwd(),
            env_vars={"NODE_NO_WARNINGS": "1"},
            startup_commands=[
                "console.log('Node.js Agent Ready')"
            ],
            prompt_pattern="> ",
            timeout=30
        )

        # PowerShell configuration (Windows)
        if os.name == 'nt':
            configs[CLIType.POWERSHELL] = CLIConfig(
                command=["powershell", "-NoProfile", "-Interactive"],
                working_dir=os.getcwd(),
                env_vars={},
                startup_commands=[
                    "Write-Host 'PowerShell Agent Ready'"
                ],
                prompt_pattern="PS ",
                timeout=30
            )

        # Bash shell configuration (Unix-like)
        else:
            configs[CLIType.BASH_SHELL] = CLIConfig(
                command=["/bin/bash", "--norc", "-i"],
                working_dir=os.getcwd(),
                env_vars={"PS1": "bash-agent$ "},
                startup_commands=[
                    "echo 'Bash Agent Ready'"
                ],
                prompt_pattern="$ ",
                timeout=30
            )

        # Try to detect Claude CLI
        if self._check_cli_available("claude"):
            configs[CLIType.CLAUDE_CLI] = CLIConfig(
                command=["claude", "chat"],
                working_dir=os.getcwd(),
                env_vars={},
                startup_commands=[],
                prompt_pattern="Human: ",
                timeout=60
            )

        # Try to detect OpenAI CLI
        if self._check_cli_available("openai"):
            configs[CLIType.OPENAI_CLI] = CLIConfig(
                command=["openai", "api", "chat.completions.create"],
                working_dir=os.getcwd(),
                env_vars={},
                startup_commands=[],
                prompt_pattern="",
                timeout=60
            )

        return configs

    def _check_cli_available(self, command: str) -> bool:
        """Check if a CLI tool is available on the system"""
        try:
            result = subprocess.run([command, "--help"],
                                  capture_output=True,
                                  timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False

    async def start_agent(self, agent_id: str, cli_type: CLIType) -> bool:
        """Start a real CLI agent"""

        if cli_type not in self.cli_configs:
            logger.error(f"CLI type {cli_type.value} not available")
            return False

        if agent_id in self.agents:
            logger.warning(f"Agent {agent_id} already exists")
            return True

        # Create and start CLI process
        config = self.cli_configs[cli_type]
        cli_process = RealCLIProcess(cli_type, config)

        success = await cli_process.start()
        if success:
            self.agents[agent_id] = cli_process
            logger.info(f"Started agent {agent_id} with {cli_type.value}")
            return True
        else:
            logger.error(f"Failed to start agent {agent_id}")
            return False

    async def send_message_to_agent(self, agent_id: str, message: str) -> str:
        """Send message to specific agent and get response"""

        if agent_id not in self.agents:
            return f"ERROR: Agent {agent_id} not found"

        agent = self.agents[agent_id]

        # Log the interaction
        self.conversation_log.append({
            "timestamp": time.time(),
            "agent_id": agent_id,
            "message": message,
            "type": "input"
        })

        # Send message and get response
        response = await agent.send_message(message)

        # Log the response
        self.conversation_log.append({
            "timestamp": time.time(),
            "agent_id": agent_id,
            "message": response,
            "type": "output"
        })

        logger.info(f"Agent {agent_id} responded: {response[:100]}...")
        return response

    async def facilitate_conversation(self, agent_a_id: str, agent_b_id: str, objective: str, autonomy_level: str = "max") -> Dict[str, Any]:
        """Facilitate real conversation between two agents with unlimited autonomy"""

        if agent_a_id not in self.agents or agent_b_id not in self.agents:
            return {"error": "One or both agents not found"}

        self.is_active = True
        conversation_history = []
        round_num = 0

        try:
            # Initial setup - give each agent expert-level context
            expert_setup = f"""EXPERT MISSION BRIEFING:

OBJECTIVE: {objective}

You are a WORLD-CLASS EXPERT in your specialization. Act with the knowledge, experience, and authority of the top 1% professionals in your field.

AUTONOMY LEVEL: MAXIMUM
- Pursue this objective with professional excellence
- Continue until COMPLETELY accomplished
- No artificial limits or constraints
- Make executive decisions as needed
- Collaborate intelligently with your expert colleague

Expected behavior: World-class professional standards, thorough execution, complete objective achievement.

Provide your expert analysis and approach. What do you need from the other expert to achieve total success?"""

            response_a = await self.send_message_to_agent(agent_a_id, expert_setup)
            response_b = await self.send_message_to_agent(agent_b_id, expert_setup)

            conversation_history.extend([
                {"agent": agent_a_id, "message": expert_setup, "response": response_a, "round": 0},
                {"agent": agent_b_id, "message": expert_setup, "response": response_b, "round": 0}
            ])

            # Unlimited autonomous collaboration until objective completion
            current_agent = agent_a_id
            other_agent = agent_b_id
            consecutive_completion_signals = 0
            no_progress_counter = 0
            last_significant_progress = ""

            while True:  # UNLIMITED ROUNDS - continue until objective is achieved
                round_num += 1
                
                # Prepare expert-level context message
                if len(conversation_history) >= 2:
                    last_other_response = conversation_history[-2]["response"] if current_agent == agent_a_id else conversation_history[-1]["response"]
                    expert_context = f"""EXPERT COLLABORATION - Round {round_num}

Your expert colleague's latest contribution:
"{last_other_response}"

OBJECTIVE STATUS: {objective}

As a world-class expert, analyze their contribution and provide your professional response:
1. What has been accomplished so far?
2. What specific next steps are needed?
3. What do you need from your colleague?
4. How close are we to COMPLETE objective achievement?

Continue with expert-level execution until the objective is COMPLETELY fulfilled."""
                else:
                    expert_context = f"EXPERT CONTINUATION - Round {round_num}\n\nObjective: {objective}\n\nAs a world-class expert, continue your professional work toward complete objective achievement."

                # Get expert response from current agent
                response = await self.send_message_to_agent(current_agent, expert_context)

                conversation_history.append({
                    "agent": current_agent,
                    "message": expert_context,
                    "response": response,
                    "round": round_num
                })

                # Intelligent completion detection
                completion_indicators = [
                    "objective completed", "fully accomplished", "task finished", 
                    "implementation complete", "project completed", "goal achieved",
                    "successfully delivered", "fully functional", "ready for production",
                    "completely implemented", "objective fulfilled", "mission accomplished"
                ]
                
                response_lower = response.lower()
                
                # Check for genuine completion signals
                if any(indicator in response_lower for indicator in completion_indicators):
                    consecutive_completion_signals += 1
                    if consecutive_completion_signals >= 2:  # Both agents must confirm completion
                        logger.info(f"Objective achieved after {round_num} rounds of expert collaboration")
                        break
                else:
                    consecutive_completion_signals = 0

                # Progress tracking
                if response != last_significant_progress:
                    last_significant_progress = response
                    no_progress_counter = 0
                else:
                    no_progress_counter += 1
                    
                # Safety valve: If no progress for many rounds, but still allow continuation
                if no_progress_counter > 50:  # Much higher threshold
                    logger.warning(f"No progress detected for {no_progress_counter} rounds, but continuing...")
                    no_progress_counter = 0  # Reset and continue

                # Switch agents for continued collaboration
                current_agent, other_agent = other_agent, current_agent

                # Brief pause for processing
                await asyncio.sleep(1)

            return {
                "success": True,
                "conversation_history": conversation_history,
                "total_rounds": round_num,
                "agents": [agent_a_id, agent_b_id],
                "autonomy_level": autonomy_level,
                "completion_reason": "objective_achieved" if consecutive_completion_signals >= 2 else "manual_stop"
            }

        except Exception as e:
            logger.error(f"Error in conversation facilitation: {e}")
            return {"error": str(e)}

        finally:
            self.is_active = False

    def get_available_cli_types(self) -> List[str]:
        """Get list of available CLI types on this system"""
        return [cli_type.value for cli_type in self.cli_configs.keys()]

    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get status of specific agent"""
        if agent_id not in self.agents:
            return {"error": "Agent not found"}

        return self.agents[agent_id].get_status()

    def get_all_agents_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            agent_id: agent.get_status()
            for agent_id, agent in self.agents.items()
        }

    def get_conversation_log(self) -> List[Dict[str, Any]]:
        """Get complete conversation log"""
        return self.conversation_log

    async def stop_agent(self, agent_id: str):
        """Stop specific agent"""
        if agent_id in self.agents:
            await self.agents[agent_id].stop()
            del self.agents[agent_id]
            logger.info(f"Stopped agent {agent_id}")

    async def stop_all_agents(self):
        """Stop all agents"""
        for agent_id in list(self.agents.keys()):
            await self.stop_agent(agent_id)
        logger.info("Stopped all agents")

# Global instance
real_cli_bridge = RealCLIBridge()