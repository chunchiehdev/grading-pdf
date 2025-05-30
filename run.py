#!/usr/bin/env python3
"""
Entry point for the PDF Parser service
"""
import uvicorn
import os

if __name__ == "__main__":
    # Production optimized settings for Kubernetes
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 8000)),
        workers=1,  # Single worker per pod - scaling via K8s replicas
        reload=False,  # Disable reload in production
        access_log=True
    ) 