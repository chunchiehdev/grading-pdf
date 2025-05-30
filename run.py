#!/usr/bin/env python3
"""
Entry point for the PDF Parser service
"""
import uvicorn
import os

if __name__ == "__main__":
    # Production optimized settings
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 8000)),
        workers=int(os.getenv("WORKERS", 4)),  # Multiple workers for concurrency
        reload=False,  # Disable reload in production
        access_log=True
    ) 