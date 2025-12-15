"""
FastAPI Application Example

This example shows how to integrate BrainUs API with FastAPI.
FastAPI is built for async operations.

Requirements:
    pip install fastapi uvicorn brainus-ai

Usage:
    export BRAINUS_API_KEY=your_api_key
    python fastapi_example.py
    
    Or with uvicorn:
    uvicorn fastapi_example:app --reload
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
from brainus_ai import BrainusAI, BrainusError
import os
from datetime import datetime

app = FastAPI(
    title="BrainUs Proxy API",
    description="FastAPI wrapper for BrainUs AI",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class QueryRequest(BaseModel):
    query: str
    store_id: str = "default"
    filters: Optional[Dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is photosynthesis?",
                "store_id": "default",
                "filters": None
            }
        }


class QueryResponse(BaseModel):
    answer: str
    citations: List[dict]
    has_citations: bool


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "BrainUs Proxy API",
        "version": "1.0.0",
        "status": "online"
    }


@app.post("/api/query", response_model=QueryResponse)
async def query_endpoint(
    request: QueryRequest, 
    background_tasks: BackgroundTasks
):
    """
    Query BrainUs AI
    
    Args:
        request: QueryRequest with query, store_id, and optional filters
        background_tasks: FastAPI background tasks
        
    Returns:
        QueryResponse with answer, citations, and has_citations flag
        
    Raises:
        HTTPException: On API errors
    """
    try:
        async with BrainusAI(api_key=os.getenv("BRAINUS_API_KEY")) as client:
            result = await client.query(
                query=request.query,
                store_id=request.store_id,
                filters=request.filters,
            )

        # Log query in background
        background_tasks.add_task(
            log_query, 
            request.query, 
            f"query_{datetime.now().timestamp()}"
        )

        return QueryResponse(
            answer=result.answer,
            citations=[
                c.model_dump() if hasattr(c, 'model_dump') else c.__dict__ 
                for c in result.citations
            ] if result.citations else [],
            has_citations=result.has_citations
        )

    except BrainusError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


def log_query(query: str, query_id: str):
    """
    Log query for analytics
    
    This runs in the background after the response is sent
    """
    print(f"Query logged: {query_id} - {query[:50]}...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
