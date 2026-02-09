"""
Costanza Integration — Structured Intelligence for Reports & Presentations

Connects Genie's financial reports to Costanza's 21 frameworks:
- Pyramid Principle for executive summaries (answer first, MECE structure)
- SCQA for narrative reports (Situation, Complication, Question, Answer)
- ABT for financial storytelling (And, But, Therefore)
- Rule of Three for key metrics and recommendations
- SWOT for business health analysis
- Pre-Mortem for cash flow risk scenarios
- Balanced Scorecard for dashboard structure

"If George had used the Pyramid Principle, he might have kept a job."
"If George had run SCQA on his lie, it would have held up in court."

Part of the Elaine ecosystem. Because someone had to clean up after George.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger("genie.costanza")


# ═══════════════════════════════════════════════════════════
# REPORT INTELLIGENCE
# ═══════════════════════════════════════════════════════════

class ReportType(str, Enum):
    MONTHLY_SUMMARY = "monthly_summary"
    BAS_WORKSHEET = "bas_worksheet"
    ACCOUNTANT_PACK = "accountant_pack"
    CASH_FLOW_FORECAST = "cash_flow_forecast"
    BUSINESS_HEALTH = "business_health"
    FRAUD_REPORT = "fraud_report"
    LEARNING_REPORT = "learning_report"
    CLIENT_PROFITABILITY = "client_profitability"
    VENDOR_ANALYSIS = "vendor_analysis"


class AudienceLevel(str, Enum):
    OWNER = "owner"               # Wants: answer first, plain English, what to do
    ACCOUNTANT = "accountant"     # Wants: accuracy, detail, compliance, drill-down
    BANK_MANAGER = "bank_manager" # Wants: stability, cash position, forecast
    INVESTOR = "investor"         # Wants: growth, margins, scalability


@dataclass
class PyramidStructure:
    """Minto Pyramid — answer first, MECE supporting arguments, evidence base."""
    answer: str
    supporting_arguments: List[str] = field(default_factory=list)
    evidence: List[List[str]] = field(default_factory=list)


@dataclass
class SCQAStructure:
    """Situation-Complication-Question-Answer narrative arc."""
    situation: str
    complication: str
    question: str
    answer: str


@dataclass
class ABTStructure:
    """And-But-Therefore for financial storytelling."""
    context: str       # And: the setup
    conflict: str      # But: the tension
    resolution: str    # Therefore: the recommendation


@dataclass
class RuleOfThree:
    """Three key items clustered for memorability."""
    items: List[str]   # Exactly 3
    label: str = ""


@dataclass
class StructuredReport:
    """A Genie report enhanced with Costanza intelligence."""
    title: str
    report_type: ReportType
    audience: AudienceLevel
    date: str
    pyramid: Optional[PyramidStructure] = None
    scqa: Optional[SCQAStructure] = None
    abt: Optional[ABTStructure] = None
    key_three: Optional[RuleOfThree] = None
    sections: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CostanzaReportEngine:
    """
    Apply Costanza frameworks to Genie financial data.

    George's approach to reports:
    - "I just told them what they wanted to hear" (no structure)
    - "I led with the bad news" (buried the recommendation)
    - "I forgot the second page" (incomplete MECE)

    Costanza engine approach:
    - Pyramid: answer first, then why, then evidence
    - SCQA: narrative arc that holds attention
    - MECE: no gaps, no overlaps
    - Rule of Three: memorable takeaways
    """

    def __init__(self):
        self.framework_usage = {}

    def monthly_summary(self, data: Dict[str, Any], audience: AudienceLevel = AudienceLevel.OWNER) -> StructuredReport:
        """
        Generate a structured monthly summary using Costanza frameworks.

        Pyramid: "Your business is [healthy/at risk]. Here's why."
        SCQA: Context → what changed → what to do about it
        Rule of Three: Top 3 actions for next month
        """
        cash = data.get("cash_position", 0)
        revenue = data.get("revenue", 0)
        expenses = data.get("expenses", 0)
        net = revenue - expenses
        fragility = data.get("fragility_score", 0)
        overdue = data.get("overdue_invoices", 0)
        uncategorised = data.get("uncategorised", 0)

        # Determine health
        if fragility > 2.0 and overdue == 0:
            health = "strong"
            health_detail = "obligations covered twice over, no overdue invoices"
        elif fragility > 1.0:
            health = "stable with attention needed"
            health_detail = "obligations covered but margins are tight"
        else:
            health = "critical"
            health_detail = "obligations exceed available cash"

        # Pyramid: Answer first
        pyramid = PyramidStructure(
            answer=f"Business health is {health}. Revenue ${revenue:,.0f}, expenses ${expenses:,.0f}, net ${net:,.0f}.",
            supporting_arguments=[
                f"Cash position: ${cash:,.0f} ({health_detail})",
                f"Revenue trend: ${revenue:,.0f} this month",
                f"Operational health: {uncategorised} uncategorised, {overdue} overdue",
            ],
            evidence=[
                [f"Fragility score: {fragility:.1f}", f"Safe-to-spend: ${data.get('safe_to_spend', 0):,.0f}"],
                [f"Income sources: {data.get('income_sources', 'N/A')}", f"Avg invoice: ${data.get('avg_invoice', 0):,.0f}"],
                [f"Audit readiness: {data.get('audit_readiness', 0):.0f}%", f"Auto-categorised: {data.get('auto_pct', 0):.0f}%"],
            ],
        )

        # SCQA: Narrative arc
        if net > 0:
            scqa = SCQAStructure(
                situation=f"This month your business generated ${revenue:,.0f} in revenue against ${expenses:,.0f} in expenses.",
                complication=f"{'However, ' + str(overdue) + ' invoices are overdue totalling $' + str(data.get('overdue_amount', 0)) + '.' if overdue > 0 else 'Cash position is healthy with obligations well covered.'}",
                question="What should you focus on next month?",
                answer=f"{'Chase the ' + str(overdue) + ' overdue invoices to maintain cash flow.' if overdue > 0 else 'Maintain current trajectory. Consider early vendor payments to capture discounts.'}",
            )
        else:
            scqa = SCQAStructure(
                situation=f"This month expenses (${expenses:,.0f}) exceeded revenue (${revenue:,.0f}).",
                complication=f"Net loss of ${abs(net):,.0f}. Fragility score is {fragility:.1f}.",
                question="How do we restore positive cash flow?",
                answer="Review recurring expenses (Zombie Hunter), chase overdue invoices, and consider delaying non-essential purchases.",
            )

        # ABT: Storytelling
        abt = ABTStructure(
            context=f"Your business processed ${data.get('total_transactions', 0)} transactions this month",
            conflict=f"but {uncategorised} remain uncategorised and {overdue} invoices are overdue",
            resolution=f"therefore focus on clearing the backlog to maintain {data.get('audit_readiness', 0):.0f}% audit readiness",
        )

        # Rule of Three: Key actions
        actions = []
        if overdue > 0:
            actions.append(f"Chase {overdue} overdue invoice(s) — ${data.get('overdue_amount', 0):,.0f} outstanding")
        if uncategorised > 5:
            actions.append(f"Categorise {uncategorised} transactions — audit readiness drops ~{uncategorised}% each")
        if fragility < 1.5:
            actions.append("Review cash flow forecast — fragility below comfortable threshold")
        if data.get("zombie_expenses", 0) > 0:
            actions.append(f"Review {data.get('zombie_expenses')} potential zombie subscriptions")
        if data.get("unverified_vendors", 0) > 0:
            actions.append(f"Verify {data.get('unverified_vendors')} unverified vendor(s)")
        # Ensure exactly 3
        while len(actions) < 3:
            actions.append("All clear — maintain current operations")
        actions = actions[:3]

        key_three = RuleOfThree(items=actions, label="Top 3 Actions for Next Month")

        report = StructuredReport(
            title=f"Monthly Summary — {data.get('month', 'This Month')}",
            report_type=ReportType.MONTHLY_SUMMARY,
            audience=audience,
            date=datetime.now().strftime("%d %B %Y"),
            pyramid=pyramid,
            scqa=scqa,
            abt=abt,
            key_three=key_three,
            sections=[
                {"title": "Cash Position", "data": {"cash": cash, "safe_to_spend": data.get("safe_to_spend", 0), "fragility": fragility}},
                {"title": "Revenue & Expenses", "data": {"revenue": revenue, "expenses": expenses, "net": net}},
                {"title": "Receivables", "data": {"total": data.get("receivables", 0), "overdue": overdue}},
                {"title": "Payables", "data": {"total": data.get("payables", 0), "due_this_week": data.get("payables_due_week", 0)}},
                {"title": "Genie Intelligence", "data": {"accuracy": data.get("accuracy", 0), "time_saved": data.get("time_saved", 0), "money_saved": data.get("money_saved", 0)}},
            ],
            recommendations=actions,
        )

        self._track("monthly_summary")
        return report

    def cash_flow_narrative(self, forecast_data: Dict[str, Any], audience: AudienceLevel = AudienceLevel.OWNER) -> SCQAStructure:
        """SCQA narrative for cash flow forecast — used in reports and presentations."""
        current = forecast_data.get("current_cash", 0)
        buffer = forecast_data.get("min_buffer", 5000)
        weeks_above = sum(1 for w in forecast_data.get("forecast", []) if w.get("expected", 0) > buffer)
        total_weeks = len(forecast_data.get("forecast", []))
        worst_week = min(forecast_data.get("forecast", [{"expected": current}]), key=lambda w: w.get("expected", 0))

        if weeks_above == total_weeks:
            answer_text = "Yes — cash stays above buffer throughout."
        else:
            risk_week = worst_week.get("week", "?")
            answer_text = f"Risk in week {risk_week}: consider chasing receivables or deferring payments."

        return SCQAStructure(
            situation=f"Current cash position is ${current:,.0f} with a ${buffer:,.0f} minimum buffer.",
            complication=f"The 13-week forecast shows cash above buffer for {weeks_above} of {total_weeks} weeks. Lowest point: ${worst_week.get('expected', 0):,.0f} in week {worst_week.get('week', '?')}.",
            question="Will cash flow remain healthy over the forecast period?",
            answer=answer_text,
        )

    def presentation_structure(self, report: StructuredReport) -> List[Dict[str, Any]]:
        """
        Convert a StructuredReport into a slide deck structure.
        Uses 10-20-30 rule: ≤10 slides, ≤20 minutes, ≥30pt font.
        """
        slides = [
            {"type": "title", "title": report.title, "subtitle": f"Prepared {report.date} | {report.audience.value}", "notes": "Open with the headline number."},
            {"type": "answer", "title": "Executive Summary", "content": report.pyramid.answer if report.pyramid else "", "notes": "Lead with the answer. Don't bury it."},
        ]

        # SCQA narrative slide
        if report.scqa:
            slides.append({
                "type": "narrative", "title": "The Story",
                "content": {
                    "situation": report.scqa.situation,
                    "complication": report.scqa.complication,
                    "question": report.scqa.question,
                    "answer": report.scqa.answer,
                },
                "notes": "Walk through the narrative. Pause after complication — let it land.",
            })

        # Section slides
        for section in report.sections[:5]:
            slides.append({
                "type": "data", "title": section["title"],
                "content": section["data"],
                "notes": f"Key point for {section['title']}.",
            })

        # Recommendations slide (Rule of Three)
        if report.key_three:
            slides.append({
                "type": "actions", "title": report.key_three.label,
                "content": report.key_three.items,
                "notes": "Three actions only. Don't dilute with extras.",
            })

        # Close
        slides.append({
            "type": "close", "title": "Next Steps",
            "content": "Review these actions. Genie will track progress and report back next month.",
            "notes": "End with a clear call to action.",
        })

        return slides

    def _track(self, framework: str):
        self.framework_usage[framework] = self.framework_usage.get(framework, 0) + 1


# ═══════════════════════════════════════════════════════════
# PRE-MORTEM FOR CASH FLOW RISK
# ═══════════════════════════════════════════════════════════

class CostanzaRiskEngine:
    """
    Pre-Mortem analysis for financial risk scenarios.

    George's approach to risk: "I'll deal with it when it happens."
    Costanza approach: "Assume it already failed. Now figure out why."
    """

    def pre_mortem(self, scenario: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run a pre-mortem on a financial scenario."""
        risks = []

        if data.get("fragility_score", 999) < 1.5:
            risks.append({
                "risk": "Cash reserves insufficient to absorb shock",
                "probability": "high" if data.get("fragility_score", 0) < 1.0 else "medium",
                "impact": "Business cannot meet obligations",
                "mitigation": "Build cash buffer to 2x obligations",
            })

        if data.get("client_concentration", 0) > 30:
            risks.append({
                "risk": f"Revenue concentration: top client = {data.get('client_concentration')}%",
                "probability": "medium",
                "impact": "Loss of one client threatens viability",
                "mitigation": "Diversify client base — target 3 new clients this quarter",
            })

        if data.get("overdue_invoices", 0) > 3:
            risks.append({
                "risk": f"{data.get('overdue_invoices')} invoices overdue",
                "probability": "high",
                "impact": "Cash flow disruption within 30 days",
                "mitigation": "Escalate collection — send Level 3 reminders today",
            })

        if data.get("unverified_vendors", 0) > 0:
            risks.append({
                "risk": f"{data.get('unverified_vendors')} unverified vendor(s) in payment queue",
                "probability": "low",
                "impact": "Potential invoice fraud / misdirected payment",
                "mitigation": "Complete 4-step verification before any payment",
            })

        return {
            "scenario": scenario,
            "risks_identified": len(risks),
            "risks": risks,
            "overall_risk": "high" if any(r["probability"] == "high" for r in risks) else "medium" if risks else "low",
            "george_would_say": "I'm sure it'll be fine.",
            "costanza_says": f"We identified {len(risks)} risk(s). Address them before they address you.",
        }


# ═══════════════════════════════════════════════════════════
# CONVENIENCE
# ═══════════════════════════════════════════════════════════

# Singleton instances for easy import
report_engine = CostanzaReportEngine()
risk_engine = CostanzaRiskEngine()
