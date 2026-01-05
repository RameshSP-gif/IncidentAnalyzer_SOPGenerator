"""
ServiceNow Integration Module

Handles connection to ServiceNow instance and fetches incident data.
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from requests.auth import HTTPBasicAuth
from loguru import logger


class ServiceNowClient:
    """Client for interacting with ServiceNow API"""
    
    def __init__(self, instance: str, username: str, password: str):
        """
        Initialize ServiceNow client
        
        Args:
            instance: ServiceNow instance URL (e.g., your-instance.service-now.com)
            username: ServiceNow username
            password: ServiceNow password
        """
        self.instance = instance
        self.base_url = f"https://{instance}/api/now"
        self.auth = HTTPBasicAuth(username, password)
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
    def test_connection(self) -> bool:
        """Test connection to ServiceNow instance"""
        try:
            response = requests.get(
                f"{self.base_url}/table/incident",
                auth=self.auth,
                headers=self.headers,
                params={"sysparm_limit": 1}
            )
            response.raise_for_status()
            logger.info("Successfully connected to ServiceNow")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to ServiceNow: {e}")
            return False
    
    def fetch_incidents(
        self,
        fields: List[str],
        days_back: int = 90,
        state: str = "closed",
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Fetch incidents from ServiceNow
        
        Args:
            fields: List of fields to retrieve
            days_back: Number of days to look back
            state: Incident state to filter (default: closed)
            limit: Maximum number of records to fetch
            
        Returns:
            List of incident records
        """
        logger.info(f"Fetching incidents from last {days_back} days")
        
        # Calculate date filter
        start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        # Build query
        query_parts = [
            f"state={self._get_state_value(state)}",
            f"sys_created_on>={start_date}"
        ]
        query = "^".join(query_parts)
        
        # Build parameters
        params = {
            "sysparm_query": query,
            "sysparm_fields": ",".join(fields),
            "sysparm_display_value": "true"
        }
        
        if limit:
            params["sysparm_limit"] = limit
        
        incidents = []
        offset = 0
        batch_size = 1000
        
        while True:
            params["sysparm_offset"] = offset
            params["sysparm_limit"] = batch_size
            
            try:
                response = requests.get(
                    f"{self.base_url}/table/incident",
                    auth=self.auth,
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                batch = data.get("result", [])
                
                if not batch:
                    break
                
                incidents.extend(batch)
                logger.info(f"Fetched {len(incidents)} incidents so far...")
                
                if limit and len(incidents) >= limit:
                    incidents = incidents[:limit]
                    break
                
                offset += batch_size
                
            except Exception as e:
                logger.error(f"Error fetching incidents: {e}")
                break
        
        logger.info(f"Total incidents fetched: {len(incidents)}")
        return incidents
    
    def _get_state_value(self, state: str) -> str:
        """Convert state name to ServiceNow state value"""
        state_mapping = {
            "new": "1",
            "in_progress": "2",
            "on_hold": "3",
            "resolved": "6",
            "closed": "7",
            "cancelled": "8"
        }
        return state_mapping.get(state.lower(), "7")
    
    def get_incident_by_number(self, incident_number: str) -> Optional[Dict]:
        """
        Get a specific incident by its number
        
        Args:
            incident_number: Incident number (e.g., INC0012345)
            
        Returns:
            Incident record or None if not found
        """
        try:
            response = requests.get(
                f"{self.base_url}/table/incident",
                auth=self.auth,
                headers=self.headers,
                params={
                    "sysparm_query": f"number={incident_number}",
                    "sysparm_limit": 1
                }
            )
            response.raise_for_status()
            
            data = response.json()
            results = data.get("result", [])
            
            if results:
                return results[0]
            return None
            
        except Exception as e:
            logger.error(f"Error fetching incident {incident_number}: {e}")
            return None


def create_client_from_env() -> ServiceNowClient:
    """Create ServiceNow client from environment variables"""
    instance = os.getenv("SERVICENOW_INSTANCE")
    username = os.getenv("SERVICENOW_USERNAME")
    password = os.getenv("SERVICENOW_PASSWORD")
    
    if not all([instance, username, password]):
        raise ValueError(
            "Missing required environment variables: "
            "SERVICENOW_INSTANCE, SERVICENOW_USERNAME, SERVICENOW_PASSWORD"
        )
    
    return ServiceNowClient(instance, username, password)
