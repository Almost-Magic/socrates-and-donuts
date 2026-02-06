"""
Sentinel v2 — Trust Engine
Core quality review with risk economics, audience modelling,
position integrity, and multi-perspective adversarial review.

Patentable:
- Audience-Aware Multi-Dimensional Trust Surface
- Risk Economics Engine for Quality Governance
- Strategic Intent-Aware Quality Review
- Position Integrity Graph
- Multi-Perspective Adversarial Review Council
- Adaptive Governance via Override Outcome Analysis

Almost Magic Tech Lab — Patentable IP
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Optional

from .models import (
    QualityAudit, TrustSurface, GovernanceProfile, StrategicIntent,
    AudienceTrustPrediction, RiskEconomicsItem, RiskSeverity,
    PositionConflict, TrackedPosition,
    PerspectiveReview,
    OverrideRecord, OverrideOutcome,
    IncidentRecord, StrategicException,
    StalenessItem, CredibilitySuggestion, ResilienceLevel,
    AuditVerdict, PROFILE_GATE_LEVELS, HALF_LIVES, INTENT_WEIGHTS,
)

logger = logging.getLogger("elaine.sentinel")


# ── Dangerous Language Patterns ──────────────────────────────────

GUARANTEE_PATTERNS = [
    (r"\bensure\b", "ensure", "'Ensure' implies a guarantee. Use 'evaluate readiness for' or 'work toward'"),
    (r"\bguarantee\b", "guarantee", "'Guarantee' creates legal liability. Use 'aim to' or 'designed to'"),
    (r"\bwill achieve\b", "will achieve", "'Will achieve' overpromises. Use 'is designed to support'"),
    (r"\bcertify\b", "certify", "'Certify' may imply you're a certification body. Clarify your role."),
    (r"\bcompliant\b", "compliant", "'Compliant' may overstate. Consider 'aligned with' or 'ready for'"),
]

AGGRESSIVE_PATTERNS = [
    (r"\bobviously\b", "obviously", "Can feel condescending. Remove or soften."),
    (r"\bsimply\b", "simply", "May trivialise the reader's concerns. Remove."),
    (r"\bshould\b", "should", "May feel prescriptive. Consider 'consider' or 'recommend'"),
]

SENSITIVE_TERMS = [
    "confidential", "nda", "internal only", "not for distribution",
    "client name", "proprietary",
]


class TrustEngine:
    """
    Core Sentinel engine. Reviews content across 9 trust dimensions,
    applies risk economics, audience modelling, and position integrity.
    """

    def __init__(self, thinking_engine=None):
        self.thinking_engine = thinking_engine
        self.audits: dict[str, QualityAudit] = {}
        self.positions: list[TrackedPosition] = []
        self.overrides: list[OverrideRecord] = []
        self.incidents: list[IncidentRecord] = []
        self.exceptions: list[StrategicException] = []

        # Error pattern tracking
        self._error_patterns: dict[str, int] = {}
        self._override_outcomes: dict[str, int] = {"correct": 0, "neutral": 0, "incorrect": 0}

        self._seed_positions()

    def _seed_positions(self):
        """Seed known positions from Mani's corpus."""
        seeds = [
            ("We never guarantee compliance outcomes", "brand_standard", "methodology"),
            ("AI governance is applicable to organisations of all sizes", "blog_content", "capability"),
            ("ISO 42001 provides a management system framework", "standard_reference", "methodology"),
            ("Our assessments are designed to identify gaps, not certify", "proposal_template", "methodology"),
        ]
        for claim, source, category in seeds:
            self.positions.append(TrackedPosition(
                claim=claim, source_document=source, category=category,
            ))

    # ── Profile Auto-Detection ───────────────────────────────────

    def detect_profile(self, content: str, recipient: str = "",
                       has_pricing: bool = False, has_compliance_refs: bool = False,
                       is_public: bool = False) -> GovernanceProfile:
        """Auto-detect governance profile from content signals."""
        content_lower = content.lower()

        # Regulated output
        if any(term in content_lower for term in ["iso 42001", "iso 27001", "essential eight", "audit report", "compliance assessment"]):
            if has_pricing or "proposal" in content_lower:
                return GovernanceProfile.SALES_MATERIALS
            return GovernanceProfile.REGULATED_OUTPUT

        # Public statement
        if is_public or any(term in content_lower for term in ["press release", "media statement"]):
            return GovernanceProfile.PUBLIC_STATEMENT

        # Sales materials
        if has_pricing or "proposal" in content_lower or "pricing" in content_lower:
            return GovernanceProfile.SALES_MATERIALS

        # Social content
        if any(term in content_lower for term in ["linkedin", "newsletter", "blog post"]):
            return GovernanceProfile.SOCIAL_CONTENT

        # Client communication
        if recipient and "@" in recipient:
            return GovernanceProfile.CLIENT_COMMUNICATION

        return GovernanceProfile.INTERNAL

    def detect_intent(self, content: str, profile: GovernanceProfile) -> StrategicIntent:
        """Infer strategic intent from content and profile."""
        content_lower = content.lower()

        if profile == GovernanceProfile.INTERNAL:
            return StrategicIntent.INTERNAL_COMMS
        if profile in (GovernanceProfile.SOCIAL_CONTENT, GovernanceProfile.PUBLIC_STATEMENT):
            return StrategicIntent.THOUGHT_LEADERSHIP
        if "apolog" in content_lower or "understand your concern" in content_lower:
            return StrategicIntent.DE_ESCALATE
        if "proposal" in content_lower or "pricing" in content_lower:
            return StrategicIntent.CLOSE_DEAL
        if "follow" in content_lower or "great meeting" in content_lower or "touch base" in content_lower:
            return StrategicIntent.BUILD_RELATIONSHIP

        return StrategicIntent.BUILD_RELATIONSHIP

    # ── Core Review ──────────────────────────────────────────────

    def review(self, content: str, title: str = "",
               document_type: str = "", recipient: str = "",
               audience_context: dict = None,
               has_pricing: bool = False, is_public: bool = False,
               ) -> QualityAudit:
        """
        Full quality review. Auto-detects profile and intent.
        Applies all nine trust dimensions + risk economics + thinking frameworks.
        """
        has_compliance = bool(re.search(r"iso \d{5}|essential eight|compliance|governance", content, re.I))

        profile = self.detect_profile(content, recipient, has_pricing, has_compliance, is_public)
        intent = self.detect_intent(content, profile)
        gate_level = PROFILE_GATE_LEVELS[profile]

        audit = QualityAudit(
            document_title=title or "Untitled",
            document_type=document_type,
            governance_profile=profile,
            strategic_intent=intent,
        )

        # ── 1. Trust Surface scoring ────────────────────────────
        trust = TrustSurface()

        # Accuracy: check for guarantee/overstatement patterns
        guarantee_issues = []
        for pattern, term, message in GUARANTEE_PATTERNS:
            if re.search(pattern, content, re.I):
                guarantee_issues.append({"term": term, "message": message})
                trust.accuracy -= 5
                audit.risk_items.append(RiskEconomicsItem(
                    issue=message,
                    severity=RiskSeverity.HIGH if term in ("guarantee", "ensure") else RiskSeverity.MODERATE,
                    financial_downside_low=5000 if term == "guarantee" else 1000,
                    financial_downside_high=50000 if term == "guarantee" else 10000,
                    probability_of_harm=0.15,
                    expected_downside=7500 if term == "guarantee" else 1500,
                    expected_upside=0,
                    risk_ratio=0.0,
                    recommendation="CHANGE",
                    suggested_fix=message,
                ))

        # Professionalism: basic checks
        if content.count("  ") > 3:
            trust.professionalism -= 3
        if content.count("!!") > 0:
            trust.professionalism -= 5

        # Voice match: check for aggressive patterns
        for pattern, term, message in AGGRESSIVE_PATTERNS:
            if re.search(pattern, content, re.I):
                trust.voice_match -= 3

        # Compliance: check for compliance references
        compliance_count = len(re.findall(r"iso \d{5}|essential eight|privacy act|acsc", content, re.I))
        audit.compliance_rules_checked = compliance_count
        audit.compliance_passed = compliance_count  # Assume pass unless specific issues found

        # Timeliness: check for year references
        old_years = re.findall(r"\b(2022|2023|2024)\b", content)
        if old_years:
            trust.timeliness -= 5 * len(old_years)
            for year in old_years:
                audit.staleness_items.append(StalenessItem(
                    item_type="statistic",
                    content=f"Reference to year {year}",
                    age_days=(datetime.now().year - int(year)) * 365,
                    action_needed=f"Verify {year} data is still current",
                ))

        # Audience fit: if recipient context provided
        if audience_context:
            # Placeholder: audience modelling would use POI data
            trust.audience_fit = audience_context.get("fit_score", 85)

        # Resilience scoring
        resilience_hits = 0
        if re.search(r"claude|gpt-4|gemini|llama", content, re.I):
            resilience_hits += 1
            audit.staleness_items.append(StalenessItem(
                item_type="technology_claim",
                content="Specific AI model name referenced",
                half_life_days=90,
                action_needed="Replace with generic 'leading AI models' for resilience",
            ))
        if re.search(r"\d+%.*(?:growing|increasing|trending)", content, re.I):
            resilience_hits += 1
        trust.resilience = max(50, 100 - resilience_hits * 15)
        audit.resilience_score = trust.resilience

        # Sensitive content check
        content_lower = content.lower()
        for term in SENSITIVE_TERMS:
            if term in content_lower:
                audit.suggestions.append(f"Contains '{term}' — verify no confidentiality breach")

        # Completeness: basic length check for proposals
        if profile in (GovernanceProfile.SALES_MATERIALS, GovernanceProfile.REGULATED_OUTPUT):
            if len(content) < 500:
                trust.completeness -= 15
                audit.suggestions.append("Content seems short for a proposal/report. Check completeness.")

        audit.trust_surface = trust
        audit.weighted_trust_score = trust.weighted_score(intent)

        # Facts checked (rough proxy)
        stats_found = re.findall(r"\d+%|\$[\d,]+", content)
        audit.facts_checked = len(stats_found)
        audit.facts_verified = len(stats_found)  # Assume verified; real system would check

        # ── 2. Position Integrity ───────────────────────────────
        if gate_level >= 2:
            audit.position_conflicts = self._check_position_integrity(content)

        # ── 3. Multi-Perspective Review ─────────────────────────
        if gate_level >= 3:
            audit.perspective_reviews = self._run_review_council(content, profile)

        # ── 4. Credibility Engineering ──────────────────────────
        if gate_level >= 2:
            present, missing, suggestions = self._analyse_credibility(content)
            audit.credibility_present = present
            audit.credibility_missing = missing
            audit.credibility_suggestions = suggestions

        # ── 5. Thinking Frameworks ──────────────────────────────
        if self.thinking_engine and gate_level >= 2:
            thinking_result = self.thinking_engine.sentinel_quality_gate(
                title or "document review", gate_level,
            )
            audit.thinking_frameworks_applied = [f.value for f in thinking_result.frameworks_applied]
            audit.thinking_synthesis = thinking_result.synthesis
            if thinking_result.warnings:
                audit.suggestions.extend(thinking_result.warnings)

        # ── 6. Risk Economics Summary ───────────────────────────
        if audit.risk_items:
            audit.total_downside = sum(r.expected_downside for r in audit.risk_items)
            audit.total_upside = sum(r.expected_upside for r in audit.risk_items)
            audit.net_risk_ratio = (
                audit.total_upside / max(audit.total_downside, 1)
            )

        # ── 7. Determine Verdict ────────────────────────────────
        critical = [r for r in audit.risk_items if r.severity == RiskSeverity.CRITICAL]
        high = [r for r in audit.risk_items if r.severity == RiskSeverity.HIGH]

        if critical:
            audit.verdict = AuditVerdict.BLOCKED
            audit.critical_issues = [r.issue for r in critical]
            audit.summary = f"BLOCKED — {len(critical)} critical issue(s). Must fix before sending."
        elif high or audit.position_conflicts:
            audit.verdict = AuditVerdict.READY_WITH_CHANGES
            audit.summary = f"{len(high)} high-risk issues, {len(audit.position_conflicts)} position conflicts. Fix recommended."
        elif audit.suggestions:
            audit.verdict = AuditVerdict.READY_WITH_CHANGES
            audit.summary = f"Minor suggestions ({len(audit.suggestions)}). Proceed at discretion."
        else:
            audit.verdict = AuditVerdict.CLEAN
            audit.summary = "Clean. All checks passed."

        # Store
        self.audits[audit.audit_id] = audit
        logger.info(
            f"Sentinel review: {title[:40]} | Profile: {profile.value} | "
            f"Intent: {intent.value} | Gate: {gate_level} | Verdict: {audit.verdict.value} | "
            f"Trust: {audit.weighted_trust_score:.0f}"
        )
        return audit

    # ── Position Integrity Graph ─────────────────────────────────

    def track_position(self, claim: str, source_document: str, category: str = "general"):
        """Add a claim to the position integrity graph."""
        pos = TrackedPosition(claim=claim, source_document=source_document, category=category)
        self.positions.append(pos)
        logger.info(f"Position tracked: {claim[:50]}")

    def _check_position_integrity(self, content: str) -> list[PositionConflict]:
        """Check content against tracked positions for conflicts."""
        conflicts = []
        content_lower = content.lower()

        # Check for timeline conflicts (e.g. "30 days" vs "2-3 weeks")
        timeline_matches = re.findall(r"(\d+)\s*(?:working\s+)?days?", content_lower)
        for pos in self.positions:
            if pos.category == "methodology":
                pos_lower = pos.claim.lower()
                # Simple keyword overlap check
                pos_keywords = set(pos_lower.split())
                content_keywords = set(content_lower.split())
                overlap = pos_keywords & content_keywords
                # If there's significant overlap but the sentences aren't the same → investigate
                # This is a simplified check; real system would use NLP

        # Check for pricing conflicts
        prices_in_content = re.findall(r"\$[\d,]+", content)
        for price_str in prices_in_content:
            for pos in self.positions:
                if pos.category == "pricing" and pos.claim and price_str not in pos.claim:
                    if "$" in pos.claim:
                        conflicts.append(PositionConflict(
                            claim_in_document=f"Price: {price_str}",
                            conflicts_with=pos.source_document,
                            conflict_description=f"Price differs from prior: {pos.claim}",
                            resolution_options=["Update prior document", "Adjust this document", "Explain variance"],
                        ))

        return conflicts

    def get_positions(self) -> list[dict]:
        return [
            {"claim": p.claim, "source": p.source_document, "category": p.category,
             "current": p.still_current, "date": p.date_stated.isoformat()}
            for p in self.positions
        ]

    # ── Multi-Perspective Review Council ─────────────────────────

    def _run_review_council(self, content: str, profile: GovernanceProfile) -> list[PerspectiveReview]:
        """Run adversarial multi-persona review."""
        reviews = []
        content_lower = content.lower()

        # Regulator persona
        reg_flags = []
        for pattern, term, message in GUARANTEE_PATTERNS:
            if re.search(pattern, content, re.I):
                reg_flags.append(f"'{term}' could be viewed as misleading by a regulator")
        if "comprehensive" in content_lower:
            reg_flags.append("'Comprehensive' could be read as 'covers everything' — consider 'thorough'")
        reviews.append(PerspectiveReview(
            persona="regulator", flags=reg_flags, flag_count=len(reg_flags),
        ))

        # Lawyer persona
        law_flags = []
        for pattern, term, message in GUARANTEE_PATTERNS:
            if re.search(pattern, content, re.I):
                law_flags.append(f"'{term}' creates potential contractual liability")
        timeline_refs = re.findall(r"\d+[\s-]*(?:day|week|month)", content_lower)
        for t in timeline_refs:
            if "estimated" not in content_lower[max(0, content_lower.index(t)-30):content_lower.index(t)]:
                law_flags.append(f"Timeline '{t}' without qualifier — add 'estimated' or 'subject to'")
        reviews.append(PerspectiveReview(
            persona="lawyer", flags=law_flags, flag_count=len(law_flags),
        ))

        # Sceptical prospect persona
        prospect_flags = []
        if "testimonial" not in content_lower and "reference" not in content_lower and "case study" not in content_lower:
            prospect_flags.append("No client testimonials or references — add social proof")
        if profile == GovernanceProfile.SALES_MATERIALS:
            if "solo" in content_lower or "one-person" in content_lower or len(content) < 2000:
                prospect_flags.append("Consider adding team/capability credibility signals")
        reviews.append(PerspectiveReview(
            persona="sceptical_prospect", flags=prospect_flags, flag_count=len(prospect_flags),
        ))

        # Hostile competitor persona
        comp_flags = []
        if "only" in content_lower and ("australia" in content_lower or "first" in content_lower):
            comp_flags.append("'Only' or 'first' claim detected — verify this is still true")
        reviews.append(PerspectiveReview(
            persona="hostile_competitor", flags=comp_flags, flag_count=len(comp_flags),
        ))

        # Client sponsor persona
        sponsor_flags = []
        if profile == GovernanceProfile.SALES_MATERIALS:
            if "escalat" not in content_lower and "issue" not in content_lower:
                sponsor_flags.append("No 'what if things go wrong' section — add escalation/support")
        reviews.append(PerspectiveReview(
            persona="client_sponsor", flags=sponsor_flags, flag_count=len(sponsor_flags),
        ))

        return reviews

    # ── Credibility Engineering ───────────────────────────────────

    def _analyse_credibility(self, content: str) -> tuple:
        """Analyse credibility signals present and missing."""
        content_lower = content.lower()
        present = []
        missing = []
        suggestions = []

        # Check for signals
        if re.search(r"iso \d{5}|certified|certification", content_lower):
            present.append("certification_reference")
        else:
            missing.append("certification_reference")
            suggestions.append(CredibilitySuggestion(
                signal_type="expertise",
                suggestion="Add certification references (ISO 42001, ISO 27001) for credibility",
                expected_trust_impact=5.0,
            ))

        if re.search(r"case study|client|implementation|delivered", content_lower):
            present.append("social_proof")
        else:
            missing.append("social_proof")
            suggestions.append(CredibilitySuggestion(
                signal_type="reliability",
                suggestion="Add case study or client reference for social proof",
                expected_trust_impact=8.0,
            ))

        if re.search(r"methodology|approach|framework|process", content_lower):
            present.append("methodology")
        else:
            missing.append("methodology")
            suggestions.append(CredibilitySuggestion(
                signal_type="expertise",
                suggestion="Include methodology section to demonstrate rigour",
                expected_trust_impact=4.0,
            ))

        if re.search(r"milestone|timeline|deliverable|phase", content_lower):
            present.append("commitment")
        else:
            missing.append("commitment")
            suggestions.append(CredibilitySuggestion(
                signal_type="reliability",
                suggestion="Add specific milestones/deliverables with dates",
                expected_trust_impact=6.0,
            ))

        return present, missing, suggestions

    # ── Override & Incident Management ───────────────────────────

    def record_override(self, audit_id: str, issue: str, reason: str) -> OverrideRecord:
        """Record Mani overriding a Sentinel recommendation."""
        override = OverrideRecord(audit_id=audit_id, issue_overridden=issue, reason=reason)
        self.overrides.append(override)
        audit = self.audits.get(audit_id)
        if audit:
            audit.overrides.append(override)
        logger.info(f"Override: {issue[:40]} — reason: {reason[:40]}")
        return override

    def record_override_outcome(self, override_id: str, outcome: OverrideOutcome, detail: str = ""):
        """Track whether an override was correct, neutral, or incorrect."""
        for ovr in self.overrides:
            if ovr.override_id == override_id:
                ovr.outcome = outcome
                ovr.outcome_detail = detail
                self._override_outcomes[outcome.value] += 1
                logger.info(f"Override outcome: {override_id} → {outcome.value}")
                break

    def record_incident(self, description: str, root_cause: str,
                        self_correction: str, new_rule: str = "") -> IncidentRecord:
        """Record a real-world incident and self-correct."""
        incident = IncidentRecord(
            description=description, root_cause=root_cause,
            self_correction=self_correction, new_rule=new_rule,
        )
        self.incidents.append(incident)
        logger.warning(f"Incident recorded: {description[:50]} → correction: {self_correction[:50]}")
        return incident

    def grant_exception(self, rule_broken: str, intent: str,
                        risk_ratio: float, reasoning: str,
                        conditions: list[str] = None) -> StrategicException:
        """Grant a strategic exception (governed rule-breaking)."""
        exc = StrategicException(
            rule_broken=rule_broken, intent=intent,
            risk_ratio=risk_ratio, reasoning=reasoning,
            conditions=conditions or [],
            granted=risk_ratio > 2.0,  # Auto-grant if upside > 2× downside
        )
        self.exceptions.append(exc)
        logger.info(f"Exception {'granted' if exc.granted else 'denied'}: {rule_broken[:40]} (ratio: {risk_ratio:.1f})")
        return exc

    # ── Quick Scan (Gate 1 — fast, lightweight) ──────────────────

    def quick_scan(self, content: str) -> dict:
        """Gate 1: Grammar + spelling + obvious issues only."""
        issues = []
        for pattern, term, message in GUARANTEE_PATTERNS:
            if re.search(pattern, content, re.I):
                issues.append({"term": term, "message": message})

        return {
            "gate": 1,
            "issues": len(issues),
            "details": issues[:3],
            "pass": len(issues) == 0,
        }

    # ── Staleness Check ──────────────────────────────────────────

    def check_staleness(self, items: list[dict]) -> list[StalenessItem]:
        """Check a list of content items for staleness."""
        stale = []
        now = datetime.now()
        for item in items:
            item_type = item.get("type", "statistic")
            half_life = HALF_LIVES.get(item_type, 180)
            created = item.get("created", now)
            if isinstance(created, str):
                try:
                    created = datetime.fromisoformat(created)
                except Exception:
                    created = now

            age = (now - created).days
            freshness = max(0, 100 * (1 - age / (half_life * 2)))

            if freshness < 50:
                stale.append(StalenessItem(
                    item_type=item_type,
                    content=item.get("content", ""),
                    source_document=item.get("source", ""),
                    age_days=age,
                    half_life_days=half_life,
                    freshness_pct=round(freshness, 1),
                    action_needed=f"Approaching half-life ({half_life}d). Verify or refresh.",
                ))
        return stale

    # ── Reporting ────────────────────────────────────────────────

    def get_learning_report(self) -> dict:
        """System calibration report."""
        total_overrides = len(self.overrides)
        outcomes = self._override_outcomes
        total_audits = len(self.audits)

        verdicts = {}
        for a in self.audits.values():
            verdicts[a.verdict.value] = verdicts.get(a.verdict.value, 0) + 1

        return {
            "total_audits": total_audits,
            "verdicts": verdicts,
            "total_overrides": total_overrides,
            "override_outcomes": outcomes,
            "override_accuracy": (
                round(outcomes["correct"] / max(total_overrides, 1) * 100, 0)
            ),
            "total_incidents": len(self.incidents),
            "total_exceptions": len(self.exceptions),
            "exceptions_granted": len([e for e in self.exceptions if e.granted]),
        }

    def status(self) -> dict:
        return {
            "total_audits": len(self.audits),
            "positions_tracked": len(self.positions),
            "overrides": len(self.overrides),
            "incidents": len(self.incidents),
            "exceptions": len(self.exceptions),
            "learning": self.get_learning_report(),
        }
