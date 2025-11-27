#!/usr/bin/env python3
"""
F1 Race Outcome Predictor - Startup Script
Launches all services for the F1 prediction platform
"""

import asyncio
import subprocess
import sys
import os
import time
from pathlib import Path

def print_banner():
    """Print startup banner"""
    banner = """
    ==============================================================
                                                              
                   F1 RACE OUTCOME PREDICTOR               
                                                              
         A cutting-edge machine learning platform for F1         
         race predictions, real-time analytics, and fan          
         engagement features.                                     
                                                              
         Author: Prathyusha Shetty                               
         Version: 1.0.0                                          
                                                              
    ==============================================================
    """
    try:
        print(banner)
    except UnicodeEncodeError:
        print("F1 RACE OUTCOME PREDICTOR (Banner skipped due to encoding)")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("[INFO] Checking dependencies...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("[ERROR] Python 3.8+ is required")
        return False
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("[WARN] Warning: Virtual environment not detected. Consider using a virtual environment.")
    
    # Check if requirements.txt exists
    if not Path("requirements.txt").exists():
        print("[ERROR] requirements.txt not found")
        return False
    
    print("[OK] Dependencies check passed")
    return True

def check_environment():
    """Check environment configuration"""
    print("[INFO] Checking environment configuration...")
    
    # Check if .env file exists
    if not Path(".env").exists():
        if Path(".env.example").exists():
            print("[WARN] .env file not found. Please copy .env.example to .env and configure it.")
            return False
        else:
            print("[ERROR] .env.example file not found")
            return False
    
    print("[OK] Environment configuration check passed")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("[INFO] Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("[OK] Python dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to install dependencies: {e}")
        return False

def initialize_database():
    """Initialize the database"""
    print("[INFO] Initializing database...")
    try:
        subprocess.run([sys.executable, "scripts/init_db.py"], check=True)
        print("[OK] Database initialized successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Database initialization failed: {e}")
        return False

def start_api_server():
    """Start the API server"""
    print("[INFO] Starting API server...")
    try:
        # Start API server in background
        process = subprocess.Popen([sys.executable, "-m", "app.main"])
        time.sleep(3)  # Give it time to start
        
        if process.poll() is None:  # Process is still running
            print("[OK] API server started successfully on http://localhost:8000")
            return process
        else:
            print("[ERROR] API server failed to start")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to start API server: {e}")
        return None

def start_live_predictor():
    """Start the live prediction service"""
    print("[INFO] Starting live prediction service...")
    try:
        # Start live predictor in background
        process = subprocess.Popen([sys.executable, "-m", "services.live_predictor"])
        time.sleep(2)  # Give it time to start
        
        if process.poll() is None:  # Process is still running
            print("[OK] Live prediction service started successfully on ws://localhost:8001")
            return process
        else:
            print("[ERROR] Live prediction service failed to start")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to start live prediction service: {e}")
        return None

def start_web_interface():
    """Start the web interface"""
    print("[INFO] Starting web interface...")
    
    web_dir = Path("web")
    if not web_dir.exists():
        print("[WARN] Web interface directory not found. Skipping web interface.")
        return None
    
    try:
        # Check if node_modules exists
        if not (web_dir / "node_modules").exists():
            print("[INFO] Installing web dependencies...")
            npm_cmd = "npm.cmd" if os.name == 'nt' else "npm"
            subprocess.run([npm_cmd, "install"], cwd=web_dir, check=True)
        
        # Start web interface
        # Use cmd /c to avoid PowerShell execution policy issues on Windows
        npm_cmd = "npm.cmd" if os.name == 'nt' else "npm"
        process = subprocess.Popen([npm_cmd, "start"], cwd=web_dir)
        time.sleep(5)  # Give it time to start
        
        if process.poll() is None:  # Process is still running
            print("[OK] Web interface started successfully on http://localhost:3000")
            return process
        else:
            print("[ERROR] Web interface failed to start")
            return None
    except FileNotFoundError:
        print("[WARN] Node.js/npm not found. Skipping web interface.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to start web interface: {e}")
        return None

def print_status(api_process, live_process, web_process):
    """Print service status"""
    print("\n" + "="*60)
    print("   F1 RACE OUTCOME PREDICTOR - SERVICE STATUS")
    print("="*60)
    
    # API Server
    if api_process and api_process.poll() is None:
        print("[OK] API Server: Running on http://localhost:8000")
        print("   API Documentation: http://localhost:8000/docs")
    else:
        print("[ERROR] API Server: Not running")
    
    # Live Prediction Service
    if live_process and live_process.poll() is None:
        print("[OK] Live Predictor: Running on ws://localhost:8001")
    else:
        print("[ERROR] Live Predictor: Not running")
    
    # Web Interface
    if web_process and web_process.poll() is None:
        print("[OK] Web Interface: Running on http://localhost:3000")
    else:
        print("[WARN] Web Interface: Not running")
    
    print("="*60)
    print("   Ready for F1 predictions!")
    print("="*60)

def main():
    """Main startup function"""
    print_banner()
    
    # Pre-flight checks
    if not check_dependencies():
        print("[ERROR] Dependency check failed. Please install required dependencies.")
        return 1
    
    if not check_environment():
        print("[ERROR] Environment check failed. Please configure your environment.")
        return 1
    
    # Install dependencies if needed
    try:
        import fastapi
        import uvicorn
        import pandas
        import numpy
        import sklearn
    except ImportError:
        print("[INFO] Some dependencies are missing. Installing...")
        if not install_dependencies():
            return 1
    
    # Initialize database
    if not initialize_database():
        print("[ERROR] Database initialization failed.")
        return 1
    
    # Start services
    api_process = start_api_server()
    live_process = start_live_predictor()
    web_process = start_web_interface()
    
    # Print status
    print_status(api_process, live_process, web_process)
    
    # Keep running
    try:
        print("\n[INFO] Services are running. Press Ctrl+C to stop all services.")
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if api_process and api_process.poll() is not None:
                print("[WARN] API server stopped unexpectedly")
                break
            if live_process and live_process.poll() is not None:
                print("[WARN] Live predictor stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n[INFO] Stopping all services...")
        
        # Stop all processes
        for process in [api_process, live_process, web_process]:
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        print("[OK] All services stopped successfully")
        return 0

if __name__ == "__main__":
    sys.exit(main())
