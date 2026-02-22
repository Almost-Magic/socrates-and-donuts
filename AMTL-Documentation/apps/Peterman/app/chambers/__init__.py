"""
PETERMAN Chambers

All measurement chambers for the LLM SEO intelligence system.
"""

# Chamber exports
from app.chambers.chamber_02_semantic import (
    compute_sgs,
    get_semantic_map_data,
    get_sgs_history,
    SemanticGravityRecord,
)

from app.chambers.chamber_03_survivability import (
    compute_lcri,
    get_lcri_history,
    get_latest_lcri,
    LCRIRecord,
)

from app.chambers.chamber_04_authority import (
    compute_authority,
    get_authority_summary,
    get_authority_history,
    AuthorityRecord,
)

from app.chambers.chamber_07_amplifier import (
    check_cannibalisation,
    measure_performance,
    get_performance_history,
    get_performance_summary,
    PerformanceRecord,
)

from app.chambers.chamber_08_competitive import (
    discover_competitors,
    add_competitor,
    get_competitors,
    assess_threats,
    CompetitorDomain,
)

from app.chambers.chamber_09_oracle import (
    generate_forecast,
    get_latest_forecast,
    get_calendar,
    OracleForecast,
)

from app.chambers.chamber_11_defensive import (
    analyze_perception,
    get_latest_perception,
    get_perception_trends,
    generate_correction_prompt,
    PerceptionRecord,
)


__all__ = [
    # Chamber 2 - Semantic Gravity
    'compute_sgs',
    'get_semantic_map_data',
    'get_sgs_history',
    'SemanticGravityRecord',
    
    # Chamber 3 - Content Survivability
    'compute_lcri',
    'get_lcri_history',
    'get_latest_lcri',
    'LCRIRecord',
    
    # Chamber 4 - Authority
    'compute_authority',
    'get_authority_summary',
    'get_authority_history',
    'AuthorityRecord',
    
    # Chamber 7 - Amplifier
    'check_cannibalisation',
    'measure_performance',
    'get_performance_history',
    'get_performance_summary',
    'PerformanceRecord',
    
    # Chamber 8 - Competitive
    'discover_competitors',
    'add_competitor',
    'get_competitors',
    'assess_threats',
    'CompetitorDomain',
    
    # Chamber 9 - Oracle
    'generate_forecast',
    'get_latest_forecast',
    'get_calendar',
    'OracleForecast',
    
    # Chamber 11 - Defensive
    'analyze_perception',
    'get_latest_perception',
    'get_perception_trends',
    'generate_correction_prompt',
    'PerceptionRecord',
]
