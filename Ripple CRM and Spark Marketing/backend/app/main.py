"""Ripple CRM v3 — FastAPI Application.

Made with love by Mani Padisetti @ Almost Magic Tech Lab
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.middleware.rate_limit import RateLimitMiddleware
from app.routers import (
    attention_allocation,
    audit,
    channel_dna,
    channel_interactions,
    commute_briefing,
    companies,
    rep_bias,
    commitments,
    contacts,
    dashboard,
    deal_analytics,
    deals,
    emails,
    health,
    import_export,
    interactions,
    lead_scoring,
    meetings,
    notes,
    privacy,
    pulse,
    relationships,
    scoring_rules,
    seed_data,
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
app.include_router(privacy.contact_router, prefix="/api")
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
# Phase 2.2: Channel DNA v1 Enhancement
app.include_router(channel_interactions.router, prefix="/api")
app.include_router(channel_interactions.contact_router, prefix="/api")
# Phase 2b: Email Integration + Scoring Rules
app.include_router(emails.router, prefix="/api")
app.include_router(emails.contact_router, prefix="/api")
app.include_router(emails.deal_router, prefix="/api")
app.include_router(scoring_rules.router, prefix="/api")
# Phase 2.1: Meeting Intelligence Hub
app.include_router(meetings.router, prefix="/api")
app.include_router(meetings.contact_router, prefix="/api")
app.include_router(meetings.deal_router, prefix="/api")
# Phase 2.4: Rep Bias Brain
app.include_router(rep_bias.router, prefix="/api")
app.include_router(rep_bias.deal_router, prefix="/api")
# Phase 2.3: Commute Briefing
app.include_router(commute_briefing.router, prefix="/api")
app.include_router(commute_briefing.meeting_router, prefix="/api")
app.include_router(commute_briefing.contact_router, prefix="/api")
# Phase 2.5: Attention Allocation Engine
app.include_router(attention_allocation.router, prefix="/api")
app.include_router(attention_allocation.contact_router, prefix="/api")
# Phase 3: Pulse — Sales Intelligence
app.include_router(pulse.router, prefix="/api")
# Seed data management
app.include_router(seed_data.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Ripple CRM v3 — Relationship Intelligence Engine"}
