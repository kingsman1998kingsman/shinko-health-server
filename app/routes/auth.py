from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from supabase import Client

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

def init_auth_routes(supabase: Client):
    @router.post("/login")
    def login(data: LoginRequest):
        resp = supabase.table("users").select("id,name,email").eq("email", data.email).eq("password", data.password).execute()
        if not resp.data:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user = resp.data[0]
        return {"user_id": user["id"], "name": user["name"], "email": user["email"]}

    return router