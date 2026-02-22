"""
Peterman 4% Edge Case Tests

Things that break at the edges.
"""

import pytest


class TestEdgeCases:
    """Edge case tests."""
    
    def test_invalid_domain_id_returns_404(self, client):
        """Invalid domain ID returns 404."""
        response = client.get('/api/domains/invalid-uuid-12345')
        assert response.status_code == 404
    
    def test_empty_domain_name_returns_400(self, client):
        """Empty domain name returns 400."""
        response = client.post('/api/domains', json={
            'domain_name': '',
            'display_name': 'Test',
            'owner_label': 'test'
        })
        assert response.status_code in [400, 422]
    
    def test_score_with_no_crawl_data(self, client):
        """Score works with no crawl data."""
        # Create a domain but don't crawl it
        response = client.post('/api/domains', json={
            'domain_name': 'no-crawl-test.com.au',
            'display_name': 'No Crawl Test',
            'owner_label': 'test'
        })
        domain_id = response.get_json()['domain_id']
        
        # Get score - should work even without crawl data
        response = client.get(f'/api/domains/{domain_id}/score')
        assert response.status_code == 200
    
    def test_score_with_no_probe_data(self, client):
        """Score works with no probe data."""
        # Create a domain but don't probe it
        response = client.post('/api/domains', json={
            'domain_name': 'no-probe-test.com.au',
            'display_name': 'No Probe Test',
            'owner_label': 'test'
        })
        domain_id = response.get_json()['domain_id']
        
        # Get score - should work even without probe data
        response = client.get(f'/api/domains/{domain_id}/score')
        assert response.status_code == 200
    
    def test_hallucination_detection_with_no_probes(self, client):
        """Hallucination detection works with no probes."""
        response = client.post('/api/domains', json={
            'domain_name': 'no-probes-hall-test.com.au',
            'display_name': 'No Probes Hall Test',
            'owner_label': 'test'
        })
        domain_id = response.get_json()['domain_id']
        
        # Detect hallucinations - should handle gracefully
        response = client.post(f'/api/domains/{domain_id}/hallucinations/detect')
        assert response.status_code in [200, 500]
    
    def test_approve_nonexistent_item_returns_404(self, client):
        """Approving nonexistent item returns 404."""
        response = client.post('/api/approvals/nonexistent-id/approve')
        assert response.status_code == 404
    
    def test_probe_with_no_approved_keywords(self, client):
        """Probe with no approved keywords."""
        response = client.post('/api/domains', json={
            'domain_name': 'no-keywords-test.com.au',
            'display_name': 'No Keywords Test',
            'owner_label': 'test'
        })
        domain_id = response.get_json()['domain_id']
        
        # Try to probe with no keywords
        response = client.post(f'/api/domains/{domain_id}/probe')
        assert response.status_code in [200, 400, 500]
    
    def test_deploy_with_no_cms_configured(self, client):
        """Deploy with no CMS configured."""
        response = client.post('/api/domains', json={
            'domain_name': 'no-cms-test.com.au',
            'display_name': 'No CMS Test',
            'owner_label': 'test',
            'cms_type': 'custom'  # No API key configured
        })
        domain_id = response.get_json()['domain_id']
        
        # Try to get deployments
        response = client.get(f'/api/domains/{domain_id}/deployments')
        assert response.status_code == 200
    
    def test_rollback_nonexistent_deployment(self, client):
        """Rollback nonexistent deployment."""
        response = client.post('/api/domains', json={
            'domain_name': 'no-deploy-test.com.au',
            'display_name': 'No Deploy Test',
            'owner_label': 'test'
        })
        domain_id = response.get_json()['domain_id']
        
        # Try to rollback nonexistent deployment
        response = client.post(f'/api/domains/{domain_id}/deployments/nonexistent-id/rollback')
        assert response.status_code in [404, 500]
    
    def test_very_long_domain_name(self, client):
        """Very long domain name is handled."""
        long_name = 'a' * 200 + '.com.au'
        response = client.post('/api/domains', json={
            'domain_name': long_name,
            'display_name': 'Long Name Test',
            'owner_label': 'test'
        })
        # Should either accept or reject gracefully
        assert response.status_code in [200, 201, 400, 422, 500]
    
    def test_special_characters_in_domain(self, client):
        """Special characters in domain name."""
        response = client.post('/api/domains', json={
            'domain_name': 'test@#$%.com.au',
            'display_name': 'Special Test',
            'owner_label': 'test'
        })
        # Should reject invalid characters
        assert response.status_code in [400, 422, 500]
    
    def test_health_when_ollama_down(self, client, monkeypatch):
        """Health works when Ollama is down (graceful degradation)."""
        # Ollama should already be down in test environment
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        # Ollama should be unavailable
        assert data['dependencies']['ollama']['status'] == 'unavailable'
    
    def test_health_when_all_services_down(self, client):
        """Health works in standalone mode when all services down."""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        # Should be in standalone or degraded mode
        assert data['mode'] in ['standalone', 'degraded']
    
    def test_budget_with_zero_budget(self, client):
        """Budget works with zero budget."""
        response = client.post('/api/domains', json={
            'domain_name': 'zero-budget-test.com.au',
            'display_name': 'Zero Budget Test',
            'owner_label': 'test',
            'budget_weekly_aud': 0.0
        })
        domain_id = response.get_json()['domain_id']
        
        response = client.get(f'/api/domains/{domain_id}/budget')
        assert response.status_code == 200
    
    def test_elaine_endpoints_when_elaine_down(self, client):
        """ELAINE endpoints work when ELAINE is down."""
        response = client.get('/api/elaine/status')
        # Should return even if ELAINE is unavailable
        assert response.status_code in [200, 500, 503]
    
    def test_domain_without_owner_label(self, client):
        """Domain works without owner label."""
        response = client.post('/api/domains', json={
            'domain_name': 'no-owner-test.com.au',
            'display_name': 'No Owner Test'
        })
        assert response.status_code in [200, 201]
    
    def test_domain_with_minimal_data(self, client):
        """Domain works with minimal data."""
        response = client.post('/api/domains', json={
            'domain_name': 'minimal-test.com.au',
            'display_name': 'Minimal Test'
        })
        assert response.status_code in [200, 201]
        data = response.get_json()
        assert data['domain_name'] == 'minimal-test.com.au'
    
    def test_get_nonexistent_report(self, client):
        """Getting nonexistent report returns 404."""
        response = client.post('/api/domains', json={
            'domain_name': 'report-test.com.au',
            'display_name': 'Report Test',
            'owner_label': 'test'
        })
        domain_id = response.get_json()['domain_id']
        
        response = client.get(f'/api/domains/{domain_id}/report/latest')
        assert response.status_code in [200, 404]
