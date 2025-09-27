#!/usr/bin/env python3
"""
AI-Bridge CLI System - Local Launcher
Starts the complete AI-Bridge system locally (ASCII-safe output)
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def start_backend() -> bool:
    """Start the AI-Bridge backend server"""
    print("[AI-Bridge] Starting Backend...")
    backend_path = Path("backend")
    if not backend_path.exists():
        print("[AI-Bridge] Backend directory not found!")
        return False

    try:
        env = dict(**os.environ)
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        env["PYTHONLEGACYWINDOWSSTDIO"] = "1"
        process = subprocess.Popen([sys.executable, "main.py"], cwd=backend_path, env=env)
        print(f"[AI-Bridge] Backend started with PID: {process.pid}")
        return True
    except Exception as e:
        print(f"[AI-Bridge] Error starting backend: {e}")
        return False


def start_frontend() -> bool:
    """Start the frontend control cabin"""
    print("[AI-Bridge] Starting Frontend Control Cabin...")
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print("[AI-Bridge] Frontend directory not found!")
        return False

    try:
        # Install dependencies if needed (shell=True for Windows compatibility)
        print("[AI-Bridge] Installing frontend dependencies...")
        subprocess.run(["npm", "install"], cwd=frontend_path, shell=True, check=True)
        print("[AI-Bridge] Frontend dependencies installed")

        # Start frontend dev server (shell=True for Windows compatibility)
        print("[AI-Bridge] Starting frontend dev server...")
        process = subprocess.Popen(["npm", "run", "dev"], cwd=frontend_path, shell=True)
        print(f"[AI-Bridge] Frontend started with PID: {process.pid}")
        return True
    except Exception as e:
        print(f"[AI-Bridge] Error starting frontend: {e}")
        return False


def main():
    print("=" * 60)
    print("AI-BRIDGE CLI SYSTEM - LOCAL LAUNCHER")
    print("First Autonomous AI Development Team")
    print("Using CLI memberships - NO API keys required")
    print("=" * 60)

    # Check Python version
    if sys.version_info < (3, 8):
        print("[AI-Bridge] Python 3.8+ required!")
        return

    print("[AI-Bridge] Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("[AI-Bridge] Dependencies installed")
    except Exception as e:
        print(f"[AI-Bridge] Error installing dependencies: {e}")
        return

    # Start services
    backend_started = start_backend()
    if backend_started:
        time.sleep(3)
        frontend_started = start_frontend()

        if frontend_started:
            print("\n" + "=" * 60)
            print("AI-BRIDGE SYSTEM RUNNING!")
            print("Backend API: http://localhost:8000")
            print("Control Cabin: http://localhost:5000")
            print("=" * 60)
            print("\nReady for autonomous AI collaboration!")
            print("Open the Control Cabin to supervise your AI team.")
        else:
            print("[AI-Bridge] Failed to start frontend")
    else:
        print("[AI-Bridge] Failed to start backend")


if __name__ == "__main__":
    main()
