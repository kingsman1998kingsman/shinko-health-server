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
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inltc2N0aWJseWZseG1iZ2VwdHBqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE2NTUyODYsImV4cCI6MjA4NzIzMTI4Nn0.zspLRpB843cPcnLLaZk--a4163Uce9x0iN7mbGtnfGA"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# routes
app.include_router(init_auth_routes(supabase))
app.include_router(qr_router, prefix="/qr", tags=["qr"])

@app.get("/")
def root():
    return {"message": "Server is running"}