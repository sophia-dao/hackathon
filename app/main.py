from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.gssi import router as gssi_router

app = FastAPI(
    title="Global Supply Chain Stress Index API",
    description="Backend for monitoring and forecasting global supply chain stress",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(gssi_router, prefix="/gssi", tags=["GSSI"])


@app.get("/")
def root():
    return {
        "message": "GSSI backend is running"
    }