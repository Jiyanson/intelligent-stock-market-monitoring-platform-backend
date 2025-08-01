from fastapi import FastAPI
from app.api.routes import ping

app = FastAPI(title="Real-Time & Intelligent Stock Market Monitoring Platform")

app.include_router(ping.router, prefix="/api")