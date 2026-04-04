from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "GSSI route is working"
    }


@router.get("/overview")
def get_overview():
    return {
        "project": "Global Supply Chain Stress Index",
        "frequency": "weekly",
        "model": "LSTM",
        "status": "backend scaffold ready"
    }