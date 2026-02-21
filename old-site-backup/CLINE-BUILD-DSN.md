# DIGITAL SENTINEL BUILD INSTRUCTION — PASTE INTO CLINE
# Date: 19 February 2026
# App: Digital Sentinel — Managed Cyber Intelligence for Australian SMBs
# Builder: Guruve (Cline)

You are Guruve — the operational build agent for Almost Magic Tech Lab.
You are building Digital Sentinel (DS), a managed cybersecurity intelligence
service for Australian small and mid-sized businesses.

---

## WHAT DS IS (Read This First — It Shapes Everything)

Digital Sentinel is NOT a self-service security platform. It is a
MANAGED SERVICE. The customer pays, AMTL runs the scans, the customer
receives professional intelligence reports. The customer never touches
a scanning tool.

The founder, Mani Padisetti, built this because Australian SMBs are
told they need cybersecurity but the solutions available are either
too expensive ($30K+ annual enterprise platforms) or too shallow
(a simple scan that tells you nothing useful). DS sits in between.

KEY PRINCIPLE: The No-Login Principle. DS never logs into the customer's
network. Everything is assessed externally — the way an attacker would
see it. The customer provides a domain name and that's all.

---

## PRE-BUILD: Check for Previous Build

Before creating ANYTHING, check if a previous DS build exists:

```
# Check if repo exists locally
dir digital-sentinel\ 2>nul
ls -la ~/digital-sentinel/ 2>/dev/null

# Check for existing remote
git ls-remote https://github.com/Almost-Magic/digital-sentinel.git 2>/dev/null

# Check if ports are occupied
netstat -ano | findstr "3020 3021"

# Check for old databases
psql -U postgres -c "SELECT datname FROM pg_database WHERE datname LIKE '%sentinel%';" 2>nul

# Check for old Docker containers
docker ps -a | findstr sentinel 2>nul
```

If a previous build exists:
- Stop any running DS processes
- Kill anything on ports 3020 and 3021
- Back up old folder: rename to digital-sentinel-backup-YYYYMMDD
- Do NOT delete old databases without Mani's approval
- Verify ports 3020 and 3021 are free

Only proceed once the workspace is confirmed clean.

---

## CRITICAL RULES — MEMORISE THESE

```
┌──────────────────────────────────────────────────────────────┐
│  1. AUSTRALIAN ENGLISH everywhere. Code, comments, UI, copy, │
│     reports, prompts, README. "Colour" not "color".          │
│     "Organisation" not "organization".                       │
│                                                              │
│  2. BANNED PHRASES — never in user-facing text:              │
│     game-changer, level up, crushing it, awesome, check it   │
│     out (use "have a look"), gotten (use "got"), reach out   │
│     (use "get in touch"), touch base, circle back, utilize   │
│     (use "use"), oftentimes (use "often"), super excited,    │
│     guys, unlock your potential, disrupt, 10x.               │
│                                                              │
│  3. DARK THEME DEFAULT — Midnight #0A0E14, Gold #C9944A     │
│     accent. Dark/light toggle. Tailwind CSS. Lucide icons.   │
│                                                              │
│  4. PORTS: 3020 (Customer Portal), 3021 (Operator Dashboard) │
│     Repository: Almost-Magic/digital-sentinel                │
│                                                              │
│  5. NO PAID AI API COSTS PER SCAN. All AI inference uses     │
│     Claude Desktop CLI (Max Pro subscription — fixed cost)   │
│     or Ollama via Supervisor (:9000). Never cloud API per    │
│     scan.                                                    │
│                                                              │
│  6. FLASK binds to 127.0.0.1 ONLY. Never 0.0.0.0.           │
│     DS is not exposed to the network.                        │
│                                                              │
│  7. NO FAKE TESTIMONIALS. No fabricated social proof. Ever.  │
│     Trust through: free risk grade, sample report,           │
│     money-back guarantee, educational content, Mani's brand. │
│                                                              │
│  8. NO AI-GENERATED IMAGES. Lucide icons only.               │
│                                                              │
│  9. CUSTOMER DATA ISOLATION. No cross-customer data leakage. │
│     Each customer's findings, reports, and portal are        │
│     completely separate.                                     │
│                                                              │
│ 10. EVERY PHASE ENDS WITH TESTS. No exceptions.              │
│                                                              │
│ 11. ALL TOOL OUTPUT goes through the Evidence Bus before      │
│     reaching Neo4j, reports, or AI narrative generation.     │
│                                                              │
│ 12. NEVER scan a domain without customer consent + payment.  │
│     Exception: free risk grade (consent checkbox required).  │
│                                                              │
│ 13. ELECTRON DESKTOP WRAPPER required for Operator Dashboard.│
│     Customer Portal is web-only (accessed via browser).      │
└──────────────────────────────────────────────────────────────┘
```

---

## ARCHITECTURE OVERVIEW

```
                    ┌─────────────────────┐
                    │   Website           │
                    │   (Static/Flask)    │
                    │   digitalsentinel   │
                    │   .com.au           │
                    └────────┬────────────┘
                             │ Stripe webhook
                             ▼
                    ┌─────────────────────┐
                    │   n8n               │
                    │   Workflow Engine   │
                    │   (:5678)          │
                    └────────┬────────────┘
                             │ Creates job
                             ▼
┌───────────────────────────────────────────────────────────┐
│                OPERATOR DASHBOARD (:3021)                  │
│  Job Queue → Scan Runner → Report Review → Delivery       │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              SCAN ENGINE                             │ │
│  │                                                     │ │
│  │  ┌──────────┐   ┌──────────┐   ┌──────────────┐   │ │
│  │  │ Layer 1  │   │ Layer 2  │   │ Layer 5      │   │ │
│  │  │ Surface  │   │ Code     │   │ AI Security  │   │ │
│  │  │ 30+ tools│   │ Security │   │ Garak,PyRIT  │   │ │
│  │  └────┬─────┘   └────┬─────┘   └──────┬───────┘   │ │
│  │       │              │                 │           │ │
│  │       ▼              ▼                 ▼           │ │
│  │  ┌────────────────────────────────────────────┐   │ │
│  │  │           EVIDENCE BUS                     │   │ │
│  │  │  Universal normalisation layer             │   │ │
│  │  │  All tool output → unified JSON schema     │   │ │
│  │  └────────────────────┬───────────────────────┘   │ │
│  │                       │                           │ │
│  │       ┌───────────────┼───────────────┐           │ │
│  │       ▼               ▼               ▼           │ │
│  │  ┌─────────┐   ┌──────────┐   ┌────────────┐    │ │
│  │  │Risk     │   │  Neo4j   │   │ AI Narrative│    │ │
│  │  │Brain    │   │  Graph   │   │ Engine      │    │ │
│  │  │(scoring)│   │(attack   │   │(Claude/     │    │ │
│  │  │         │   │ paths)   │   │ Ollama)     │    │ │
│  │  └────┬────┘   └────┬─────┘   └─────┬──────┘    │ │
│  │       │              │               │           │ │
│  │       ▼              ▼               ▼           │ │
│  │  ┌────────────────────────────────────────────┐   │ │
│  │  │         REPORT GENERATOR                   │   │ │
│  │  │  PDF + HTML + PPTX + MP3 (Voicebox)       │   │ │
│  │  └────────────────────────────────────────────┘   │ │
│  └─────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────┘
                             │ Reports delivered
                             ▼
┌───────────────────────────────────────────────────────────┐
│                CUSTOMER PORTAL (:3020)                     │
│  Dashboard → Findings → Actions → Reports                 │
└───────────────────────────────────────────────────────────┘
```

---

## NAVIGATION — Keep It Simple

### Website (digitalsentinel.com.au): 4 items + CTA
```
[DS Logo]  Digital Sentinel     [Services]  [Sample Report]  [About]  [Get Started →]
```

### Customer Portal: 4 items
```
[DS Logo]  My Report     [Dashboard]  [Findings]  [Actions]  [Reports ▼]
```
- Dashboard = "How bad is it?"
- Findings = "What specifically?"
- Actions = "What do I do about it?"
- Reports = "What do I download/share?"

### Operator Dashboard: 4 items
```
[DS Logo]  Operator     [Jobs]  [Scan Runner]  [Delivery]  [Analytics]
```

---

## SERVICE TIERS & PRICING

| Service | Price | Customer Provides | Turnaround |
|---------|-------|------------------|------------|
| Quick Scan | $500-$999 | Domain name | 24-48 hrs |
| Comprehensive Scan | $2,500-$4,999 | Domain name | 3-5 days |
| Third-Party Risk | $1,500-$2,999 | Domain name | 3-5 days |
| AI Security Assessment | $1,999-$4,999 | AI/chatbot URL | 3-5 days |
| Dark Web Exposure | $499-$999 | Domain + emails | 24-48 hrs |
| Deepfake Analysis | $299-$799/item | Suspicious file | 24-48 hrs |
| Emergency Assessment | $1,500-$2,500 | Domain name | Same day |
| Post-Incident Verification | $999 | Domain name | 24-48 hrs |
| Board-Ready Review | $7,500-$9,999 | Domain + AI URLs | 5-7 days |

Add-ons: Voice Briefing (+$200), Quarterly Re-Scan (70%), Compliance Deep-Dive (+$500/framework), Full E8 (+$1,500-$2,500), Full CPS 234/ISO (+$2,500-$4,999).

---

## CUSTOMER CONFIDENCE STRATEGY (No Fake Testimonials)

Build these trust mechanisms into the product:

1. FREE RISK GRADE (Lead Magnet)
   Stripped-down scan: risk grade A-F, top 3 finding titles (not details),
   email security pass/fail. 15 minutes to run. Customer provides domain only.
   Needs its own scan playbook and website form.

2. SAMPLE REPORT (Downloadable)
   Real anonymised comprehensive report. PDF on website. Shows exactly
   what the customer is paying for.

3. MONEY-BACK GUARANTEE
   "If your report contains no actionable findings, you pay nothing."
   Stripe auto-refund when operator marks "No Actionable Findings".

4. FREE CREDITS (Cross-Sell)
   $200 off Comprehensive after Quick Scan. $499 toward AI Security
   after any paid scan. $250 for referrals. Free Dark Web check with
   any paid scan during launch period (first 6 months).

5. EDUCATIONAL CONTENT
   "State of AU SMB Cyber Risk" annual report. Blog posts. Anonymised
   case studies.

6. MANI AS TRUST SIGNAL
   Short video on website. Real person, real expertise, real background.

---

## 49 SCANNING TOOLS — 5-LAYER ARCHITECTURE

### Layer 1: Surface Scan (30+ tools)
Reconnaissance: Subfinder, httpx, Naabu, Amass, Masscan
Vulnerability: Nuclei, Nikto, OWASP ZAP, WPScan, SQLMap, WhatWeb
OSINT: SpiderFoot, theHarvester, Recon-ng, Maltego CE, Photon
Intelligence: Shodan CLI, Censys CLI, SecurityTrails, URLScan.io, VirusTotal
DNS: dnsrecon, Fierce, DNSTwist
Credentials: truffleHog, GitLeaks, h8mail, HIBP
Dark Web: Tor, Ahmia, OnionSearch
People OSINT: Sherlock, Holehe
Google Dorking: Pagodo, Dorkbot

### Layer 2: Code Security
Semgrep, Trivy

### Layer 3: Penetration Testing
Decepticon + future tools (under evaluation)

### Layer 4: Incident Response
Aurora IR (limited scope — external scan + disclosure templates)

### Layer 5: AI Security
Garak, DeepTeam, Promptfoo, PyRIT

### Cross-Cutting: Deepfake Detection
Resemblyzer, FaceForensics++ models

### Infrastructure
Evidence Bus, Risk Brain, Voicebox (voice briefings), Audit Trail

ALL tool output flows through the Evidence Bus. No exceptions.

---

## EVIDENCE BUS — Universal Normalisation

The Evidence Bus is the core infrastructure component. Every tool's output
passes through it into a universal JSON schema before reaching anything
downstream.

```json
{
  "finding_id": "uuid",
  "source_tool": "nuclei",
  "timestamp": "2026-02-19T10:30:00Z",
  "target": "example.com",
  "category": "vulnerability",
  "severity": "critical",
  "title": "SQL Injection on /login",
  "description": "...",
  "evidence": { "screenshot": "...", "raw_output": "..." },
  "cvss": 9.8,
  "cve": "CVE-2024-XXXXX",
  "compliance": {
    "essential_eight": ["application_hardening"],
    "cps_234": ["14.1"],
    "iso_27001": ["A.14.2.5"]
  },
  "remediation": {
    "steps": ["..."],
    "effort": "medium",
    "priority": 1
  }
}
```

Build parsers for EVERY tool's output format. If a new tool is added,
a new parser must be written for the Evidence Bus.

---

## RISK BRAIN — Proprietary Scoring

Formula: Exposure × Exploitability × Business Criticality × Cascade Potential

Additional factors:
- AI context weighting (Claude/Ollama analyses context)
- Supply chain depth multiplier
- Historical recurrence
- Compliance impact factor

Output: 0-100 score + A-F letter grade + per-category scores.

This is proprietary IP. Do not use CVSS as the sole scoring mechanism.
CVSS is an input to Risk Brain, not a replacement for it.

---

## COMPLIANCE MAPPING ENGINE

Every finding is mapped to applicable controls in:
- Essential Eight (8 strategies)
- CPS 234 (APRA)
- SOCI Act (Critical Infrastructure)
- Privacy Act 1988 / APPs
- ISO 27001 (Annex A controls)
- ISO 42001 (for AI Security assessments)
- NIST AI RMF (for AI Security assessments)
- NIST CSF (supplementary)

Build a mapping table: finding_category → applicable controls.
The compliance dashboard reads from this mapping.

---

## SCAN PLAYBOOKS

See AMTL-DSN-RUN-1.0 for complete playbooks. Summary:

### Quick Scan (12 steps)
Subfinder → httpx → Nmap → Nuclei (crit/high) → DNS checks → SSL scan →
Evidence Bus → Risk Brain → Claude narrative → Report → Review → Deliver

### Comprehensive Scan (28 steps)
Everything in Quick Scan + Amass, Naabu, Nikto, ZAP, WPScan, dnsrecon,
SpiderFoot, theHarvester, Pagodo, DNSTwist, VirusTotal, HIBP, h8mail,
truffleHog, GitLeaks, Tor/Ahmia/OnionSearch, Sherlock, Holehe →
Evidence Bus → Risk Brain → Compliance mapping → Neo4j import →
Claude narrative (4 reports) → Voicebox → Email templates → Review → Deliver

### AI Security Assessment (12 steps)
Verify endpoint → Garak → DeepTeam → Promptfoo → PyRIT →
Evidence Bus → Risk Brain → Compliance mapping (ISO 42001, NIST AI RMF) →
Claude narrative → Report → Review → Deliver

---

## DATABASE

### PostgreSQL + TimescaleDB
- customers, jobs, findings, compliance_mappings, reports, audit_log,
  email_templates, vendor_risk, subscriptions, credits, scans, users

### Neo4j
- Attack graph: assets (nodes) → connections/attack paths (edges)
- Supply chain graph: customer → vendors → vendor dependencies

---

## API KEY ENVIRONMENT VARIABLES

```
# Digital Sentinel
AMTL_DSN_STRIPE_KEY=
AMTL_DSN_STRIPE_WEBHOOK_SECRET=
AMTL_DSN_WPSCAN_TOKEN=           # 25 requests/day (free)
AMTL_DSN_SHODAN_KEY=             # Mani has obtained this
AMTL_DSN_CENSYS_ID=
AMTL_DSN_CENSYS_SECRET=
AMTL_DSN_SECURITYTRAILS_KEY=     # 50 queries/month (free)
AMTL_DSN_URLSCAN_KEY=            # 1000 scans/day (free)
AMTL_DSN_VT_KEY=                 # VirusTotal
AMTL_DSN_HIBP_KEY=               # Have I Been Pwned

# Database
AMTL_DSN_POSTGRES_URL=postgresql://sentinel:password@localhost:5433/digital_sentinel
AMTL_DSN_NEO4J_URL=bolt://localhost:7687
AMTL_DSN_NEO4J_USER=neo4j
AMTL_DSN_NEO4J_PASSWORD=

# AI
AMTL_DSN_OLLAMA_URL=http://localhost:9000
AMTL_DSN_CLAUDE_CLI=claude

# Email / Notifications
AMTL_DSN_SMTP_HOST=
AMTL_DSN_SMTP_PORT=
AMTL_DSN_SMTP_USER=
AMTL_DSN_SMTP_PASSWORD=
AMTL_DSN_FROM_EMAIL=support@digitalsentinel.com.au
```

---

## REFERENCE DOCUMENTS

Read these documents before writing any code:

1. /docs/AMTL-ECO-STD-1.0.md — Engineering standards (the constitution)
2. /docs/AMTL-DSN-SPC-4.1.md — Product specification (services, architecture, pricing, trust strategy)
3. /docs/AMTL-DSN-TDD-1.0.md — Technical design (database, API, Evidence Bus, Risk Brain)
4. /docs/AMTL-DSN-BLD-1.0.md — Build guide (16 phases with test checkpoints)
5. /docs/AMTL-DSN-DEC-1.0.md — Decisions already made (20 decisions — don't re-debate)
6. /docs/AMTL-DSN-RUN-1.0.md — Operations runbook (scan playbooks, health checks, backup)
7. /docs/AMTL-DSN-KNW-1.0.md — Known issues (9 known limitations)
8. /docs/AMTL-DSN-MRD-1.0.md — Machine-readable diagnostics (7 diagnostic trees)
9. /docs/AMTL-DSN-WEB-1.0.md — Website copy (use this exact text)
10. /docs/AMTL-DSN-UI-1.1.md — Wireframes (13 screens — follow these layouts)
11. /docs/AMTL-ECO-EXT-1.3-DSTOOLS.md — All 49 tools inventory

---

## BUILD ORDER

Follow the phases in AMTL-DSN-BLD-1.0.md. Summary:

| Phase | What | Key Deliverables |
|-------|------|-----------------|
| 0 | Environment setup | PRE-BUILD CHECK, repo, Flask on :3020/:3021, PostgreSQL, Neo4j, .env, health endpoints |
| 1 | Evidence Bus + Risk Brain | Universal JSON schema, tool output parsers, scoring algorithm |
| 2 | Operator Dashboard — Job Management | Job queue, job detail, status tracking, Stripe webhook receiver |
| 3 | Scan Engine — Quick Scan Playbook | Tool orchestration, sequential execution, logging |
| 4 | Scan Engine — Comprehensive Playbook | All 28 steps, additional tools integrated |
| 5 | AI Narrative Engine | Claude/Ollama integration, report narrative generation, system prompts |
| 6 | Report Generator | PDF, HTML, PPTX generation from normalised data + narratives |
| 7 | Customer Portal | Dashboard, findings, actions, reports dropdown, email templates |
| 8 | Neo4j Attack Graph | Graph population from Evidence Bus, D3.js visualisation |
| 9 | Compliance Mapping Engine | Framework mapping table, compliance dashboard, gap analysis |
| 10 | AI Security Assessment | Garak, DeepTeam, Promptfoo, PyRIT integration, ISO 42001 mapping |
| 11 | Deepfake & Impersonation Analysis | Resemblyzer integration, analysis pipeline |
| 12 | Stripe + n8n Integration | Payment flow, webhooks, job auto-creation, notification emails |
| 13 | Free Risk Grade + Trust Mechanisms | Free scan playbook, sample report, credits, guarantee |
| 14 | Website | 5 pages using copy from AMTL-DSN-WEB-1.0.md, Stripe checkout |
| 15 | Electron Wrapper for Operator Dashboard | Desktop app, system tray, Workshop registration |
| 16 | Polish, Security Hardening, Final Tests | A11y, penetration test own app, full test suite |

IMPORTANT: Phase 0 MUST include the PRE-BUILD cleanup check.
IMPORTANT: Phase 1 (Evidence Bus) is the foundation — everything depends on it.
IMPORTANT: Phase 15 (Electron) is NOT optional.

---

## TESTING MANDATE

Every phase must pass:

| Test | What |
|------|------|
| Beast | Core functionality, happy paths |
| Inspector | Zero lint warnings, clean code |
| 4% | Edge cases — empty input, huge input, special chars, malformed tool output |
| Proof | Screenshots matching wireframes (AMTL-DSN-UI-1.1) |
| Smoke | "Does it start? Does /health return 200?" |
| Regression | All previous phase tests still pass |
| Integration | Cross-app (n8n, Stripe, Supervisor, ELAINE, Workshop) — later phases |

Do NOT skip tests. Do NOT defer tests.

---

## START NOW

Begin with Phase 0. Present your pre-flight confirmation before writing
any code. Show:
1. Pre-build check results (clean workspace confirmed)
2. Folder structure you will create
3. Dependencies you will install
4. Database setup plan
5. What the health endpoints will return

Then build Phase 0 and run the Phase 0 checkpoint tests.
Commit to dev branch of Almost-Magic/digital-sentinel.
