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
        """Extract resolution steps from resolutions - handles both structured and unstructured text"""
        all_steps = []
        
        for res_data in resolutions:
            resolution = res_data["resolution"]
            
            # Skip placeholder or empty resolutions
            if not resolution or 'pending' in resolution.lower() or 'manually' in resolution.lower():
                continue
            
            # Split by common delimiters to find sentences
            lines = resolution.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check for already numbered/bulleted steps
                if any(line.startswith(prefix) for prefix in ['1.', '2.', '3.', '4.', '5.', '-', '*', '•']):
                    # Clean up the step
                    step = line.lstrip('0123456789.-*•) \t')
                    if len(step) > 10:  # Meaningful step
                        all_steps.append(step)
                # Handle plain sentences - split by period if multiple sentences
                elif '.' in line:
                    sentences = [s.strip() for s in line.split('.') if len(s.strip()) > 10]
                    all_steps.extend(sentences)
                # Handle sentences separated by 'and'
                elif ' and ' in line:
                    parts = [p.strip() for p in line.split(' and ') if len(p.strip()) > 10]
                    all_steps.extend(parts)
                # Single meaningful sentence
                elif len(line) > 10:
                    all_steps.append(line)
        
        # Remove duplicates while preserving order and frequency
        seen = set()
        unique_steps = []
        step_freq = {}
        
        for step in all_steps:
            # Normalize for comparison (case-insensitive, first 60 chars)
            normalized = step.lower()[:60]
            
            # Track frequency
            if normalized not in step_freq:
                step_freq[normalized] = []
            step_freq[normalized].append(step)
        
        # Get the best version of each unique step and sort by frequency
        step_list = []
        for normalized, variants in step_freq.items():
            # Use the longest variant (most detailed)
            best_step = max(variants, key=len)
            step_list.append((best_step, len(variants)))
        
        # Sort by frequency (descending) and return top steps
        sorted_steps = sorted(step_list, key=lambda x: x[1], reverse=True)
        return [step for step, _ in sorted_steps[:15]]  # Return top 15 steps
    
    def _generate_markdown_sop(self, cluster_id: int, data: Dict) -> str:
        """Generate SOP in Markdown format - concise and action-oriented"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        sop = f"""# SOP-{cluster_id:04d}: {data['category']} Resolution

**Category**: {data['category']} | **Created**: {timestamp}

---

## Problem
"""
        
        # Add problems - concise format
        for problem in data['problems'][:3]:  # Top 3 problems
            sop += f"- {problem}\n"
        
        sop += "\n---\n\n## Resolution Steps\n\n"
        
        # Add resolution steps - direct and actionable
        if data['resolution_steps']:
            for i, step in enumerate(data['resolution_steps'], 1):
                # Make step more direct/command-like
                step_text = step.strip()
                if not step_text[0].isupper():
                    step_text = step_text[0].upper() + step_text[1:]
                # Remove trailing period if present and make it imperative
                step_text = step_text.rstrip('.')
                sop += f"{i}. {step_text}\n"
        else:
            sop += "1. Review the related incidents below for resolution guidance\n"
        
        sop += "\n---\n\n## Verification\n\n"
        sop += "- Issue resolved with user\n"
        sop += "- Systems functioning normally\n"
        sop += "- Resolution documented in ticket\n"
        
        # Add related incidents only if multiple exist
        if len(data['related_incidents']) > 1:
            sop += "\n---\n\n## Related Incidents\n\n"
            for incident_num in data['related_incidents'][:5]:  # Top 5 related
                sop += f"- {incident_num}\n"
        
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
