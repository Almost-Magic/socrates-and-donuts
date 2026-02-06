"""
Cartographer v2 — Discovery Engine
Governor, Narrative Engine, Source Intelligence, Discovery lifecycle.

Patentable:
- Cognitive Budget Discovery Governance
- Synthesised Intelligence Narrative
- Convergence-Based Dynamic Source Credibility
- Self-Correcting Discovery via Counterfactual Gap Analysis

Almost Magic Tech Lab — Patentable IP
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional

from .models import (
    Discovery, DiscoveryLayer, ActionabilityLevel, InteractionType,
    Source, SourceTier, SOURCE_BASE_CREDIBILITY, INTERACTION_WEIGHTS,
    CognitiveBudget, CognitivePhase,
    Pattern, CounterfactualGap,
    NewsCategory, IntelligenceCalendarSlot,
)

logger = logging.getLogger("elaine.cartographer.discovery")


class SourceRegistry:
    """
    Dynamic source credibility management.
    Base tiers + engagement adjustments + convergence bonuses.
    """

    def __init__(self):
        self.sources: dict[str, Source] = {}
        self._seed_sources()

    def _seed_sources(self):
        seeds = [
            ("afr", "Australian Financial Review", SourceTier.AUTHORITATIVE, ["finance", "business", "policy"], "Australia"),
            ("acsc", "ACSC Alerts", SourceTier.PRIMARY, ["cybersecurity", "essential_eight"], "Australia"),
            ("reuters", "Reuters", SourceTier.AUTHORITATIVE, ["international", "markets", "policy"], "Global"),
            ("ft", "Financial Times", SourceTier.AUTHORITATIVE, ["finance", "markets", "technology"], "Global"),
            ("iso", "ISO Standards", SourceTier.PRIMARY, ["governance", "standards", "certification"], "Global"),
            ("nist", "NIST", SourceTier.PRIMARY, ["cybersecurity", "frameworks", "standards"], "US"),
            ("arxiv", "arXiv Preprints", SourceTier.EXPERT, ["ai_research", "technology"], "Global"),
            ("hn", "Hacker News", SourceTier.COMMUNITY, ["technology", "startups", "ai"], "Global"),
            ("linkedin", "LinkedIn Feed", SourceTier.COMMUNITY, ["professional", "industry"], "Global"),
        ]
        for sid, name, tier, domains, geo in seeds:
            self.sources[sid] = Source(
                source_id=sid, name=name, base_tier=tier,
                domains=domains, geographic_focus=geo,
            )

    def get_source(self, source_id: str) -> Optional[Source]:
        return self.sources.get(source_id)

    def adjust_credibility(self, source_id: str, delta: float, reason: str):
        src = self.sources.get(source_id)
        if src:
            src.credibility_adjustments.append({
                "delta": max(-0.20, min(0.20, delta)),
                "reason": reason,
                "date": datetime.now().isoformat(),
            })
            logger.info(f"Source credibility adjusted: {src.name} {delta:+.2f} ({reason})")

    def record_early_detection(self, source_id: str):
        """Source reported something first that was later confirmed."""
        src = self.sources.get(source_id)
        if src:
            src.early_detection_count += 1
            self.adjust_credibility(source_id, +0.15, "early_detection_bonus")

    def record_false_report(self, source_id: str):
        src = self.sources.get(source_id)
        if src:
            src.false_report_count += 1
            self.adjust_credibility(source_id, -0.15, "false_report")

    def record_engagement(self, source_id: str, engaged: bool):
        delta = +0.05 if engaged else -0.05
        reason = "mani_engagement" if engaged else "mani_dismissal"
        self.adjust_credibility(source_id, delta, reason)

    def get_all(self) -> list[dict]:
        return [
            {
                "source_id": s.source_id,
                "name": s.name,
                "base_tier": s.base_tier.name,
                "current_credibility": round(s.current_credibility, 2),
                "domains": s.domains,
                "engagement_rate": s.engagement_rate,
                "early_detections": s.early_detection_count,
                "false_reports": s.false_report_count,
            }
            for s in sorted(self.sources.values(), key=lambda s: s.current_credibility, reverse=True)
        ]


class DiscoveryGovernor:
    """
    Cognitive Budget Discovery Governance.
    Controls how many discoveries reach Mani based on current phase.
    """

    def __init__(self):
        self.budget = CognitiveBudget()
        self._phase_history: list[dict] = []

    def set_phase(self, phase: CognitivePhase, reason: str = ""):
        old = self.budget.current_phase
        self.budget.current_phase = phase
        self._phase_history.append({
            "from": old.value, "to": phase.value,
            "reason": reason, "timestamp": datetime.now().isoformat(),
        })
        logger.info(f"Discovery phase: {old.value} → {phase.value} ({reason})")

    def auto_detect_phase(self, red_giant_count: int, has_deadline: bool) -> CognitivePhase:
        """Auto-detect phase from Gravity field state."""
        if red_giant_count >= 3:
            phase = CognitivePhase.CRISIS
        elif has_deadline or red_giant_count >= 1:
            phase = CognitivePhase.EXECUTION
        else:
            phase = CognitivePhase.RECOVERY
        self.set_phase(phase, f"auto: {red_giant_count} red giants")
        return phase

    def gate(self, discovery: Discovery) -> bool:
        """
        Should this discovery be delivered to Mani?
        Returns True if it passes the gate.
        """
        # Urgent always passes
        if discovery.actionability == ActionabilityLevel.URGENT:
            return True

        # Check budget
        if not self.budget.can_deliver(discovery.layer):
            logger.debug(f"Budget exhausted for {discovery.layer.value}: {discovery.title[:40]}")
            return False

        # Archive never passes
        if discovery.actionability == ActionabilityLevel.ARCHIVE:
            return False

        # Phase-specific suppression
        if self.budget.current_phase == CognitivePhase.CRISIS:
            if discovery.layer != DiscoveryLayer.SIGNAL:
                return False
            if discovery.actionability not in (ActionabilityLevel.ACT, ActionabilityLevel.URGENT):
                return False

        return True

    def consume(self, discovery: Discovery):
        self.budget.consume(discovery.layer)

    def reset_daily(self):
        self.budget.signal_used = 0

    def reset_weekly(self):
        self.budget.pattern_used_this_week = 0
        self.budget.horizon_used_this_week = 0

    def status(self) -> dict:
        b = self.budget
        return {
            "phase": b.current_phase.value,
            "signal_budget": f"{b.signal_used}/{b.effective_signal_max}",
            "pattern_budget": f"{b.pattern_used_this_week}/{b.pattern_max_per_week}",
            "horizon_suppressed": b.horizon_suppressed,
            "serendipity_suppressed": b.serendipity_suppressed,
        }


class DiscoveryEngine:
    """
    Core discovery lifecycle: create, gate, deliver, track, learn.
    """

    def __init__(self):
        self.discoveries: dict[str, Discovery] = {}
        self.patterns: dict[str, Pattern] = {}
        self.gaps: list[CounterfactualGap] = []
        self.governor = DiscoveryGovernor()
        self.sources = SourceRegistry()

        # Engagement learning
        self._engagement_stats: dict[str, dict] = {}  # territory → {read, saved, acted, dismissed, ignored}

    # ── Discovery Lifecycle ──────────────────────────────────────

    def create_discovery(self, title: str, summary: str, so_what: str,
                         source_id: str, layer: DiscoveryLayer,
                         actionability: ActionabilityLevel,
                         territory: str = "", **kwargs) -> Discovery:
        """Create a new discovery and pass through the governor gate."""
        source = self.sources.get_source(source_id)
        disc = Discovery(
            discovery_id=f"disc_{uuid.uuid4().hex[:8]}",
            title=title,
            summary=summary,
            so_what=so_what,
            source_name=source.name if source else source_id,
            source_credibility=source.current_credibility if source else 0.5,
            layer=layer,
            actionability=actionability,
            territory=territory,
            **kwargs,
        )
        self.discoveries[disc.discovery_id] = disc

        # Gate check
        if self.governor.gate(disc):
            self.governor.consume(disc)
            logger.info(f"Discovery delivered: [{layer.value}] {title[:50]}")
        else:
            disc.actionability = ActionabilityLevel.ARCHIVE
            logger.info(f"Discovery gated (archived): {title[:50]}")

        return disc

    def get_delivered(self, layer: DiscoveryLayer = None,
                      territory: str = "", limit: int = 20) -> list[Discovery]:
        """Get discoveries that passed the gate."""
        results = [
            d for d in self.discoveries.values()
            if d.actionability != ActionabilityLevel.ARCHIVE
        ]
        if layer:
            results = [d for d in results if d.layer == layer]
        if territory:
            results = [d for d in results if d.territory == territory]
        return sorted(results, key=lambda d: d.discovered_at, reverse=True)[:limit]

    # ── Interaction Tracking ─────────────────────────────────────

    def record_interaction(self, discovery_id: str, interaction: InteractionType):
        """Record Mani's interaction with a discovery. Feeds learning."""
        disc = self.discoveries.get(discovery_id)
        if not disc:
            return

        disc.interaction = interaction
        disc.interaction_timestamp = datetime.now()

        # Update source engagement
        if disc.source_name:
            for src in self.sources.sources.values():
                if src.name == disc.source_name:
                    engaged = interaction in (InteractionType.READ, InteractionType.SAVED,
                                               InteractionType.ACTED_ON, InteractionType.SHARED)
                    self.sources.record_engagement(src.source_id, engaged)
                    break

        # Update territory engagement stats
        if disc.territory:
            if disc.territory not in self._engagement_stats:
                self._engagement_stats[disc.territory] = {t.value: 0 for t in InteractionType}
            self._engagement_stats[disc.territory][interaction.value] += 1

        logger.info(f"Interaction: {interaction.value} on {disc.title[:40]}")

    # ── Pattern Detection ────────────────────────────────────────

    def detect_patterns(self) -> list[Pattern]:
        """
        Detect emerging patterns from 3+ discoveries converging on same theme.
        """
        # Group by territory
        territory_groups: dict[str, list[Discovery]] = {}
        recent_cutoff = datetime.now() - timedelta(days=30)
        for d in self.discoveries.values():
            if d.discovered_at > recent_cutoff and d.territory:
                territory_groups.setdefault(d.territory, []).append(d)

        new_patterns = []
        for territory, discs in territory_groups.items():
            if len(discs) >= 3 and territory not in self.patterns:
                pattern = Pattern(
                    pattern_id=f"pat_{uuid.uuid4().hex[:6]}",
                    label=f"Emerging: {territory}",
                    description=f"{len(discs)} signals in 30 days",
                    discovery_ids=[d.discovery_id for d in discs],
                    signal_count=len(discs),
                    confidence=min(0.95, 0.3 + len(discs) * 0.1),
                    territory=territory,
                )
                self.patterns[pattern.pattern_id] = pattern
                new_patterns.append(pattern)
                logger.info(f"Pattern detected: {territory} ({len(discs)} signals)")

        return new_patterns

    # ── Counterfactual Gap Detection ─────────────────────────────

    def record_gap(self, title: str, where_found: str,
                   root_causes: list[str] = None) -> CounterfactualGap:
        """
        Mani found something valuable elsewhere that we missed.
        Record it, analyse why, and self-correct.
        """
        gap = CounterfactualGap(
            gap_id=f"gap_{uuid.uuid4().hex[:6]}",
            title=title,
            where_found=where_found,
            root_causes=root_causes or [],
        )
        self.gaps.append(gap)
        logger.warning(f"Counterfactual gap: {title} (found via {where_found})")
        return gap

    # ── Convergence Scoring ──────────────────────────────────────

    def calculate_convergence(self, discovery_ids: list[str]) -> float:
        """
        Multi-source convergence confidence.
        3+ sources across different tiers = 1.2× highest individual.
        """
        discs = [self.discoveries.get(did) for did in discovery_ids if did in self.discoveries]
        if not discs:
            return 0.0

        credibilities = [d.source_credibility for d in discs if d]
        if not credibilities:
            return 0.0

        highest = max(credibilities)
        if len(credibilities) >= 3:
            return min(0.99, highest * 1.2)
        elif len(credibilities) >= 2:
            return min(0.95, highest * 1.1)
        return highest

    # ── Morning Briefing ─────────────────────────────────────────

    def get_morning_briefing(self) -> dict:
        """Today's synthesised intelligence narrative."""
        today_start = datetime.now().replace(hour=0, minute=0, second=0)

        signals = [
            d for d in self.discoveries.values()
            if d.layer == DiscoveryLayer.SIGNAL
            and d.actionability != ActionabilityLevel.ARCHIVE
            and d.discovered_at >= today_start - timedelta(days=1)
        ]

        active_patterns = [
            p for p in self.patterns.values()
            if p.confidence > 0.4
        ]

        return {
            "date": datetime.now().strftime("%d %B %Y"),
            "prepared_by": "Cartographer",
            "signal_count": len(signals),
            "signals": [
                {
                    "title": d.title,
                    "so_what": d.so_what,
                    "actionability": d.actionability.value,
                    "territory": d.territory,
                    "source": d.source_name,
                    "credibility": round(d.source_credibility, 2),
                }
                for d in sorted(signals, key=lambda d: d.relevance_score, reverse=True)[:5]
            ],
            "active_patterns": [
                {
                    "label": p.label,
                    "confidence": round(p.confidence, 2),
                    "signal_count": p.signal_count,
                    "action": p.action_recommended,
                }
                for p in active_patterns[:3]
            ],
            "governor": self.governor.status(),
            "gaps_this_month": len([g for g in self.gaps if (datetime.now() - g.timestamp).days <= 30]),
        }

    # ── Engagement Learning ──────────────────────────────────────

    def get_learning_report(self) -> dict:
        """What Mani acts on most, what he ignores."""
        report = {}
        for territory, stats in self._engagement_stats.items():
            total = sum(stats.values())
            if total == 0:
                continue
            acted = stats.get(InteractionType.ACTED_ON.value, 0)
            ignored = stats.get(InteractionType.IGNORED.value, 0)
            report[territory] = {
                "total_interactions": total,
                "action_rate": round(acted / max(total, 1), 2),
                "ignore_rate": round(ignored / max(total, 1), 2),
            }
        return {
            "by_territory": report,
            "top_acted": sorted(
                report.items(), key=lambda x: x[1]["action_rate"], reverse=True
            )[:5],
        }

    def status(self) -> dict:
        return {
            "total_discoveries": len(self.discoveries),
            "delivered": len([d for d in self.discoveries.values() if d.actionability != ActionabilityLevel.ARCHIVE]),
            "archived": len([d for d in self.discoveries.values() if d.actionability == ActionabilityLevel.ARCHIVE]),
            "patterns": len(self.patterns),
            "gaps": len(self.gaps),
            "governor": self.governor.status(),
            "sources": len(self.sources.sources),
        }
