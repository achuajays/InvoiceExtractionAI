#!/usr/bin/env python3
"""
Script to run the Invoice Extraction FastAPI server
"""
import uvicorn
import sys
import os

def main():
    """Run the FastAPI server with optional configuration."""
    host = "0.0.0.0"  # Allow external connections
    port = 8000
    reload = "--reload" in sys.argv
    
    print(f"🚀 Starting Invoice Extraction API server...")
    print(f"📍 Server will be available at: http://localhost:{port}")
    print(f"📚 API documentation: http://localhost:{port}/docs")
    print(f"📖 Alternative docs: http://localhost:{port}/redoc")
    print(f"🧪 Test frontend: Open test_frontend.html in your browser")
    print(f"🔄 Auto-reload: {'Enabled' if reload else 'Disabled'}")
    print("\n" + "="*50 + "\n")
    
    # Ensure temp directories exist
    os.makedirs("temp_images", exist_ok=True)
    os.makedirs("temp_uploads", exist_ok=True)
    
    # Run the server
    uvicorn.run(
        "app_fastapi:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    main()
