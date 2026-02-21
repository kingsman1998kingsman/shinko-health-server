import os
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client

router = APIRouter()

UTC = timezone.utc

# ===== Supabase Config (use ENV on Railway) =====
SUPABASE_URL = "https://ymsctiblyflxmbgeptpj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inltc2N0aWJseWZseG1iZ2VwdHBqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE2NTUyODYsImV4cCI6MjA4NzIzMTI4Nn0.zspLRpB843cPcnLLaZk--a4163Uce9x0iN7mbGtnfGA"

if not SUPABASE_URL or not SUPABASE_KEY:
    # Don't crash import; but endpoints will fail clearly.
    supabase: Client | None = None
else:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ===== Models =====
class CreateQRRequest(BaseModel):
    user_id: str  # uuid/string/int ok as string
    ttl_seconds: int | None = 30  # optional override

class ConsumeQRRequest(BaseModel):
    token: str


def _require_supabase() -> Client:
    if supabase is None:
        raise HTTPException(status_code=500, detail="Supabase env is not configured")
    return supabase


@router.post("/create")
def create_qr(data: CreateQRRequest):
    sb = _require_supabase()

    ttl = data.ttl_seconds or 30
    if ttl < 5 or ttl > 300:
        ttl = 30  # keep it sane

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(UTC) + timedelta(seconds=ttl)

    ins = sb.table("qr_tokens").insert({
        "token": token,
        "user_id": data.user_id,
        "expires_at": expires_at.isoformat(),
        "used_at": None,
    }).execute()

    if not ins.data:
        raise HTTPException(status_code=500, detail="Failed to create QR token")

    return {
        "token": token,
        "expires_in_seconds": ttl
    }


@router.post("/consume")
def consume_qr(data: ConsumeQRRequest):
    sb = _require_supabase()

    # 1) token lookup
    resp = sb.table("qr_tokens") \
        .select("token,user_id,expires_at,used_at") \
        .eq("token", data.token) \
        .execute()

    if not resp.data:
        raise HTTPException(status_code=401, detail="Invalid token")

    row = resp.data[0]

    # 2) one-time
    if row.get("used_at"):
        raise HTTPException(status_code=401, detail="Token already used")

    # 3) expiry
    # Supabase returns ISO string, sometimes with Z
    expires_at_str = row["expires_at"].replace("Z", "+00:00")
    expires_at = datetime.fromisoformat(expires_at_str)
    if datetime.now(UTC) > expires_at:
        raise HTTPException(status_code=401, detail="Token expired")

    # 4) mark used
    sb.table("qr_tokens").update({
        "used_at": datetime.now(UTC).isoformat()
    }).eq("token", data.token).execute()

    # 5) fetch user
    user_resp = sb.table("users") \
        .select("id,name,email") \
        .eq("id", row["user_id"]) \
        .execute()

    if not user_resp.data:
        raise HTTPException(status_code=401, detail="User not found")

    user = user_resp.data[0]

    return {
        "message": f"Welcome {user['name']}",
        "user": user
    }