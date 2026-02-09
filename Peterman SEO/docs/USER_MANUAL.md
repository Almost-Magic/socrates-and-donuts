# Genie v2.1 — User Manual

**Almost Magic Finance Suite — Agent 01: The AI Bookkeeper**

## Getting Started

1. Extract Genie to a folder (e.g. C:\AlmostMagic\Genie)
2. Open PowerShell, navigate to the folder
3. Run setup commands (see SETUP_COMMANDS.ps1)
4. API available at http://localhost:8000/api/docs

Your data is local. Nothing is sent to the cloud.

## Onboarding (5-10 minutes)

1. Business name and ABN (auto-validates against ABR)
2. GST status and financial year
3. First bank account (BSB auto-validates)
4. First import (drag-drop your bank statement)
5. First 10 categorisations (teach Genie your business)

## Importing Transactions

Supports: CSV, XLSX, XLS, TSV, OFX, QIF, PDF (OCR). Auto-detects CBA, ANZ, NAB, Westpac formats. Duplicate detection prevents double-imports. Import rollback available.

Pro tip: Import your accountant's pre-categorised spreadsheet to jump-start Genie's learning.

## Categorisation (4 Phases)

1. **Observation** — You categorise, Genie watches (first 50-150 transactions)
2. **Suggestion** — Genie suggests with confidence scores, you confirm/correct
3. **Automation** — High-confidence auto-categorised, low-confidence flagged for review
4. **Autonomous** — Full auto, only anomalies surface

Confidence threshold: adjustable 50-99% in Settings > AI Behaviour.

Confidence decay: Rules lose 5% confidence per quarter without validation. Genie asks "is this still right?" Prevents stale automation.

## Bank Reconciliation

Split-view: bank transactions left, match suggestions right. Each match shows confidence and explanation ("Matched on: amount exact, client name in reference, date within 3 days").

Actions: Accept (right arrow), Reject (left), Accept one-off (Shift+right, don't learn), Mark reviewed (Space).

## Invoicing

Ctrl+I to create. Client type-ahead with hover-card. Line items with GST. Templates for recurring invoices. Status tracking: Draft > Sent > Overdue > Paid. Debtor ageing and payment velocity tracking per client.

## Bills / AP

Manual entry or PDF drop (OCR extraction). New vendors require 4-step verification (ABN, BSB, phone, email) before any payment. Bank detail changes block all payments until re-verified.

## Cash Flow

- **Fragility Score**: Cash / Obligations. Green (>2.0), Amber (1-2), Red (<1.0).
- **Safe-to-Spend**: Cash minus all obligations minus buffer.
- **13-Week Forecast**: Three scenarios (optimistic/expected/conservative).

## Fraud Guard

Monitors: new unverified vendors, bank detail changes, duplicate invoices, unusual amounts, PDF metadata anomalies, round-number threshold avoidance. Fraud Prevention Score: 0-100.

## GST & BAS

Continuous tracking per quarter. BAS pre-fill with all fields. Audit Readiness Score (0-100%) with specific gap identification.

## Ask Genie (Ctrl+J)

Natural language queries: "How much did I spend on marketing?", "What's my GST position?", "Who are my top vendors?"

## Reports & Exports

Accountant Pack: one-click export of Trial Balance, GL, GST, Ageing, Reconciliations. All exports are macro-free XLSX. Zero VBA, zero exceptions.

## Settings

Business, Mode (Standard/Professional), AI Behaviour, Cash Flow, Fraud Guard, Display (dark/light), Hourly Rate for ROI calculation.

## Keyboard Shortcuts

Ctrl+K Search | Ctrl+J Ask Genie | Ctrl+I Invoice | Ctrl+B Bill | Ctrl+Z Undo | Ctrl+E Export | Ctrl+/ Sidebar | Tab Navigate | Enter Confirm | Escape Cancel | Arrow keys for reconciliation | Space = reviewed.

## Troubleshooting

- Backend won't start: check Python 3.10+, venv active, pip install requirements
- Database issues: daily backups in ~/.genie/backups/, delete genie.db to reset
- AI offline: core bookkeeping works without Ollama
- Import issues: try CSV format, check headers in row 1

---
*Almost Magic Tech Lab Pty Ltd — Genie v2.1*
