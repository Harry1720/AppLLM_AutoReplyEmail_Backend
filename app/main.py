from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth_router import router as auth_router
from app.api.email_router import email_router
from app.api.user_router import user_router
from app.api.ai_router import ai_router
import logging
import asyncio

app = FastAPI(
    title="My AutoReplyEmail App",
    description="Demo AutoReplyEmail with Swagger UI",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event():
    """Schedule background preload of AI models to prioritize fast startup."""
    app.state.model_loaded = False
    logging.info("Server starting - scheduling background preload of AI models...")

    async def _preload():
        from app.infra.ai.reasoning import get_embeddings_model
        logging.info("Background: Loading Embeddings Model...")
        try:
            await asyncio.to_thread(get_embeddings_model)
            app.state.model_loaded = True
            logging.info("Background: AI models loaded and ready!")
        except Exception as e:
            logging.error(f"Background preload failed: {e}")

    asyncio.create_task(_preload())

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://harrydev-autoreplyemail.vercel.app/"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(auth_router)
app.include_router(email_router, tags=["Email Management"])
app.include_router(user_router, tags=["User Profile"])
app.include_router(ai_router, tags=["AI Agents"])


@app.get("/")
def read_root():
    return {"message": "Hello FastAPI"}


@app.get('/health')
def health():
    return {"status": "ok"}


@app.get('/ready')
def ready():
    return {"ready": bool(getattr(app.state, 'model_loaded', False))}