"""
Google Search Console Integration for Peterman.

Optional integration to pull CTR, impressions, and position data.
Feeds into Chamber 7 (Amplifier) for content performance tracking.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# Configuration
GSC_PROPERTY_URL = os.getenv('AMTL_PTR_GSC_PROPERTY', None)
GSC_CREDENTIALS_FILE = os.getenv('AMTL_PTR_GSC_CREDS', None)


class GSCIntegration:
    """Handles integration with Google Search Console API."""
    
    def __init__(self):
        self.property_url = GSC_PROPERTY_URL
        self.credentials = None
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Search Console."""
        
        if not GSC_CREDENTIALS_FILE or not os.path.exists(GSC_CREDENTIALS_FILE):
            logger.info('GSC credentials not configured - skipping Google Search Console integration')
            return
        
        try:
            self.credentials = Credentials.from_authorized_user_info(
                info={},
                scopes=['https://www.googleapis.com/auth/webmasters.readonly']
            )
            self.service = build('searchconsole', 'v1', credentials=self.credentials)
            logger.info('GSC authenticated successfully')
        except Exception as e:
            logger.warning(f'GSC authentication failed: {e}')
    
    def is_configured(self) -> bool:
        """Check if GSC is configured."""
        return self.service is not None and self.property_url is not None
    
    def get_search_performance(
        self,
        start_date: str = None,
        end_date: str = None,
        dimensions: List[str] = None
    ) -> Dict[str, Any]:
        """
        Get search performance data from GSC.
        
        Args:
            start_date: Start date (YYYY-MM-DD), defaults to 28 days ago
            end_date: End date (YYYY-MM-DD), defaults to today
            dimensions: List of dimensions to group by (query, page, country, device)
        
        Returns:
            Dict with impressions, clicks, CTR, position data
        """
        
        if not self.is_configured():
            return {
                'status': 'not_configured',
                'message': 'Google Search Console not configured',
            }
        
        # Default to last 28 days
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=28)).strftime('%Y-%m-%d')
        if not dimensions:
            dimensions = ['query']
        
        try:
            request = {
                'startDate': {'year': int(start_date[:4]), 'month': int(start_date[5:7]), 'day': int(start_date[8:10])},
                'endDate': {'year': int(end_date[:4]), 'month': int(end_date[5:7]), 'day': int(end_date[8:10])},
                'dimensions': dimensions,
                'rowLimit': 1000,
            }
            
            response = self.service.searchanalytics().query(
                siteUrl=self.property_url,
                body=request
            ).execute()
            
            return {
                'status': 'ok',
                'data': response.get('rows', []),
                'start_date': start_date,
                'end_date': end_date,
            }
            
        except HttpError as e:
            logger.error(f'GSC API error: {e}')
            return {'status': 'error', 'error': str(e)}
        except Exception as e:
            logger.error(f'GSC query failed: {e}')
            return {'status': 'error', 'error': str(e)}
    
    def get_top_queries(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get top performing queries by clicks."""
        
        result = self.get_search_performance(dimensions=['query'])
        
        if result.get('status') != 'ok':
            return []
        
        queries = []
        for row in result.get('data', [])[:limit]:
            queries.append({
                'query': row.get('keys', [''])[0],
                'clicks': row.get('clicks', 0),
                'impressions': row.get('impressions', 0),
                'ctr': row.get('ctr', 0) * 100,  # Convert to percentage
                'position': row.get('position', 0),
            })
        
        return queries
    
    def get_page_performance(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get top performing pages by clicks."""
        
        result = self.get_search_performance(dimensions=['page'])
        
        if result.get('status') != 'ok':
            return []
        
        pages = []
        for row in result.get('data', [])[:limit]:
            pages.append({
                'page': row.get('keys', [''])[0],
                'clicks': row.get('clicks', 0),
                'impressions': row.get('impressions', 0),
                'ctr': row.get('ctr', 0) * 100,
                'position': row.get('position', 0),
            })
        
        return pages
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary."""
        
        result = self.get_search_performance(dimensions=[])
        
        if result.get('status') != 'ok':
            return result
        
        # Aggregate totals from all rows
        rows = result.get('data', [])
        
        total_clicks = sum(r.get('clicks', 0) for r in rows)
        total_impressions = sum(r.get('impressions', 0) for r in rows)
        
        # Calculate average CTR and position
        avg_ctr = (sum(r.get('ctr', 0) for r in rows) / len(rows) * 100) if rows else 0
        avg_position = sum(r.get('position', 0) for r in rows) / len(rows) if rows else 0
        
        return {
            'status': 'ok',
            'total_clicks': total_clicks,
            'total_impressions': total_impressions,
            'average_ctr': round(avg_ctr, 2),
            'average_position': round(avg_position, 2),
            'top_queries': self.get_top_queries(10),
            'top_pages': self.get_page_performance(10),
        }


def get_gsc_performance() -> Dict[str, Any]:
    """Convenience function to get GSC performance."""
    integration = GSCIntegration()
    return integration.get_performance_summary()


def get_top_queries(limit: int = 20) -> List[Dict[str, Any]]:
    """Convenience function to get top queries."""
    integration = GSCIntegration()
    return integration.get_top_queries(limit)


def get_page_performance(limit: int = 20) -> List[Dict[str, Any]]:
    """Convenience function to get page performance."""
    integration = GSCIntegration()
    return integration.get_page_performance(limit)
