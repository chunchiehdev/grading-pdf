#!/usr/bin/env python3
"""
Script to start Celery worker
"""
import subprocess
import sys

if __name__ == "__main__":
    cmd = [
        "celery", "-A", "app.worker.celery_app", "worker",
        "--loglevel=info",
        "--concurrency=4"
    ]
    
    print("Starting Celery worker...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nShutting down worker...")
        sys.exit(0) 