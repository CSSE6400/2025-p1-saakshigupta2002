from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Check the health of the service.
    Returns 200 if the service is healthy.
    """
    return {"status": "healthy"}
