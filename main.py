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
        "https://shinko-health-mobile.netlify.app",
        "https://shinko-health-tablet.netlify.app",
        "http://localhost:5500",  # Add this for local testing
        "http://127.0.0.1:5500",  # Add this for local testing
        "http://localhost:5501",  # Add this for local testing
        "http://127.0.0.1:5501",  # Add this for local testing
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Replace these with your actual Supabase credentials for local testing
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://masjsqdopdecrvjnsyrf.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1hc2pzcWRvcGRlY3J2am5zeXJmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE2ODQ1NjQsImV4cCI6MjA4NzI2MDU2NH0.CIQneYtGVLtkY5SnDkZsKSYNT7qP_eS72J9P3nfBt0M")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Register Routes
app.include_router(init_auth_routes(supabase))
app.include_router(init_qr_routes(supabase), prefix="/qr", tags=["qr"])
app.include_router(init_metrics_routes(supabase), prefix="/metrics", tags=["metrics"])

@app.get("/")
def root():
    return {"status": "online", "environment": "localhost"}