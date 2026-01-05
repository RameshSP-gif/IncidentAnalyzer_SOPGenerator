"""
Unit tests for Data Validator
"""

import unittest
from src.data_validation import DataValidator


class TestDataValidator(unittest.TestCase):
    """Test cases for DataValidator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = DataValidator(
            required_fields=["number", "short_description", "resolution_notes"],
            min_description_length=20,
            min_resolution_length=30
        )
    
    def test_valid_incident(self):
        """Test validation of a valid incident"""
        incident = {
            "number": "INC0001",
            "short_description": "Email access issue",
            "description": "User cannot access email system due to password expiration",
            "resolution_notes": "Reset user password and cleared browser cache. User confirmed access restored.",
            "category": "Email"
        }
        
        result = self.validator.validate_incident(incident)
        self.assertTrue(result["is_valid"])
        self.assertEqual(len(result["errors"]), 0)
    
    def test_missing_required_field(self):
        """Test incident with missing required field"""
        incident = {
            "number": "INC0002",
            "description": "Some description here that meets length requirements"
        }
        
        result = self.validator.validate_incident(incident)
        self.assertFalse(result["is_valid"])
        self.assertTrue(any(e["type"] == "missing_fields" for e in result["errors"]))
    
    def test_short_description(self):
        """Test incident with too short description"""
        incident = {
            "number": "INC0003",
            "short_description": "Email",
            "description": "Short",  # Too short
            "resolution_notes": "Fixed the issue by resetting password and clearing cache",
            "category": "Email"
        }
        
        result = self.validator.validate_incident(incident)
        self.assertFalse(result["is_valid"])
        self.assertTrue(any(e["type"] == "insufficient_description" for e in result["errors"]))
    
    def test_short_resolution(self):
        """Test incident with too short resolution"""
        incident = {
            "number": "INC0004",
            "short_description": "Network issue",
            "description": "Network connection is unstable and dropping frequently",
            "resolution_notes": "Fixed",  # Too short
            "category": "Network"
        }
        
        result = self.validator.validate_incident(incident)
        self.assertFalse(result["is_valid"])
        self.assertTrue(any(e["type"] == "insufficient_resolution" for e in result["errors"]))
    
    def test_placeholder_content(self):
        """Test incident with placeholder content"""
        incident = {
            "number": "INC0005",
            "short_description": "Test test",
            "description": "This is a test test placeholder text for testing",
            "resolution_notes": "Lorem ipsum dolor sit amet consectetur adipiscing",
            "category": "Test"
        }
        
        result = self.validator.validate_incident(incident)
        self.assertFalse(result["is_valid"])
        self.assertTrue(any(e["type"] == "placeholder_content" for e in result["errors"]))
    
    def test_invalid_category(self):
        """Test incident with invalid category"""
        incident = {
            "number": "INC0006",
            "short_description": "Some issue description",
            "description": "Detailed description of the problem that meets length requirements",
            "resolution_notes": "Detailed resolution steps that were taken to fix the issue",
            "category": "Unknown"  # Invalid category
        }
        
        result = self.validator.validate_incident(incident)
        self.assertFalse(result["is_valid"])
        self.assertTrue(any(e["type"] == "invalid_category" for e in result["errors"]))
    
    def test_validate_incidents_batch(self):
        """Test batch validation of incidents"""
        incidents = [
            {
                "number": "INC0001",
                "short_description": "Valid incident",
                "description": "This is a valid incident with proper description",
                "resolution_notes": "Resolution was completed successfully with all steps documented",
                "category": "Email"
            },
            {
                "number": "INC0002",
                "short_description": "Invalid",
                "description": "Short",
                "resolution_notes": "Done",
                "category": "Test"
            }
        ]
        
        valid, invalid = self.validator.validate_incidents(incidents)
        self.assertEqual(len(valid), 1)
        self.assertEqual(len(invalid), 1)
    
    def test_quality_report(self):
        """Test quality report generation"""
        valid = [{"number": "INC0001"}, {"number": "INC0002"}]
        invalid = [{"number": "INC0003", "_validation_errors": [{"type": "missing_fields"}]}]
        
        report = self.validator.generate_quality_report(valid, invalid)
        
        self.assertEqual(report["total_incidents"], 3)
        self.assertEqual(report["valid_incidents"], 2)
        self.assertEqual(report["invalid_incidents"], 1)
        self.assertAlmostEqual(report["quality_score"], 66.67, places=1)


if __name__ == "__main__":
    unittest.main()
