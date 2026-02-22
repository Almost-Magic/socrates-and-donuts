"""
Base CMS Adapter Interface.

All CMS adapters must implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from uuid import UUID


class CMSAdapter(ABC):
    """Base class for all CMS adapters."""
    
    @abstractmethod
    def deploy(self, domain_id: UUID, content: Dict[str, Any], target: str) -> Dict[str, Any]:
        """
        Deploy content to the CMS.
        
        Args:
            domain_id: The domain ID
            content: Content to deploy (title, body, meta, etc.)
            target: Target path or page ID
            
        Returns:
            Dict with deployment_id, status, and details
        """
        pass
    
    @abstractmethod
    def rollback(self, domain_id: UUID, deployment_id: str) -> Dict[str, Any]:
        """
        Rollback a deployment.
        
        Args:
            domain_id: The domain ID
            deployment_id: The deployment ID to rollback
            
        Returns:
            Dict with status and details
        """
        pass
    
    @abstractmethod
    def verify(self, domain_id: UUID, deployment_id: str) -> Dict[str, Any]:
        """
        Verify a deployment was successful.
        
        Args:
            domain_id: The domain ID
            deployment_id: The deployment ID to verify
            
        Returns:
            Dict with verification status and details
        """
        pass
    
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the CMS adapter is properly configured."""
        pass
