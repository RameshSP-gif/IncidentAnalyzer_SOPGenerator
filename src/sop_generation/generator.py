"""
SOP Generation Module

Generates Standard Operating Procedures from clustered incidents.
"""

from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger


class SOPGenerator:
    """Generates SOPs from incident clusters"""
    
    def __init__(
        self,
        min_incidents: int = 3,
        template_format: str = "markdown"
    ):
        """
        Initialize SOP generator
        
        Args:
            min_incidents: Minimum number of incidents required for SOP
            template_format: Output format (markdown, html, etc.)
        """
        self.min_incidents = min_incidents
        self.template_format = template_format
        
    def generate_sop(
        self,
        cluster_id: int,
        incidents: List[Dict],
        analysis: Dict
    ) -> Optional[str]:
        """
        Generate SOP from incident cluster
        
        Args:
            cluster_id: ID of the cluster
            incidents: List of incidents in cluster
            analysis: Cluster analysis data
            
        Returns:
            Generated SOP as string or None if insufficient data
        """
        if len(incidents) < self.min_incidents:
            logger.warning(
                f"Cluster {cluster_id} has only {len(incidents)} incidents. "
                f"Minimum {self.min_incidents} required."
            )
            return None
        
        logger.info(f"Generating SOP for cluster {cluster_id}")
        
        # Extract SOP components
        sop_data = self._extract_sop_components(incidents, analysis)
        
        # Generate SOP based on format
        if self.template_format == "markdown":
            return self._generate_markdown_sop(cluster_id, sop_data)
        else:
            return self._generate_markdown_sop(cluster_id, sop_data)
    
    def _extract_sop_components(
        self,
        incidents: List[Dict],
        analysis: Dict
    ) -> Dict:
        """Extract components needed for SOP"""
        
        # Extract problem patterns
        problems = set()
        symptoms = set()
        resolutions = []
        
        for incident in incidents:
            # Short description as problem
            short_desc = incident.get("short_description", "")
            if short_desc:
                problems.add(short_desc)
            
            # Extract symptoms from description
            desc = incident.get("description", "")
            if desc:
                symptoms.add(desc[:200])  # First 200 chars
            
            # Collect resolutions
            resolution = (
                incident.get("resolution_notes", "") or
                incident.get("close_notes", "")
            )
            if resolution:
                resolutions.append({
                    "incident_number": incident.get("number"),
                    "resolution": resolution,
                    "priority": incident.get("priority")
                })
        
        # Extract common resolution steps
        common_steps = self._extract_resolution_steps(resolutions)
        
        # Get category information
        categories = analysis.get("common_categories", {})
        primary_category = max(categories.items(), key=lambda x: x[1])[0] if categories else "General"
        
        return {
            "problems": list(problems)[:5],  # Top 5 problem descriptions
            "symptoms": list(symptoms)[:5],   # Top 5 symptom descriptions
            "resolution_steps": common_steps,
            "category": primary_category,
            "incident_count": len(incidents),
            "priority_distribution": analysis.get("priority_distribution", {}),
            "avg_resolution_time": analysis.get("avg_resolution_time", 0),
            "representative_incident": analysis.get("representative_incident"),
            "related_incidents": [inc.get("number") for inc in incidents[:10]]
        }
    
    def _extract_resolution_steps(self, resolutions: List[Dict]) -> List[str]:
        """Extract common resolution steps from resolutions and convert to actionable instructions"""
        all_steps = []
        
        # First try to find existing numbered/bulleted steps
        for res_data in resolutions:
            resolution = res_data["resolution"]
            lines = resolution.split('\n')
            
            for line in lines:
                line = line.strip()
                # Look for step indicators
                if any(line.startswith(prefix) for prefix in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '0.', '-', '*', '•', '▪', '○']):
                    step = line.lstrip('0123456789.-*•▪○) \t')
                    if len(step) > 10:
                        all_steps.append(self._convert_to_imperative(step))
        
        # If no structured steps found, convert resolution into action steps
        if not all_steps:
            for res_data in resolutions:
                resolution = res_data["resolution"]
                
                # Split by common delimiters
                sentences = []
                for delimiter in ['. ', '.\n', '; ', ';\n']:
                    if delimiter in resolution:
                        sentences.extend([s.strip() for s in resolution.split(delimiter) if s.strip()])
                        break
                
                if not sentences:
                    sentences = [resolution]
                
                # Convert each sentence into a step
                for sentence in sentences:
                    sentence = sentence.strip().rstrip('.')
                    if sentence and len(sentence) > 15:
                        imperative_step = self._convert_to_imperative(sentence)
                        if imperative_step:
                            all_steps.append(imperative_step)
        
        # If still no steps, create detailed steps from the full resolution
        if not all_steps and resolutions:
            resolution_text = resolutions[0]["resolution"]
            problem = resolutions[0].get('problem', 'the reported issue')
            
            if resolution_text and len(resolution_text) > 20:
                # Create detailed actionable steps
                all_steps = [
                    f"Identify and verify the symptoms of {problem}",
                    f"Follow these resolution steps: {self._convert_to_imperative(resolution_text)}",
                    "Test the solution to confirm the issue is resolved",
                    "Verify all affected systems/services are functioning normally",
                    "Document the resolution and close the incident ticket"
                ]
        
        # Get unique steps (deduplicate similar ones)
        unique_steps = []
        seen_patterns = set()
        
        for step in all_steps:
            # Use first 50 chars as pattern for deduplication
            pattern = step.lower()[:50]
            if pattern not in seen_patterns:
                seen_patterns.add(pattern)
                unique_steps.append(step)
        
        return unique_steps[:20]  # Return up to 20 steps
    
    def _convert_to_imperative(self, text: str) -> str:
        """Convert past-tense resolution text to imperative instructions"""
        text = text.strip()
        
        # Mapping of past tense verbs to imperative commands
        verb_conversions = {
            # Past tense -> Imperative
            'restarted': 'Restart',
            'reset': 'Reset',
            'checked': 'Check',
            'verified': 'Verify',
            'updated': 'Update',
            'configured': 'Configure',
            'installed': 'Install',
            'removed': 'Remove',
            'disabled': 'Disable',
            'enabled': 'Enable',
            'replaced': 'Replace',
            'tested': 'Test',
            'ran': 'Run',
            'opened': 'Open',
            'closed': 'Close',
            'cleared': 'Clear',
            'recreated': 'Recreate',
            'increased': 'Increase',
            'decreased': 'Decrease',
            'set': 'Set',
            'changed': 'Change',
            'added': 'Add',
            'deleted': 'Delete',
            'modified': 'Modify',
            'reviewed': 'Review',
            'rebuilt': 'Rebuild',
            'reconfigured': 'Reconfigure',
            'repaired': 'Repair',
            'fixed': 'Fix',
            'resolved': 'Resolve',
            'ensured': 'Ensure',
            'rebooted': 'Reboot',
            'downloaded': 'Download',
            'uploaded': 'Upload',
            'adjusted': 'Adjust',
            'diagnosed': 'Diagnose',
            'identified': 'Identify',
            'confirmed': 'Confirm',
            'advised': 'Advise',
            'implemented': 'Implement',
            'created': 'Create',
            'sent': 'Send',
            'unlocked': 'Unlock',
            'logged': 'Log',
            'connected': 'Connect',
            'disconnected': 'Disconnect',
            'found': 'Find',
            'located': 'Locate',
            'navigated': 'Navigate',
            'selected': 'Select',
            'clicked': 'Click',
            'entered': 'Enter',
            'typed': 'Type',
            'executed': 'Execute',
            'performed': 'Perform',
            'applied': 'Apply',
            'activated': 'Activate',
            'deactivated': 'Deactivate'
        }
        
        # Convert text
        words = text.split()
        if not words:
            return text
        
        first_word_lower = words[0].lower().rstrip('.,;:')
        
        # Check if first word is a past tense verb we can convert
        if first_word_lower in verb_conversions:
            words[0] = verb_conversions[first_word_lower]
            result = ' '.join(words)
        else:
            # Try to detect past tense patterns and convert
            result = text
            for past, imperative in verb_conversions.items():
                # Replace at word boundaries
                import re
                pattern = r'\b' + past + r'\b'
                # Only replace if it's at the beginning or after common phrases
                if re.match(pattern, result.lower()):
                    result = re.sub(pattern, imperative, result, count=1, flags=re.IGNORECASE)
                    break
        
        # Ensure proper capitalization
        if result:
            result = result[0].upper() + result[1:]
        
        # Remove trailing period and ensure instruction format
        result = result.rstrip('.')
        
        # Add period at the end
        if result and not result.endswith(('.', '!', '?')):
            result += '.'
        
        return result
    
    def _generate_markdown_sop(self, cluster_id: int, data: Dict) -> str:
        """Generate SOP in Markdown format"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        sop = f"""# Standard Operating Procedure

## SOP Information
- **SOP ID**: SOP-{cluster_id:04d}
- **Category**: {data['category']}
- **Based on**: {data['incident_count']} incidents
- **Generated**: {timestamp}
- **Average Resolution Time**: {data['avg_resolution_time']:.1f} hours

---

## Overview

This SOP provides step-by-step instructions for resolving incidents related to **{data['category']}**. This procedure has been created by analyzing {data['incident_count']} similar incidents.

---

## Problem Statement

Common problems addressed by this SOP:

"""
        
        # Add problems
        for i, problem in enumerate(data['problems'], 1):
            sop += f"{i}. {problem}\n"
        
        sop += "\n---\n\n## Symptoms\n\nUsers may experience the following symptoms:\n\n"
        
        # Add symptoms
        for i, symptom in enumerate(data['symptoms'], 1):
            sop += f"{i}. {symptom}...\n"
        
        sop += "\n---\n\n## Prerequisites\n\n"
        sop += "- Access to relevant systems\n"
        sop += "- Appropriate permissions\n"
        sop += "- User information and affected systems identified\n"
        
        sop += "\n---\n\n## Resolution Steps\n\n"
        
        # Add resolution steps
        if data['resolution_steps']:
            for i, step in enumerate(data['resolution_steps'], 1):
                sop += f"### Step {i}\n\n{step}\n\n"
        else:
            sop += "_No structured steps available. Please refer to related incidents below._\n\n"
        
        sop += "---\n\n## Verification\n\n"
        sop += "After completing the resolution steps:\n\n"
        sop += "1. Verify the issue is resolved with the user\n"
        sop += "2. Confirm all systems are functioning normally\n"
        sop += "3. Document the resolution in the incident ticket\n"
        sop += "4. Close the incident\n"
        
        sop += "\n---\n\n## Related Incidents\n\n"
        sop += "This SOP is based on the following incidents:\n\n"
        
        for incident_num in data['related_incidents']:
            sop += f"- {incident_num}\n"
        
        sop += f"\n**Representative Incident**: {data['representative_incident']}\n"
        
        sop += "\n---\n\n## Priority Distribution\n\n"
        for priority, count in data['priority_distribution'].items():
            sop += f"- Priority {priority}: {count} incidents\n"
        
        sop += "\n---\n\n## Notes\n\n"
        sop += "- This SOP was automatically generated from incident analysis\n"
        sop += "- Review and customize based on your environment\n"
        sop += "- Update as new information becomes available\n"
        sop += f"- Last updated: {timestamp}\n"
        
        return sop
    
    def generate_summary_report(
        self,
        all_sops: List[Dict]
    ) -> str:
        """
        Generate summary report of all SOPs
        
        Args:
            all_sops: List of SOP data dictionaries
            
        Returns:
            Summary report as string
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""# SOP Generation Summary Report

**Generated**: {timestamp}
**Total SOPs Created**: {len(all_sops)}

---

## SOPs Overview

"""
        
        for i, sop_data in enumerate(all_sops, 1):
            report += f"""
### {i}. SOP-{sop_data['cluster_id']:04d}
- **Category**: {sop_data['category']}
- **Incidents Analyzed**: {sop_data['incident_count']}
- **Avg Resolution Time**: {sop_data['avg_resolution_time']:.1f} hours
- **File**: `SOP-{sop_data['cluster_id']:04d}.md`

"""
        
        report += "\n---\n\n## Statistics\n\n"
        
        total_incidents = sum(sop['incident_count'] for sop in all_sops)
        avg_incidents_per_sop = total_incidents / len(all_sops) if all_sops else 0
        
        report += f"- Total incidents analyzed: {total_incidents}\n"
        report += f"- Average incidents per SOP: {avg_incidents_per_sop:.1f}\n"
        
        # Category distribution
        categories = {}
        for sop in all_sops:
            cat = sop['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        report += "\n### SOPs by Category\n\n"
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            report += f"- {cat}: {count} SOPs\n"
        
        return report


def create_generator_from_config(config: Dict) -> SOPGenerator:
    """Create SOP generator from configuration"""
    sop_config = config.get("sop_generation", {})
    
    return SOPGenerator(
        min_incidents=sop_config.get("min_incidents_for_sop", 3),
        template_format=sop_config.get("output_format", "markdown")
    )
