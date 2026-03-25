from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import init_db
from app.routers import document

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="AI-powered tool that simplifies complex legal and medical documents into plain language.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Allow Streamlit frontend and local dev to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(document.router, prefix="/api/v1", tags=["Documents"])


@app.on_event("startup")
def on_startup():
    init_db()
    s = get_settings()
    key = s.groq_api_key
    masked = (key[:6] + "..." + key[-4:]) if len(key) > 10 else f"(empty: len={len(key)})"
    print(f"[WORKER-STARTUP] ai_provider  = {s.ai_provider}", flush=True)
    print(f"[WORKER-STARTUP] groq_model   = {s.groq_model}", flush=True)
    print(f"[WORKER-STARTUP] groq_api_key = {masked}", flush=True)


@app.get("/debug-settings", tags=["Health"])
def debug_settings():
    s = get_settings()
    key = s.groq_api_key
    masked = (key[:6] + "..." + key[-4:]) if len(key) > 10 else f"(empty: len={len(key)})"
    return {
        "ai_provider": s.ai_provider,
        "groq_model": s.groq_model,
        "groq_api_key_masked": masked,
        "google_api_key_len": len(s.google_api_key),
    }


@app.get("/", tags=["Health"])
def root():
    return {"message": f"Welcome to {settings.app_name} API", "docs": "/docs"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
