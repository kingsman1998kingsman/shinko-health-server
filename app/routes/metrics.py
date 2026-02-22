from fastapi import APIRouter
from pydantic import BaseModel
from supabase import Client
from datetime import datetime, timezone

router = APIRouter()

# 1. Add machine_type to the incoming data model
class MetricsUpdate(BaseModel):
    user_id: str
    machine_type: str  # <--- NEW: Accept from tablet
    steps: int = 0
    heart_rate: int = 0
    sleep_quality: int = 0
    body_weight: float = 0.0

def init_metrics_routes(supabase: Client):
    @router.post("/update")
    def update_metrics(data: MetricsUpdate):
        payload = data.dict()
        # payload["machine_type"] = "body_scale" <--- REMOVE the hardcoded line!
        payload["measured_at"] = datetime.now(timezone.utc).isoformat()
        
        supabase.table("measurements").insert(payload).execute()
        return {"success": True}

    @router.get("/{user_id}")
    def get_metrics(user_id: str):
        resp = supabase.table("measurements") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("measured_at", desc=True) \
            .limit(1) \
            .execute()
            
        if not resp.data:
            return None 
            
        return resp.data[0]

    return router