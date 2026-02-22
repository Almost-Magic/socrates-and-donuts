# PETERMAN BUILD — PHASE 3: DEPLOYMENT & INTEGRATION
# Date: 20 February 2026
# Prerequisite: Phase 2 smoke test + audit PASSED
# Paste into a FRESH Cline session

You are Guruve — the operational build agent for Almost Magic Tech Lab.

## PREREQUISITE CHECK

Phase 2 must be complete:
- All 11 chambers return real data
- Semantic Map, LCRI, Oracle, Defensive Shield all working
- APScheduler running chamber cycles
- All Phase 1 + Phase 2 tests pass

If ANY fails, fix it before starting Phase 3.

## RULES (Same as always)

- ZERO API costs — Claude CLI primary, Ollama embeddings only
- Australian English everywhere
- Dark theme (#0A0E14), Gold accent (#C9944A)
- Port 5008, database peterman_flask
- HTML/CSS/JS, no framework
- Audit log append-only

---

### Step 1: WordPress CMS Deployment

Build `app/services/deployment_engine.py`:

This is how Peterman deploys approved content to live websites.

**WordPress REST API integration:**
1. Domain settings include: CMS type, CMS API URL, CMS API key
2. For approved content briefs with completed content:
   - Create/update WordPress posts via REST API
   - Create/update pages
   - Update meta descriptions, schema markup
   - Update robots.txt, sitemap triggers
3. Risk classification per action:
   - Auto-deploy: meta description updates, schema markup
   - Low-gate: new FAQ entries, minor content updates
   - Medium-gate: new pages, significant content changes
   - Hard-gate: robots.txt changes, canonical URL changes
   - Prohibited: page deletion, domain-level redirects

**Pre-deployment:**
- Create snapshot (full HTML + metadata) — stored in deployments table
- Generate unified diff (what will change)
- Dry-run sandbox: render preview HTML

**Post-deployment:**
- Verify change applied (re-fetch page, compare)
- Log in audit trail
- Schedule 48-hour re-probe to measure impact

Endpoints:
- `POST /api/domains/<id>/deploy/<brief_id>` — deploy a brief
- `GET /api/domains/<id>/deployments` — deployment history
- `GET /api/domains/<id>/deployments/<did>/preview` — dry-run preview

### Step 2: Rollback Layer

Build rollback into deployment_engine.py:

1. Every deployment creates pre/post snapshots
2. Snapshots retained 30 days (DEC-011)
3. One-click rollback via Journey Timeline or API
4. If Peterman Score drops >5 points within 48 hours post-deploy:
   - Alert via ELAINE
   - Offer one-tap rollback
   - NEVER auto-rollback without operator confirmation

Endpoint:
- `POST /api/domains/<id>/rollback/<deployment_id>` — rollback
- `GET /api/domains/<id>/deployments/<did>/diff` — view diff

### Step 3: ELAINE Integration

Build `app/services/elaine_integration.py` + `app/routes/elaine.py`:

**Outbound to ELAINE (Peterman → ELAINE):**
1. Content briefs → ELAINE's brief queue
2. Approval requests with voice scripts:
   - Low-gate: "Peterman wants to update the meta description for [page]. 
     I'll proceed in 10 seconds unless you object."
   - Medium-gate: "Peterman has generated a new FAQ page about [topic]. 
     Shall I approve?"
   - Hard-gate: "Peterman recommends changing the canonical URL for [page]. 
     This is high-risk. Would you like to review the preview?"
3. Critical alerts: hallucination severity 8+, competitive threat level 4+,
   defensive shield critical
4. Morning briefing data: overnight score changes, pending approvals,
   new hallucinations detected

**Inbound from ELAINE (ELAINE → Peterman):**
1. Status queries: "What's our Peterman Score?"
2. Approval responses: yes/no from operator
3. Strategic queries: "What would happen if we published 3 articles on X?"
4. Trigger commands: "Run a probe on [query] now"

Endpoints:
- `GET /api/elaine/status/<domain_id>` — status for ELAINE
- `GET /api/elaine/score/<domain_id>` — score for ELAINE
- `GET /api/elaine/briefs/pending` — pending briefs for ELAINE
- `POST /api/elaine/approve/<approval_id>` — ELAINE forwards approval
- `GET /api/elaine/morning-briefing/<domain_id>` — morning data

### Step 4: CK Writer Integration

Build `app/services/ckwriter_integration.py`:

When a content brief is approved, it can be sent to CK Writer for drafting:
1. Brief goes to ELAINE → ELAINE assigns to CK Writer
2. CK Writer drafts content following the brief
3. CK Writer returns completed content → ELAINE notifies Peterman
4. Peterman runs alignment check (brief vs content match)
5. If alignment score > 80%: queue for deployment approval
6. If alignment score < 80%: flag for revision

Endpoint:
- `POST /api/domains/<id>/briefs/<bid>/send-to-writer` — send to CK Writer

### Step 5: Workshop Registration

Register Peterman with The Workshop (port 5003):

Provide:
- App name: Peterman
- Port: 5008
- Health endpoint: /api/health
- Favicon: /static/img/favicon.svg
- Launch command: `python run.py`
- Stop command: graceful Flask shutdown
- Recovery procedure: kill → clear Redis cache → restart
- Dependencies: PostgreSQL, Redis, Ollama (Supervisor)

### Step 6: ntfy.sh Mobile Push Notifications

Build `app/services/push_notification.py`:

For critical alerts that need immediate attention:
- Hallucination severity 8+ detected
- Competitive threat level 4+
- Defensive Shield critical alert
- Peterman Score dropped >10 points
- Deployment failure

Use ntfy.sh (self-hosted or free tier):
```python
import requests

def send_push(title: str, message: str, priority: str = 'default'):
    """Send push notification via ntfy.sh. Zero cost."""
    topic = os.getenv('AMTL_PTR_NTFY_TOPIC', 'peterman-alerts')
    requests.post(
        f'https://ntfy.sh/{topic}',
        headers={'Title': title, 'Priority': priority},
        data=message, timeout=10
    )
```

### Step 7: Google Search Console Integration (Optional)

Build `app/services/gsc_integration.py`:

If Mani has GSC credentials configured:
- Pull CTR data, impressions, average position for target queries
- Feed into Chamber 7 (Amplifier) for content performance tracking
- Show in War Room alongside LLM probe data

If not configured: skip gracefully — Chamber 7 notes "partial — no GSC data"

### Step 8: Client Mode Reports

Build `app/services/report_generator.py`:

For client-facing reporting (when Peterman manages client domains):
1. PDF generation using WeasyPrint
2. Report includes:
   - Current Peterman Score with trend
   - LLM Share of Voice per provider
   - Top hallucinations fixed this period
   - Content published and measured impact
   - Competitor overview
   - 90-day forward calendar preview
3. Generate on demand or auto-weekly (Monday 7am AEST)
4. AMTL branding: dark theme, gold accent

Endpoint:
- `POST /api/domains/<id>/report/generate` — generate PDF
- `GET /api/domains/<id>/report/latest` — download latest

---

## PHASE 3 SMOKE TEST

1. ✅/❌ Deploy content to WordPress test site via API
2. ✅/❌ Rollback the deployment — original content restored
3. ✅/❌ Pre/post snapshots exist in deployments table
4. ✅/❌ ELAINE receives approval request and can respond
5. ✅/❌ ELAINE status query returns real Peterman data
6. ✅/❌ Morning briefing data endpoint returns useful summary
7. ✅/❌ CK Writer brief submission works (or stubs correctly)
8. ✅/❌ Workshop shows Peterman with health status
9. ✅/❌ ntfy.sh push notification received on phone
10. ✅/❌ Client Mode PDF generates with real data
11. ✅/❌ All Phase 1 + Phase 2 tests still pass

ALL 11 must pass.

---

## PHASE 3 AUDIT

After smoke test, verify:
1. WordPress API integration uses CMS key from domain settings (not hardcoded)
2. Rollback snapshots stored correctly with 30-day retention
3. ELAINE integration follows approval gate levels correctly
4. No cloud API imports anywhere
5. Australian English in all new UI text
6. Audit log captures all deployments and rollbacks

Produce: PETERMAN-PHASE3-AUDIT-2026-02-XX.md
