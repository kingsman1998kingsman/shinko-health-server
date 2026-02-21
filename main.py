from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.qr import router as qr_router

app = FastAPI()

# ✅ Allow Netlify origins (your error shows mobile is netlify)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://shinko-health-mobile.netlify.app",
        "https://shinko-health-tablet.netlify.app",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(qr_router, prefix="/qr", tags=["qr"])

@app.get("/")
def root():
    return {"message": "Server is running"}