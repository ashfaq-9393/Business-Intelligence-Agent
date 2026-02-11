"""
Business Intelligence Agent - FastAPI Backend
Provides REST API endpoints for the BI Agent
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
from bi_agent import BusinessIntelligenceAgent

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Business Intelligence Agent API",
    description="REST API for BI Agent - Sales Pipeline & Project Execution Analytics",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize BI Agent
agent = None

class QuestionRequest(BaseModel):
    question: str

class AnalysisResponse(BaseModel):
    question: str
    executive_summary: str
    key_metrics: dict
    insights: list
    ai_powered: bool
    data_sources: list


@app.on_event("startup")
async def startup_event():
    """Initialize agent on startup"""
    global agent
    api_key = os.getenv("MONDAY_API_KEY")
    deals_board_id = os.getenv("DEALS_BOARD_ID")
    work_orders_board_id = os.getenv("WORK_ORDERS_BOARD_ID")
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not all([api_key, deals_board_id, work_orders_board_id]):
        raise RuntimeError("Missing required environment variables")
    
    agent = BusinessIntelligenceAgent(api_key, deals_board_id, work_orders_board_id, groq_api_key)
    
    # Load data
    if not agent.refresh_data():
        raise RuntimeError("Failed to load initial data from monday.com")
    
    print(f"✅ Agent initialized with {len(agent.deals_data)} deals and {len(agent.work_orders_data)} work orders")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if agent is None:
        return {"status": "initializing"}
    return {
        "status": "healthy",
        "deals": len(agent.deals_data),
        "work_orders": len(agent.work_orders_data),
        "ai_enabled": agent.groq_engine.enabled if agent.groq_engine else False
    }


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: QuestionRequest):
    """
    Analyze a business question
    
    Args:
        request: QuestionRequest with 'question' field
        
    Returns:
        Analysis result with metrics and insights
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        response = agent.ask_question(request.question)
        
        return AnalysisResponse(
            question=response.get("question", request.question),
            executive_summary=response.get("executive_summary", ""),
            key_metrics=response.get("key_metrics", {}),
            insights=response.get("insights", []),
            ai_powered=response.get("ai_powered", False),
            data_sources=response.get("data_used", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/refresh")
async def refresh_data():
    """Refresh data from monday.com"""
    if agent is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    if agent.refresh_data():
        return {
            "status": "refreshed",
            "deals": len(agent.deals_data),
            "work_orders": len(agent.work_orders_data)
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to refresh data")


@app.get("/metrics")
async def get_metrics():
    """Get current metrics"""
    if agent is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    # Analyze deals
    metrics = agent.insight_engine.analyze_deals_pipeline(agent.deals_data)
    
    return {
        "deals": {
            "total": len(agent.deals_data),
            "metrics": metrics
        },
        "work_orders": {
            "total": len(agent.work_orders_data),
            "metrics": agent.insight_engine.analyze_work_orders(agent.work_orders_data)
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000))
    )
