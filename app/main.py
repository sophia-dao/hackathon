from fastapi import FastAPI
from app.routes.gssi import router as gssi_router

app = FastAPI(
    title="Global Supply Chain Stress Index API",
    description="Backend for monitoring and forecasting global supply chain stress",
    version="1.0.0"
)

app.include_router(gssi_router, prefix="/gssi", tags=["GSSI"])


@app.get("/")
def root():
    return {
        "message": "GSSI backend is running"
    }