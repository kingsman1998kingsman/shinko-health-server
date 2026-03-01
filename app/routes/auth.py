import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from supabase import Client

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    age: int
    height: float
    gender: str  # This receives "Male" or "Female" from the HTML

def init_auth_routes(supabase: Client):
    @router.post("/login")
    def login(data: LoginRequest):
        resp = supabase.table("users").select("*").eq("email", data.email).eq("password", data.password).execute()
        if not resp.data:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user = resp.data[0]
        return {
            "user_id": user["id"], 
            "name": user["name"], 
            "email": user["email"],
            "height": user.get("height"),
            "age": user.get("age")
        }

    @router.post("/register")
    def register(data: RegisterRequest):
        # 1. Check if user already exists
        existing = supabase.table("users").select("id").eq("email", data.email).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="Email already registered")

        # 2. Convert Gender String to Integer (Fixes the 500 error)
        # 1 for Male, 2 for Female
        gender_int = 1 if data.gender == "Male" else 2

        new_user_id = str(uuid.uuid4())
        user_payload = {
            "id": new_user_id,
            "name": data.name,
            "email": data.email,
            "password": data.password,
            "age": data.age,
            "height": data.height,
            "gender": gender_int  # Send the integer 1 or 2
        }

        # 3. Insert into Supabase
        try:
            resp = supabase.table("users").insert(user_payload).execute()
            if not resp.data:
                raise Exception("Insert failed")
            return {"message": "Success", "user_id": new_user_id}
        except Exception as e:
            # This will show you the exact DB error if it fails again
            print(f"Database Error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    return router