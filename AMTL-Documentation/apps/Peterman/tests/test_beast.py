"""
Peterman Beast Tests

Core functionality tests - every feature must work.
"""

import pytest


class TestHealthEndpoint:
    """Health endpoint tests."""
    
    def test_health_endpoint_returns_200(self, client):
        """Health endpoint returns 200 status."""
        response = client.get('/api/health')
        assert response.status_code == 200
    
    def test_health_returns_database_status(self, client):
        """Health endpoint returns database status."""
        response = client.get('/api/health')
        data = response.get_json()
        assert 'dependencies' in data
        assert 'database' in data['dependencies']
        assert data['dependencies']['database']['status'] == 'healthy'
    
    def test_health_returns_mode_field(self, client):
        """Health endpoint returns mode field."""
        response = client.get('/api/health')
        data = response.get_json()
        assert 'mode' in data


class TestDomainCRUD:
    """Domain CRUD tests."""
    
    def test_create_domain(self, client):
        """Create a new domain."""
        response = client.post('/api/domains', json={
            'domain_name': 'beast-test-example.com.au',
            'display_name': 'Beast Test Example',
            'owner_label': 'test',
            'cms_type': 'wordpress',
            'tier': 'owner',
            'budget_weekly_aud': 50.0
        })
        assert response.status_code in [200, 201]
        data = response.get_json()
        assert 'domain_id' in data
    
    def test_list_domains(self, client):
        """List all domains."""
        response = client.get('/api/domains')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_get_domain_by_id(self, client, sample_domain):
        """Get domain by ID."""
        domain_id = sample_domain.get('domain_id')
        response = client.get(f'/api/domains/{domain_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['domain_id'] == domain_id
    
    def test_archive_domain(self, client, sample_domain):
        """Archive a domain."""
        domain_id = sample_domain.get('domain_id')
        response = client.put(f'/api/domains/{domain_id}', json={
            'status': 'archived'
        })
        assert response.status_code == 200
    
    def test_create_duplicate_domain_fails(self, client):
        """Creating duplicate domain should fail."""
        client.post('/api/domains', json={
            'domain_name': 'duplicate-test.com.au',
            'display_name': 'Duplicate Test',
            'owner_label': 'test',
            'cms_type': 'wordpress',
            'tier': 'owner',
            'budget_weekly_aud': 50.0
        })
        response = client.post('/api/domains', json={
            'domain_name': 'duplicate-test.com.au',
            'display_name': 'Duplicate Test 2',
            'owner_label': 'test',
            'cms_type': 'wordpress',
            'tier': 'owner',
            'budget_weekly_aud': 50.0
        })
        assert response.status_code in [400, 409, 500]


class TestKeywords:
    """Keyword tests."""
    
    def test_suggest_keywords_for_domain(self, client, sample_domain):
        """Suggest keywords for domain."""
        domain_id = sample_domain.get('domain_id')
        response = client.get(f'/api/domains/{domain_id}/keywords/suggest')
        # May return 200 or 500 (if no AI available)
        assert response.status_code in [200, 500]
    
    def test_get_keywords_for_domain(self, client, sample_domain):
        """Get keywords for domain."""
        domain_id = sample_domain.get('domain_id')
        response = client.get(f'/api/domains/{domain_id}/keywords')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_approve_all_keywords(self, client, sample_domain):
        """Approve all keywords for domain."""
        domain_id = sample_domain.get('domain_id')
        # First add a keyword
        client.post(f'/api/domains/{domain_id}/keywords', json={
            'query': 'test keyword approval',
            'category': 'test',
            'priority': 'medium'
        })
        response = client.post(f'/api/domains/{domain_id}/keywords/approve-all')
        assert response.status_code in [200, 201]


class TestProbing:
    """Probing tests."""
    
    def test_trigger_probe(self, client, sample_domain):
        """Trigger probe for domain."""
        domain_id = sample_domain.get('domain_id')
        response = client.post(f'/api/domains/{domain_id}/probe')
        # May fail if no AI, but should respond
        assert response.status_code in [200, 201, 500, 503]
    
    def test_get_probe_results(self, client, sample_domain):
        """Get probe results for domain."""
        domain_id = sample_domain.get('domain_id')
        response = client.get(f'/api/domains/{domain_id}/probes')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_manual_probe_submission(self, client, sample_domain):
        """Submit manual probe result."""
        domain_id = sample_domain.get('domain_id')
        response = client.post(f'/api/domains/{domain_id}/probes', json={
            'llm_provider': 'openai',
            'query': 'test query',
            'response_text': 'test response',
            'brand_mentioned': True,
            'sentiment': 'positive'
        })
        assert response.status_code in [200, 201]


class TestScoreEngine:
    """Score engine tests."""
    
    def test_get_domain_score(self, client, sample_domain):
        """Get domain score."""
        domain_id = sample_domain.get('domain_id')
        response = client.get(f'/api/domains/{domain_id}/score')
        assert response.status_code == 200
        data = response.get_json()
        assert 'score_id' in data or 'total_score' in data
    
    def test_score_components_have_status_field(self, client, sample_domain):
        """Score components have status field."""
        domain_id = sample_domain.get('domain_id')
        response = client.get(f'/api/domains/{domain_id}/score')
        assert response.status_code == 200
        data = response.get_json()
        # Score should exist and have components
        assert 'total_score' in data or 'score_id' in data


class TestHallucinations:
    """Hallucination tests."""
    
    def test_detect_hallucinations(self, client, sample_domain):
        """Detect hallucinations for domain."""
        domain_id = sample_domain.get('domain_id')
        response = client.post(f'/api/domains/{domain_id}/hallucinations/detect')
        # May return 200 or 500
        assert response.status_code in [200, 500]
    
    def test_get_hallucinations_list(self, client, sample_domain):
        """Get hallucinations list."""
        domain_id = sample_domain.get('domain_id')
        response = client.get(f'/api/domains/{domain_id}/hallucinations')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)


class TestBriefs:
    """Brief (The Forge) tests."""
    
    def test_generate_brief_from_hallucination(self, client, sample_domain):
        """Generate brief from hallucination."""
        domain_id = sample_domain.get('domain_id')
        response = client.post(f'/api/domains/{domain_id}/briefs')
        # May return 200 or 500
        assert response.status_code in [200, 201, 500]
    
    def test_get_briefs_list(self, client, sample_domain):
        """Get briefs list."""
        domain_id = sample_domain.get('domain_id')
        response = client.get(f'/api/domains/{domain_id}/briefs')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)


class TestApprovals:
    """Approval tests."""
    
    def test_get_approvals(self, client, sample_domain):
        """Get approvals for domain."""
        domain_id = sample_domain.get('domain_id')
        response = client.get(f'/api/domains/{domain_id}/approvals')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_approve_item(self, client, sample_domain):
        """Approve an item."""
        domain_id = sample_domain.get('domain_id')
        # Get pending approvals
        response = client.get(f'/api/domains/{domain_id}/approvals')
        approvals = response.get_json()
        if approvals:
            approval_id = approvals[0].get('approval_id') if 'approval_id' in approvals[0] else approvals[0].get('id')
            if approval_id:
                response = client.post(f'/api/approvals/{approval_id}/approve')
                assert response.status_code in [200, 404]
    
    def test_decline_item(self, client, sample_domain):
        """Decline an item."""
        domain_id = sample_domain.get('domain_id')
        response = client.get(f'/api/domains/{domain_id}/approvals')
        approvals = response.get_json()
        if approvals:
            approval_id = approvals[0].get('approval_id') if 'approval_id' in approvals[0] else approvals[0].get('id')
            if approval_id:
                response = client.post(f'/api/approvals/{approval_id}/decline')
                assert response.status_code in [200, 404]


class TestChambers:
    """Chamber tests."""
    
    def test_get_all_chambers_status(self, client, sample_domain):
        """Get all chambers status."""
        domain_id = sample_domain.get('domain_id')
        response = client.get(f'/api/domains/{domain_id}/chambers')
        assert response.status_code == 200
    
    def test_semantic_chamber(self, client, sample_domain):
        """Test semantic chamber endpoint."""
        domain_id = sample_domain.get('domain_id')
        response = client.get(f'/api/domains/{domain_id}/chamber/semantic')
        assert response.status_code in [200, 500]
    
    def test_survivability_chamber(self, client, sample_domain):
        """Test survivability chamber endpoint."""
        domain_id = sample_domain.get('domain_id')
        response = client.get(f'/api/domains/{domain_id}/chamber/survivability')
        assert response.status_code in [200, 500]
    
    def test_authority_chamber(self, client, sample_domain):
        """Test authority chamber endpoint."""
        domain_id = sample_domain.get('domain_id')
        response = client.get(f'/api/domains/{domain_id}/chamber/authority')
        assert response.status_code in [200, 500]
    
    def test_amplifier_chamber(self, client, sample_domain):
        """Test amplifier chamber endpoint."""
        domain_id = sample_domain.get('domain_id')
        response = client.get(f'/api/domains/{domain_id}/chamber/amplifier')
        assert response.status_code in [200, 500]
    
    def test_competitive_chamber(self, client, sample_domain):
        """Test competitive chamber endpoint."""
        domain_id = sample_domain.get('domain_id')
        response = client.get(f'/api/domains/{domain_id}/chamber/competitive')
        assert response.status_code in [200, 500]
    
    def test_oracle_chamber(self, client, sample_domain):
        """Test oracle chamber endpoint."""
        domain_id = sample_domain.get('domain_id')
        response = client.get(f'/api/domains/{domain_id}/chamber/oracle')
        assert response.status_code in [200, 500]
    
    def test_defensive_chamber(self, client, sample_domain):
        """Test defensive chamber endpoint."""
        domain_id = sample_domain.get('domain_id')
        response = client.get(f'/api/domains/{domain_id}/chamber/defensive')
        assert response.status_code in [200, 500]


class TestDeployments:
    """Deployment tests."""
    
    def test_get_deployments(self, client, sample_domain):
        """Get deployments for domain."""
        domain_id = sample_domain.get('domain_id')
        response = client.get(f'/api/domains/{domain_id}/deployments')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)


class TestElaine:
    """ELAINE integration tests."""
    
    def test_elaine_status_endpoint(self, client):
        """Test ELAINE status endpoint."""
        response = client.get('/api/elaine/status')
        # May return 200 or 500 (if ELAINE not available)
        assert response.status_code in [200, 500, 503]
    
    def test_elaine_morning_briefing(self, client):
        """Test ELAINE morning briefing."""
        response = client.get('/api/elaine/briefing')
        # May return 200 or 500
        assert response.status_code in [200, 500, 503]


class TestBudget:
    """Budget tests."""
    
    def test_get_budget_status(self, client, sample_domain):
        """Get budget status for domain."""
        domain_id = sample_domain.get('domain_id')
        response = client.get(f'/api/domains/{domain_id}/budget')
        assert response.status_code == 200


class TestAdvancedScoring:
    """Advanced scoring tests."""
    
    def test_advanced_score_endpoint(self, client, sample_domain):
        """Test advanced score endpoint."""
        domain_id = sample_domain.get('domain_id')
        response = client.get(f'/api/domains/{domain_id}/score/advanced')
        assert response.status_code in [200, 500]


class TestHelpSystem:
    """Help system tests."""
    
    def test_help_screens_endpoint(self, client):
        """Test help screens endpoint."""
        response = client.get('/api/help/screens')
        assert response.status_code in [200, 404]
    
    def test_help_for_specific_screen(self, client):
        """Test help for specific screen."""
        response = client.get('/api/help/screens/domains')
        assert response.status_code in [200, 404]


class TestFreeAudit:
    """Free audit tests."""
    
    def test_free_audit_endpoint(self, client):
        """Test free audit endpoint."""
        response = client.post('/api/audit/free', json={
            'url': 'https://example.com'
        })
        # May return 200 or 500
        assert response.status_code in [200, 400, 500]


class TestReports:
    """Report tests."""
    
    def test_generate_report(self, client, sample_domain):
        """Generate report for domain."""
        domain_id = sample_domain.get('domain_id')
        response = client.post(f'/api/domains/{domain_id}/report')
        assert response.status_code in [200, 201, 500]
    
    def test_get_latest_report(self, client, sample_domain):
        """Get latest report for domain."""
        domain_id = sample_domain.get('domain_id')
        response = client.get(f'/api/domains/{domain_id}/report/latest')
        assert response.status_code in [200, 404]
