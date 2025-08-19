#!/usr/bin/env python3
"""
Simple test server to verify basic setup
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Simple Test Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Simple test server is working!", "status": "success"}

@app.get("/health")
async def health():
    return {"status": "healthy", "server": "simple_test"}

if __name__ == "__main__":
    import uvicorn
    print("Starting simple test server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
