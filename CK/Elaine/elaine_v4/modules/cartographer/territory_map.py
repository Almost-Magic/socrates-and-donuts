"""
Cartographer v2 — Knowledge Territory Map
Auto-calculated depth with temporal decay.

Patentable: Topographic Intelligence Mapping with Auto-Calculated Depth

Almost Magic Tech Lab — Patentable IP
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from .models import (
    KnowledgeTerritory, DepthSignals, DepthLevel,
    TerritoryTrend, DEPTH_THRESHOLDS,
)

logger = logging.getLogger("elaine.cartographer.territory")


class TerritoryMap:
    """
    Living map of Mani's knowledge territory.
    Mountains = deep expertise. Fog = unexplored.
    Auto-calculates depth from multi-signal analysis.
    """

    def __init__(self):
        self.territories: dict[str, KnowledgeTerritory] = {}
        self._seed_initial_territories()

    def _seed_initial_territories(self):
        """Seed Mani's known territories from profile."""
        seeds = [
            ("ai_governance", "AI Governance", DepthSignals(
                credentials=100, content_production=90, time_investment=85,
                query_complexity=90, teaching_evidence=80, peer_recognition=60,
            ), 0.02),  # Credentialed — slow decay
            ("cybersecurity", "Cybersecurity", DepthSignals(
                credentials=95, content_production=70, time_investment=90,
                query_complexity=85, teaching_evidence=70, peer_recognition=50,
            ), 0.02),
            ("business_strategy", "Business Strategy", DepthSignals(
                credentials=80, content_production=75, time_investment=80,
                query_complexity=80, teaching_evidence=65, peer_recognition=40,
            ), 0.03),
            ("ai_agents", "AI Agents", DepthSignals(
                credentials=30, content_production=60, time_investment=90,
                query_complexity=70, teaching_evidence=40, peer_recognition=20,
            ), 0.05),
            ("regulatory_landscape", "Regulatory Landscape (AU/EU/US)", DepthSignals(
                credentials=40, content_production=30, time_investment=40,
                query_complexity=35, teaching_evidence=15, peer_recognition=10,
            ), 0.05),
            ("quantum_computing", "Quantum Computing", DepthSignals(
                credentials=0, content_production=0, time_investment=10,
                query_complexity=15, teaching_evidence=0, peer_recognition=0,
            ), 0.05),
        ]

        for tid, label, signals, decay in seeds:
            self.territories[tid] = KnowledgeTerritory(
                territory_id=tid,
                label=label,
                depth_signals=signals,
                decay_rate_per_quarter=decay,
                last_engagement=datetime.now(),
            )

        # Set adjacencies
        self.territories["ai_governance"].adjacent_territories = [
            "ai_liability", "ai_regulation", "data_governance", "ai_insurance",
        ]
        self.territories["ai_governance"].negative_spaces = [
            "ai_governance_micro_business", "ai_relational_ethics", "ai_governance_insurance_standards",
        ]
        self.territories["cybersecurity"].adjacent_territories = [
            "quantum_safe_crypto", "supply_chain_security", "ot_security",
        ]
        self.territories["ai_agents"].adjacent_territories = [
            "agent_certification", "autonomous_ai_safety", "mcp_protocol",
        ]

    # ── Territory CRUD ───────────────────────────────────────────

    def get_territory(self, territory_id: str) -> Optional[KnowledgeTerritory]:
        return self.territories.get(territory_id)

    def add_territory(self, territory_id: str, label: str,
                      signals: DepthSignals = None, **kwargs) -> KnowledgeTerritory:
        t = KnowledgeTerritory(
            territory_id=territory_id,
            label=label,
            depth_signals=signals or DepthSignals(),
            last_engagement=datetime.now(),
            **kwargs,
        )
        self.territories[territory_id] = t
        logger.info(f"New territory: {label} (depth: {t.depth.value})")
        return t

    def get_map(self) -> list[dict]:
        """Full territory map for display."""
        return sorted(
            [
                {
                    "territory_id": t.territory_id,
                    "label": t.label,
                    "depth": t.depth.value,
                    "depth_score": round(t.depth_score, 1),
                    "trend": t.trend.value,
                    "adjacent": t.adjacent_territories,
                    "negative_spaces": t.negative_spaces,
                    "knowledge_debt_hours": t.knowledge_debt_hours,
                    "last_engagement": t.last_engagement.isoformat() if t.last_engagement else None,
                }
                for t in self.territories.values()
            ],
            key=lambda x: x["depth_score"],
            reverse=True,
        )

    # ── Depth Decay ──────────────────────────────────────────────

    def apply_quarterly_decay(self) -> list[dict]:
        """
        Apply temporal depth decay.
        Knowledge decays 5%/quarter (2% for credentialed).
        Alert when depth drops a level.
        """
        alerts = []
        now = datetime.now()

        for t in self.territories.values():
            if not t.last_engagement:
                continue

            quarters_since = (now - t.last_engagement).days / 90.0
            if quarters_since < 1.0:
                continue  # No decay within first quarter

            decay_factor = 1.0 - (t.decay_rate_per_quarter * quarters_since)
            decay_factor = max(0.3, decay_factor)  # Never decay below 30%

            old_depth = t.depth
            # Apply decay to all signals proportionally
            t.depth_signals.content_production *= decay_factor
            t.depth_signals.time_investment *= decay_factor
            t.depth_signals.query_complexity *= decay_factor
            t.depth_signals.teaching_evidence *= decay_factor
            t.depth_signals.peer_recognition *= decay_factor
            # Credentials decay slower (already in decay_rate)

            new_depth = t.depth
            if new_depth != old_depth:
                t.trend = TerritoryTrend.STALE
                alert = {
                    "territory": t.label,
                    "old_depth": old_depth.value,
                    "new_depth": new_depth.value,
                    "quarters_inactive": round(quarters_since, 1),
                    "message": (
                        f"Your {t.label} knowledge was '{old_depth.value}' "
                        f"but you haven't engaged in {quarters_since:.0f} quarters. "
                        f"It's now '{new_depth.value}'. Recommend a refresh."
                    ),
                }
                alerts.append(alert)
                logger.warning(f"Depth decay: {t.label} {old_depth.value} → {new_depth.value}")

        return alerts

    # ── Engagement Recording ─────────────────────────────────────

    def record_engagement(self, territory_id: str, signal_type: str = "general"):
        """Record that Mani engaged with a territory — resets decay timer."""
        t = self.territories.get(territory_id)
        if t:
            t.last_engagement = datetime.now()
            if t.trend == TerritoryTrend.STALE:
                t.trend = TerritoryTrend.EXPANDING
            logger.info(f"Engagement: {t.label} ({signal_type})")

    # ── Knowledge Debt ───────────────────────────────────────────

    def calculate_knowledge_debt(self, required_territories: dict[str, DepthLevel]) -> list[dict]:
        """
        Compare required depth (from clients, pipeline, market) against actual depth.
        Returns gaps with learning paths.
        """
        debts = []
        for tid, required_depth in required_territories.items():
            t = self.territories.get(tid)
            if not t:
                # Territory doesn't exist yet — full debt
                debts.append({
                    "territory": tid,
                    "required": required_depth.value,
                    "current": "unexplored",
                    "gap_severity": "critical",
                    "estimated_hours": 20,
                })
                continue

            req_threshold = DEPTH_THRESHOLDS[required_depth]
            if t.depth_score < req_threshold:
                gap = req_threshold - t.depth_score
                hours = gap * 0.5  # Rough: 0.5 hours per point of gap
                debts.append({
                    "territory": t.label,
                    "required": required_depth.value,
                    "current": t.depth.value,
                    "current_score": round(t.depth_score, 1),
                    "gap_points": round(gap, 1),
                    "estimated_hours": round(hours, 0),
                    "gap_severity": "critical" if gap > 40 else "moderate" if gap > 20 else "low",
                    "debt_description": t.knowledge_debt_description,
                    "roi": t.knowledge_debt_roi,
                })

        return sorted(debts, key=lambda d: d.get("gap_points", 100), reverse=True)

    # ── Adjacency Detection ──────────────────────────────────────

    def get_adjacent_territories(self) -> list[dict]:
        """Get all adjacent (unexplored) territories with context."""
        adjacent = {}
        for t in self.territories.values():
            if t.depth_score < 25:
                continue  # Don't look for adjacencies from shallow territories
            for adj_id in t.adjacent_territories:
                if adj_id not in self.territories:
                    if adj_id not in adjacent:
                        adjacent[adj_id] = {
                            "territory_id": adj_id,
                            "adjacent_to": [],
                            "discovery_potential": "unknown",
                        }
                    adjacent[adj_id]["adjacent_to"].append(t.label)

        return list(adjacent.values())
