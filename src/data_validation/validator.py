"""
Data Validation Module

Detects missing or inconsistent data in incident tickets.
"""

from typing import List, Dict, Set, Tuple
from datetime import datetime
from loguru import logger


class DataValidator:
    """Validates incident data quality"""
    
    def __init__(
        self,
        required_fields: List[str],
        min_description_length: int = 20,
        min_resolution_length: int = 30
    ):
        """
        Initialize data validator
        
        Args:
            required_fields: List of required fields
            min_description_length: Minimum length for description
            min_resolution_length: Minimum length for resolution notes
        """
        self.required_fields = required_fields
        self.min_description_length = min_description_length
        self.min_resolution_length = min_resolution_length
        
    def validate_incidents(self, incidents: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Validate all incidents and separate valid from invalid
        
        Args:
            incidents: List of incident dictionaries
            
        Returns:
            Tuple of (valid_incidents, invalid_incidents)
        """
        logger.info(f"Validating {len(incidents)} incidents")
        
        valid = []
        invalid = []
        
        for incident in incidents:
            validation_result = self.validate_incident(incident)
            
            if validation_result["is_valid"]:
                valid.append(incident)
            else:
                incident["_validation_errors"] = validation_result["errors"]
                invalid.append(incident)
        
        logger.info(f"Valid incidents: {len(valid)}, Invalid: {len(invalid)}")
        return valid, invalid
    
    def validate_incident(self, incident: Dict) -> Dict:
        """
        Validate a single incident
        
        Args:
            incident: Incident dictionary
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        
        # Check required fields
        missing_fields = self._check_required_fields(incident)
        if missing_fields:
            errors.append({
                "type": "missing_fields",
                "fields": missing_fields,
                "severity": "critical"
            })
        
        # Check description length
        description = incident.get("description", "") or ""
        if len(description.strip()) < self.min_description_length:
            errors.append({
                "type": "insufficient_description",
                "message": f"Description too short ({len(description)} chars)",
                "severity": "high"
            })
        
        # Check resolution notes
        resolution = incident.get("resolution_notes", "") or incident.get("close_notes", "") or ""
        if len(resolution.strip()) < self.min_resolution_length:
            errors.append({
                "type": "insufficient_resolution",
                "message": f"Resolution notes too short ({len(resolution)} chars)",
                "severity": "high"
            })
        
        # Check for empty or placeholder content
        if self._has_placeholder_content(incident):
            errors.append({
                "type": "placeholder_content",
                "message": "Contains placeholder or template content",
                "severity": "medium"
            })
        
        # Check category consistency
        if not self._has_valid_category(incident):
            errors.append({
                "type": "invalid_category",
                "message": "Missing or invalid category information",
                "severity": "medium"
            })
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "incident_number": incident.get("number", "UNKNOWN")
        }
    
    def _check_required_fields(self, incident: Dict) -> List[str]:
        """Check for missing required fields"""
        missing = []
        for field in self.required_fields:
            value = incident.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                missing.append(field)
        return missing
    
    def _has_placeholder_content(self, incident: Dict) -> bool:
        """Check if incident has placeholder or template content"""
        placeholders = [
            "lorem ipsum",
            "test test",
            "placeholder",
            "sample text",
            "tbd",
            "to be determined",
            "xxx",
            "n/a"
        ]
        
        text_fields = ["description", "short_description", "resolution_notes", "close_notes"]
        
        for field in text_fields:
            content = str(incident.get(field, "")).lower()
            for placeholder in placeholders:
                if placeholder in content:
                    return True
        
        return False
    
    def _has_valid_category(self, incident: Dict) -> bool:
        """Check if incident has valid category information"""
        category = incident.get("category")
        if not category or category.strip() == "":
            return False
        
        # Check for invalid category values
        invalid_categories = ["none", "other", "unknown", "n/a", "tbd"]
        if category.lower() in invalid_categories:
            return False
        
        return True
    
    def detect_duplicates(self, incidents: List[Dict]) -> List[List[Dict]]:
        """
        Detect potential duplicate incidents
        
        Args:
            incidents: List of incidents
            
        Returns:
            List of duplicate groups
        """
        logger.info("Detecting duplicate incidents")
        
        duplicates = []
        seen = {}
        
        for incident in incidents:
            # Create a key based on description and resolution
            desc = str(incident.get("short_description", "")).lower().strip()
            
            if not desc:
                continue
            
            if desc in seen:
                seen[desc].append(incident)
            else:
                seen[desc] = [incident]
        
        # Find groups with more than one incident
        for key, group in seen.items():
            if len(group) > 1:
                duplicates.append(group)
        
        logger.info(f"Found {len(duplicates)} potential duplicate groups")
        return duplicates
    
    def generate_quality_report(
        self,
        valid: List[Dict],
        invalid: List[Dict]
    ) -> Dict:
        """
        Generate data quality report
        
        Args:
            valid: List of valid incidents
            invalid: List of invalid incidents
            
        Returns:
            Quality report dictionary
        """
        total = len(valid) + len(invalid)
        
        # Count error types
        error_summary = {}
        for incident in invalid:
            errors = incident.get("_validation_errors", [])
            for error in errors:
                error_type = error["type"]
                error_summary[error_type] = error_summary.get(error_type, 0) + 1
        
        report = {
            "total_incidents": total,
            "valid_incidents": len(valid),
            "invalid_incidents": len(invalid),
            "quality_score": (len(valid) / total * 100) if total > 0 else 0,
            "error_summary": error_summary,
            "timestamp": datetime.now().isoformat()
        }
        
        return report


def create_validator_from_config(config: Dict) -> DataValidator:
    """Create validator from configuration"""
    validation_config = config.get("data_validation", {})
    
    return DataValidator(
        required_fields=validation_config.get("required_fields", []),
        min_description_length=validation_config.get("min_description_length", 20),
        min_resolution_length=validation_config.get("min_resolution_length", 30)
    )
