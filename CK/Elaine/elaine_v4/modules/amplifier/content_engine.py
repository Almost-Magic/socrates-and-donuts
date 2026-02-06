"""
Amplifier v2 — Content Engine
Genome evolution, restraint engine, quality gate, authority graph.

Patentable:
- Evolving Content DNA with Closed-Loop Learning
- Strategic Content Suppression for Authority Preservation
- Multi-Model Content Review (Quality Gate)
- Content Authority Graph with Compound Tracking
- Bi-Directional Sales-Content Orchestration

Almost Magic Tech Lab — Patentable IP
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional

from .models import (
    ContentItem, ContentGenome, ContentPerformance,
    ContentStatus, ContentFormat, ContentPillar, ContentObjective,
    EpistemicLevel, QualityGateResult, QualityGateStatus,
    RestraintSignal, RestraintType,
    GeneWeight, AudienceFitness,
    CommentaryOpportunity, WarmLead,
)

logger = logging.getLogger("elaine.amplifier")


class GenomeEvolutionEngine:
    """
    Closed-loop content genome optimisation.
    Learns which hooks, structures, and evidence types work.
    """

    def __init__(self):
        # Global gene weights (learned across all content)
        self.hook_weights: dict[str, GeneWeight] = {
            "contrarian_reframe": GeneWeight("hook", "contrarian_reframe", 0.87, 12),
            "here_is_what_i_learned": GeneWeight("hook", "here_is_what_i_learned", 0.79, 10),
            "question_opener": GeneWeight("hook", "question_opener", 0.64, 8),
            "statistic_lead": GeneWeight("hook", "statistic_lead", 0.58, 6),
            "story_opener": GeneWeight("hook", "story_opener", 0.70, 4),
        }
        self.structure_weights: dict[str, GeneWeight] = {
            "contrarian_stats_analogy_cta": GeneWeight("structure", "contrarian_stats_analogy_cta", 0.81, 8),
            "story_lesson_framework_cta": GeneWeight("structure", "story_lesson_framework_cta", 0.76, 6),
            "problem_solution_proof_cta": GeneWeight("structure", "problem_solution_proof_cta", 0.71, 7),
            "list_format": GeneWeight("structure", "list_format", 0.45, 5),
        }
        self.evidence_weights: dict[str, GeneWeight] = {
            "case_study": GeneWeight("evidence", "case_study", 0.88, 10),
            "named_statistic": GeneWeight("evidence", "named_statistic", 0.79, 8),
            "personal_experience": GeneWeight("evidence", "personal_experience", 0.72, 6),
            "framework_model": GeneWeight("evidence", "framework_model", 0.68, 5),
            "expert_quote": GeneWeight("evidence", "expert_quote", 0.41, 4),
        }

    def update_from_performance(self, content: ContentItem):
        """Update gene weights from content performance data."""
        score = content.performance.multi_objective_score
        genome = content.genome

        # Update hook weight
        hook_type = genome.argument_structure.split("_")[0] if genome.argument_structure else ""
        if hook_type in self.hook_weights:
            self.hook_weights[hook_type].update(score / 10.0)

        # Update structure weight
        if genome.argument_structure in self.structure_weights:
            self.structure_weights[genome.argument_structure].update(score / 10.0)

        # Update evidence weights
        for ev in genome.evidence:
            ev_type = ev.get("type", "")
            if ev_type in self.evidence_weights:
                self.evidence_weights[ev_type].update(score / 10.0)

        logger.info(f"Genome evolved from: {content.title[:40]} (score: {score:.1f})")

    def recommend_genome(self, pillar: ContentPillar, objective: ContentObjective) -> dict:
        """Recommend best gene combination for next content."""
        best_hook = max(self.hook_weights.values(), key=lambda g: g.effectiveness)
        best_structure = max(self.structure_weights.values(), key=lambda g: g.effectiveness)
        best_evidence = sorted(self.evidence_weights.values(), key=lambda g: g.effectiveness, reverse=True)[:2]

        return {
            "recommended_hook": best_hook.value,
            "hook_effectiveness": round(best_hook.effectiveness, 2),
            "recommended_structure": best_structure.value,
            "structure_effectiveness": round(best_structure.effectiveness, 2),
            "recommended_evidence": [{"type": e.value, "effectiveness": round(e.effectiveness, 2)} for e in best_evidence],
            "pillar": pillar.value,
            "objective": objective.value,
        }

    def get_evolution_report(self) -> dict:
        """Monthly gene evolution report."""
        return {
            "hooks": sorted(
                [{"type": g.value, "effectiveness": round(g.effectiveness, 2), "samples": g.sample_size}
                 for g in self.hook_weights.values()],
                key=lambda x: x["effectiveness"], reverse=True,
            ),
            "structures": sorted(
                [{"type": g.value, "effectiveness": round(g.effectiveness, 2), "samples": g.sample_size}
                 for g in self.structure_weights.values()],
                key=lambda x: x["effectiveness"], reverse=True,
            ),
            "evidence": sorted(
                [{"type": g.value, "effectiveness": round(g.effectiveness, 2), "samples": g.sample_size}
                 for g in self.evidence_weights.values()],
                key=lambda x: x["effectiveness"], reverse=True,
            ),
        }


class RestraintEngine:
    """
    Strategic Content Suppression.
    Knows when NOT to publish.
    """

    def __init__(self):
        self._topic_history: dict[str, list[datetime]] = {}  # pillar → publish dates
        self._weekly_count: int = 0
        self._last_reset: datetime = datetime.now()

    def check_restraints(self, content: ContentItem,
                         red_giant_count: int = 0) -> list[RestraintSignal]:
        """Run all restraint checks. Returns list of signals (empty = clear)."""
        signals = []

        # Red Giant suppression
        if red_giant_count >= 3:
            signals.append(RestraintSignal(
                restraint_type=RestraintType.RED_GIANT_ACTIVE,
                message=f"{red_giant_count} Red Giants active. Suppress non-urgent content. Focus on delivery.",
                severity="block",
            ))

        # Overexposure check
        pillar = content.genome.pillar.value
        recent = self._topic_history.get(pillar, [])
        recent_7d = [d for d in recent if (datetime.now() - d).days <= 7]
        if len(recent_7d) >= 3:
            signals.append(RestraintSignal(
                restraint_type=RestraintType.OVEREXPOSURE,
                message=f"You've published {len(recent_7d)} posts on {pillar} this week. Audience is saturating. Wait or switch topic.",
                severity="warning",
            ))

        recent_30d = [d for d in recent if (datetime.now() - d).days <= 30]
        if len(recent_30d) >= 7:
            signals.append(RestraintSignal(
                restraint_type=RestraintType.OVEREXPOSURE,
                message=f"{len(recent_30d)} posts on {pillar} this month. Audience saturation risk. Shift to adjacent topic.",
                severity="warning",
            ))

        # Silence premium
        if self._weekly_count >= 7:
            signals.append(RestraintSignal(
                restraint_type=RestraintType.SILENCE_PREMIUM,
                message="You've posted every day this week. Skipping tomorrow increases perceived selectivity.",
                severity="advisory",
            ))

        return signals

    def record_publish(self, content: ContentItem):
        pillar = content.genome.pillar.value
        self._topic_history.setdefault(pillar, []).append(datetime.now())
        self._weekly_count += 1

    def reset_weekly(self):
        self._weekly_count = 0
        self._last_reset = datetime.now()

    def get_overexposure_report(self) -> dict:
        report = {}
        for pillar, dates in self._topic_history.items():
            recent_7d = len([d for d in dates if (datetime.now() - d).days <= 7])
            recent_30d = len([d for d in dates if (datetime.now() - d).days <= 30])
            status = "clear"
            if recent_7d >= 3:
                status = "saturating"
            elif recent_30d >= 5:
                status = "moderate"
            report[pillar] = {
                "posts_7d": recent_7d,
                "posts_30d": recent_30d,
                "status": status,
            }
        return report


class QualityGate:
    """
    Multi-check content review before publish.
    Integrates with Thinking Frameworks Engine.
    """

    def __init__(self, thinking_engine=None):
        self.thinking_engine = thinking_engine

    def review(self, content: ContentItem) -> QualityGateResult:
        """Run full quality gate on content."""
        result = QualityGateResult()
        warnings = []
        suggestions = []

        # 1. Epistemic alignment
        if content.genome.certainty_level == EpistemicLevel.CONVICTION:
            evidence_count = len(content.genome.evidence)
            if evidence_count < 2:
                warnings.append(
                    "Stated as CONVICTION but only has {0} evidence items. "
                    "Consider PROVISIONAL framing or add more evidence.".format(evidence_count)
                )
                result.epistemic_alignment = "warning"
            else:
                result.epistemic_alignment = "pass"
        else:
            result.epistemic_alignment = "pass"

        # 2. Voice consistency
        result.voice_consistency = content.genome.voice_score
        if content.genome.voice_score < 80:
            warnings.append(
                f"Voice consistency score: {content.genome.voice_score:.0f}/100. "
                "Below threshold. Review tone and phrasing."
            )

        # 3. Client sensitivity (basic check)
        sensitive_terms = ["client", "confidential", "internal", "nda"]
        body_lower = content.body.lower()
        for term in sensitive_terms:
            if term in body_lower:
                warnings.append(f"Content contains '{term}' — verify no client confidentiality breach.")
                result.client_sensitivity = "warning"
                break
        else:
            result.client_sensitivity = "pass"

        # 4. Brand alignment
        result.brand_alignment = "pass"

        # 5. Factual accuracy placeholder
        result.factual_accuracy = "pass"

        # 6. Audience fitness prediction placeholder
        result.audience_fitness_prediction = "pass"

        # 7. Thinking Frameworks integration
        if self.thinking_engine and content.genome.objective in (
            ContentObjective.AUTHORITY, ContentObjective.PIPELINE
        ):
            thinking_result = self.thinking_engine.amplifier_content_review(
                content.title,
                is_public=(content.genome.format != ContentFormat.CLIENT_EMAIL),
            )
            result.thinking_frameworks_applied = [
                f.value for f in thinking_result.frameworks_applied
            ]
            if thinking_result.warnings:
                warnings.extend(thinking_result.warnings)

        result.warnings = warnings
        result.suggestions = suggestions

        # Determine gate status
        blocks = [w for w in warnings if "BLOCK" in w.upper()]
        if blocks:
            result.gate_status = QualityGateStatus.FAIL
        elif warnings:
            result.gate_status = QualityGateStatus.PASS_WITH_EDITS
        else:
            result.gate_status = QualityGateStatus.PASS

        logger.info(f"Quality gate: {content.title[:40]} → {result.gate_status.value}")
        return result


class ContentEngine:
    """
    Main Amplifier engine. Manages content lifecycle, genome evolution,
    restraint, quality gate, and authority graph.
    """

    def __init__(self, thinking_engine=None):
        self.items: dict[str, ContentItem] = {}
        self.genome_engine = GenomeEvolutionEngine()
        self.restraint_engine = RestraintEngine()
        self.quality_gate = QualityGate(thinking_engine)
        self.warm_leads: list[WarmLead] = []
        self.commentary_queue: list[CommentaryOpportunity] = []

    # ── Content Lifecycle ────────────────────────────────────────

    def create_idea(self, title: str, thesis: str, pillar: ContentPillar,
                    certainty: EpistemicLevel = EpistemicLevel.CONVICTION,
                    objective: ContentObjective = ContentObjective.AUTHORITY,
                    **kwargs) -> ContentItem:
        """Capture a new content idea into the vault."""
        genome = ContentGenome(
            thesis=thesis,
            pillar=pillar,
            certainty_level=certainty,
            objective=objective,
        )
        item = ContentItem(
            title=title,
            genome=genome,
            status=ContentStatus.IDEA,
            **kwargs,
        )
        self.items[item.content_id] = item
        logger.info(f"Idea captured: {title[:50]}")
        return item

    def advance_status(self, content_id: str, new_status: ContentStatus):
        item = self.items.get(content_id)
        if item:
            old = item.status
            item.status = new_status
            logger.info(f"Content advanced: {item.title[:40]} {old.value} → {new_status.value}")

    def run_quality_gate(self, content_id: str) -> QualityGateResult:
        item = self.items.get(content_id)
        if not item:
            return QualityGateResult(gate_status=QualityGateStatus.FAIL, warnings=["Content not found"])
        result = self.quality_gate.review(item)
        item.quality_gate = result
        item.status = ContentStatus.QUALITY_GATE
        return result

    def check_restraints(self, content_id: str, red_giant_count: int = 0) -> list[dict]:
        item = self.items.get(content_id)
        if not item:
            return []
        signals = self.restraint_engine.check_restraints(item, red_giant_count)
        item.restraint_signals = signals
        return [{"type": s.restraint_type.value, "message": s.message, "severity": s.severity} for s in signals]

    def publish(self, content_id: str) -> bool:
        item = self.items.get(content_id)
        if not item:
            return False
        item.status = ContentStatus.PUBLISHED
        item.published_date = datetime.now()
        self.restraint_engine.record_publish(item)
        logger.info(f"Published: {item.title[:40]}")
        return True

    def record_performance(self, content_id: str, **kwargs):
        item = self.items.get(content_id)
        if not item:
            return
        perf = item.performance
        for k, v in kwargs.items():
            if hasattr(perf, k):
                setattr(perf, k, v)

        # Trigger genome evolution
        self.genome_engine.update_from_performance(item)

    # ── Idea Vault ───────────────────────────────────────────────

    def get_ideas(self, pillar: ContentPillar = None, limit: int = 20) -> list[ContentItem]:
        items = [i for i in self.items.values() if i.status == ContentStatus.IDEA]
        if pillar:
            items = [i for i in items if i.genome.pillar == pillar]
        return sorted(items, key=lambda i: i.created_at, reverse=True)[:limit]

    def get_published(self, limit: int = 20) -> list[ContentItem]:
        items = [i for i in self.items.values() if i.status == ContentStatus.PUBLISHED]
        return sorted(items, key=lambda i: i.published_date or i.created_at, reverse=True)[:limit]

    # ── Content Calendar ─────────────────────────────────────────

    def suggest_next_content(self, red_giant_count: int = 0) -> dict:
        """AI-suggested next content based on genome learning and restraints."""
        # Check if we should even publish
        if red_giant_count >= 3:
            return {"suggestion": "HOLD — Red Giant active. Focus on delivery.", "blocked": True}

        overexposure = self.restraint_engine.get_overexposure_report()

        # Find least-saturated pillar
        clear_pillars = [p for p, info in overexposure.items() if info["status"] == "clear"]
        if not clear_pillars:
            clear_pillars = [p.value for p in ContentPillar]

        target_pillar = ContentPillar(clear_pillars[0]) if clear_pillars else ContentPillar.THOUGHT_LEADERSHIP

        # Get genome recommendation
        recommendation = self.genome_engine.recommend_genome(target_pillar, ContentObjective.AUTHORITY)

        return {
            "blocked": False,
            "recommended_pillar": target_pillar.value,
            "genome_recommendation": recommendation,
            "overexposure_status": overexposure,
            "vault_ideas_available": len([
                i for i in self.items.values()
                if i.status == ContentStatus.IDEA and i.genome.pillar == target_pillar
            ]),
        }

    # ── Commentary Swarm ─────────────────────────────────────────

    def add_commentary_opportunity(self, poi_name: str, post_topic: str,
                                    suggested_comment: str, why: str = "",
                                    **kwargs) -> CommentaryOpportunity:
        opp = CommentaryOpportunity(
            poi_name=poi_name,
            post_topic=post_topic,
            suggested_comment=suggested_comment,
            why=why,
            **kwargs,
        )
        self.commentary_queue.append(opp)
        return opp

    def get_commentary_queue(self) -> list[dict]:
        return [
            {
                "poi": c.poi_name,
                "topic": c.post_topic,
                "comment": c.suggested_comment,
                "why": c.why,
                "objective": c.objective.value,
            }
            for c in self.commentary_queue[-10:]
        ]

    # ── Warm Lead Detection ──────────────────────────────────────

    def detect_warm_lead(self, name: str, company: str, engagement: list[str],
                          intent_score: float, **kwargs) -> WarmLead:
        lead = WarmLead(
            name=name, company=company,
            engagement_pattern=engagement,
            intent_score=intent_score,
            **kwargs,
        )
        self.warm_leads.append(lead)
        logger.info(f"Warm lead detected: {name} ({company}) — intent: {intent_score:.0f}")
        return lead

    # ── Authority Graph ──────────────────────────────────────────

    def get_authority_graph(self) -> dict:
        """Content relationship graph with gap analysis."""
        published = [i for i in self.items.values() if i.status == ContentStatus.PUBLISHED]
        ideas = [i for i in self.items.values() if i.status == ContentStatus.IDEA]

        # Count by pillar
        pillar_counts = {}
        for item in published:
            p = item.genome.pillar.value
            pillar_counts[p] = pillar_counts.get(p, 0) + 1

        # Gap analysis
        gaps = []
        for pillar in ContentPillar:
            count = pillar_counts.get(pillar.value, 0)
            if count < 3:
                gaps.append(f"Weak coverage: {pillar.value} ({count} published)")

        # Compound leaders
        compound_leaders = sorted(
            published,
            key=lambda i: i.performance.compound_score,
            reverse=True,
        )[:5]

        return {
            "total_published": len(published),
            "total_ideas": len(ideas),
            "by_pillar": pillar_counts,
            "gaps": gaps,
            "compound_leaders": [
                {"title": i.title, "compound_score": i.performance.compound_score}
                for i in compound_leaders
            ],
        }

    # ── Reporting ────────────────────────────────────────────────

    def get_morning_briefing_data(self) -> dict:
        """Data for Elaine's morning briefing — content section."""
        return {
            "ideas_in_vault": len([i for i in self.items.values() if i.status == ContentStatus.IDEA]),
            "in_pipeline": len([i for i in self.items.values() if i.status in (ContentStatus.DRAFT, ContentStatus.REVIEW, ContentStatus.QUALITY_GATE)]),
            "commentary_opportunities": len(self.commentary_queue),
            "warm_leads": len(self.warm_leads),
            "next_suggestion": self.suggest_next_content(),
            "overexposure": self.restraint_engine.get_overexposure_report(),
        }

    def status(self) -> dict:
        status_counts = {}
        for item in self.items.values():
            status_counts[item.status.value] = status_counts.get(item.status.value, 0) + 1
        return {
            "total_items": len(self.items),
            "by_status": status_counts,
            "warm_leads": len(self.warm_leads),
            "commentary_queue": len(self.commentary_queue),
            "genome_evolution": self.genome_engine.get_evolution_report(),
        }
