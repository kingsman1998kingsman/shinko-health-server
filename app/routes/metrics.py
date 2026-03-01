from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from supabase import Client
from datetime import datetime, timezone
from typing import Optional, List

router = APIRouter()

class MetricsUpdate(BaseModel):
    user_id: str
    machine_type: str 
    
    # Aliases MUST match the uppercase keys sent by scan.js
    body_weight: float = Field(0.0, alias="Wk")    
    body_fat_pct: float = Field(0.0, alias="FW")   
    muscle_mass: float = Field(0.0, alias="MW")    
    bmi: float = Field(0.0, alias="MI")             
    visceral_fat: int = Field(0, alias="IF") 
    metabolic_age: int = Field(0, alias="BA")
    
    # Extra data points
    bmr: int = Field(0, alias="rB")
    body_water: float = Field(0.0, alias="wW")

    class Config:
        populate_by_name = True 

def init_metrics_routes(supabase: Client):
    
    # --- 1. POST: Update/Insert new data (From Tablet) ---
    @router.post("/update")
    def update_metrics(data: MetricsUpdate):
        try:
            payload = data.model_dump(by_alias=False)
            payload["measured_at"] = datetime.now(timezone.utc).isoformat()
            
            response = supabase.table("measurements").insert(payload).execute()
            
            if not response.data:
                raise HTTPException(status_code=500, detail="Failed to insert into Supabase")
                
            return {"success": True, "data": response.data}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    # --- 2. GET: Latest session for Dashboard (From Mobile) ---
    @router.get("/{user_id}")
    def get_latest_metrics(user_id: str):
        try:
            response = supabase.table("measurements")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("measured_at", desc=True)\
                .limit(1)\
                .execute()
            
            if not response.data:
                return None
            return response.data[0]
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    # --- 3. GET: Full History for Table (From Mobile) ---
    @router.get("/history/{user_id}")
    def get_history(user_id: str):
        try:
            response = supabase.table("measurements")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("measured_at", desc=True)\
                .execute()
            
            return response.data
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    return router