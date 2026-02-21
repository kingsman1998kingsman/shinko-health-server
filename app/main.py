import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.routes.qr import router as qr_router

load_dotenv()

app = FastAPI()

# ===== CORS (because phone/tablet are different domains) =====
ALLOWED_ORIGINS = [
    os.getenv("PHONE_ORIGIN", "https://shinko-health-phone-production.up.railway.app"),
    os.getenv("TABLET_ORIGIN", "https://shinko-health-tablet-production.up.railway.app"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Routes =====
app.include_router(qr_router, prefix="/qr", tags=["qr"])

@app.get("/")
def root():
    return {"message": "Server is running"}