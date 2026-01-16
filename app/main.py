from fastapi import FastAPI
from app.routers.analyze import router as analyze_router

app = FastAPI(title="Wannatrack AI Receipt Analyzer")

app.include_router(analyze_router)