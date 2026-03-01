import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client

from app.routes.auth import init_auth_routes
from app.routes.qr import init_qr_routes
from app.routes.metrics import init_metrics_routes

app = FastAPI(title="Shinko Health API - Localhost")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://shinko-mobile.netlify.app",
        "https://shinko-tablet.netlify.app",
        "http://localhost:5500",  # Add this for local testing
        "http://127.0.0.1:5500",  # Add this for local testing
        "http://localhost:5501",  # Add this for local testing
        "http://127.0.0.1:5501",  # Add this for local testing
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Replace these with your actual Supabase credentials for local testing
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://yzlnimudrgwgvaungghf.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl6bG5pbXVkcmd3Z3ZhdW5nZ2hmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTkxNDQzNywiZXhwIjoyMDg3NDkwNDM3fQ.eXxAUy0sA1E5sXf3Egr9hC5kl-hYF9ksXNhr8_Conxs")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Register Routes
app.include_router(init_auth_routes(supabase))
app.include_router(init_qr_routes(supabase), prefix="/qr", tags=["qr"])
app.include_router(init_metrics_routes(supabase), prefix="/metrics", tags=["metrics"])

@app.get("/")
def root():
    return {"status": "online", "environment": "localhost"}