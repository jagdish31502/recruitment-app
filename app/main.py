"""
Main FastAPI application for Recruitment AI Agent
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utilities.logger import setup_logger

# Import routers
from app.routers import job_description, resume_matching, email_generation, database

logger = setup_logger()

# Create FastAPI app
app = FastAPI(
    title="Recruitment AI Agent API",
    description="AI-powered recruitment system for matching candidates with job descriptions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(job_description.router, prefix="/api/v1", tags=["Job Description"])
app.include_router(resume_matching.router, prefix="/api/v1", tags=["Resume Matching"])
app.include_router(email_generation.router, prefix="/api/v1", tags=["Email Generation"])
app.include_router(database.router, prefix="/api/v1", tags=["Database"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Recruitment AI Agent API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Recruitment AI Agent"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)