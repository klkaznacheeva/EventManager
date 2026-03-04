from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def admin_health():
    return {"status": "admin working"}