#!/usr/bin/env python3
"""
Simple server starter for AI Bridge System
Runs backend on port 8000 and serves frontend through static files
"""

import uvicorn
import os
import sys

# Add backend directory to Python path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

if __name__ == "__main__":
    print("🚀 Starting AI Bridge System...")
    print("- Backend API: http://localhost:8000")
    print("- Frontend: http://localhost:5000 (when started)")
    
    # Start the backend server
    try:
        uvicorn.run(
            "backend.main:app",
            host="localhost",
            port=8000,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        sys.exit(1)