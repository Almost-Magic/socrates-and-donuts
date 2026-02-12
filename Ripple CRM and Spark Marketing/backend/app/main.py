"""Ripple CRM v3 — FastAPI Application.

Made with love by Mani Padisetti @ Almost Magic Tech Lab
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.middleware.rate_limit import RateLimitMiddleware
from app.routers import (
    audit,
    channel_dna,
    companies,
    commitments,
    contacts,
    dashboard,
    deal_analytics,
    deals,
    health,
    import_export,
    interactions,
    lead_scoring,
    notes,
    privacy,
    relationships,
    settings as settings_router,
    tags,
    tasks,
    trust_decay,
    validation,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Relationship Intelligence Engine — Almost Magic Tech Lab",
    lifespan=lifespan,
)

app.add_middleware(RateLimitMiddleware, max_requests=200, window_seconds=60)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(companies.router, prefix="/api")
app.include_router(deals.router, prefix="/api")
app.include_router(interactions.router, prefix="/api")
app.include_router(interactions.timeline_router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(commitments.router, prefix="/api")
app.include_router(notes.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(relationships.router, prefix="/api")
app.include_router(privacy.router, prefix="/api")
app.include_router(import_export.router, prefix="/api")
app.include_router(settings_router.router, prefix="/api")
app.include_router(validation.router, prefix="/api")
app.include_router(audit.router, prefix="/api")
# Phase 2: Intelligence
app.include_router(tags.router, prefix="/api")
app.include_router(lead_scoring.router, prefix="/api")
app.include_router(lead_scoring.contact_router, prefix="/api")
app.include_router(channel_dna.router, prefix="/api")
app.include_router(channel_dna.contact_router, prefix="/api")
app.include_router(trust_decay.router, prefix="/api")
app.include_router(trust_decay.contact_router, prefix="/api")
app.include_router(deal_analytics.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Ripple CRM v3 — Relationship Intelligence Engine"}
