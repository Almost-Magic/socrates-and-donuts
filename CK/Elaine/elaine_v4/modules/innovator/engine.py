"""
App Innovator + Beast — Innovation Engine
Cross-module opportunity detection with structured research delegation.

Patentable:
- Autonomous Opportunity Detection for Product Innovation
- Beast Integration Protocol for Market Validation
- Cross-Module Signal Convergence for Innovation Scoring

Almost Magic Tech Lab — Patentable IP
"""

import logging
from datetime import datetime
from typing import Optional

from .models import (
    Opportunity, InnovationType, InnovationStatus, InnovationSignal,
    SignalSource, Recommendation,
    ResearchBrief, ResearchQuestion, ResearchType, ResearchStatus,
    ResearchResult, ResearchFinding,
)

logger = logging.getLogger("elaine.innovator")


# ── Seeded Opportunities (from Mani's ecosystem) ────────────────

SEED_OPPORTUNITIES = [
    {
        "title": "6-Week Governance Sprint Package",
        "type": InnovationType.SERVICE_PACKAGE,
        "description": "Fixed scope, fixed price ($15K) AI governance assessment. Board-ready in 6 weeks.",
        "signals": [
            InnovationSignal(SignalSource.CHRONICLE, "4 of 6 prospects mentioned 'board deadline'", 0.85),
            InnovationSignal(SignalSource.CARTOGRAPHER, "3 articles on fast-track governance trending", 0.70),
            InnovationSignal(SignalSource.AMPLIFIER, "'Speed' content gets 2.5x engagement", 0.75),
        ],
        "revenue": "$180K annually (12 clients × $15K)",
        "recommendation": Recommendation.BUILD,
    },
    {
        "title": "AI Policy-as-a-Service",
        "type": InnovationType.CUSTOMER_PRODUCT,
        "description": "Recurring AI policy maintenance. Monitor regulatory changes, update client policies monthly.",
        "signals": [
            InnovationSignal(SignalSource.CHRONICLE, "3 clients asked 'can you maintain our AI policy?'", 0.80),
            InnovationSignal(SignalSource.CARTOGRAPHER, "Regulatory changes occurring every 6-8 weeks", 0.75),
        ],
        "revenue": "$24K/year per client × target 20 clients = $480K ARR",
        "recommendation": Recommendation.INVESTIGATE,
    },
    {
        "title": "Proposal Generator",
        "type": InnovationType.INTERNAL_TOOL,
        "description": "Automated proposal generation. 70% template + 30% custom from meeting intelligence.",
        "signals": [
            InnovationSignal(SignalSource.GRAVITY, "Mani spends avg 4.5 hours per proposal", 0.90),
            InnovationSignal(SignalSource.SENTINEL, "70% of proposal content is templated patterns", 0.80),
        ],
        "revenue": "36 hours/month saved (12 proposals × 3 hours)",
        "recommendation": Recommendation.BUILD,
    },
    {
        "title": "Compliance Gap Checker Tool",
        "type": InnovationType.CUSTOMER_PRODUCT,
        "description": "Self-service Essential Eight / ISO 42001 gap assessment tool for SMBs.",
        "signals": [
            InnovationSignal(SignalSource.SENTINEL, "Every client fails the same 3 compliance checks", 0.85),
            InnovationSignal(SignalSource.CARTOGRAPHER, "250K SMBs in ANZ need governance — most can't afford full assessment", 0.70),
            InnovationSignal(SignalSource.AMPLIFIER, "Compliance content has highest authority score", 0.65),
        ],
        "revenue": "$99/month SaaS × 500 users = $594K ARR",
        "recommendation": Recommendation.INVESTIGATE,
    },
]


class InnovationEngine:
    """
    Cross-module opportunity detection engine.
    Synthesises signals from Chronicle, Cartographer, Amplifier,
    Sentinel, Gravity, and Constellation to identify innovations.
    Delegates market research to Beast.
    """

    def __init__(self):
        self.opportunities: dict[str, Opportunity] = {}
        self.research_briefs: dict[str, ResearchBrief] = {}
        self.research_results: dict[str, ResearchResult] = {}

        self._seed_opportunities()

    def _seed_opportunities(self):
        for seed in SEED_OPPORTUNITIES:
            opp = Opportunity(
                title=seed["title"],
                innovation_type=seed["type"],
                description=seed["description"],
                signals=seed["signals"],
                estimated_revenue=seed["revenue"],
                recommendation=seed["recommendation"],
                confidence=0.0,  # Will be calculated
            )
            opp.confidence = opp.composite_confidence
            self.opportunities[opp.opportunity_id] = opp

    # ── Opportunity Detection ────────────────────────────────────

    def add_signal(self, opportunity_id: str, source: SignalSource,
                   evidence: str, strength: float = 0.5):
        """Add a new signal to an existing opportunity."""
        opp = self.opportunities.get(opportunity_id)
        if opp:
            opp.signals.append(InnovationSignal(source, evidence, strength))
            opp.confidence = opp.composite_confidence
            logger.info(f"Signal added to {opp.title}: {source.value} ({strength:.2f})")

    def create_opportunity(self, title: str, innovation_type: InnovationType,
                           description: str, signals: list[dict] = None,
                           estimated_revenue: str = "") -> Opportunity:
        """Create a new opportunity from detected signals."""
        parsed_signals = []
        for s in (signals or []):
            parsed_signals.append(InnovationSignal(
                source=SignalSource(s.get("source", "chronicle")),
                evidence=s.get("evidence", ""),
                strength=s.get("strength", 0.5),
            ))

        opp = Opportunity(
            title=title,
            innovation_type=innovation_type,
            description=description,
            signals=parsed_signals,
            estimated_revenue=estimated_revenue,
        )
        opp.confidence = opp.composite_confidence
        self.opportunities[opp.opportunity_id] = opp
        logger.info(f"Opportunity created: {title} (confidence: {opp.confidence:.2f})")
        return opp

    def detect_from_modules(self, module_data: dict) -> list[Opportunity]:
        """
        Scan data from all modules and detect new opportunities.
        module_data = {
            "chronicle": {"hot_buttons": [...], "repeated_questions": [...]},
            "cartographer": {"negative_space": [...], "emerging_topics": [...]},
            "amplifier": {"high_engagement_topics": [...], "authority_leaders": [...]},
            "sentinel": {"common_failures": [...], "pattern_alerts": [...]},
            "gravity": {"time_sinks": [...], "repeated_tasks": [...]},
            "constellation": {"competitor_moves": [...], "peer_launches": [...]},
        }
        """
        new_opportunities = []

        # Chronicle: repeated client questions → product opportunity
        chronicle = module_data.get("chronicle", {})
        for question in chronicle.get("repeated_questions", []):
            existing = self._find_similar(question)
            if existing:
                self.add_signal(existing.opportunity_id, SignalSource.CHRONICLE, question, 0.7)
            else:
                opp = self.create_opportunity(
                    title=f"Product from client need: {question[:50]}",
                    innovation_type=InnovationType.CUSTOMER_PRODUCT,
                    description=f"Multiple clients asking: '{question}'",
                    signals=[{"source": "chronicle", "evidence": question, "strength": 0.7}],
                )
                new_opportunities.append(opp)

        # Cartographer: negative space → first-mover opportunity
        cartographer = module_data.get("cartographer", {})
        for gap in cartographer.get("negative_space", []):
            opp = self.create_opportunity(
                title=f"Market gap: {gap[:50]}",
                innovation_type=InnovationType.CUSTOMER_PRODUCT,
                description=f"Cartographer detected: nobody is offering '{gap}' in ANZ",
                signals=[{"source": "cartographer", "evidence": gap, "strength": 0.6}],
            )
            new_opportunities.append(opp)

        # Gravity: time sinks → internal tool opportunity
        gravity = module_data.get("gravity", {})
        for task in gravity.get("time_sinks", []):
            opp = self.create_opportunity(
                title=f"Automate: {task[:50]}",
                innovation_type=InnovationType.INTERNAL_TOOL,
                description=f"Mani spends significant time on '{task}' — automate it",
                signals=[{"source": "gravity", "evidence": task, "strength": 0.8}],
            )
            new_opportunities.append(opp)

        return new_opportunities

    def _find_similar(self, text: str) -> Optional[Opportunity]:
        """Find an existing opportunity that matches this signal."""
        text_lower = text.lower()
        for opp in self.opportunities.values():
            if any(word in opp.title.lower() for word in text_lower.split() if len(word) > 4):
                return opp
        return None

    # ── Mani's Decision ──────────────────────────────────────────

    def decide(self, opportunity_id: str, decision: str, notes: str = ""):
        """Record Mani's decision on an opportunity."""
        opp = self.opportunities.get(opportunity_id)
        if not opp:
            return
        opp.mani_decision = decision
        opp.decided_at = datetime.now()
        status_map = {
            "build": InnovationStatus.APPROVED,
            "reject": InnovationStatus.REJECTED,
            "research": InnovationStatus.RESEARCH_PENDING,
            "defer": InnovationStatus.DETECTED,
        }
        opp.status = status_map.get(decision, InnovationStatus.DETECTED)
        logger.info(f"Opportunity {opp.title}: Mani decided → {decision}")

    # ── Beast Research Delegation ────────────────────────────────

    def create_research_brief(self, opportunity_id: str,
                               questions: list[dict],
                               deadline_days: int = 5) -> ResearchBrief:
        """Create a structured research brief for Beast."""
        opp = self.opportunities.get(opportunity_id)
        if not opp:
            return ResearchBrief()

        parsed_questions = [
            ResearchQuestion(
                question=q.get("question", ""),
                research_type=ResearchType(q.get("type", "competitor_analysis")),
                priority=q.get("priority", 1),
            )
            for q in questions
        ]

        brief = ResearchBrief(
            opportunity_id=opportunity_id,
            title=f"Research: {opp.title}",
            context=opp.description,
            questions=parsed_questions,
            deadline_days=deadline_days,
        )

        self.research_briefs[brief.brief_id] = brief
        opp.status = InnovationStatus.RESEARCH_PENDING
        logger.info(f"Beast brief created: {brief.title} ({len(parsed_questions)} questions)")
        return brief

    def auto_generate_brief(self, opportunity_id: str) -> ResearchBrief:
        """Auto-generate research questions based on opportunity type."""
        opp = self.opportunities.get(opportunity_id)
        if not opp:
            return ResearchBrief()

        questions = []

        # Always: competitor analysis
        questions.append({
            "question": f"Who offers similar products/services to '{opp.title}' in ANZ? Price points, scope, reviews?",
            "type": "competitor_analysis",
            "priority": 1,
        })

        # Customer product: TAM + regulatory
        if opp.innovation_type in (InnovationType.CUSTOMER_PRODUCT, InnovationType.SERVICE_PACKAGE):
            questions.append({
                "question": f"How many ANZ SMBs would pay for '{opp.title}'? Estimated TAM?",
                "type": "tam_estimation",
                "priority": 1,
            })
            questions.append({
                "question": "What regulatory requirements are coming in 2026-2027 that create urgency?",
                "type": "regulatory_pipeline",
                "priority": 2,
            })
            questions.append({
                "question": "What claims can AMTL make that competitors can't? (ISO certs, speed, quality)",
                "type": "positioning_gaps",
                "priority": 2,
            })

        # Internal tool: time savings validation
        if opp.innovation_type == InnovationType.INTERNAL_TOOL:
            questions.append({
                "question": f"What existing tools solve '{opp.title}'? Build vs buy analysis.",
                "type": "competitor_analysis",
                "priority": 1,
            })

        return self.create_research_brief(opportunity_id, questions)

    def submit_research_result(self, brief_id: str,
                                findings: list[dict],
                                recommendation: str = "investigate",
                                summary: str = "",
                                risks: list[str] = None) -> ResearchResult:
        """Submit Beast research results."""
        brief = self.research_briefs.get(brief_id)
        if not brief:
            return ResearchResult()

        parsed_findings = [
            ResearchFinding(
                question_answered=f.get("question", ""),
                finding=f.get("finding", ""),
                confidence=f.get("confidence", 0.7),
                sources=f.get("sources", []),
                data_points=f.get("data_points", {}),
            )
            for f in findings
        ]

        result = ResearchResult(
            brief_id=brief_id,
            findings=parsed_findings,
            recommendation=Recommendation(recommendation),
            executive_summary=summary,
            risks=risks or [],
        )

        self.research_results[brief_id] = result
        brief.status = ResearchStatus.COMPLETE
        brief.completed_at = datetime.now()

        # Update opportunity with Beast findings
        opp = self.opportunities.get(brief.opportunity_id)
        if opp:
            opp.status = InnovationStatus.RESEARCH_COMPLETE
            opp.recommendation = result.recommendation
            # Add Beast signal
            avg_confidence = sum(f.confidence for f in parsed_findings) / max(len(parsed_findings), 1)
            opp.signals.append(InnovationSignal(
                SignalSource.BEAST,
                f"Beast research: {summary[:100]}",
                avg_confidence,
            ))
            opp.confidence = opp.composite_confidence

        logger.info(f"Beast research complete: {brief.title} → {recommendation}")
        return result

    # ── Opportunity Ranking ──────────────────────────────────────

    def get_ranked_opportunities(self, status: str = "") -> list[dict]:
        """Rank opportunities by composite confidence and multi-source bonus."""
        opps = list(self.opportunities.values())
        if status:
            opps = [o for o in opps if o.status.value == status]

        ranked = sorted(opps, key=lambda o: o.composite_confidence, reverse=True)
        return [
            {
                "id": o.opportunity_id,
                "title": o.title,
                "type": o.innovation_type.value,
                "status": o.status.value,
                "confidence": round(o.composite_confidence, 2),
                "signal_count": o.signal_count,
                "multi_source": o.multi_source,
                "sources": list(set(s.source.value for s in o.signals)),
                "recommendation": o.recommendation.value,
                "revenue": o.estimated_revenue,
                "description": o.description,
            }
            for o in ranked
        ]

    def get_monthly_report(self) -> dict:
        """Monthly innovation report for Mani."""
        all_opps = list(self.opportunities.values())
        by_type = {}
        for o in all_opps:
            t = o.innovation_type.value
            by_type.setdefault(t, []).append(o.title)

        return {
            "total_opportunities": len(all_opps),
            "by_type": {k: len(v) for k, v in by_type.items()},
            "by_status": {
                s.value: len([o for o in all_opps if o.status == s])
                for s in InnovationStatus
                if any(o.status == s for o in all_opps)
            },
            "top_3": [
                {"title": o.title, "confidence": round(o.composite_confidence, 2),
                 "recommendation": o.recommendation.value}
                for o in sorted(all_opps, key=lambda o: o.composite_confidence, reverse=True)[:3]
            ],
            "research_pending": len([b for b in self.research_briefs.values() if b.status == ResearchStatus.QUEUED]),
            "research_complete": len([b for b in self.research_briefs.values() if b.status == ResearchStatus.COMPLETE]),
        }

    def get_morning_briefing_data(self) -> dict:
        high_confidence = [
            o for o in self.opportunities.values()
            if o.composite_confidence >= 0.7 and o.status == InnovationStatus.DETECTED
        ]
        research_pending = [
            b for b in self.research_briefs.values()
            if b.status in (ResearchStatus.QUEUED, ResearchStatus.IN_PROGRESS)
        ]
        return {
            "unreviewed_opportunities": len(high_confidence),
            "top_opportunity": high_confidence[0].title if high_confidence else None,
            "research_pending": len(research_pending),
        }

    def status(self) -> dict:
        return {
            "opportunities": len(self.opportunities),
            "research_briefs": len(self.research_briefs),
            "research_complete": len(self.research_results),
            "approved": len([o for o in self.opportunities.values() if o.status == InnovationStatus.APPROVED]),
        }
