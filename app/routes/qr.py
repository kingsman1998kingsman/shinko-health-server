import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from supabase import Client

router = APIRouter()
UTC = timezone.utc

class CreateQRRequest(BaseModel):
    user_id: str
    ttl_seconds: int = 30

class ConsumeQRRequest(BaseModel):
    token: str

def init_qr_routes(supabase: Client):
    @router.post("/create")
    def create_qr(data: CreateQRRequest):
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(UTC) + timedelta(seconds=data.ttl_seconds)
        
        resp = supabase.table("qr_tokens").insert({
            "token": token,
            "user_id": data.user_id,
            "expires_at": expires_at.isoformat()
        }).execute()

        if not resp.data:
            raise HTTPException(status_code=500, detail="Failed to create QR token")

        return {"token": token, "expires_in_seconds": data.ttl_seconds}

    @router.post("/consume")
    def consume_qr(data: ConsumeQRRequest):
        resp = supabase.table("qr_tokens").select("token,user_id,expires_at,used_at").eq("token", data.token).execute()
        if not resp.data:
            raise HTTPException(status_code=401, detail="Invalid token")

        row = resp.data[0]
        if row.get("used_at"):
            raise HTTPException(status_code=401, detail="Token already used")

        expires_at = datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00"))
        if datetime.now(UTC) > expires_at:
            raise HTTPException(status_code=401, detail="Token expired")

        # Mark used
        supabase.table("qr_tokens").update({"used_at": datetime.now(UTC).isoformat()}).eq("token", data.token).execute()
        
        # Get user details for tablet display
        user_resp = supabase.table("users").select("id,name").eq("id", row["user_id"]).execute()
        
        return {"message": "Success", "user": {"user_id": row["user_id"], "name": user_resp.data[0]["name"]}}

    @router.get("/status/{token}")
    def check_qr_status(token: str):
        resp = supabase.table("qr_tokens").select("used_at").eq("token", token).execute()
        if not resp.data:
            return {"status": "invalid"}
        
        is_used = resp.data[0].get("used_at") is not None
        return {"status": "consumed" if is_used else "pending"}

    return router