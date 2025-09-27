#!/usr/bin/env python3
"""
ProcessCommunicator - Advanced stdin/stdout Communication Handler
Handles sophisticated message passing with real CLI processes.

Características:
- Protocolo de comunicación robusto via stdin/stdout
- Manejo de timeouts y reintentos
- Formateo de mensajes para diferentes CLI tools
- Buffer management y streaming de respuestas
- Zero dependencies on API keys
"""

import asyncio
import json
import logging
import re
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum
import queue

logger = logging.getLogger(__name__)

class MessageFormat(Enum):
    """Message formats for different CLI tools"""
    PLAIN_TEXT = "plain_text"
    JSON = "json"
    MARKDOWN = "markdown"
    CHAT_PROMPT = "chat_prompt"
    CODE_CONTEXT = "code_context"

class ResponsePattern(Enum):
    """Response detection patterns"""
    END_MARKER = "end_marker"         # Look for specific end marker
    TIMEOUT = "timeout"               # Wait for timeout
    SILENT_PERIOD = "silent_period"   # Wait for period of no output
    PROMPT_RETURN = "prompt_return"   # Wait for CLI prompt to return

@dataclass 
class MessageProtocol:
    """Protocol configuration for CLI communication"""
    input_format: MessageFormat
    output_format: MessageFormat  
    response_pattern: ResponsePattern
    end_marker: Optional[str] = None
    timeout_seconds: int = 30
    silent_period_seconds: float = 2.0
    prompt_regex: Optional[str] = None
    max_buffer_size: int = 1024 * 1024  # 1MB buffer
    
class ProcessCommunicator:
    """
    Advanced communication handler for CLI processes.
    
    Features:
    - Protocol-aware message formatting
    - Smart response detection and parsing
    - Buffer management for large outputs
    - Streaming response handling
    - Timeout and retry mechanisms
    - CLI-specific optimizations
    """
    
    def __init__(self):
        self.protocols: Dict[str, MessageProtocol] = {}
        self.active_communications: Dict[str, Dict[str, Any]] = {}
        
        # Default protocols for common CLI tools
        self._initialize_default_protocols()
        
        logger.info("ProcessCommunicator initialized - Ready for CLI communication")
    
    def _initialize_default_protocols(self):
        """Initialize default communication protocols"""
        
        # Claude CLI Protocol
        self.protocols["claude_cli"] = MessageProtocol(
            input_format=MessageFormat.CHAT_PROMPT,
            output_format=MessageFormat.MARKDOWN,
            response_pattern=ResponsePattern.SILENT_PERIOD,
            silent_period_seconds=3.0,
            timeout_seconds=60,
            prompt_regex=r"(?:Claude|>|$)\s*$"
        )
        
        # Codex/GPT CLI Protocol
        self.protocols["codex_cli"] = MessageProtocol(
            input_format=MessageFormat.CODE_CONTEXT,
            output_format=MessageFormat.PLAIN_TEXT,
            response_pattern=ResponsePattern.SILENT_PERIOD,
            silent_period_seconds=2.0,
            timeout_seconds=90,
            prompt_regex=r"(?:>>>|>|$)\s*$"
        )
        
        # Generic GPT CLI Protocol
        self.protocols["gpt_cli"] = MessageProtocol(
            input_format=MessageFormat.CHAT_PROMPT,
            output_format=MessageFormat.PLAIN_TEXT,
            response_pattern=ResponsePattern.PROMPT_RETURN,
            timeout_seconds=45,
            prompt_regex=r"(?:GPT|>|\$)\s*$"
        )
        
        # Custom CLI Protocol Template
        self.protocols["custom_cli"] = MessageProtocol(
            input_format=MessageFormat.PLAIN_TEXT,
            output_format=MessageFormat.PLAIN_TEXT,
            response_pattern=ResponsePattern.TIMEOUT,
            timeout_seconds=30
        )
    
    def register_protocol(self, cli_type: str, protocol: MessageProtocol):
        """Register a custom communication protocol"""
        self.protocols[cli_type] = protocol
        logger.info(f"Registered communication protocol for {cli_type}")
    
    def format_input_message(self, message: str, cli_type: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Format input message for specific CLI tool.
        
        Args:
            message: Raw message content
            cli_type: Type of CLI tool 
            context: Optional context information
            
        Returns:
            Formatted message ready for CLI input
        """
        if cli_type not in self.protocols:
            logger.warning(f"No protocol found for {cli_type}, using plain text")
            return message
        
        protocol = self.protocols[cli_type]
        context = context or {}
        
        if protocol.input_format == MessageFormat.CHAT_PROMPT:
            # Format as conversational prompt
            formatted = f"Human: {message}\n\nAssistant: "
            
        elif protocol.input_format == MessageFormat.CODE_CONTEXT:
            # Format with code context
            project_context = context.get("project_context", "")
            code_context = context.get("code_context", "")
            
            formatted = f"""
# Development Context
Project: {project_context}

# Code Context
{code_context}

# Task
{message}

Please provide implementation:
"""
            
        elif protocol.input_format == MessageFormat.JSON:
            # Format as JSON message
            formatted = json.dumps({
                "message": message,
                "context": context,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
        elif protocol.input_format == MessageFormat.MARKDOWN:
            # Format as markdown
            formatted = f"""
## Task Request

{message}

### Context
{json.dumps(context, indent=2) if context else "No additional context"}
"""
            
        else:
            # Plain text fallback
            formatted = message
        
        return formatted
    
    async def send_and_receive(self, 
                             process: asyncio.subprocess.Process,
                             message: str,
                             cli_type: str,
                             context: Optional[Dict[str, Any]] = None) -> str:
        """
        Send message to CLI process and receive response.
        
        Args:
            process: CLI subprocess
            message: Message to send
            cli_type: Type of CLI tool
            context: Optional context
            
        Returns:
            Complete response from CLI process
        """
        if cli_type not in self.protocols:
            raise ValueError(f"No protocol configured for CLI type: {cli_type}")
        
        protocol = self.protocols[cli_type]
        
        try:
            # Format input message
            formatted_message = self.format_input_message(message, cli_type, context)
            
            logger.info(f"Sending message to {cli_type}: {formatted_message[:100]}...")
            
            # Send message to process
            process.stdin.write(formatted_message.encode('utf-8') + b'\n')
            await process.stdin.drain()
            
            # Receive response based on protocol
            response = await self._receive_response(process, protocol)
            
            # Parse and format response
            parsed_response = self.parse_output_response(response, cli_type)
            
            logger.info(f"Received response from {cli_type}: {parsed_response[:100]}...")
            
            return parsed_response
            
        except Exception as e:
            logger.error(f"Communication error with {cli_type}: {e}")
            raise
    
    async def _receive_response(self, process: asyncio.subprocess.Process, protocol: MessageProtocol) -> str:
        """Receive response from CLI process based on protocol"""
        
        if protocol.response_pattern == ResponsePattern.TIMEOUT:
            return await self._receive_with_timeout(process, protocol.timeout_seconds)
            
        elif protocol.response_pattern == ResponsePattern.SILENT_PERIOD:
            return await self._receive_with_silent_period(process, protocol.silent_period_seconds, protocol.timeout_seconds)
            
        elif protocol.response_pattern == ResponsePattern.END_MARKER:
            return await self._receive_with_end_marker(process, protocol.end_marker, protocol.timeout_seconds)
            
        elif protocol.response_pattern == ResponsePattern.PROMPT_RETURN:
            return await self._receive_with_prompt_return(process, protocol.prompt_regex, protocol.timeout_seconds)
            
        else:
            # Default to timeout method
            return await self._receive_with_timeout(process, protocol.timeout_seconds)
    
    async def _receive_with_timeout(self, process: asyncio.subprocess.Process, timeout: int) -> str:
        """Receive response with simple timeout"""
        try:
            output_lines = []
            
            while True:
                line = await asyncio.wait_for(process.stdout.readline(), timeout=timeout)
                
                if not line:  # EOF
                    break
                    
                line_str = line.decode('utf-8').rstrip()
                output_lines.append(line_str)
                
        except asyncio.TimeoutError:
            # Timeout reached, return what we have
            pass
        
        return "\n".join(output_lines)
    
    async def _receive_with_silent_period(self, process: asyncio.subprocess.Process, silent_period: float, max_timeout: int) -> str:
        """Receive response until silent period detected"""
        output_lines = []
        last_output_time = datetime.now()
        start_time = datetime.now()
        
        try:
            while True:
                try:
                    # Try to read with short timeout
                    line = await asyncio.wait_for(process.stdout.readline(), timeout=0.1)
                    
                    if not line:  # EOF
                        break
                    
                    line_str = line.decode('utf-8').rstrip()
                    if line_str.strip():  # Only count non-empty lines
                        output_lines.append(line_str)
                        last_output_time = datetime.now()
                
                except asyncio.TimeoutError:
                    # Check if silent period has passed
                    silent_duration = (datetime.now() - last_output_time).total_seconds()
                    
                    if silent_duration >= silent_period:
                        # Silent period reached
                        break
                    
                    # Check max timeout
                    total_duration = (datetime.now() - start_time).total_seconds()
                    if total_duration >= max_timeout:
                        logger.warning(f"Max timeout reached: {max_timeout}s")
                        break
                    
                    continue
        
        except Exception as e:
            logger.error(f"Error during silent period reception: {e}")
        
        return "\n".join(output_lines)
    
    async def _receive_with_end_marker(self, process: asyncio.subprocess.Process, end_marker: str, timeout: int) -> str:
        """Receive response until end marker detected"""
        output_lines = []
        start_time = datetime.now()
        
        try:
            while True:
                line = await asyncio.wait_for(process.stdout.readline(), timeout=1.0)
                
                if not line:  # EOF
                    break
                
                line_str = line.decode('utf-8').rstrip()
                
                # Check for end marker
                if end_marker in line_str:
                    # Remove end marker from output if present
                    line_str = line_str.replace(end_marker, "").strip()
                    if line_str:
                        output_lines.append(line_str)
                    break
                
                output_lines.append(line_str)
                
                # Check timeout
                duration = (datetime.now() - start_time).total_seconds()
                if duration >= timeout:
                    logger.warning(f"Timeout waiting for end marker: {end_marker}")
                    break
        
        except asyncio.TimeoutError:
            logger.warning(f"Timeout waiting for end marker: {end_marker}")
        
        return "\n".join(output_lines)
    
    async def _receive_with_prompt_return(self, process: asyncio.subprocess.Process, prompt_regex: str, timeout: int) -> str:
        """Receive response until CLI prompt returns"""
        output_lines = []
        start_time = datetime.now()
        prompt_pattern = re.compile(prompt_regex) if prompt_regex else None
        
        try:
            while True:
                line = await asyncio.wait_for(process.stdout.readline(), timeout=1.0)
                
                if not line:  # EOF
                    break
                
                line_str = line.decode('utf-8').rstrip()
                
                # Check for prompt return
                if prompt_pattern and prompt_pattern.search(line_str):
                    # Don't include the prompt line in output
                    break
                
                output_lines.append(line_str)
                
                # Check timeout
                duration = (datetime.now() - start_time).total_seconds()
                if duration >= timeout:
                    logger.warning(f"Timeout waiting for prompt return")
                    break
        
        except asyncio.TimeoutError:
            logger.warning(f"Timeout waiting for prompt return")
        
        return "\n".join(output_lines)
    
    def parse_output_response(self, response: str, cli_type: str) -> str:
        """
        Parse and clean response from CLI tool.
        
        Args:
            response: Raw response from CLI
            cli_type: Type of CLI tool
            
        Returns:
            Cleaned and parsed response
        """
        if cli_type not in self.protocols:
            return response
        
        protocol = self.protocols[cli_type]
        
        if protocol.output_format == MessageFormat.MARKDOWN:
            # Clean markdown artifacts
            cleaned = self._clean_markdown_response(response)
            
        elif protocol.output_format == MessageFormat.JSON:
            # Parse JSON response
            try:
                parsed = json.loads(response)
                cleaned = parsed.get("response", response)
            except json.JSONDecodeError:
                cleaned = response
            
        elif protocol.output_format == MessageFormat.CODE_CONTEXT:
            # Extract code blocks and clean
            cleaned = self._extract_code_blocks(response)
            
        else:
            # Plain text cleanup
            cleaned = self._clean_plain_text_response(response)
        
        return cleaned
    
    def _clean_markdown_response(self, response: str) -> str:
        """Clean markdown-formatted response"""
        lines = response.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove certain markdown artifacts
            line = re.sub(r'^#+\s*', '', line)  # Remove header markers
            line = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)  # Remove bold markers
            line = re.sub(r'\*([^*]+)\*', r'\1', line)  # Remove italic markers
            
            # Keep the line if it has content
            if line.strip():
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _extract_code_blocks(self, response: str) -> str:
        """Extract code blocks from response"""
        # Look for code blocks in various formats
        code_block_patterns = [
            r'```[\w]*\n(.*?)\n```',  # Markdown code blocks
            r'<code>(.*?)</code>',     # HTML code blocks
            r'`([^`]+)`'               # Inline code
        ]
        
        extracted_code = []
        
        for pattern in code_block_patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            extracted_code.extend(matches)
        
        if extracted_code:
            return '\n\n'.join(extracted_code)
        else:
            return response  # Return original if no code blocks found
    
    def _clean_plain_text_response(self, response: str) -> str:
        """Clean plain text response"""
        lines = response.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and common CLI artifacts
            if not line or line.startswith('>>>') or line.startswith('$'):
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def get_protocol_info(self, cli_type: str) -> Dict[str, Any]:
        """Get protocol information for CLI type"""
        if cli_type not in self.protocols:
            return {"error": "Protocol not found"}
        
        protocol = self.protocols[cli_type]
        
        return {
            "cli_type": cli_type,
            "input_format": protocol.input_format.value,
            "output_format": protocol.output_format.value,
            "response_pattern": protocol.response_pattern.value,
            "timeout_seconds": protocol.timeout_seconds,
            "silent_period_seconds": protocol.silent_period_seconds,
            "has_end_marker": protocol.end_marker is not None,
            "has_prompt_regex": protocol.prompt_regex is not None
        }
    
    def list_protocols(self) -> List[Dict[str, Any]]:
        """List all available protocols"""
        return [self.get_protocol_info(cli_type) for cli_type in self.protocols.keys()]