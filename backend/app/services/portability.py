"""Portability service - Settings, export, import, SQLite database"""

import json
import os
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

# Data directory - use user's home directory for data persistence
DATA_DIR = Path.home() / ".socrates-and-donuts"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "vault.db"
SETTINGS_FILE = DATA_DIR / "settings.json"
VAULT_FILE = DATA_DIR / "vault.json"


def get_db_connection():
    """Get a database connection with WAL mode."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_database():
    """Initialise the SQLite database with all required tables."""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            question_id TEXT NOT NULL,
            question_text TEXT NOT NULL,
            framework TEXT,
            domain TEXT,
            intensity TEXT,
            response_text TEXT,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            silence_duration_seconds INTEGER DEFAULT 300
        );

        CREATE TABLE IF NOT EXISTS vault_entries (
            id TEXT PRIMARY KEY,
            entry_type TEXT NOT NULL,
            title TEXT,
            content TEXT NOT NULL,
            tags TEXT DEFAULT '[]',
            session_id TEXT,
            opens_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );

        CREATE TABLE IF NOT EXISTS arc_sessions (
            id TEXT PRIMARY KEY,
            theme TEXT NOT NULL,
            total_days INTEGER NOT NULL,
            current_day INTEGER DEFAULT 1,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            abandoned_at TEXT
        );

        CREATE TABLE IF NOT EXISTS feedback_log (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            framework TEXT,
            feedback TEXT NOT NULL,
            logged_at TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
    """)
    
    # Insert default settings if not present
    defaults = [
        ('intensity', 'reflective'),
        ('domains_enabled', '["work","relationships","body","belief","money","grief","creativity"]'),
        ('silence_duration', '300'),
        ('notifications_enabled', 'false'),
        ('llm_provider', 'none'),
        ('llm_api_key', ''),
        ('llm_endpoint', ''),
        ('theme', 'dark')
    ]
    for key, value in defaults:
        c.execute(
            "INSERT OR IGNORE INTO settings (key, value, updated_at) VALUES (?, ?, datetime('now'))",
            (key, value)
        )
    
    conn.commit()
    conn.close()


# Initialize database on module load
init_database()


def load_settings() -> dict:
    """Load user settings from SQLite database."""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT key, value FROM settings")
        rows = c.fetchall()
        conn.close()
        
        settings = {row['key']: row['value'] for row in rows}
        
        # Parse JSON fields
        if 'domains_enabled' in settings:
            settings['domains_enabled'] = json.loads(settings['domains_enabled'])
        
        return settings if settings else {
            "intensity": "reflective",
            "domains_enabled": ["work", "relationships", "body", "belief", "money", "grief", "creativity"],
            "theme": "dark",
            "llm_provider": "none",
            "notifications_enabled": False,
            "silence_duration": 300
        }
    except Exception as e:
        # Fallback to old JSON file if DB fails
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        return {
            "intensity": "reflective",
            "domains_enabled": ["work", "relationships", "body", "belief", "money", "grief", "creativity"],
            "theme": "dark",
            "llm_provider": "none",
            "notifications_enabled": False,
            "silence_duration": 300
        }


def save_settings(settings: dict) -> None:
    """Save user settings to SQLite database."""
    conn = get_db_connection()
    c = conn.cursor()
    
    for key, value in settings.items():
        # Serialize lists to JSON
        if isinstance(value, (list, dict)):
            value = json.dumps(value)
        elif isinstance(value, bool):
            value = 'true' if value else 'false'
        
        c.execute(
            "INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, datetime('now'))",
            (key, str(value))
        )
    
    conn.commit()
    conn.close()


def get_vault_entry_count() -> int:
    """Get the total number of vault entries."""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) as count FROM vault_entries")
        count = c.fetchone()['count']
        conn.close()
        return count
    except:
        return 0


def get_active_arc() -> dict | None:
    """Get the currently active arc session if any."""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""
            SELECT id, theme, total_days, current_day, started_at 
            FROM arc_sessions 
            WHERE completed_at IS NULL AND abandoned_at IS NULL
            ORDER BY started_at DESC LIMIT 1
        """)
        row = c.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row['id'],
                'theme': row['theme'],
                'total_days': row['total_days'],
                'current_day': row['current_day'],
                'started_at': row['started_at']
            }
        return None
    except:
        return None


def load_vault() -> dict:
    """Load vault data from file."""
    if not VAULT_FILE.exists():
        return {
            "insights": [],
            "letters": [],
            "aphorisms": [],
            "tags": []
        }
    
    with open(VAULT_FILE, 'r') as f:
        return json.load(f)


def save_vault(vault: dict) -> None:
    """Save vault data to file."""
    with open(VAULT_FILE, 'w') as f:
        json.dump(vault, f, indent=2)


def export_vault_data() -> dict:
    """Export all vault data as JSON."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get sessions
    c.execute("SELECT * FROM sessions ORDER BY started_at DESC")
    sessions = [dict(row) for row in c.fetchall()]
    
    # Get vault entries
    c.execute("SELECT * FROM vault_entries ORDER BY created_at DESC")
    vault_entries = [dict(row) for row in c.fetchall()]
    
    # Get feedback log
    c.execute("SELECT * FROM feedback_log ORDER BY logged_at DESC")
    feedback_log = [dict(row) for row in c.fetchall()]
    
    # Get settings
    c.execute("SELECT * FROM settings")
    settings_rows = c.fetchall()
    settings = {row['key']: row['value'] for row in settings_rows}
    
    conn.close()
    
    return {
        "export_version": "1.0",
        "exported_at": datetime.utcnow().isoformat() + "Z",
        "app": "Socrates & Donuts",
        "sessions": sessions,
        "vault_entries": vault_entries,
        "feedback_log": feedback_log,
        "settings": settings
    }


def import_vault_data(data: dict, mode: str = 'merge') -> dict:
    """Import vault data from JSON.
    
    Args:
        data: The imported data dict
        mode: 'merge' to combine with existing, 'replace' to overwrite
    
    Returns:
        Result dict with status
    """
    try:
        if mode == 'replace':
            if 'settings' in data:
                save_settings(data['settings'])
            if 'vault' in data:
                save_vault(data['vault'])
        else:
            # Merge - load existing and update
            existing_settings = load_settings()
            existing_vault = load_vault()
            
            if 'settings' in data:
                existing_settings.update(data['settings'])
                save_settings(existing_settings)
            
            if 'vault' in data:
                # Merge lists
                for key in ['insights', 'letters', 'aphorisms']:
                    if key in data['vault'] and key in existing_vault:
                        # Combine and deduplicate by ID
                        existing_ids = {item.get('id') for item in existing_vault[key]}
                        for item in data['vault'][key]:
                            if item.get('id') not in existing_ids:
                                existing_vault[key].append(item)
                save_vault(existing_vault)
        
        return {"status": "success", "message": "Data imported successfully"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
