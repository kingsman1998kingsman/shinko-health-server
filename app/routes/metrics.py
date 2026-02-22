from fastapi import APIRouter
from pydantic import BaseModel
from supabase import Client
from datetime import datetime, timezone

router = APIRouter()

class MetricsUpdate(BaseModel):
    user_id: str
    machine_type: str 
    steps: int = 0
    heart_rate: int = 0
    sleep_quality: int = 0
    body_weight: float = 0.0

def init_metrics_routes(supabase: Client):
    @router.post("/update")
    def update_metrics(data: MetricsUpdate):
        payload = data.dict()
        payload["measured_at"] = datetime.now(timezone.utc).isoformat()
        
        supabase.table("measurements").insert(payload).execute()
        return {"success": True}

    @router.get("/{user_id}")
    def get_metrics(user_id: str):
        # Fetch only the 1 latest record for the home dashboard
        resp = supabase.table("measurements") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("measured_at", desc=True) \
            .limit(1) \
            .execute()
            
        if not resp.data:
            return None 
            
        return resp.data[0]

    # --- NEW: Endpoint to fetch all history for the table ---
    @router.get("/history/{user_id}")
    def get_history(user_id: str):
        # Fetch all records for this user, ordered by date (newest first)
        resp = supabase.table("measurements") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("measured_at", desc=True) \
            .execute()
            
        return resp.data # Returns an array of objects
    # -------------------------------------------------------

    return router