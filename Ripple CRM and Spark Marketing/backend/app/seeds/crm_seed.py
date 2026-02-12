"""Ripple CRM — Seed data: 15 Australian companies, 30 contacts, 20 deals,
15 interactions, 5 tasks.

All seed records are tagged with source='seed_data' (on contacts + deals)
so they can be identified and safely removed without touching real data.

Run:  cd backend && python -m app.seeds.crm_seed
Clear: cd backend && python -m app.seeds.crm_seed --clear
"""

import asyncio
import random
import sys
import uuid
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select, delete

from app.database import async_session
from app.models.channel_interaction import ChannelInteraction
from app.models.commitment import Commitment
from app.models.company import Company
from app.models.contact import Contact
from app.models.deal import Deal
from app.models.consent_preference import ConsentPreference
from app.models.dsar_request import DsarRequest
from app.models.email import Email
from app.models.interaction import Interaction
from app.models.lead_score import LeadScore
from app.models.meeting import Meeting, MeetingAction
from app.models.note import Note
from app.models.privacy_consent import PrivacyConsent
from app.models.pulse_action import PulseAction
from app.models.relationship import Relationship
from app.models.rep_forecast import RepForecastHistory
from app.models.tag import contact_tags
from app.models.task import Task

SEED_SOURCE = "seed_data"

# ── 15 Australian Companies ─────────────────────────────────────────

COMPANIES = [
    {
        "name": "Wattle AI Solutions Pty Ltd",
        "trading_name": "Wattle AI",
        "abn": "12 345 678 901",
        "industry": "Artificial Intelligence",
        "revenue": 2_500_000.0,
        "employee_count": 25,
        "website": "https://wattleai.com.au",
        "address": "Level 5, 100 Harris Street, Pyrmont",
        "city": "Sydney",
        "state": "NSW",
        "postcode": "2009",
    },
    {
        "name": "Banksia Consulting Group",
        "trading_name": "Banksia",
        "abn": "23 456 789 012",
        "industry": "Management Consulting",
        "revenue": 8_000_000.0,
        "employee_count": 80,
        "website": "https://banksiaconsulting.com.au",
        "address": "Level 12, 360 Collins Street",
        "city": "Melbourne",
        "state": "VIC",
        "postcode": "3000",
    },
    {
        "name": "Southern Cross Cyber Pty Ltd",
        "trading_name": "SXC",
        "abn": "34 567 890 123",
        "industry": "Cybersecurity",
        "revenue": 5_200_000.0,
        "employee_count": 45,
        "website": "https://southerncrosscyber.com.au",
        "address": "Suite 8, 20 Bridge Street",
        "city": "Sydney",
        "state": "NSW",
        "postcode": "2000",
    },
    {
        "name": "Harbour Digital Transformation",
        "trading_name": "Harbour Digital",
        "abn": "45 678 901 234",
        "industry": "Digital Transformation",
        "revenue": 15_000_000.0,
        "employee_count": 150,
        "website": "https://harbourdigital.com.au",
        "address": "Level 25, 1 Macquarie Place",
        "city": "Sydney",
        "state": "NSW",
        "postcode": "2000",
    },
    {
        "name": "Redgum Analytics",
        "trading_name": "Redgum",
        "abn": "56 789 012 345",
        "industry": "Data Analytics",
        "revenue": 3_200_000.0,
        "employee_count": 30,
        "website": "https://redgumanalytics.com.au",
        "address": "Level 3, 145 Eagle Street",
        "city": "Brisbane",
        "state": "QLD",
        "postcode": "4000",
    },
    {
        "name": "Ironbark Technologies Pty Ltd",
        "trading_name": "Ironbark Tech",
        "abn": "67 890 123 456",
        "industry": "Cloud Infrastructure",
        "revenue": 6_800_000.0,
        "employee_count": 60,
        "website": "https://ironbarktech.com.au",
        "address": "Level 8, 500 Bourke Street",
        "city": "Melbourne",
        "state": "VIC",
        "postcode": "3000",
    },
    {
        "name": "Cockatoo Financial Services",
        "trading_name": "Cockatoo Finance",
        "abn": "78 901 234 567",
        "industry": "Financial Technology",
        "revenue": 22_000_000.0,
        "employee_count": 200,
        "website": "https://cockatoofinance.com.au",
        "address": "Level 30, 200 George Street",
        "city": "Sydney",
        "state": "NSW",
        "postcode": "2000",
    },
    {
        "name": "Platypus Health Tech",
        "trading_name": "Platypus Health",
        "abn": "89 012 345 678",
        "industry": "Healthcare Technology",
        "revenue": 4_100_000.0,
        "employee_count": 35,
        "website": "https://platypushealth.com.au",
        "address": "Suite 2, 40 City Road, Southbank",
        "city": "Melbourne",
        "state": "VIC",
        "postcode": "3006",
    },
    {
        "name": "Barramundi Resources Group",
        "trading_name": "Barramundi",
        "abn": "90 123 456 789",
        "industry": "Mining Technology",
        "revenue": 45_000_000.0,
        "employee_count": 500,
        "website": "https://barramundiresources.com.au",
        "address": "Level 18, 240 Queen Street",
        "city": "Brisbane",
        "state": "QLD",
        "postcode": "4000",
    },
    {
        "name": "Kookaburra Creative Agency",
        "trading_name": "Kookaburra",
        "abn": "01 234 567 890",
        "industry": "Digital Marketing",
        "revenue": 1_800_000.0,
        "employee_count": 20,
        "website": "https://kookaburracreative.com.au",
        "address": "12 Fitzroy Street, Surry Hills",
        "city": "Sydney",
        "state": "NSW",
        "postcode": "2010",
    },
    {
        "name": "Jacaranda Education Pty Ltd",
        "trading_name": "Jacaranda Ed",
        "abn": "11 223 344 556",
        "industry": "Education Technology",
        "revenue": 3_800_000.0,
        "employee_count": 40,
        "website": "https://jacarandaed.com.au",
        "address": "Level 2, 88 Creek Street",
        "city": "Brisbane",
        "state": "QLD",
        "postcode": "4000",
    },
    {
        "name": "Bottlebrush Legal Tech",
        "trading_name": "Bottlebrush",
        "abn": "22 334 455 667",
        "industry": "Legal Technology",
        "revenue": 1_200_000.0,
        "employee_count": 15,
        "website": "https://bottlebrushlegal.com.au",
        "address": "Suite 4, 600 Lonsdale Street",
        "city": "Melbourne",
        "state": "VIC",
        "postcode": "3000",
    },
    {
        "name": "Grevillea Property Group",
        "trading_name": "Grevillea",
        "abn": "33 445 566 778",
        "industry": "Property Technology",
        "revenue": 9_500_000.0,
        "employee_count": 90,
        "website": "https://grevilleaproperty.com.au",
        "address": "Level 15, 60 Martin Place",
        "city": "Sydney",
        "state": "NSW",
        "postcode": "2000",
    },
    {
        "name": "Numbat Logistics Solutions",
        "trading_name": "Numbat",
        "abn": "44 556 677 889",
        "industry": "Supply Chain & Logistics",
        "revenue": 12_000_000.0,
        "employee_count": 120,
        "website": "https://numbatlogistics.com.au",
        "address": "Level 6, 125 St Georges Terrace",
        "city": "Perth",
        "state": "WA",
        "postcode": "6000",
    },
    {
        "name": "Waratah Defence Systems",
        "trading_name": "Waratah Defence",
        "abn": "55 667 788 990",
        "industry": "Defence Technology",
        "revenue": 35_000_000.0,
        "employee_count": 300,
        "website": "https://waratahdefence.com.au",
        "address": "Level 10, 33 Allara Street",
        "city": "Canberra",
        "state": "ACT",
        "postcode": "2601",
    },
]

# Company names used for identification during clear
SEED_COMPANY_NAMES = [c["name"] for c in COMPANIES]

# ── 30 Australian Contacts ──────────────────────────────────────────
# (company_idx references the COMPANIES list above)

CONTACTS = [
    # Wattle AI (0)
    {"first_name": "James", "last_name": "Mitchell", "email": "james.mitchell@wattleai.com.au", "phone": "0412 345 678", "role": "CEO", "title": "Chief Executive Officer", "type": "customer", "company_idx": 0},
    {"first_name": "Sarah", "last_name": "Chen", "email": "sarah.chen@wattleai.com.au", "phone": "0423 456 789", "role": "CTO", "title": "Chief Technology Officer", "type": "customer", "company_idx": 0},
    # Banksia Consulting (1)
    {"first_name": "David", "last_name": "Papadopoulos", "email": "david.p@banksiaconsulting.com.au", "phone": "0434 567 890", "role": "Managing Director", "title": "Managing Director", "type": "customer", "company_idx": 1},
    {"first_name": "Emma", "last_name": "Thompson", "email": "emma.t@banksiaconsulting.com.au", "phone": "0445 678 901", "role": "Head of Strategy", "title": "Head of Strategy", "type": "contact", "company_idx": 1},
    # Southern Cross Cyber (2)
    {"first_name": "Michael", "last_name": "Nguyen", "email": "michael.n@southerncrosscyber.com.au", "phone": "0456 789 012", "role": "CEO", "title": "Chief Executive Officer", "type": "contact", "company_idx": 2},
    {"first_name": "Rachel", "last_name": "Kumar", "email": "rachel.k@southerncrosscyber.com.au", "phone": "0467 890 123", "role": "CISO", "title": "Chief Information Security Officer", "type": "contact", "company_idx": 2},
    # Harbour Digital (3)
    {"first_name": "Andrew", "last_name": "Harris", "email": "andrew.h@harbourdigital.com.au", "phone": "0478 901 234", "role": "CEO", "title": "Chief Executive Officer", "type": "customer", "company_idx": 3},
    {"first_name": "Priya", "last_name": "Sharma", "email": "priya.s@harbourdigital.com.au", "phone": "0489 012 345", "role": "Head of Marketing", "title": "Head of Marketing", "type": "contact", "company_idx": 3},
    # Redgum Analytics (4)
    {"first_name": "Tom", "last_name": "O'Brien", "email": "tom.obrien@redgumanalytics.com.au", "phone": "0490 123 456", "role": "Director", "title": "Director", "type": "lead", "company_idx": 4},
    {"first_name": "Lisa", "last_name": "Tran", "email": "lisa.t@redgumanalytics.com.au", "phone": "0401 234 567", "role": "Data Science Lead", "title": "Data Science Lead", "type": "lead", "company_idx": 4},
    # Ironbark Technologies (5)
    {"first_name": "Mark", "last_name": "Rossetti", "email": "mark.r@ironbarktech.com.au", "phone": "0412 111 222", "role": "CTO", "title": "Chief Technology Officer", "type": "contact", "company_idx": 5},
    {"first_name": "Sophie", "last_name": "Williams", "email": "sophie.w@ironbarktech.com.au", "phone": "0423 222 333", "role": "Sales Director", "title": "Sales Director", "type": "contact", "company_idx": 5},
    # Cockatoo Financial (6)
    {"first_name": "Daniel", "last_name": "Lee", "email": "daniel.lee@cockatoofinance.com.au", "phone": "0434 333 444", "role": "CEO", "title": "Chief Executive Officer", "type": "customer", "company_idx": 6},
    {"first_name": "Jessica", "last_name": "Aboud", "email": "jessica.a@cockatoofinance.com.au", "phone": "0445 444 555", "role": "CFO", "title": "Chief Financial Officer", "type": "customer", "company_idx": 6},
    # Platypus Health (7)
    {"first_name": "Ben", "last_name": "Crawford", "email": "ben.c@platypushealth.com.au", "phone": "0456 555 666", "role": "COO", "title": "Chief Operating Officer", "type": "lead", "company_idx": 7},
    {"first_name": "Ming", "last_name": "Zhang", "email": "ming.z@platypushealth.com.au", "phone": "0467 666 777", "role": "Head of Product", "title": "Head of Product", "type": "lead", "company_idx": 7},
    # Barramundi Resources (8)
    {"first_name": "Chris", "last_name": "Walker", "email": "chris.w@barramundiresources.com.au", "phone": "0478 777 888", "role": "CEO", "title": "Chief Executive Officer", "type": "contact", "company_idx": 8},
    {"first_name": "Anika", "last_name": "Patel", "email": "anika.p@barramundiresources.com.au", "phone": "0489 888 999", "role": "Head of Innovation", "title": "Head of Innovation", "type": "contact", "company_idx": 8},
    # Kookaburra Creative (9)
    {"first_name": "Nick", "last_name": "Georgiou", "email": "nick.g@kookaburracreative.com.au", "phone": "0490 999 000", "role": "Creative Director", "title": "Creative Director", "type": "lead", "company_idx": 9},
    {"first_name": "Tara", "last_name": "McCarthy", "email": "tara.m@kookaburracreative.com.au", "phone": "0401 000 111", "role": "Account Director", "title": "Account Director", "type": "lead", "company_idx": 9},
    # Jacaranda Education (10)
    {"first_name": "Sam", "last_name": "Dimitriou", "email": "sam.d@jacarandaed.com.au", "phone": "0412 222 444", "role": "CEO", "title": "Chief Executive Officer", "type": "contact", "company_idx": 10},
    {"first_name": "Emily", "last_name": "Foster", "email": "emily.f@jacarandaed.com.au", "phone": "0423 333 555", "role": "Head of Curriculum", "title": "Head of Curriculum", "type": "contact", "company_idx": 10},
    # Bottlebrush Legal (11)
    {"first_name": "Ryan", "last_name": "Kim", "email": "ryan.k@bottlebrushlegal.com.au", "phone": "0434 444 666", "role": "Founder", "title": "Founder & CEO", "type": "lead", "company_idx": 11},
    {"first_name": "Charlotte", "last_name": "Brown", "email": "charlotte.b@bottlebrushlegal.com.au", "phone": "0445 555 777", "role": "Head of Operations", "title": "Head of Operations", "type": "lead", "company_idx": 11},
    # Grevillea Property (12)
    {"first_name": "Marcus", "last_name": "Taylor", "email": "marcus.t@grevilleaproperty.com.au", "phone": "0456 666 888", "role": "CEO", "title": "Chief Executive Officer", "type": "customer", "company_idx": 12},
    {"first_name": "Hannah", "last_name": "Singh", "email": "hannah.s@grevilleaproperty.com.au", "phone": "0467 777 999", "role": "Head of Technology", "title": "Head of Technology", "type": "customer", "company_idx": 12},
    # Numbat Logistics (13)
    {"first_name": "Luke", "last_name": "Henderson", "email": "luke.h@numbatlogistics.com.au", "phone": "0478 888 000", "role": "General Manager", "title": "General Manager", "type": "contact", "company_idx": 13},
    {"first_name": "Olivia", "last_name": "Moretti", "email": "olivia.m@numbatlogistics.com.au", "phone": "0489 999 111", "role": "Head of Supply Chain", "title": "Head of Supply Chain", "type": "contact", "company_idx": 13},
    # Waratah Defence (14)
    {"first_name": "Alex", "last_name": "Whitfield", "email": "alex.w@waratahdefence.com.au", "phone": "0490 000 222", "role": "Director", "title": "Director of Programs", "type": "contact", "company_idx": 14},
    {"first_name": "Deepa", "last_name": "Ramanathan", "email": "deepa.r@waratahdefence.com.au", "phone": "0401 111 333", "role": "Chief Scientist", "title": "Chief Scientist", "type": "contact", "company_idx": 14},
]

# ── 20 Deals ────────────────────────────────────────────────────────
# (contact_idx + company_idx reference the lists above)

DEALS = [
    # Closed Won (4)
    {"title": "Wattle AI - AI Governance Audit", "value": 45_000.0, "stage": "closed_won", "probability": 100, "contact_idx": 0, "company_idx": 0, "days_ago": 15, "close_days_ago": 5},
    {"title": "Harbour Digital - Enterprise AI Strategy", "value": 120_000.0, "stage": "closed_won", "probability": 100, "contact_idx": 6, "company_idx": 3, "days_ago": 40, "close_days_ago": 8},
    {"title": "Cockatoo Finance - Compliance Framework", "value": 85_000.0, "stage": "closed_won", "probability": 100, "contact_idx": 12, "company_idx": 6, "days_ago": 30, "close_days_ago": 3},
    {"title": "Grevillea Property - Data Strategy Workshop", "value": 25_000.0, "stage": "closed_won", "probability": 100, "contact_idx": 24, "company_idx": 12, "days_ago": 20, "close_days_ago": 2},
    # Closed Lost (2)
    {"title": "Barramundi - Digital Twin Pilot", "value": 200_000.0, "stage": "closed_lost", "probability": 0, "contact_idx": 16, "company_idx": 8, "days_ago": 35, "close_days_ago": 10},
    {"title": "Numbat Logistics - Route Optimisation PoC", "value": 65_000.0, "stage": "closed_lost", "probability": 0, "contact_idx": 26, "company_idx": 13, "days_ago": 25, "close_days_ago": 7},
    # Negotiation (3)
    {"title": "Southern Cross Cyber - Pen Test Programme", "value": 95_000.0, "stage": "negotiation", "probability": 70, "contact_idx": 4, "company_idx": 2, "days_ago": 14, "close_days_ago": None},
    {"title": "Banksia Consulting - AI Readiness Assessment", "value": 55_000.0, "stage": "negotiation", "probability": 65, "contact_idx": 2, "company_idx": 1, "days_ago": 10, "close_days_ago": None},
    {"title": "Waratah Defence - Secure AI Deployment", "value": 350_000.0, "stage": "negotiation", "probability": 50, "contact_idx": 28, "company_idx": 14, "days_ago": 20, "close_days_ago": None},
    # Proposal (4)
    {"title": "Ironbark Tech - Cloud Security Review", "value": 42_000.0, "stage": "proposal", "probability": 45, "contact_idx": 10, "company_idx": 5, "days_ago": 7, "close_days_ago": None},
    {"title": "Platypus Health - HIPAA Alignment Audit", "value": 38_000.0, "stage": "proposal", "probability": 40, "contact_idx": 14, "company_idx": 7, "days_ago": 5, "close_days_ago": None},
    {"title": "Jacaranda Ed - LMS AI Integration", "value": 72_000.0, "stage": "proposal", "probability": 55, "contact_idx": 20, "company_idx": 10, "days_ago": 8, "close_days_ago": None},
    {"title": "Cockatoo Finance - Phase 2 Automation", "value": 160_000.0, "stage": "proposal", "probability": 60, "contact_idx": 13, "company_idx": 6, "days_ago": 6, "close_days_ago": None},
    # Qualified (4)
    {"title": "Kookaburra Creative - AI Content Pipeline", "value": 28_000.0, "stage": "qualified", "probability": 30, "contact_idx": 18, "company_idx": 9, "days_ago": 4, "close_days_ago": None},
    {"title": "Bottlebrush Legal - Contract AI Review", "value": 35_000.0, "stage": "qualified", "probability": 25, "contact_idx": 22, "company_idx": 11, "days_ago": 3, "close_days_ago": None},
    {"title": "Redgum Analytics - ML Ops Setup", "value": 48_000.0, "stage": "qualified", "probability": 35, "contact_idx": 8, "company_idx": 4, "days_ago": 6, "close_days_ago": None},
    {"title": "Barramundi - Safety AI Monitoring", "value": 180_000.0, "stage": "qualified", "probability": 20, "contact_idx": 17, "company_idx": 8, "days_ago": 2, "close_days_ago": None},
    # Lead (3)
    {"title": "Numbat - Warehouse Automation Scoping", "value": 90_000.0, "stage": "lead", "probability": 10, "contact_idx": 27, "company_idx": 13, "days_ago": 1, "close_days_ago": None},
    {"title": "Wattle AI - Phase 2 Advisory Retainer", "value": 60_000.0, "stage": "lead", "probability": 15, "contact_idx": 1, "company_idx": 0, "days_ago": 2, "close_days_ago": None},
    {"title": "Harbour Digital - Board AI Briefing", "value": 18_000.0, "stage": "lead", "probability": 20, "contact_idx": 7, "company_idx": 3, "days_ago": 1, "close_days_ago": None},
]

# ── 15 Interactions (spread over last 30 days) ──────────────────────

INTERACTION_TYPES = ["email", "call", "meeting", "note"]

INTERACTIONS = [
    {"contact_idx": 0, "type": "email", "subject": "AI Governance audit follow-up", "content": "Thanks for the session last week, James. Attached is the preliminary findings report. Happy to walk through it next Tuesday.", "sentiment": 0.7, "days_ago": 2},
    {"contact_idx": 2, "type": "meeting", "subject": "AI Readiness kickoff meeting", "content": "Met with David and Emma at Banksia Collins St office. Discussed current AI maturity, key pain points around data governance. They want a formal proposal by end of week.", "sentiment": 0.6, "duration": 60, "days_ago": 5},
    {"contact_idx": 4, "type": "call", "subject": "Pen test programme scope discussion", "content": "Michael wants to expand scope to include cloud infrastructure. Needs board sign-off on the additional $30K. Will know by Friday.", "sentiment": 0.5, "duration": 25, "days_ago": 7},
    {"contact_idx": 6, "type": "email", "subject": "Enterprise AI Strategy - final deliverable", "content": "Andrew, please find the completed strategy document attached. It was a pleasure working with the Harbour Digital team.", "sentiment": 0.8, "days_ago": 9},
    {"contact_idx": 12, "type": "meeting", "subject": "Phase 2 automation planning", "content": "Walked through the compliance automation roadmap with Daniel and Jessica. Strong interest in proceeding. Jessica wants ROI projections before budget approval.", "sentiment": 0.7, "duration": 45, "days_ago": 3},
    {"contact_idx": 10, "type": "email", "subject": "Cloud security review proposal sent", "content": "Hi Mark, attached is our proposal for the cloud security review. We have included the hybrid-cloud assessment you requested. Look forward to your feedback.", "sentiment": 0.5, "days_ago": 6},
    {"contact_idx": 28, "type": "call", "subject": "Waratah Defence - security clearance requirements", "content": "Alex confirmed we need baseline clearance for the secure AI work. They will sponsor the application. Timeline: 6-8 weeks.", "sentiment": 0.4, "duration": 30, "days_ago": 12},
    {"contact_idx": 24, "type": "email", "subject": "Data strategy workshop recap", "content": "Marcus, thanks for hosting us at Martin Place. The team left energised. Workshop summary and next steps attached.", "sentiment": 0.9, "days_ago": 1},
    {"contact_idx": 20, "type": "meeting", "subject": "LMS AI integration discovery", "content": "Sam showed us the Jacaranda platform. Impressive content library. AI integration points are clear: content recommendations, adaptive learning paths, and assessment generation.", "sentiment": 0.6, "duration": 90, "days_ago": 8},
    {"contact_idx": 14, "type": "call", "subject": "HIPAA alignment requirements chat", "content": "Ben explained their US expansion plans. Need HIPAA alignment urgently before Q2 launch. Budget approved internally.", "sentiment": 0.7, "duration": 20, "days_ago": 4},
    {"contact_idx": 17, "type": "email", "subject": "Safety AI monitoring - initial brief", "content": "Anika, thanks for the mine-site walkthrough in Brisbane. Attached is our initial brief on AI-powered safety monitoring. The real-time alerting capability you described is exactly what we can deliver.", "sentiment": 0.6, "days_ago": 2},
    {"contact_idx": 22, "type": "call", "subject": "Contract AI review platform demo", "content": "Showed Ryan and Charlotte a quick demo of AI contract analysis. They were impressed with the clause extraction accuracy. Want to run a pilot with 50 sample contracts.", "sentiment": 0.8, "duration": 35, "days_ago": 3},
    {"contact_idx": 8, "type": "email", "subject": "ML Ops proposal discussion", "content": "Tom, great chat about the ML Ops challenges at Redgum. I think our phased approach makes sense for your team size. Will send the detailed proposal tomorrow.", "sentiment": 0.5, "days_ago": 5},
    {"contact_idx": 18, "type": "note", "subject": "Kookaburra Creative - internal note", "content": "Nick is keen but budget is tight. They are a small agency. Might work as a showcase project with reduced fee in exchange for a case study.", "sentiment": 0.3, "days_ago": 4},
    {"contact_idx": 7, "type": "email", "subject": "Board AI briefing - agenda draft", "content": "Priya, here is the draft agenda for the board briefing. I have structured it around the three themes Andrew mentioned: risk, opportunity, and governance.", "sentiment": 0.6, "days_ago": 1},
]

# ── 5 Tasks (due in next 7 days) ────────────────────────────────────

TASKS = [
    {"contact_idx": 2, "deal_idx": 7, "title": "[SEED] Send AI Readiness proposal to Banksia", "description": "David wants the proposal by Friday. Include pricing tiers and timeline options.", "due_days": 2, "priority": "high", "status": "todo"},
    {"contact_idx": 4, "deal_idx": 6, "title": "[SEED] Follow up on SXC board decision", "description": "Michael said the board meets Thursday. Call Friday morning for the outcome on expanded pen test scope.", "due_days": 3, "priority": "high", "status": "todo"},
    {"contact_idx": 13, "deal_idx": 12, "title": "[SEED] Prepare ROI projections for Cockatoo Phase 2", "description": "Jessica needs ROI numbers before she can get budget sign-off. Use the compliance automation benchmarks.", "due_days": 5, "priority": "medium", "status": "todo"},
    {"contact_idx": 28, "deal_idx": 8, "title": "[SEED] Submit security clearance application for Waratah", "description": "Alex is sponsoring. Complete the forms and submit via the portal. Timeline is critical.", "due_days": 7, "priority": "urgent", "status": "in_progress"},
    {"contact_idx": 22, "deal_idx": 14, "title": "[SEED] Send contract AI pilot scope to Bottlebrush", "description": "Ryan wants a pilot with 50 sample contracts. Draft the scope document with success criteria and timeline.", "due_days": 4, "priority": "medium", "status": "todo"},
]


# ── Load seed data ──────────────────────────────────────────────────

async def load_seed_data(db=None):
    """Create all seed records. Returns summary dict."""
    own_session = db is None
    if own_session:
        db = async_session()

    try:
        # Check if already loaded
        existing = (await db.execute(
            select(func.count()).select_from(
                select(Contact.id).where(Contact.source == SEED_SOURCE).subquery()
            )
        )).scalar() or 0
        if existing > 0:
            return {"error": f"Seed data already loaded ({existing} contacts). Clear first."}

        # 1. Companies
        company_ids = []
        for c in COMPANIES:
            company = Company(**c)
            db.add(company)
            await db.flush()
            company_ids.append(company.id)
        print(f"  Created {len(company_ids)} companies")

        # 2. Contacts
        contact_ids = []
        for c in CONTACTS:
            data = {k: v for k, v in c.items() if k != "company_idx"}
            data["company_id"] = company_ids[c["company_idx"]]
            data["source"] = SEED_SOURCE
            contact = Contact(**data)
            db.add(contact)
            await db.flush()
            contact_ids.append(contact.id)
        print(f"  Created {len(contact_ids)} contacts")

        # 3. Deals
        now = datetime.now(timezone.utc)
        today = date.today()
        deal_ids = []
        for d in DEALS:
            data = {
                "title": d["title"],
                "value": d["value"],
                "stage": d["stage"],
                "probability": d["probability"],
                "currency": "AUD",
                "source": SEED_SOURCE,
                "owner": "Mani Padisetti",
                "contact_id": contact_ids[d["contact_idx"]],
                "company_id": company_ids[d["company_idx"]],
                "expected_close_date": today + timedelta(days=30),
            }
            if d["close_days_ago"] is not None:
                data["actual_close_date"] = today - timedelta(days=d["close_days_ago"])
                data["expected_close_date"] = data["actual_close_date"]
            deal = Deal(**data)
            db.add(deal)
            await db.flush()
            deal_ids.append(deal.id)
        print(f"  Created {len(deal_ids)} deals")

        # 4. Interactions
        interaction_count = 0
        for ix in INTERACTIONS:
            data = {
                "contact_id": contact_ids[ix["contact_idx"]],
                "type": ix["type"],
                "subject": ix["subject"],
                "content": ix["content"],
                "sentiment_score": ix.get("sentiment"),
                "duration_minutes": ix.get("duration"),
                "occurred_at": now - timedelta(days=ix["days_ago"]),
            }
            interaction = Interaction(**data)
            db.add(interaction)
            interaction_count += 1
        print(f"  Created {interaction_count} interactions")

        # 5. Tasks
        task_count = 0
        for t in TASKS:
            data = {
                "contact_id": contact_ids[t["contact_idx"]],
                "deal_id": deal_ids[t["deal_idx"]],
                "title": t["title"],
                "description": t["description"],
                "due_date": today + timedelta(days=t["due_days"]),
                "priority": t["priority"],
                "status": t["status"],
            }
            task = Task(**data)
            db.add(task)
            task_count += 1
        print(f"  Created {task_count} tasks")

        await db.commit()
        summary = {
            "companies": len(company_ids),
            "contacts": len(contact_ids),
            "deals": len(deal_ids),
            "interactions": interaction_count,
            "tasks": task_count,
        }
        print(f"  Seed data loaded: {summary}")
        return summary

    except Exception as e:
        await db.rollback()
        raise
    finally:
        if own_session:
            await db.close()


# ── Clear seed data ─────────────────────────────────────────────────

async def get_seed_counts(db):
    """Return counts of seed vs real records."""
    # Seed contacts
    seed_contacts = (await db.execute(
        select(func.count()).select_from(
            select(Contact.id).where(
                Contact.source == SEED_SOURCE,
                Contact.is_deleted == False,  # noqa: E712
            ).subquery()
        )
    )).scalar() or 0

    # Real contacts
    real_contacts = (await db.execute(
        select(func.count()).select_from(
            select(Contact.id).where(
                (Contact.source != SEED_SOURCE) | (Contact.source == None),  # noqa: E711
                Contact.is_deleted == False,  # noqa: E712
            ).subquery()
        )
    )).scalar() or 0

    # Seed deals
    seed_deals = (await db.execute(
        select(func.count()).select_from(
            select(Deal.id).where(
                Deal.source == SEED_SOURCE,
                Deal.is_deleted == False,  # noqa: E712
            ).subquery()
        )
    )).scalar() or 0

    # Real deals
    real_deals = (await db.execute(
        select(func.count()).select_from(
            select(Deal.id).where(
                (Deal.source != SEED_SOURCE) | (Deal.source == None),  # noqa: E711
                Deal.is_deleted == False,  # noqa: E712
            ).subquery()
        )
    )).scalar() or 0

    # Seed companies (by name)
    seed_companies = (await db.execute(
        select(func.count()).select_from(
            select(Company.id).where(
                Company.name.in_(SEED_COMPANY_NAMES),
                Company.is_deleted == False,  # noqa: E712
            ).subquery()
        )
    )).scalar() or 0

    # Real companies
    real_companies = (await db.execute(
        select(func.count()).select_from(
            select(Company.id).where(
                Company.name.notin_(SEED_COMPANY_NAMES),
                Company.is_deleted == False,  # noqa: E712
            ).subquery()
        )
    )).scalar() or 0

    # Seed interactions (belonging to seed contacts)
    seed_contact_ids_q = select(Contact.id).where(Contact.source == SEED_SOURCE)
    seed_interactions = (await db.execute(
        select(func.count()).select_from(
            select(Interaction.id).where(
                Interaction.contact_id.in_(seed_contact_ids_q)
            ).subquery()
        )
    )).scalar() or 0

    # Seed tasks (with [SEED] prefix)
    seed_tasks = (await db.execute(
        select(func.count()).select_from(
            select(Task.id).where(
                Task.title.like("[SEED]%")
            ).subquery()
        )
    )).scalar() or 0

    return {
        "seed": {
            "companies": seed_companies,
            "contacts": seed_contacts,
            "deals": seed_deals,
            "interactions": seed_interactions,
            "tasks": seed_tasks,
        },
        "real": {
            "companies": real_companies,
            "contacts": real_contacts,
            "deals": real_deals,
        },
    }


async def clear_seed_data(db=None, confirm=False):
    """Delete only seed records. Returns summary of what was/would be deleted."""
    own_session = db is None
    if own_session:
        db = async_session()

    try:
        counts = await get_seed_counts(db)

        if not confirm:
            return {"dry_run": True, "would_delete": counts["seed"]}

        # Delete in FK-safe order — all child tables first, then parents
        seed_contact_ids_q = select(Contact.id).where(Contact.source == SEED_SOURCE)
        seed_deal_ids_q = select(Deal.id).where(Deal.source == SEED_SOURCE)
        seed_meeting_ids_q = select(Meeting.id).where(
            Meeting.contact_id.in_(seed_contact_ids_q)
        )

        # 1. Meeting actions (FK to meetings)
        await db.execute(
            delete(MeetingAction).where(
                MeetingAction.meeting_id.in_(seed_meeting_ids_q)
            )
        )
        # 2. Meetings
        await db.execute(
            delete(Meeting).where(Meeting.contact_id.in_(seed_contact_ids_q))
        )
        # 3. Rep forecast history (FK to deals)
        await db.execute(
            delete(RepForecastHistory).where(
                RepForecastHistory.deal_id.in_(seed_deal_ids_q)
            )
        )
        # 4. Pulse actions (FK to contacts/deals)
        await db.execute(
            delete(PulseAction).where(PulseAction.contact_id.in_(seed_contact_ids_q))
        )
        await db.execute(
            delete(PulseAction).where(PulseAction.deal_id.in_(seed_deal_ids_q))
        )
        # 5. Tasks
        await db.execute(
            delete(Task).where(Task.title.like("[SEED]%"))
        )
        await db.execute(
            delete(Task).where(Task.contact_id.in_(seed_contact_ids_q))
        )
        # 6. Commitments
        await db.execute(
            delete(Commitment).where(Commitment.contact_id.in_(seed_contact_ids_q))
        )
        await db.execute(
            delete(Commitment).where(Commitment.deal_id.in_(seed_deal_ids_q))
        )
        # 7. Interactions
        await db.execute(
            delete(Interaction).where(Interaction.contact_id.in_(seed_contact_ids_q))
        )
        # 8. Channel interactions
        await db.execute(
            delete(ChannelInteraction).where(
                ChannelInteraction.contact_id.in_(seed_contact_ids_q)
            )
        )
        # 9. Emails
        await db.execute(
            delete(Email).where(Email.contact_id.in_(seed_contact_ids_q))
        )
        # 10. Notes
        await db.execute(
            delete(Note).where(Note.contact_id.in_(seed_contact_ids_q))
        )
        await db.execute(
            delete(Note).where(Note.deal_id.in_(seed_deal_ids_q))
        )
        # 11. Lead scores
        await db.execute(
            delete(LeadScore).where(LeadScore.contact_id.in_(seed_contact_ids_q))
        )
        # 12. Relationships
        await db.execute(
            delete(Relationship).where(
                Relationship.contact_id.in_(seed_contact_ids_q)
            )
        )
        # 13. Privacy consents
        await db.execute(
            delete(PrivacyConsent).where(
                PrivacyConsent.contact_id.in_(seed_contact_ids_q)
            )
        )
        # 14. DSAR requests
        await db.execute(
            delete(DsarRequest).where(
                DsarRequest.contact_id.in_(seed_contact_ids_q)
            )
        )
        # 14b. Consent preferences
        await db.execute(
            delete(ConsentPreference).where(
                ConsentPreference.contact_id.in_(seed_contact_ids_q)
            )
        )
        # 15. Contact-tag associations
        await db.execute(
            contact_tags.delete().where(
                contact_tags.c.contact_id.in_(seed_contact_ids_q)
            )
        )
        # 16. Deals
        await db.execute(
            delete(Deal).where(Deal.source == SEED_SOURCE)
        )
        # 17. Contacts
        await db.execute(
            delete(Contact).where(Contact.source == SEED_SOURCE)
        )
        # 18. Companies
        await db.execute(
            delete(Company).where(Company.name.in_(SEED_COMPANY_NAMES))
        )

        await db.commit()
        return {"dry_run": False, "deleted": counts["seed"]}

    except Exception as e:
        await db.rollback()
        raise
    finally:
        if own_session:
            await db.close()


# ── CLI entry point ─────────────────────────────────────────────────

async def main():
    if "--clear" in sys.argv:
        confirm = "--confirm" in sys.argv
        print("Clearing seed data...")
        result = await clear_seed_data(confirm=confirm)
        if result.get("dry_run"):
            print(f"DRY RUN - would delete: {result['would_delete']}")
            print("Run with --clear --confirm to actually delete.")
        else:
            print(f"Deleted: {result['deleted']}")
    elif "--status" in sys.argv:
        async with async_session() as db:
            counts = await get_seed_counts(db)
            print(f"Seed records: {counts['seed']}")
            print(f"Real records: {counts['real']}")
    else:
        print("Loading seed data...")
        result = await load_seed_data()
        if "error" in result:
            print(f"ERROR: {result['error']}")
        else:
            print(f"Done: {result}")


if __name__ == "__main__":
    asyncio.run(main())
