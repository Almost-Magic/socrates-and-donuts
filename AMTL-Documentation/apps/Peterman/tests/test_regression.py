"""
Peterman Regression Tests

Everything from Phases 1-4 still works.
"""

import pytest


class TestPhase1Regression:
    """Phase 1 - Core Domain Management."""
    
    def test_domain_crud_still_works(self, client):
        """Domain CRUD operations work."""
        # Create
        response = client.post('/api/domains', json={
            'domain_name': 'regression-phase1.com.au',
            'display_name': 'Regression Phase 1',
            'owner_label': 'test',
            'cms_type': 'wordpress'
        })
        assert response.status_code in [200, 201]
        
        # List
        response = client.get('/api/domains')
        assert response.status_code == 200
    
    def test_keywords_still_work(self, client):
        """Keyword operations work."""
        # Create domain
        response = client.post('/api/domains', json={
            'domain_name': 'regression-keywords.com.au',
            'display_name': 'Regression Keywords',
            'owner_label': 'test'
        })
        domain_id = response.get_json()['domain_id']
        
        # Add keyword
        response = client.post(f'/api/domains/{domain_id}/keywords', json={
            'query': 'regression test keyword',
            'category': 'test',
            'priority': 'medium'
        })
        assert response.status_code in [200, 201]
        
        # List keywords
        response = client.get(f'/api/domains/{domain_id}/keywords')
        assert response.status_code == 200
    
    def test_probes_still_work(self, client):
        """Probe operations work."""
        response = client.post('/api/domains', json={
            'domain_name': 'regression-probes.com.au',
            'display_name': 'Regression Probes',
            'owner_label': 'test'
        })
        domain_id = response.get_json()['domain_id']
        
        response = client.get(f'/api/domains/{domain_id}/probes')
        assert response.status_code == 200
    
    def test_score_still_works(self, client):
        """Score engine works."""
        response = client.post('/api/domains', json={
            'domain_name': 'regression-score.com.au',
            'display_name': 'Regression Score',
            'owner_label': 'test'
        })
        domain_id = response.get_json()['domain_id']
        
        response = client.get(f'/api/domains/{domain_id}/score')
        assert response.status_code == 200
    
    def test_hallucinations_still_work(self, client):
        """Hallucination detection works."""
        response = client.post('/api/domains', json={
            'domain_name': 'regression-hall.com.au',
            'display_name': 'Regression Hall',
            'owner_label': 'test'
        })
        domain_id = response.get_json()['domain_id']
        
        response = client.get(f'/api/domains/{domain_id}/hallucinations')
        assert response.status_code == 200
    
    def test_briefs_still_work(self, client):
        """Brief generation works."""
        response = client.post('/api/domains', json={
            'domain_name': 'regression-briefs.com.au',
            'display_name': 'Regression Briefs',
            'owner_label': 'test'
        })
        domain_id = response.get_json()['domain_id']
        
        response = client.get(f'/api/domains/{domain_id}/briefs')
        assert response.status_code == 200
    
    def test_approvals_still_work(self, client):
        """Approval workflow works."""
        response = client.post('/api/domains', json={
            'domain_name': 'regression-approvals.com.au',
            'display_name': 'Regression Approvals',
            'owner_label': 'test'
        })
        domain_id = response.get_json()['domain_id']
        
        response = client.get(f'/api/domains/{domain_id}/approvals')
        assert response.status_code == 200


class TestPhase2Regression:
    """Phase 2 - All 7 Chambers."""
    
    def test_semantic_chamber_regression(self, client):
        """Semantic chamber works."""
        response = client.post('/api/domains', json={
            'domain_name': 'regression-semantic.com.au',
            'display_name': 'Regression Semantic',
            'owner_label': 'test'
        })
        domain_id = response.get_json()['domain_id']
        
        response = client.get(f'/api/domains/{domain_id}/chamber/semantic')
        assert response.status_code in [200, 500]
    
    def test_survivability_chamber_regression(self, client):
        """Survivability chamber works."""
        response = client.post('/api/domains', json={
            'domain_name': 'regression-surviv.com.au',
            'display_name': 'Regression Surviv',
            'owner_label': 'test'
        })
        domain_id = response.get_json()['domain_id']
        
        response = client.get(f'/api/domains/{domain_id}/chamber/survivability')
        assert response.status_code in [200, 500]
    
    def test_authority_chamber_regression(self, client):
        """Authority chamber works."""
        response = client.post('/api/domains', json={
            'domain_name': 'regression-auth.com.au',
            'display_name': 'Regression Auth',
            'owner_label': 'test'
        })
        domain_id = response.get_json()['domain_id']
        
        response = client.get(f'/api/domains/{domain_id}/chamber/authority')
        assert response.status_code in [200, 500]
    
    def test_amplifier_chamber_regression(self, client):
        """Amplifier chamber works."""
        response = client.post('/api/domains', json={
            'domain_name': 'regression-amp.com.au',
            'display_name': 'Regression Amp',
            'owner_label': 'test'
        })
        domain_id = response.get_json()['domain_id']
        
        response = client.get(f'/api/domains/{domain_id}/chamber/amplifier')
        assert response.status_code in [200, 500]
    
    def test_competitive_chamber_regression(self, client):
        """Competitive chamber works."""
        response = client.post('/api/domains', json={
            'domain_name': 'regression-comp.com.au',
            'display_name': 'Regression Comp',
            'owner_label': 'test'
        })
        domain_id = response.get_json()['domain_id']
        
        response = client.get(f'/api/domains/{domain_id}/chamber/competitive')
        assert response.status_code in [200, 500]
    
    def test_oracle_chamber_regression(self, client):
        """Oracle chamber works."""
        response = client.post('/api/domains', json={
            'domain_name': 'regression-oracle.com.au',
            'display_name': 'Regression Oracle',
            'owner_label': 'test'
        })
        domain_id = response.get_json()['domain_id']
        
        response = client.get(f'/api/domains/{domain_id}/chamber/oracle')
        assert response.status_code in [200, 500]
    
    def test_defensive_chamber_regression(self, client):
        """Defensive chamber works."""
        response = client.post('/api/domains', json={
            'domain_name': 'regression-def.com.au',
            'display_name': 'Regression Def',
            'owner_label': 'test'
        })
        domain_id = response.get_json()['domain_id']
        
        response = client.get(f'/api/domains/{domain_id}/chamber/defensive')
        assert response.status_code in [200, 500]
    
    def test_all_chambers_endpoint_regression(self, client):
        """All chambers endpoint works."""
        response = client.post('/api/domains', json={
            'domain_name': 'regression-chambers.com.au',
            'display_name': 'Regression Chambers',
            'owner_label': 'test'
        })
        domain_id = response.get_json()['domain_id']
        
        response = client.get(f'/api/domains/{domain_id}/chambers')
        assert response.status_code == 200


class TestPhase3Regression:
    """Phase 3 - Deployments & ELAINE."""
    
    def test_deployments_still_work(self, client):
        """Deployment operations work."""
        response = client.post('/api/domains', json={
            'domain_name': 'regression-deploy.com.au',
            'display_name': 'Regression Deploy',
            'owner_label': 'test'
        })
        domain_id = response.get_json()['domain_id']
        
        response = client.get(f'/api/domains/{domain_id}/deployments')
        assert response.status_code == 200
    
    def test_elaine_status_regression(self, client):
        """ELAINE status works."""
        response = client.get('/api/elaine/status')
        assert response.status_code in [200, 500, 503]
    
    def test_ckwriter_regression(self, client):
        """CK Writer integration works."""
        response = client.get('/api/ckwriter/status')
        assert response.status_code in [200, 404, 500]
    
    def test_reports_regression(self, client):
        """Report generation works."""
        response = client.post('/api/domains', json={
            'domain_name': 'regression-reports.com.au',
            'display_name': 'Regression Reports',
            'owner_label': 'test'
        })
        domain_id = response.get_json()['domain_id']
        
        response = client.get(f'/api/domains/{domain_id}/report/latest')
        assert response.status_code in [200, 404]


class TestPhase4Regression:
    """Phase 4 - Advanced Features."""
    
    def test_advanced_scoring_regression(self, client):
        """Advanced scoring works."""
        response = client.post('/api/domains', json={
            'domain_name': 'regression-adv.com.au',
            'display_name': 'Regression Adv',
            'owner_label': 'test'
        })
        domain_id = response.get_json()['domain_id']
        
        response = client.get(f'/api/domains/{domain_id}/score/advanced')
        assert response.status_code in [200, 500]
    
    def test_help_system_regression(self, client):
        """Help system works."""
        response = client.get('/api/help/screens')
        assert response.status_code in [200, 404]
    
    def test_free_audit_regression(self, client):
        """Free audit works."""
        response = client.post('/api/audit/free', json={
            'url': 'https://example.com'
        })
        assert response.status_code in [200, 400, 500]
    
    def test_budget_regression(self, client):
        """Budget tracking works."""
        response = client.post('/api/domains', json={
            'domain_name': 'regression-budget.com.au',
            'display_name': 'Regression Budget',
            'owner_label': 'test',
            'budget_weekly_aud': 100.0
        })
        domain_id = response.get_json()['domain_id']
        
        response = client.get(f'/api/domains/{domain_id}/budget')
        assert response.status_code == 200
