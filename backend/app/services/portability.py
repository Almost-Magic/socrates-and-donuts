"""Portability service - Settings, export, import"""

import json
import os
from pathlib import Path

# Data directory
DATA_DIR = Path(__file__).parent.parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

SETTINGS_FILE = DATA_DIR / "settings.json"
VAULT_FILE = DATA_DIR / "vault.json"


def load_settings() -> dict:
    """Load user settings from file."""
    if not SETTINGS_FILE.exists():
        return {
            "intensity": "reflective",
            "domains": ["work", "relationships", "body", "belief", "money", "grief", "creativity", "general"],
            "theme": "dark",
            "ai_provider": "none",
            "notifications_enabled": False,
            "notification_time": "07:00"
        }
    
    with open(SETTINGS_FILE, 'r') as f:
        return json.load(f)


def save_settings(settings: dict) -> None:
    """Save user settings to file."""
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)


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
    vault = load_vault()
    settings = load_settings()
    
    return {
        "exported_at": "2026-02-19T00:00:00Z",
        "version": "1.0",
        "settings": settings,
        "vault": vault
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
