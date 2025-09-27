#!/usr/bin/env python3
"""
CLI Agent Configuration Script
Configures AI-Bridge to use your local CLI tools without API keys
"""

import json
import requests
import subprocess
import sys
from pathlib import Path

def check_cli_availability():
    """Check which CLI tools are available"""
    cli_tools = {}

    # Check Claude CLI
    try:
        result = subprocess.run(["claude", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            cli_tools["claude"] = result.stdout.strip()
            print(f"[OK] Claude CLI found: {cli_tools['claude']}")
        else:
            print("[ERROR] Claude CLI not found")
    except Exception as e:
        print(f"❌ Claude CLI error: {e}")

    # Check OpenAI CLI
    try:
        result = subprocess.run(["openai", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            cli_tools["openai"] = result.stdout.strip()
            print(f"✅ OpenAI CLI found: {cli_tools['openai']}")
        else:
            print("❌ OpenAI CLI not found")
    except Exception as e:
        print(f"❌ OpenAI CLI error: {e}")

    # Check Python
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            cli_tools["python"] = result.stdout.strip()
            print(f"✅ Python found: {cli_tools['python']}")
    except Exception as e:
        print(f"❌ Python error: {e}")

    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            cli_tools["node"] = result.stdout.strip()
            print(f"✅ Node.js found: {cli_tools['node']}")
    except Exception as e:
        print(f"❌ Node.js error: {e}")

    return cli_tools

def configure_system():
    """Configure the AI-Bridge system"""
    print("🔧 Configuring AI-Bridge CLI Agents...")

    # Check available CLI tools
    cli_tools = check_cli_availability()

    if not cli_tools:
        print("❌ No CLI tools found! Please install Claude CLI or OpenAI CLI")
        return False

    # Configure system via API
    try:
        # Create configuration
        config = {
            "default_base_dir": "workspace",
            "auto_save_conversations": True,
            "auto_save_workflows": True,
            "max_conversation_history": 1000,
            "yes_all_claude_a": True,
            "yes_all_claude_b": True,
            "reflection_mode": "expert",
            "require_justification": True,
            "cross_validation": True,
            "ask_for_clarification": True,
            "unlimited_iterations": True,
            "smart_completion": True,
            "execution_philosophy": "goal_oriented",
            "cli_tools_available": cli_tools,
            "enable_real_cli_communication": True
        }

        # Send configuration to API
        response = requests.post(
            "http://localhost:8000/api/config",
            json=config,
            timeout=10
        )

        if response.status_code == 200:
            print("✅ AI-Bridge configuration updated successfully!")
            result = response.json()
            print(f"✅ Config saved to: {result.get('config_file_path', 'N/A')}")
            print(f"✅ Workspace created: {result.get('workspace_path', 'N/A')}")
            return True
        else:
            print(f"❌ Configuration failed: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_agent_communication():
    """Test if agents can communicate"""
    print("\n🧪 Testing agent communication...")

    try:
        # Test basic health
        response = requests.get("http://localhost:8000/api/health", timeout=10)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ System health: {health['status']}")
            print(f"✅ Orchestration available: {health['orchestration_available']}")

            # Try to start a simple orchestration
            test_objective = "Test agent communication - simple hello world task"
            orch_response = requests.post(
                "http://localhost:8000/api/orchestration/start",
                json={"objective": test_objective},
                timeout=15
            )

            if orch_response.status_code == 200:
                result = orch_response.json()
                session_id = result.get("session_id")
                print(f"✅ Test orchestration started: {session_id}")
                print("✅ CLI agents are configured and ready!")
                return True
            else:
                print(f"⚠️ Orchestration test failed: {orch_response.status_code}")
                print(f"Error: {orch_response.text}")
                return False
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Communication test error: {e}")
        return False

def main():
    print("=" * 60)
    print("AI-BRIDGE CLI AGENT CONFIGURATION")
    print("Configuring your system for autonomous AI collaboration")
    print("NO API KEYS REQUIRED - Uses your CLI memberships")
    print("=" * 60)

    # Step 1: Configure system
    if not configure_system():
        print("\n❌ Configuration failed!")
        return False

    # Step 2: Test communication
    if not test_agent_communication():
        print("\n⚠️ Communication test failed, but system may still work")

    print("\n" + "=" * 60)
    print("🎉 AI-BRIDGE CLI AGENTS CONFIGURED!")
    print("=" * 60)
    print("✅ System ready for autonomous AI collaboration")
    print("✅ Access Control Cabin: http://localhost:5002")
    print("✅ Access API Docs: http://localhost:8000/api/docs")
    print("✅ Backend API: http://localhost:8000")
    print("\n🚀 Ready to launch your first autonomous AI development session!")

    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Configuration interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")