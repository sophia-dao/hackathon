from fastapi import FastAPI
from app.routes.gssi import router as gssi_router

app = FastAPI(
    title="StressWatch API",
    description="Backend API for StressWatch — Global Supply Chain Stress Index early-warning system",
    version="1.0.0"
)

# Include route files
app.include_router(gssi_router, prefix="/gssi", tags=["GSSI"])


@app.get("/")
def root():
    return {
        "message": "GSSI backend is running",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}