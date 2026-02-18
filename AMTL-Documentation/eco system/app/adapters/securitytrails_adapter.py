"""SecurityTrails API adapter for Digital Sentinel."""
import os
import requests
from typing import Optional


class SecurityTrailsAdapter:
    """Queries SecurityTrails API for historical DNS data."""

    BASE_URL = "https://api.securitytrails.com/v1"

    def __init__(self):
        self.api_key = os.getenv("AMTL_DSN_SECURITYTRAILS_KEY")
        if not self.api_key:
            raise ValueError("AMTL_DSN_SECURITYTRAILS_KEY not set in environment")
        self.headers = {"APIKEY": self.api_key}

    def get_domain_info(self, domain: str) -> Optional[dict]:
        """Get current DNS records for a domain."""
        r = requests.get(f"{self.BASE_URL}/domain/{domain}", headers=self.headers)
        return r.json() if r.status_code == 200 else None

    def get_subdomains(self, domain: str) -> Optional[list]:
        """Get subdomains for a domain."""
        r = requests.get(
            f"{self.BASE_URL}/domain/{domain}/subdomains",
            headers=self.headers
        )
        if r.status_code == 200:
            data = r.json()
            return [f"{sub}.{domain}" for sub in data.get("subdomains", [])]
        return None

    def get_history(self, domain: str, record_type: str = "a") -> Optional[dict]:
        """Get historical DNS records."""
        r = requests.get(
            f"{self.BASE_URL}/history/{domain}/dns/{record_type}",
            headers=self.headers
        )
        return r.json() if r.status_code == 200 else None
