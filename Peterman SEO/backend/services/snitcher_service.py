"""
Peterman V4.1 — Snitcher Service
Almost Magic Tech Lab

Visitor intelligence — identifies companies visiting client websites.
Used by Chamber 8 (Visitor Intelligence) for lead identification.
Cost: ~$39/mo (kept because free alternatives only get ~40% accuracy vs Snitcher's ~65%)
"""
import httpx
import logging
from flask import current_app

logger = logging.getLogger(__name__)

SNITCHER_API_URL = "https://app.snitcher.com/api/v2"


class SnitcherService:
    """Interface to Snitcher for IP-to-company identification."""

    def __init__(self):
        self._api_key = None

    @property
    def api_key(self):
        if self._api_key:
            return self._api_key
        try:
            return current_app.config.get("SNITCHER_API_KEY", "")
        except RuntimeError:
            return ""

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    # ----------------------------------------------------------
    # Visitor Identification
    # ----------------------------------------------------------

    def identify_visitor(self, ip_address):
        """Identify a company from an IP address."""
        if not self.api_key:
            return {"error": "Snitcher API key not configured", "company": None}

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    f"{SNITCHER_API_URL}/identify",
                    params={"ip": ip_address},
                    headers=self._headers(),
                )
                response.raise_for_status()
                data = response.json()

                return {
                    "ip": ip_address,
                    "company": data.get("company"),
                    "domain": data.get("domain"),
                    "industry": data.get("industry"),
                    "employee_count": data.get("employee_count"),
                    "location": data.get("location"),
                    "confidence": data.get("confidence"),
                    "cost": 0.01,  # Approx per-lookup cost
                }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"ip": ip_address, "company": None, "message": "No company match"}
            logger.error(f"Snitcher API error: {e}")
            return {"ip": ip_address, "error": str(e), "company": None}
        except Exception as e:
            logger.error(f"Snitcher error: {e}")
            return {"ip": ip_address, "error": str(e), "company": None}

    def get_visitors(self, domain, date_from=None, date_to=None, limit=50):
        """Get recent website visitors identified by Snitcher."""
        if not self.api_key:
            return {"error": "Snitcher API key not configured", "visitors": []}

        params = {"domain": domain, "limit": limit}
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to

        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(
                    f"{SNITCHER_API_URL}/visitors",
                    params=params,
                    headers=self._headers(),
                )
                response.raise_for_status()
                data = response.json()

                visitors = data.get("visitors", data.get("data", []))
                return {
                    "domain": domain,
                    "visitors": [
                        {
                            "company": v.get("company", {}).get("name"),
                            "domain": v.get("company", {}).get("domain"),
                            "industry": v.get("company", {}).get("industry"),
                            "employee_count": v.get("company", {}).get("employee_count"),
                            "location": v.get("company", {}).get("location"),
                            "pages_viewed": v.get("pages_viewed", []),
                            "visit_count": v.get("visit_count", 1),
                            "first_visit": v.get("first_visit"),
                            "last_visit": v.get("last_visit"),
                        }
                        for v in visitors
                    ],
                    "total": len(visitors),
                    "cost": 0.0,  # Included in subscription
                }
        except Exception as e:
            logger.error(f"Snitcher visitors error: {e}")
            return {"domain": domain, "visitors": [], "error": str(e)}

    # ----------------------------------------------------------
    # Lead Scoring (local enrichment)
    # ----------------------------------------------------------

    def score_visitor(self, visitor_data, brand_target_audience=None):
        """
        Score a visitor as a potential lead based on behaviour and company fit.
        This runs locally — no API cost.
        """
        score = 0
        reasons = []

        # Page depth
        pages = visitor_data.get("pages_viewed", [])
        if len(pages) >= 5:
            score += 30
            reasons.append("Deep engagement (5+ pages)")
        elif len(pages) >= 3:
            score += 20
            reasons.append("Moderate engagement (3+ pages)")
        elif len(pages) >= 1:
            score += 10

        # Return visits
        visits = visitor_data.get("visit_count", 1)
        if visits >= 3:
            score += 25
            reasons.append(f"Return visitor ({visits} visits)")
        elif visits >= 2:
            score += 15

        # Company size
        employees = visitor_data.get("employee_count", 0)
        if isinstance(employees, str):
            # Handle ranges like "50-100"
            try:
                employees = int(employees.split("-")[0])
            except (ValueError, IndexError):
                employees = 0

        if employees >= 50:
            score += 20
            reasons.append(f"Mid-market+ company ({employees} employees)")
        elif employees >= 10:
            score += 10

        # Industry match
        if brand_target_audience and visitor_data.get("industry"):
            visitor_industry = visitor_data["industry"].lower()
            for target in brand_target_audience:
                if target.lower() in visitor_industry or visitor_industry in target.lower():
                    score += 25
                    reasons.append(f"Industry match: {visitor_data['industry']}")
                    break

        return {
            "score": min(score, 100),
            "tier": "hot" if score >= 70 else "warm" if score >= 40 else "cool",
            "reasons": reasons,
        }

    # ----------------------------------------------------------
    # Health Check
    # ----------------------------------------------------------

    def health_check(self):
        """Check if Snitcher API is accessible."""
        if not self.api_key:
            return {"status": "not_configured", "message": "SNITCHER_API_KEY not set"}

        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(
                    f"{SNITCHER_API_URL}/account",
                    headers=self._headers(),
                )
                if response.status_code == 200:
                    return {"status": "ok"}
                elif response.status_code == 401:
                    return {"status": "error", "message": "Invalid API key"}
                else:
                    return {"status": "error", "message": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}


# Singleton
snitcher = SnitcherService()
