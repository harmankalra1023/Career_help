from fastapi import APIRouter

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/snapshot/latest")
async def get_latest_snapshot():
    return {
        "snapshot_id": "snap-2026-11",
        "region": "global",
        "stale": False,
        "sample_size": 15000,
        "timestamp": "2026-11-15T00:00:00Z",
    }
