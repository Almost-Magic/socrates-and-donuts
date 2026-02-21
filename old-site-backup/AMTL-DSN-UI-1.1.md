# Digital Sentinel — Screen Wireframes & UI Map
## Document Code: AMTL-DSN-UI-1.1
## Almost Magic Tech Lab
## 19 February 2026

> *This document follows AMTL-ECO-STD v1.0. Supersedes AMTL-DSN-UI-1.0.*

---

## Overview

Digital Sentinel has three interfaces:

1. **Website** (digitalsentinel.com.au) — marketing, ordering, Stripe payment
2. **Customer Portal** (:3020) — report access, interactive findings, actions
3. **Operator Dashboard** (:3021) — internal AMTL tool for managing jobs and scans

Design standards: Midnight (#0A0E14) dark theme default, Gold (#C9944A) accent, dark/light toggle, Tailwind CSS, Lucide icons, Australian English throughout.

---

## NAVIGATION SUMMARY

### Website: 4 items + CTA
```
[DS Logo]  Digital Sentinel     [Services]  [Sample Report]  [About]  [Get Started →]
```

### Customer Portal: 4 items
```
[DS Logo]  My Report     [Dashboard]  [Findings]  [Actions]  [Reports ▼]
```

### Operator Dashboard: 4 items
```
[DS Logo]  Operator     [Jobs]  [Scan Runner]  [Delivery]  [Analytics]
```

---

## PART A: WEBSITE (5 screens)

### W-01: Home Page

```
┌────────────────────────────────────────────────────────────────┐
│  [DS Logo]  Digital Sentinel  [Services] [Sample Report] [About] [Get Started →]│
├────────────────────────────────────────────────────────────────┤
│                                                                │
│      See your business the way an attacker does.               │
│                                                                │
│      Digital Sentinel scans your external presence using       │
│      the same tools and techniques a real attacker would       │
│      use — then tells you what they'd find, what it means,     │
│      and exactly how to fix it.                                │
│                                                                │
│      No agents to install. No access to grant.                 │
│      Just your domain name.                                    │
│                                                                │
│      [Get Your Free Risk Grade →]                              │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│  HOW IT WORKS                                                  │
│                                                                │
│  1. You give us your       2. We scan from          3. You     │
│     domain name               the outside              receive │
│                                                        reports │
│  That's all we need.       49 security tools          Risk     │
│  We never log into         examine your public        grade,   │
│  your network.             presence.                  findings,│
│                                                       plan.    │
├────────────────────────────────────────────────────────────────┤
│  WHAT DO YOU NEED?                                             │
│                                                                │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────────┐ │
│  │ "I want to     │ │ "I need to     │ │ "We use AI /       │ │
│  │ know if we're  │ │ check our      │ │ chatbots"          │ │
│  │ exposed"       │ │ vendors"       │ │                    │ │
│  │                │ │                │ │ AI Security        │ │
│  │ Quick: $500    │ │ TPRM: $1,500   │ │ Assessment: $1,999 │ │
│  │ Full: $2,500   │ │                │ │                    │ │
│  └────────────────┘ └────────────────┘ └────────────────────┘ │
│                                                                │
│  ┌────────────────┐ ┌────────────────┐                        │
│  │ "I think we've │ │ "I need this   │                        │
│  │ been breached" │ │ for the board" │                        │
│  │                │ │                │                        │
│  │ Emergency:     │ │ Board-Ready:   │                        │
│  │ $1,500         │ │ $7,500         │                        │
│  └────────────────┘ └────────────────┘                        │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│  TRUST SIGNALS                                                 │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  SEE WHAT YOU'LL RECEIVE                                 │ │
│  │  [Download Sample Report (PDF) →]                        │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  TRY BEFORE YOU COMMIT                                   │ │
│  │  [Get Your Free Risk Grade →]                            │ │
│  │  No payment. No obligation. Just your domain name.       │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  OUR GUARANTEE                                           │ │
│  │  If your report contains no actionable findings,         │ │
│  │  you pay nothing.                                        │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  49 TOOLS: [Nuclei] [Nmap] [OWASP ZAP] [NVIDIA Garak]        │
│  [SpiderFoot] [Shodan] [+43 more]                              │
│                                                                │
│  FRAMEWORKS: [E8] [CPS 234] [ISO 27001] [SOCI] [Privacy Act] │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│  Digital Sentinel — by Almost Magic Tech Lab                   │
│  Founded by Mani Padisetti | Sydney, Australia                 │
│  [Privacy Policy]  [Terms]  [Contact]                          │
└────────────────────────────────────────────────────────────────┘
```

---

### W-02: Services Page

Full service catalogue with plain-English descriptions grouped by customer need. See AMTL-DSN-WEB-1.0 for complete copy. Layout: vertical card stack, each service is a card with description, "What you provide", turnaround, and CTA button.

---

### W-03: Sample Report Page

```
┌────────────────────────────────────────────────────────────────┐
│  [DS Logo]  Digital Sentinel  [Services] [Sample Report] [About] [Get Started →]│
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  See What You'll Receive                                       │
│                                                                │
│  This is a real report — anonymised, but real.                 │
│                                                                │
│  [Download Sample Report (PDF) →]                              │
│                                                                │
│  What's in the report:                                         │
│                                                                │
│  Executive Summary — risk grade, top findings, business impact │
│  Technical Findings — every vulnerability with evidence        │
│  Compliance Mapping — E8, CPS 234, ISO 27001, SOCI, Privacy   │
│  Remediation Playbook — prioritised fixes with effort est.     │
│  Communication Templates — 8 pre-written, customised emails    │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

### W-04: About Page

Mani's story, the problem DS solves, external-only approach, Australian compliance, guarantee. See AMTL-DSN-WEB-1.0 for complete copy.

---

### W-05: Get Started (Order Form)

```
┌────────────────────────────────────────────────────────────────┐
│  [DS Logo]  Digital Sentinel  [Services] [Sample Report] [About] [Get Started →]│
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Get Started                                                   │
│                                                                │
│  Choose your service:  [Comprehensive Scan ▼]                  │
│                                                                │
│  Your details:                                                 │
│  Company name:     [_______________________]                   │
│  Contact name:     [_______________________]                   │
│  Email:            [_______________________]                   │
│  Phone (optional): [_______________________]                   │
│                                                                │
│  Scope:                                                        │
│  Primary domain:   [_______________________]                   │
│  Additional domains: [_____________________]                   │
│  AI endpoint URL:  [_______________________]                   │
│                                                                │
│  Add-ons:                                                      │
│  □ Voice Briefing (+$200)                                      │
│  □ Quarterly Re-Scan                                           │
│  □ Compliance Deep-Dive (+$500/framework) [framework ▼]        │
│                                                                │
│  □ I confirm I am authorised to request this assessment        │
│  □ I understand this is an external assessment only             │
│                                                                │
│  [Review Order →]                                              │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Secure payment via Stripe. 256-bit encryption.          │ │
│  │  Money-back guarantee if no actionable findings.         │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## PART B: CUSTOMER PORTAL (4 screens)

Navigation: `[Dashboard]  [Findings]  [Actions]  [Reports ▼]`

### P-01: Dashboard

```
┌────────────────────────────────────────────────────────────────┐
│  [DS Logo]  My Report    [Dashboard] [Findings] [Actions] [Reports ▼]│
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                                                          │ │
│  │          YOUR RISK GRADE                                 │ │
│  │                                                          │ │
│  │              [ C ]                                       │ │
│  │             62/100                                       │ │
│  │                                                          │ │
│  │         ▲ Improved from D (last scan)                    │ │
│  │                                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  RISK CATEGORIES                                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │ External │ │ Web Apps │ │  Email   │ │  Vendor  │         │
│  │ Surface  │ │          │ │ Security │ │   Risk   │         │
│  │  [RED]   │ │ [AMBER]  │ │ [GREEN]  │ │ [AMBER]  │         │
│  │  12 iss. │ │  5 iss.  │ │  0 iss.  │ │  3 iss.  │         │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │    AI    │ │ Dark Web │ │Compliance│ │Credential│         │
│  │ Security │ │ Exposure │ │ Posture  │ │ & Leaks  │         │
│  │  [GREY]  │ │  [RED]   │ │ [AMBER]  │ │  [RED]   │         │
│  │  N/A     │ │  7 iss.  │ │  4 gaps  │ │  9 iss.  │         │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
│                                                                │
│  TOP 3 CRITICAL FINDINGS                                       │
│  1. 🔴 Admin panel exposed at admin.example.com               │
│  2. 🔴 12 employee credentials found in data breaches         │
│  3. 🔴 SQL injection vulnerability on login form               │
│                                                                │
│  [View All Findings →]        [Download Executive Summary →]   │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Purpose:** "How bad is it?" — one screen, at a glance.

---

### P-02: Findings

```
┌────────────────────────────────────────────────────────────────┐
│  [DS Logo]  My Report    [Dashboard] [Findings] [Actions] [Reports ▼]│
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Findings (36 total)                                           │
│                                                                │
│  Filter: [All Severities ▼] [All Categories ▼] [Search___]    │
│                                                                │
│  ┌────┬────────────────────────────────┬──────────┬─────────┐ │
│  │ 🔴 │ Admin panel publicly exposed   │ External │ Critical│ │
│  ├────┼────────────────────────────────┼──────────┼─────────┤ │
│  │ 🔴 │ 12 credentials in breaches     │ Leaks    │ Critical│ │
│  ├────┼────────────────────────────────┼──────────┼─────────┤ │
│  │ 🔴 │ SQL injection on /login        │ Web Apps │ Critical│ │
│  ├────┼────────────────────────────────┼──────────┼─────────┤ │
│  │ 🟡 │ Outdated jQuery 2.1.4          │ Web Apps │ Medium  │ │
│  ├────┼────────────────────────────────┼──────────┼─────────┤ │
│  │ 🟡 │ DMARC policy set to none       │ Email    │ Medium  │ │
│  ├────┼────────────────────────────────┼──────────┼─────────┤ │
│  │ 🟢 │ SSL certificate valid          │ External │ Info    │ │
│  └────┴────────────────────────────────┴──────────┴─────────┘ │
│                                                                │
│  Click any finding for full details, evidence, and fix steps.  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Click a finding → Finding Detail overlay/page:**

```
┌──────────────────────────────────────────────────────────────┐
│  [← Back to Findings]                                        │
│                                                              │
│  🔴 CRITICAL: Admin panel publicly exposed                   │
│                                                              │
│  WHAT WE FOUND                                               │
│  Your WordPress admin panel is accessible at                 │
│  https://admin.example.com/wp-admin without any IP           │
│  restriction or additional authentication layer.             │
│                                                              │
│  WHY IT MATTERS                                              │
│  Attackers can attempt brute-force login attacks against     │
│  your admin panel. If successful, they gain full control     │
│  of your website and potentially your server.                │
│                                                              │
│  EVIDENCE                                                    │
│  [Screenshot of accessible admin login page]                 │
│  Tool: Nuclei | Template: wp-admin-exposure                  │
│                                                              │
│  COMPLIANCE IMPACT                                           │
│  Essential Eight: Application Hardening (FAIL)               │
│  ISO 27001: A.9.4.1 Information access restriction           │
│                                                              │
│  HOW TO FIX IT                                               │
│  1. Restrict admin panel access to specific IP addresses     │
│  2. Enable two-factor authentication for all admin accounts  │
│  3. Consider moving admin to a non-standard URL              │
│  Effort: Low (1-2 hours for IT/MSP)                          │
│                                                              │
│  [Copy Remediation Email →]  (sends to IT/MSP)               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Purpose:** "What specifically is wrong?" — sortable, filterable, clickable for detail.

---

### P-03: Actions

```
┌────────────────────────────────────────────────────────────────┐
│  [DS Logo]  My Report    [Dashboard] [Findings] [Actions] [Reports ▼]│
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Actions — What To Do Next                                     │
│                                                                │
│  REMEDIATION PLAYBOOK                                          │
│  Prioritised fixes based on your risk score:                   │
│                                                                │
│  1. 🔴 Close admin panel exposure          [Copy Email to IT →]│
│  2. 🔴 Reset breached credentials          [Notify Staff →]   │
│  3. 🔴 Fix SQL injection                   [Copy Email to IT →]│
│  4. 🟡 Update jQuery to latest             [Copy Email to IT →]│
│  5. 🟡 Set DMARC to quarantine/reject      [Copy Email to IT →]│
│                                                                │
│  VENDOR ACTIONS                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Vendor: CloudFlare CDN         Grade: A    [No action]  │ │
│  │  Vendor: Mailchimp              Grade: B    [No action]  │ │
│  │  Vendor: Old Payment Gateway    Grade: D    [Notify →]   │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  COMMUNICATION TEMPLATES                                       │
│  [Remediation Request to IT/MSP]                               │
│  [Board/Management Summary]                                    │
│  [Staff Credential Breach Notification]                        │
│  [Vendor Risk Notification]                                    │
│  [Insurance Summary]                                           │
│  [Incident Disclosure — OAIC]                                  │
│  [Incident Disclosure — CPS 234]                               │
│  [Incident Disclosure — SOCI]                                  │
│                                                                │
│  Each template is pre-written with YOUR findings.              │
│  Click to preview, edit, and copy.                             │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Purpose:** "What do I do about it?" — prioritised fixes, one-click emails, vendor actions.

---

### P-04: Reports (Dropdown)

```
Reports ▼
├── Executive Summary (PDF)          [Download]
├── Technical Report (HTML)          [View] [Download]
├── Compliance Dashboard             [View]
├── Attack Graph                     [View]
├── Remediation Playbook (PDF)       [Download]
├── Voice Briefing (MP3)             [Play] [Download]
└── All Reports (ZIP)                [Download]
```

**Compliance Dashboard (View):**
Control-by-control view per framework. Toggle between E8, CPS 234, ISO 27001, SOCI, Privacy Act. Each control marked Pass / Fail / N/A (requires deeper access).

**Attack Graph (View):**
Interactive D3.js force-directed graph. Nodes = assets. Edges = connections/attack paths. Red = vulnerable. Click any node for details.

---

## PART C: OPERATOR DASHBOARD (4 screens)

Navigation: `[Jobs]  [Scan Runner]  [Delivery]  [Analytics]`

### O-01: Jobs

```
┌────────────────────────────────────────────────────────────────┐
│  [DS Logo]  Operator     [Jobs] [Scan Runner] [Delivery] [Analytics]│
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Job Queue                                                     │
│                                                                │
│  ┌──────┬───────────────┬──────────────┬─────────┬──────────┐ │
│  │ ID   │ Customer      │ Service      │ Status  │ Due      │ │
│  ├──────┼───────────────┼──────────────┼─────────┼──────────┤ │
│  │ 1042 │ Acme Corp     │ Comprehensive│ ▶ SCAN  │ 21 Feb   │ │
│  │ 1041 │ Smith Legal    │ Quick Scan   │ ✅ DONE │ 20 Feb   │ │
│  │ 1040 │ HealthCo      │ AI Security  │ 📝 REVIEW│ 20 Feb   │ │
│  │ 1039 │ RetailPlus    │ Emergency    │ 🔴 URGENT│ TODAY    │ │
│  └──────┴───────────────┴──────────────┴─────────┴──────────┘ │
│                                                                │
│  Click any job to open Scan Runner.                            │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

### O-02: Scan Runner

```
┌────────────────────────────────────────────────────────────────┐
│  [DS Logo]  Operator     [Jobs] [Scan Runner] [Delivery] [Analytics]│
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Job #1042 — Acme Corp — Comprehensive Scan                    │
│  Domain: acmecorp.com.au                                       │
│                                                                │
│  SCAN PLAYBOOK                                                 │
│  ┌────┬──────────────────────────────┬──────────┬────────────┐│
│  │  # │ Step                         │ Tool     │ Status     ││
│  ├────┼──────────────────────────────┼──────────┼────────────┤│
│  │  1 │ Subdomain discovery          │ Subfinder│ ✅ Done    ││
│  │  2 │ HTTP probing                 │ httpx    │ ✅ Done    ││
│  │  3 │ Port scanning                │ Nmap     │ ✅ Done    ││
│  │  4 │ Vulnerability scanning       │ Nuclei   │ ▶ Running  ││
│  │  5 │ Web server scanning          │ Nikto    │ ⏸ Queued   ││
│  │  ... (full playbook per RUN-1.0)                           ││
│  │ 28 │ Deliver                      │ System   │ ⏸ Queued   ││
│  └────┴──────────────────────────────┴──────────┴────────────┘│
│                                                                │
│  [Run Next Step]  [Run All Remaining]  [Pause]  [Cancel]       │
│                                                                │
│  LOGS                                                          │
│  [Live log output from current running tool]                   │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

### O-03: Delivery

```
┌────────────────────────────────────────────────────────────────┐
│  [DS Logo]  Operator     [Jobs] [Scan Runner] [Delivery] [Analytics]│
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Job #1042 — Report Review & Delivery                          │
│                                                                │
│  QUALITY CHECKLIST                                             │
│  □ Risk grade calculated and verified                          │
│  □ All findings have evidence (screenshots/logs)               │
│  □ Compliance mapping complete                                 │
│  □ Remediation steps are specific and actionable               │
│  □ Executive summary is non-technical and clear                │
│  □ Email templates populated with actual findings              │
│  □ Australian English throughout (no American spellings)       │
│  □ No customer data from other engagements leaked              │
│  □ Voice briefing generated (if ordered)                       │
│                                                                │
│  PREVIEW REPORTS                                               │
│  [Executive Summary]  [Technical Report]  [Compliance]         │
│  [Remediation Playbook]  [Email Templates]  [Voice Briefing]   │
│                                                                │
│  [Deliver to Customer →]                                       │
│  (Uploads to portal + sends email notification)                │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

### O-04: Analytics

```
┌────────────────────────────────────────────────────────────────┐
│  [DS Logo]  Operator     [Jobs] [Scan Runner] [Delivery] [Analytics]│
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Analytics                                                     │
│                                                                │
│  Revenue this month: $XX,XXX                                   │
│  Jobs completed: XX    │    Average turnaround: X.X days       │
│  Repeat customers: XX%  │    Most popular: Comprehensive Scan  │
│                                                                │
│  TOP 10 MOST COMMON FINDINGS (anonymised, aggregated)          │
│  1. Missing DMARC policy (78% of scans)                        │
│  2. Outdated CMS versions (65%)                                │
│  3. Exposed admin panels (52%)                                 │
│  ...                                                           │
│                                                                │
│  (This data feeds the "State of AU SMB Cyber Risk" report)     │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## SCREEN INVENTORY

| ID | Screen | Interface | Purpose |
|----|--------|-----------|---------|
| W-01 | Home | Website | Hero, services overview, trust signals |
| W-02 | Services | Website | Full service catalogue with plain-English descriptions |
| W-03 | Sample Report | Website | Download anonymised sample report |
| W-04 | About | Website | Mani's story, approach, guarantee |
| W-05 | Get Started | Website | Order form, Stripe payment, consent |
| P-01 | Dashboard | Portal | Risk grade, heat tiles, top 3 findings |
| P-02 | Findings | Portal | Filterable table + finding detail overlay |
| P-03 | Actions | Portal | Remediation playbook, vendor actions, email templates |
| P-04 | Reports | Portal | Dropdown: all downloadable/viewable reports |
| O-01 | Jobs | Operator | Job queue with status |
| O-02 | Scan Runner | Operator | Step-by-step scan playbook execution |
| O-03 | Delivery | Operator | Quality checklist + report preview + deliver |
| O-04 | Analytics | Operator | Revenue, turnaround, common findings |

**Total: 13 screens (5 website + 4 portal + 4 operator)**

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 19 February 2026 | Claude (Thalaiva) | Initial — 15 screens |
| 1.1 | 19 February 2026 | Claude (Thalaiva) | Simplified navigation (4 items per interface), customer portal reduced from 7 to 4 tabs (Dashboard/Findings/Actions/Reports), services grouped by customer need, trust signals updated, 13 screens total |

---

*Almost Magic Tech Lab*
*"Simple navigation. Clear purpose. No overwhelm."*
