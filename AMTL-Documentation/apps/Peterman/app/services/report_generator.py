"""
Report Generator for Peterman.

Generates client-facing PDF reports with:
- Current Peterman Score with trend
- LLM Share of Voice per provider
- Top hallucinations fixed this period
- Content published and measured impact
- Competitor overview
- 90-day forward calendar preview

Uses HTML generation - can be converted to PDF via browser print.
"""

import logging
from datetime import datetime, timedelta
from uuid import UUID
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates client-facing reports."""
    
    def __init__(self, domain_id: UUID):
        self.domain_id = domain_id
        self._load_domain()
    
    def _load_domain(self):
        """Load domain data."""
        from app.models.database import get_session
        from app.models.domain import Domain
        
        session = get_session()
        try:
            domain = session.query(Domain).filter_by(domain_id=self.domain_id).first()
            if domain:
                self.domain_name = domain.domain_name
                self.display_name = domain.display_name or domain.domain_name
            else:
                self.domain_name = 'Unknown'
                self.display_name = 'Unknown'
        finally:
            session.close()
    
    def generate_report(
        self,
        period_days: int = 30,
        include_gsc: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive report for the domain.
        
        Args:
            period_days: Number of days to include in report
            include_gsc: Include Google Search Console data
        
        Returns:
            Dict with report data and HTML
        """
        
        from app.services.score_engine import compute_peterman_score
        from app.models.database import get_session
        from app.models.hallucination import Hallucination
        from app.models.brief import ContentBrief
        from app.models.probe import ProbeResult
        
        session = get_session()
        try:
            # Get score data
            score_data = compute_peterman_score(self.domain_id)
            
            # Get hallucinations fixed in period
            cutoff = datetime.utcnow() - timedelta(days=period_days)
            fixed_hallucinations = session.query(Hallucination).filter(
                Hallucination.domain_id == self.domain_id,
                Hallucination.status == 'resolved',
                Hallucination.resolved_at >= cutoff
            ).all()
            
            # Get content deployed in period
            deployed_content = session.query(ContentBrief).filter(
                ContentBrief.domain_id == self.domain_id,
                ContentBrief.status == 'deployed',
                ContentBrief.deployed_at >= cutoff
            ).all()
            
            # Get probe results
            probes = session.query(ProbeResult).filter(
                ProbeResult.domain_id == self.domain_id,
                ProbeResult.probed_at >= cutoff
            ).all()
            
            # Calculate LLM Share of Voice
            llm_mentions = {}
            for probe in probes:
                if probe.brand_mentioned:
                    provider = probe.provider or 'unknown'
                    llm_mentions[provider] = llm_mentions.get(provider, 0) + 1
            
            total_mentions = sum(llm_mentions.values())
            sov_data = {
                provider: {
                    'mentions': count,
                    'percentage': (count / total_mentions * 100) if total_mentions > 0 else 0
                }
                for provider, count in llm_mentions.items()
            }
            
            # Get competitors
            from app.chambers.chamber_08_competitive import get_competitors
            competitors = get_competitors(self.domain_id)
            
            # Get oracle forecast
            from app.chambers.chamber_09_oracle import get_latest_forecast
            forecast = get_latest_forecast(self.domain_id)
            
            # GSC data (optional)
            gsc_data = None
            if include_gsc:
                try:
                    from app.services.gsc_integration import GSCIntegration
                    gsc = GSCIntegration()
                    if gsc.is_configured():
                        gsc_data = gsc.get_performance_summary()
                except Exception as e:
                    logger.warning(f'GSC data unavailable: {e}')
            
            # Build report data
            report = {
                'generated_at': datetime.utcnow().isoformat(),
                'domain_id': str(self.domain_id),
                'domain_name': self.display_name,
                'period_days': period_days,
                'score': score_data,
                'llm_share_of_voice': sov_data,
                'hallucinations_fixed': len(fixed_hallucinations),
                'content_published': len(deployed_content),
                'probes_run': len(probes),
                'competitors': competitors[:5] if competitors else [],
                'forecast': forecast,
                'gsc_data': gsc_data,
            }
            
            # Generate HTML
            report['html'] = self._generate_html(report)
            
            return report
            
        finally:
            session.close()
    
    def _generate_html(self, report: Dict[str, Any]) -> str:
        """Generate HTML report."""
        
        score = report.get('score', {})
        sov = report.get('llm_share_of_voice', {})
        
        # Format score display
        total_score = score.get('total_score', 0) or 0
        grade = score.get('grade', 'N/A')
        
        # Format SOV
        sov_rows = ''
        for provider, data in sov.items():
            sov_rows += f'''
            <tr>
                <td>{provider}</td>
                <td>{data['mentions']}</td>
                <td>{data['percentage']:.1f}%</td>
            </tr>
            '''
        
        if not sov_rows:
            sov_rows = '<tr><td colspan="3">No data available</td></tr>'
        
        # Format hallucinations
        hall_count = report.get('hallucinations_fixed', 0)
        
        # Format content
        content_count = report.get('content_published', 0)
        
        # Format competitors
        competitors = report.get('competitors', [])
        comp_rows = ''
        for comp in competitors:
            comp_rows += f'''
            <tr>
                <td>{comp.get('name', 'Unknown')}</td>
                <td>{comp.get('threat_level', 'N/A')}</td>
            </tr>
            '''
        
        if not comp_rows:
            comp_rows = '<tr><td colspan="2">No competitor data</td></tr>'
        
        html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Peterman Report - {report['domain_name']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0A0E14;
            color: #E5E5E5;
            line-height: 1.6;
            padding: 40px;
        }}
        .report {{
            max-width: 800px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 2px solid #C9944A;
        }}
        .logo {{
            font-size: 28px;
            font-weight: bold;
            color: #C9944A;
            margin-bottom: 10px;
        }}
        .subtitle {{
            color: #888;
            font-size: 14px;
        }}
        .section {{
            margin-bottom: 30px;
            background: #111820;
            border-radius: 8px;
            padding: 24px;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: 600;
            color: #C9944A;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid #2A3544;
        }}
        .score-display {{
            text-align: center;
            padding: 30px;
        }}
        .score-value {{
            font-size: 72px;
            font-weight: bold;
            color: #C9944A;
        }}
        .score-grade {{
            font-size: 36px;
            color: #888;
            margin-top: 10px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-top: 20px;
        }}
        .metric {{
            text-align: center;
            padding: 20px;
            background: #0A0E14;
            border-radius: 8px;
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: #C9944A;
        }}
        .metric-label {{
            font-size: 12px;
            color: #888;
            text-transform: uppercase;
            margin-top: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #2A3544;
        }}
        th {{
            color: #888;
            font-weight: 500;
            font-size: 12px;
            text-transform: uppercase;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #2A3544;
            color: #666;
            font-size: 12px;
        }}
        @media print {{
            body {{ background: white; color: black; }}
            .section {{ background: #f5f5f5; }}
            .score-value {{ color: #C9944A; }}
        }}
    </style>
</head>
<body>
    <div class="report">
        <div class="header">
            <div class="logo">PETERMAN</div>
            <div class="subtitle">Autonomous SEO & LLM Presence Report</div>
            <div class="subtitle">{report['domain_name']}</div>
            <div class="subtitle">Generated: {datetime.now().strftime('%d %B %Y')}</div>
        </div>
        
        <div class="section">
            <div class="section-title">Peterman Score</div>
            <div class="score-display">
                <div class="score-value">{total_score:.1f}</div>
                <div class="score-grade">Grade: {grade}</div>
                <div class="metrics-grid">
                    <div class="metric">
                        <div class="metric-value">{hall_count}</div>
                        <div class="metric-label">Hallucinations Fixed</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{content_count}</div>
                        <div class="metric-label">Content Published</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{report.get('probes_run', 0)}</div>
                        <div class="metric-label">Probes Run</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">LLM Share of Voice</div>
            <table>
                <thead>
                    <tr>
                        <th>Provider</th>
                        <th>Mentions</th>
                        <th>Share</th>
                    </tr>
                </thead>
                <tbody>
                    {sov_rows}
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <div class="section-title">Competitor Overview</div>
            <table>
                <thead>
                    <tr>
                        <th>Competitor</th>
                        <th>Threat Level</th>
                    </tr>
                </thead>
                <tbody>
                    {comp_rows}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Almost Magic Tech Lab — Autonomous SEO & LLM Presence Engine</p>
            <p>Report generated by Peterman</p>
        </div>
    </div>
</body>
</html>
'''
        return html
    
    def save_report(self, report: Dict[str, Any]) -> str:
        """Save report to file and return path."""
        import os
        
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        filename = f"peterman-report-{self.domain_id}-{datetime.now().strftime('%Y%m%d')}.html"
        filepath = os.path.join(reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report['html'])
        
        return filepath


def generate_report(domain_id: UUID, period_days: int = 30) -> Dict[str, Any]:
    """Convenience function to generate report."""
    generator = ReportGenerator(domain_id)
    return generator.generate_report(period_days=period_days)
