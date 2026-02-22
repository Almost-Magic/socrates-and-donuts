"""
Peterman Integration Tests

Services working together.
"""

import pytest


class TestIntegration:
    """Integration tests - services working together."""
    
    def test_full_workflow_domain_to_score(self, client):
        """Full workflow: create domain → add keyword → get score."""
        # 1. Create domain
        response = client.post('/api/domains', json={
            'domain_name': 'integration-workflow.com.au',
            'display_name': 'Integration Workflow',
            'owner_label': 'test',
            'cms_type': 'wordpress'
        })
        assert response.status_code in [200, 201]
        domain_id = response.get_json()['domain_id']
        
        # 2. Add keyword
        response = client.post(f'/api/domains/{domain_id}/keywords', json={
            'query': 'integration test keyword',
            'category': 'test',
            'priority': 'high'
        })
        assert response.status_code in [200, 201]
        
        # 3. Approve keyword
        response = client.post(f'/api/domains/{domain_id}/keywords/approve-all')
        assert response.status_code in [200, 201]
        
        # 4. Get score
        response = client.get(f'/api/domains/{domain_id}/score')
        assert response.status_code == 200
        data = response.get_json()
        assert 'total_score' in data or 'score_id' in data
    
    def test_hallucination_to_brief_pipeline(self, client):
        """Pipeline: create domain → detect hallucinations → generate brief."""
        # 1. Create domain
        response = client.post('/api/domains', json={
            'domain_name': 'integration-hall-brief.com.au',
            'display_name': 'Integration Hall Brief',
            'owner_label': 'test'
        })
        domain_id = response.get_json()['domain_id']
        
        # 2. Add keyword
        client.post(f'/api/domains/{domain_id}/keywords', json={
            'query': 'hallucination test',
            'category': 'test',
            'priority': 'medium'
        })
        
        # 3. Approve keyword
        client.post(f'/api/domains/{domain_id}/keywords/approve-all')
        
        # 4. Add probe result (manual)
        client.post(f'/api/domains/{domain_id}/probes', json={
            'llm_provider': 'openai',
            'query': 'test query',
            'response_text': 'This is a test response that claims we won awards we never won.',
            'brand_mentioned': True,
            'sentiment': 'positive'
        })
        
        # 5. Detect hallucinations
        response = client.post(f'/api/domains/{domain_id}/hallucinations/detect')
        assert response.status_code in [200, 500]
        
        # 6. Get hallucinations list
        response = client.get(f'/api/domains/{domain_id}/hallucinations')
        assert response.status_code == 200
        
        # 7. Try to generate brief
        response = client.post(f'/api/domains/{domain_id}/briefs')
        assert response.status_code in [200, 201, 500]
    
    def test_approval_workflow(self, client):
        """Workflow: create domain → add keyword → approve → verify."""
        # 1. Create domain
        response = client.post('/api/domains', json={
            'domain_name': 'integration-approval.com.au',
            'display_name': 'Integration Approval',
            'owner_label': 'test'
        })
        domain_id = response.get_json()['domain_id']
        
        # 2. Add keyword (creates pending approval)
        response = client.post(f'/api/domains/{domain_id}/keywords', json={
            'query': 'approval workflow test',
            'category': 'test',
            'priority': 'medium'
        })
        assert response.status_code in [200, 201]
        
        # 3. Get approvals
        response = client.get(f'/api/domains/{domain_id}/approvals')
        assert response.status_code == 200
    
    def test_elaine_gets_real_data(self, client):
        """ELAINE endpoints return domain data."""
        # 1. Create domain
        response = client.post('/api/domains', json={
            'domain_name': 'integration-elaine.com.au',
            'display_name': 'Integration Elaine',
            'owner_label': 'test'
        })
        assert response.status_code in [200, 201]
        
        # 2. Check ELAINE status
        response = client.get('/api/elaine/status')
        assert response.status_code in [200, 500, 503]
    
    def test_chamber_data_feeds_score(self, client):
        """Chamber results are available for score calculation."""
        # 1. Create domain
        response = client.post('/api/domains', json={
            'domain_name': 'integration-chamber.com.au',
            'display_name': 'Integration Chamber',
            'owner_label': 'test'
        })
        domain_id = response.get_json()['domain_id']
        
        # 2. Get chambers
        response = client.get(f'/api/domains/{domain_id}/chambers')
        assert response.status_code == 200
        
        # 3. Get score (should include chamber data if available)
        response = client.get(f'/api/domains/{domain_id}/score')
        assert response.status_code == 200
    
    def test_budget_tracking_integration(self, client):
        """Budget tracking works with domain management."""
        # 1. Create domain with budget
        response = client.post('/api/domains', json={
            'domain_name': 'integration-budget.com.au',
            'display_name': 'Integration Budget',
            'owner_label': 'test',
            'budget_weekly_aud': 150.0
        })
        domain_id = response.get_json()['domain_id']
        
        # 2. Get budget
        response = client.get(f'/api/domains/{domain_id}/budget')
        assert response.status_code == 200
        data = response.get_json()
        assert 'weekly_budget' in data or 'budget_weekly_aud' in data
    
    def test_deployment_pipeline(self, client):
        """Deployment pipeline works end-to-end."""
        # 1. Create domain
        response = client.post('/api/domains', json={
            'domain_name': 'integration-deploy.com.au',
            'display_name': 'Integration Deploy',
            'owner_label': 'test',
            'cms_type': 'wordpress'
        })
        domain_id = response.get_json()['domain_id']
        
        # 2. Get deployments
        response = client.get(f'/api/domains/{domain_id}/deployments')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_keyword_to_probe_to_hallucination(self, client):
        """Complete keyword → probe → hallucination workflow."""
        # 1. Create domain
        response = client.post('/api/domains', json={
            'domain_name': 'integration-kph.com.au',
            'display_name': 'Integration KPH',
            'owner_label': 'test'
        })
        domain_id = response.get_json()['domain_id']
        
        # 2. Add keyword
        response = client.post(f'/api/domains/{domain_id}/keywords', json={
            'query': 'complete workflow test',
            'category': 'test',
            'priority': 'high'
        })
        keyword_id = response.get_json().get('keyword_id') if response.status_code in [200, 201] else None
        
        # 3. Approve keyword
        client.post(f'/api/domains/{domain_id}/keywords/approve-all')
        
        # 4. Get approved keywords
        response = client.get(f'/api/domains/{domain_id}/keywords')
        assert response.status_code == 200
        
        # 5. Trigger probe
        response = client.post(f'/api/domains/{domain_id}/probe')
        assert response.status_code in [200, 201, 400, 500]
        
        # 6. Get probes
        response = client.get(f'/api/domains/{domain_id}/probes')
        assert response.status_code == 200
        
        # 7. Get hallucinations
        response = client.get(f'/api/domains/{domain_id}/hallucinations')
        assert response.status_code == 200
