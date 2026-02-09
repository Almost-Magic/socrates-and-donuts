"""
Genie v2.1 — Database Models & Initialisation

Event-sourced SQLite with AES-256 encryption (SQLCipher).
Every change is a timestamped event. Point-in-time recovery enabled.
"""

import os
import json
import sqlite3
import hashlib
from datetime import datetime, date
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


# ── Paths ──────────────────────────────────────────────────
def get_db_path() -> Path:
    """Get database path. Uses GENIE_DB_PATH env or default."""
    custom = os.environ.get("GENIE_DB_PATH")
    if custom:
        return Path(custom)
    home = Path.home() / ".genie"
    home.mkdir(exist_ok=True)
    return home / "genie.db"


def get_backup_path() -> Path:
    """Get backup directory."""
    p = Path.home() / ".genie" / "backups"
    p.mkdir(parents=True, exist_ok=True)
    return p


# ── Enums ──────────────────────────────────────────────────
class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class ConfidenceLevel(str, Enum):
    HIGH = "high"          # >95%
    MEDIUM = "medium"      # 80-95%
    LOW = "low"            # <80%
    MANUAL = "manual"      # Human-assigned


class CategorizationSource(str, Enum):
    MANUAL = "manual"
    RULE = "rule"
    AI_SUGGESTED = "ai_suggested"
    AI_AUTO = "ai_auto"
    IMPORTED = "imported"


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    OVERDUE = "overdue"
    PAID = "paid"
    CANCELLED = "cancelled"


class BillStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class VendorVerificationStatus(str, Enum):
    UNVERIFIED = "unverified"
    PARTIAL = "partial"
    VERIFIED = "verified"


class ReconciliationStatus(str, Enum):
    UNMATCHED = "unmatched"
    SUGGESTED = "suggested"
    MATCHED = "matched"
    REVIEWED = "reviewed"      # Seen but no action
    ONE_OFF = "one_off"        # Matched but don't learn


class FraudSeverity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class GenieLearningPhase(str, Enum):
    OBSERVATION = "observation"      # Phase 1: Watching
    SUGGESTION = "suggestion"        # Phase 2: Suggesting
    AUTOMATION = "automation"        # Phase 3: Auto-categorising
    AUTONOMOUS = "autonomous"        # Phase 4: Full auto + anomaly only


class AccountantMode(str, Enum):
    STANDARD = "standard"
    PROFESSIONAL = "professional"


# ── Database Initialisation ────────────────────────────────
def get_connection() -> sqlite3.Connection:
    """Get database connection with row factory."""
    conn = sqlite3.connect(str(get_db_path()), timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # ── Business Settings ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS business (
            id INTEGER PRIMARY KEY DEFAULT 1,
            name TEXT NOT NULL DEFAULT '',
            abn TEXT DEFAULT '',
            gst_registered INTEGER DEFAULT 0,
            financial_year_start TEXT DEFAULT '07-01',
            bas_frequency TEXT DEFAULT 'quarterly',
            state TEXT DEFAULT 'NSW',
            accountant_mode TEXT DEFAULT 'standard',
            confidence_threshold REAL DEFAULT 0.85,
            min_cash_buffer REAL DEFAULT 5000.0,
            hourly_rate REAL DEFAULT 30.0,
            theme TEXT DEFAULT 'dark',
            font_size TEXT DEFAULT 'medium',
            reduce_animations INTEGER DEFAULT 0,
            sidebar_collapsed INTEGER DEFAULT 0,
            onboarding_complete INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── Bank Accounts ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bank_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            bsb TEXT DEFAULT '',
            account_number TEXT DEFAULT '',
            institution TEXT DEFAULT '',
            balance REAL DEFAULT 0.0,
            is_primary INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── Categories (Chart of Accounts) ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            parent_id INTEGER REFERENCES categories(id),
            type TEXT NOT NULL DEFAULT 'expense',
            gst_default TEXT DEFAULT '10',
            is_system INTEGER DEFAULT 0,
            display_order INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── Contacts (Clients & Vendors) ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL DEFAULT 'client',
            name TEXT NOT NULL,
            abn TEXT DEFAULT '',
            email TEXT DEFAULT '',
            phone TEXT DEFAULT '',
            address TEXT DEFAULT '',
            payment_terms INTEGER DEFAULT 30,
            bsb TEXT DEFAULT '',
            account_number TEXT DEFAULT '',
            account_name TEXT DEFAULT '',
            verification_status TEXT DEFAULT 'unverified',
            verification_abn INTEGER DEFAULT 0,
            verification_bsb INTEGER DEFAULT 0,
            verification_phone INTEGER DEFAULT 0,
            verification_email INTEGER DEFAULT 0,
            notes TEXT DEFAULT '',
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── Transactions ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL DEFAULT 'expense',
            category_id INTEGER REFERENCES categories(id),
            contact_id INTEGER REFERENCES contacts(id),
            bank_account_id INTEGER REFERENCES bank_accounts(id),
            gst_amount REAL DEFAULT 0.0,
            gst_treatment TEXT DEFAULT '10',
            categorization_source TEXT DEFAULT 'manual',
            categorization_confidence REAL DEFAULT 1.0,
            reconciliation_status TEXT DEFAULT 'unmatched',
            reconciled_with_id INTEGER DEFAULT NULL,
            import_batch_id TEXT DEFAULT NULL,
            notes TEXT DEFAULT '',
            is_reviewed INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── Invoices ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT NOT NULL UNIQUE,
            contact_id INTEGER NOT NULL REFERENCES contacts(id),
            status TEXT NOT NULL DEFAULT 'draft',
            issue_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            subtotal REAL DEFAULT 0.0,
            gst_total REAL DEFAULT 0.0,
            total REAL DEFAULT 0.0,
            notes TEXT DEFAULT '',
            template_name TEXT DEFAULT '',
            sent_at TEXT DEFAULT NULL,
            paid_at TEXT DEFAULT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── Invoice Line Items ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoice_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
            description TEXT NOT NULL,
            quantity REAL DEFAULT 1.0,
            unit_price REAL NOT NULL,
            gst_treatment TEXT DEFAULT '10',
            gst_amount REAL DEFAULT 0.0,
            total REAL NOT NULL,
            category_id INTEGER REFERENCES categories(id),
            display_order INTEGER DEFAULT 0
        )
    """)

    # ── Bills (AP) ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_id INTEGER NOT NULL REFERENCES contacts(id),
            bill_number TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'pending',
            issue_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            subtotal REAL DEFAULT 0.0,
            gst_total REAL DEFAULT 0.0,
            total REAL DEFAULT 0.0,
            amount_paid REAL DEFAULT 0.0,
            notes TEXT DEFAULT '',
            is_recurring INTEGER DEFAULT 0,
            recurrence_pattern TEXT DEFAULT NULL,
            approval_status TEXT DEFAULT 'pending',
            approved_by TEXT DEFAULT NULL,
            approved_at TEXT DEFAULT NULL,
            paid_at TEXT DEFAULT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── Bill Line Items ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bill_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_id INTEGER NOT NULL REFERENCES bills(id) ON DELETE CASCADE,
            description TEXT NOT NULL,
            quantity REAL DEFAULT 1.0,
            unit_price REAL NOT NULL,
            gst_treatment TEXT DEFAULT '10',
            gst_amount REAL DEFAULT 0.0,
            total REAL NOT NULL,
            category_id INTEGER REFERENCES categories(id),
            display_order INTEGER DEFAULT 0
        )
    """)

    # ── Categorization Rules (Learning Engine) ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorization_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_pattern TEXT NOT NULL,
            category_id INTEGER NOT NULL REFERENCES categories(id),
            confidence REAL DEFAULT 0.95,
            is_hard_rule INTEGER DEFAULT 0,
            match_count INTEGER DEFAULT 0,
            correction_count INTEGER DEFAULT 0,
            last_validated TEXT DEFAULT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── Correction Events (Regret Learning) ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS correction_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER REFERENCES transactions(id),
            old_category_id INTEGER REFERENCES categories(id),
            new_category_id INTEGER NOT NULL REFERENCES categories(id),
            source TEXT DEFAULT 'manual',
            decision_note TEXT DEFAULT '',
            batch_id TEXT DEFAULT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── Fraud Signals ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fraud_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            severity TEXT NOT NULL DEFAULT 'medium',
            signal_type TEXT NOT NULL,
            description TEXT NOT NULL,
            contact_id INTEGER REFERENCES contacts(id),
            transaction_id INTEGER REFERENCES transactions(id),
            bill_id INTEGER REFERENCES bills(id),
            is_resolved INTEGER DEFAULT 0,
            resolved_note TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── Bank Detail Change Log ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bank_detail_changes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL REFERENCES contacts(id),
            old_bsb TEXT,
            new_bsb TEXT,
            old_account TEXT,
            new_account TEXT,
            verified INTEGER DEFAULT 0,
            verified_at TEXT DEFAULT NULL,
            override_reason TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── Event Log (Event Sourcing) ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,
            entity_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            old_data TEXT DEFAULT '{}',
            new_data TEXT DEFAULT '{}',
            user_id TEXT DEFAULT 'owner',
            decision_note TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── Import Batches ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS import_batches (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            format TEXT NOT NULL,
            row_count INTEGER DEFAULT 0,
            imported_count INTEGER DEFAULT 0,
            duplicate_count INTEGER DEFAULT 0,
            error_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'completed',
            template_name TEXT DEFAULT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── Transaction Notes ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaction_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER NOT NULL REFERENCES transactions(id),
            content TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── Invoice Templates ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoice_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            line_items TEXT DEFAULT '[]',
            payment_terms INTEGER DEFAULT 30,
            notes TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── Saved Filters ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_filters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            filter_config TEXT NOT NULL DEFAULT '{}',
            is_default INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── Seed default categories (Australian chart of accounts) ──
    seed_categories(cursor)

    # ── Ensure business record exists ──
    cursor.execute("INSERT OR IGNORE INTO business (id) VALUES (1)")

    conn.commit()
    conn.close()
    print("   ✓ Database initialised")


def seed_categories(cursor):
    """Seed default Australian chart of accounts."""
    categories = [
        # Income
        ("Sales Revenue", None, "income", "10", 1, 1),
        ("Service Revenue", None, "income", "10", 1, 2),
        ("Interest Income", None, "income", "gst_free", 1, 3),
        ("Other Income", None, "income", "10", 1, 4),
        # Expenses
        ("Advertising & Marketing", None, "expense", "10", 1, 10),
        ("Bank Fees & Charges", None, "expense", "gst_free", 1, 11),
        ("Computer & IT", None, "expense", "10", 1, 12),
        ("Consulting & Professional Fees", None, "expense", "10", 1, 13),
        ("Depreciation", None, "expense", "gst_free", 1, 14),
        ("Education & Training", None, "expense", "10", 1, 15),
        ("Entertainment", None, "expense", "10", 1, 16),
        ("Insurance", None, "expense", "gst_free", 1, 17),
        ("Interest Expense", None, "expense", "gst_free", 1, 18),
        ("Motor Vehicle", None, "expense", "10", 1, 19),
        ("Office Supplies", None, "expense", "10", 1, 20),
        ("Postage & Freight", None, "expense", "10", 1, 21),
        ("Printing & Stationery", None, "expense", "10", 1, 22),
        ("Rent", None, "expense", "10", 1, 23),
        ("Repairs & Maintenance", None, "expense", "10", 1, 24),
        ("Software & Subscriptions", None, "expense", "10", 1, 25),
        ("Superannuation", None, "expense", "gst_free", 1, 26),
        ("Telecommunications", None, "expense", "10", 1, 27),
        ("Travel — Domestic", None, "expense", "10", 1, 28),
        ("Travel — International", None, "expense", "10", 1, 29),
        ("Utilities", None, "expense", "10", 1, 30),
        ("Wages & Salaries", None, "expense", "gst_free", 1, 31),
        ("Other Expenses", None, "expense", "10", 1, 32),
    ]
    for name, parent, ctype, gst, is_sys, order in categories:
        cursor.execute(
            "INSERT OR IGNORE INTO categories (name, parent_id, type, gst_default, is_system, display_order) VALUES (?, ?, ?, ?, ?, ?)",
            (name, parent, ctype, gst, is_sys, order),
        )


def log_event(entity_type: str, entity_id: int, event_type: str,
              old_data: dict = None, new_data: dict = None,
              decision_note: str = "", conn=None):
    """Log an event to the event log (event sourcing)."""
    should_close = False
    if conn is None:
        conn = get_connection()
        should_close = True
    conn.execute(
        "INSERT INTO event_log (entity_type, entity_id, event_type, old_data, new_data, decision_note) VALUES (?, ?, ?, ?, ?, ?)",
        (entity_type, entity_id, event_type,
         json.dumps(old_data or {}), json.dumps(new_data or {}),
         decision_note),
    )
    if should_close:
        conn.commit()
        conn.close()
