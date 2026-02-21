from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client

from app.routes.qr import router as qr_router
from app.routes.auth import init_auth_routes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://shinko-health-mobile.netlify.app",
        "https://shinko-health-tablet.netlify.app",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = "https://ymsctiblyflxmbgeptpj.supabase.co"
SUPABASE_KEY = "PASTE_YOUR_REAL_SUPABASE_ANON_OR_SERVICE_ROLE_KEY"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# routes
app.include_router(init_auth_routes(supabase))
app.include_router(qr_router, prefix="/qr", tags=["qr"])

@app.get("/")
def root():
    return {"message": "Server is running"}