#!/usr/bin/env python3
"""
AI-Bridge CLI System - Local Launcher
Starts the complete AI-Bridge system locally
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def start_backend():
    """Start the AI-Bridge backend server"""
    print("🚀 Starting AI-Bridge Backend...")
    backend_path = Path("backend")
    if not backend_path.exists():
        print("❌ Backend directory not found!")
        return False
    
    try:
        # Start backend server
        process = subprocess.Popen([
            sys.executable, "main.py"
        ], cwd=backend_path)
        print(f"✅ Backend started with PID: {process.pid}")
        return True
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return False

def start_frontend():
    """Start the frontend control cabin"""
    print("🎮 Starting Frontend Control Cabin...")
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print("❌ Frontend directory not found!")
        return False
    
    try:
        # Install dependencies if needed
        subprocess.run(["npm", "install"], cwd=frontend_path, check=True)
        
        # Start frontend dev server
        process = subprocess.Popen([
            "npm", "run", "dev"
        ], cwd=frontend_path)
        print(f"✅ Frontend started with PID: {process.pid}")
        return True
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return False

def main():
    """Main launcher function"""
    print("=" * 60)
    print("🤖 AI-BRIDGE CLI SYSTEM - LOCAL LAUNCHER")
    print("First Autonomous AI Development Team")
    print("Using CLI memberships - NO API keys required")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required!")
        return
    
    print("🔧 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed")
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return
    
    # Start services
    backend_started = start_backend()
    if backend_started:
        time.sleep(3)  # Wait for backend to initialize
        frontend_started = start_frontend()
        
        if frontend_started:
            print("\n" + "=" * 60)
            print("🎉 AI-BRIDGE SYSTEM RUNNING!")
            print("🔗 Backend API: http://localhost:8000")
            print("🎮 Control Cabin: http://localhost:5000")
            print("=" * 60)
            print("\n📋 Ready for autonomous AI collaboration!")
            print("Open the Control Cabin to supervise your AI team.")
        else:
            print("❌ Failed to start frontend")
    else:
        print("❌ Failed to start backend")

if __name__ == "__main__":
    main()