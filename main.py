"""
Main Orchestrator

Coordinates all components of the SOP creation system.
"""

import os
import sys
import json
import yaml
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv
from loguru import logger

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.servicenow import create_client_from_env
from src.data_validation import create_validator_from_config
from src.categorization import create_categorizer_from_config
from src.sop_generation import create_generator_from_config
from src.database import get_db_client


class SOPOrchestrator:
    """Main orchestrator for SOP creation process"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize orchestrator
        
        Args:
            config_path: Path to configuration file
        """
        # Load environment variables
        load_dotenv()
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize components
        logger.info("Initializing SOP Orchestrator")
        self.servicenow_client = None
        self.validator = create_validator_from_config(self.config)
        self.categorizer = create_categorizer_from_config(self.config)
        self.sop_generator = create_generator_from_config(self.config)
        self.db_client = get_db_client()
        
        # Setup directories
        self.data_dir = Path(os.getenv("DATA_DIR", "./data"))
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "./output"))
        self._create_directories()
        
    def _setup_logging(self):
        """Setup logging configuration"""
        log_config = self.config.get("logging", {})
        log_level = os.getenv("LOG_LEVEL", log_config.get("level", "INFO"))
        
        # Remove default logger
        logger.remove()
        
        # Add console logger
        logger.add(
            sys.stderr,
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
        )
        
        # Add file logger
        log_file = log_config.get("file", "logs/app.log")
        logger.add(
            log_file,
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
            rotation="10 MB"
        )
    
    def _create_directories(self):
        """Create necessary directories"""
        directories = [
            self.data_dir / "incidents",
            self.data_dir / "validated",
            self.data_dir / "clusters",
            self.output_dir / "sops",
            self.output_dir / "reports",
            Path("logs")
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def fetch_incidents(self, days_back: int = 90, limit: int = None) -> List[Dict]:
        """
        Fetch incidents from ServiceNow
        
        Args:
            days_back: Number of days to look back
            limit: Maximum number of incidents to fetch
            
        Returns:
            List of incidents
        """
        logger.info("=== STEP 1: Fetching Incidents ===")
        
        if not self.servicenow_client:
            self.servicenow_client = create_client_from_env()
        
        # Test connection
        if not self.servicenow_client.test_connection():
            raise ConnectionError("Failed to connect to ServiceNow")
        
        # Fetch incidents
        fields = self.config["servicenow"]["fields"]
        incidents = self.servicenow_client.fetch_incidents(
            fields=fields,
            days_back=days_back,
            limit=limit
        )
        
        # Save raw data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.data_dir / "incidents" / f"incidents_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(incidents, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(incidents)} incidents to {output_file}")
        
        # Save to MongoDB
        logger.info("Saving incidents to MongoDB...")
        inserted_count = self.db_client.insert_many_incidents(incidents)
        logger.info(f"Inserted {inserted_count} incidents into MongoDB")
        
        return incidents
    
    def validate_incidents(self, incidents: List[Dict]) -> tuple:
        """
        Validate incidents
        
        Args:
            incidents: List of incidents to validate
            
        Returns:
            Tuple of (valid_incidents, invalid_incidents)
        """
        logger.info("=== STEP 2: Validating Incidents ===")
        
        valid, invalid = self.validator.validate_incidents(incidents)
        
        # Generate quality report
        quality_report = self.validator.generate_quality_report(valid, invalid)
        
        # Save validation results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save valid incidents
        valid_file = self.data_dir / "validated" / f"valid_{timestamp}.json"
        with open(valid_file, 'w', encoding='utf-8') as f:
            json.dump(valid, f, indent=2, ensure_ascii=False)
        
        # Save invalid incidents with errors
        invalid_file = self.data_dir / "validated" / f"invalid_{timestamp}.json"
        with open(invalid_file, 'w', encoding='utf-8') as f:
            json.dump(invalid, f, indent=2, ensure_ascii=False)
        
        # Save quality report
        report_file = self.output_dir / "reports" / f"quality_report_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(quality_report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Quality Score: {quality_report['quality_score']:.2f}%")
        logger.info(f"Valid incidents saved to {valid_file}")
        logger.info(f"Quality report saved to {report_file}")
        
        return valid, invalid
    
    def categorize_incidents(self, incidents: List[Dict]) -> Dict[int, List[Dict]]:
        """
        Categorize incidents into clusters
        
        Args:
            incidents: List of validated incidents
            
        Returns:
            Dictionary mapping cluster_id to incidents
        """
        logger.info("=== STEP 3: Categorizing Incidents ===")
        
        clusters = self.categorizer.categorize_incidents(incidents)
        
        # Analyze each cluster
        cluster_analyses = {}
        for cluster_id, cluster_incidents in clusters.items():
            analysis = self.categorizer.analyze_cluster(cluster_id, cluster_incidents)
            cluster_analyses[cluster_id] = analysis
        
        # Save clusters
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clusters_file = self.data_dir / "clusters" / f"clusters_{timestamp}.json"
        
        # Convert clusters for JSON serialization
        clusters_serializable = {
            str(cluster_id): cluster_incidents
            for cluster_id, cluster_incidents in clusters.items()
        }
        
        with open(clusters_file, 'w', encoding='utf-8') as f:
            json.dump(clusters_serializable, f, indent=2, ensure_ascii=False)
        
        # Save analyses
        analyses_file = self.output_dir / "reports" / f"cluster_analyses_{timestamp}.json"
        with open(analyses_file, 'w', encoding='utf-8') as f:
            json.dump(cluster_analyses, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Clusters saved to {clusters_file}")
        logger.info(f"Analyses saved to {analyses_file}")
        
        return clusters
    
    def generate_sops(self, clusters: Dict[int, List[Dict]]) -> List[str]:
        """
        Generate SOPs from clusters
        
        Args:
            clusters: Dictionary mapping cluster_id to incidents
            
        Returns:
            List of generated SOP file paths
        """
        logger.info("=== STEP 4: Generating SOPs ===")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sop_files = []
        sop_data_list = []
        
        for cluster_id, cluster_incidents in clusters.items():
            # Analyze cluster
            analysis = self.categorizer.analyze_cluster(cluster_id, cluster_incidents)
            
            # Generate SOP
            sop_content = self.sop_generator.generate_sop(
                cluster_id,
                cluster_incidents,
                analysis
            )
            
            if sop_content:
                # Save SOP
                sop_file = self.output_dir / "sops" / f"SOP-{cluster_id:04d}_{timestamp}.md"
                with open(sop_file, 'w', encoding='utf-8') as f:
                    f.write(sop_content)
                
                sop_files.append(str(sop_file))
                logger.info(f"Generated SOP: {sop_file}")
                
                # Collect SOP data for summary
                sop_data_list.append({
                    "cluster_id": cluster_id,
                    "category": analysis.get("common_categories", {}),
                    "incident_count": len(cluster_incidents),
                    "avg_resolution_time": analysis.get("avg_resolution_time", 0)
                })
        
        # Generate summary report
        if sop_data_list:
            # Fix category extraction for summary
            for sop_data in sop_data_list:
                categories = sop_data["category"]
                if categories:
                    sop_data["category"] = max(categories.items(), key=lambda x: x[1])[0]
                else:
                    sop_data["category"] = "General"
            
            summary = self.sop_generator.generate_summary_report(sop_data_list)
            summary_file = self.output_dir / "reports" / f"sop_summary_{timestamp}.md"
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            logger.info(f"Summary report saved to {summary_file}")
        
        logger.info(f"Generated {len(sop_files)} SOPs")
        return sop_files
    
    def analyze_from_mongodb(self, limit: int = 5000) -> Dict:
        """
        Analyze incidents directly from MongoDB and generate SOPs
        
        Args:
            limit: Maximum number of incidents to analyze
            
        Returns:
            Dictionary with analysis results
        """
        logger.info("=" * 60)
        logger.info("Analyzing Incidents from MongoDB")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Step 1: Load incidents from MongoDB
            logger.info("=== STEP 1: Loading Incidents from MongoDB ===")
            incidents = self.db_client.get_all_incidents(limit=limit)
            
            if not incidents:
                logger.error("No incidents in MongoDB. Exiting.")
                return {"status": "error", "message": "No incidents in MongoDB"}
            
            logger.info(f"Loaded {len(incidents)} incidents from MongoDB")
            
            # Step 2: Validate incidents
            valid, invalid = self.validate_incidents(incidents)
            
            if not valid:
                logger.error("No valid incidents. Exiting.")
                return {"status": "error", "message": "No valid incidents"}
            
            # Step 3: Categorize incidents
            clusters = self.categorize_incidents(valid)
            
            if not clusters:
                logger.error("No clusters created. Exiting.")
                return {"status": "error", "message": "No clusters created"}
            
            # Step 4: Generate SOPs
            sop_files = self.generate_sops(clusters)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info("=" * 60)
            logger.info("Analysis Completed Successfully")
            logger.info(f"Duration: {duration:.2f} seconds")
            logger.info(f"Total Incidents: {len(incidents)}")
            logger.info(f"Valid Incidents: {len(valid)}")
            logger.info(f"Clusters: {len(clusters)}")
            logger.info(f"SOPs Generated: {len(sop_files)}")
            logger.info("=" * 60)
            
            return {
                "status": "success",
                "total_incidents": len(incidents),
                "valid_incidents": len(valid),
                "invalid_incidents": len(invalid),
                "clusters": len(clusters),
                "sops_generated": len(sop_files),
                "duration_seconds": duration,
                "sop_files": sop_files
            }
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}
    
    def run_full_pipeline(
        self,
        days_back: int = 90,
        limit: int = None
    ) -> Dict:
        """
        Run the complete SOP generation pipeline
        
        Args:
            days_back: Number of days to look back for incidents
            limit: Maximum number of incidents to process
            
        Returns:
            Dictionary with pipeline results
        """
        logger.info("=" * 60)
        logger.info("Starting SOP Generation Pipeline")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Step 1: Fetch incidents
            incidents = self.fetch_incidents(days_back, limit)
            
            if not incidents:
                logger.error("No incidents fetched. Exiting.")
                return {"status": "error", "message": "No incidents fetched"}
            
            # Step 2: Validate incidents
            valid, invalid = self.validate_incidents(incidents)
            
            if not valid:
                logger.error("No valid incidents. Exiting.")
                return {"status": "error", "message": "No valid incidents"}
            
            # Step 3: Categorize incidents
            clusters = self.categorize_incidents(valid)
            
            if not clusters:
                logger.error("No clusters created. Exiting.")
                return {"status": "error", "message": "No clusters created"}
            
            # Step 4: Generate SOPs
            sop_files = self.generate_sops(clusters)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info("=" * 60)
            logger.info("Pipeline Completed Successfully")
            logger.info(f"Duration: {duration:.2f} seconds")
            logger.info(f"Total Incidents: {len(incidents)}")
            logger.info(f"Valid Incidents: {len(valid)}")
            logger.info(f"Clusters: {len(clusters)}")
            logger.info(f"SOPs Generated: {len(sop_files)}")
            logger.info("=" * 60)
            
            return {
                "status": "success",
                "total_incidents": len(incidents),
                "valid_incidents": len(valid),
                "invalid_incidents": len(invalid),
                "clusters": len(clusters),
                "sops_generated": len(sop_files),
                "duration_seconds": duration,
                "sop_files": sop_files
            }
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Autonomous SOP Creation System"
    )
    
    parser.add_argument(
        "--fetch",
        action="store_true",
        help="Fetch incidents from ServiceNow"
    )
    
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate incidents"
    )
    
    parser.add_argument(
        "--categorize",
        action="store_true",
        help="Categorize incidents"
    )
    
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate SOPs"
    )
    
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Number of days to look back (default: 90)"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of incidents to fetch"
    )
    
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--from-mongodb",
        action="store_true",
        help="Analyze incidents from MongoDB (skip fetch)"
    )
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = SOPOrchestrator(config_path=args.config)
    
    # If analyzing from MongoDB
    if args.from_mongodb:
        result = orchestrator.analyze_from_mongodb(limit=args.limit or 5000)
        
        if result["status"] == "success":
            print("\n✓ MongoDB analysis completed successfully!")
            print(f"  Analyzed {result['total_incidents']} incidents from MongoDB")
            print(f"  Generated {result['sops_generated']} SOPs from {result['valid_incidents']} valid incidents")
            print(f"  Duration: {result['duration_seconds']:.2f} seconds")
        else:
            print(f"\n✗ Analysis failed: {result.get('message', 'Unknown error')}")
            sys.exit(1)
        
        return
    
    # If no specific steps specified, run full pipeline
    if not any([args.fetch, args.validate, args.categorize, args.generate]):
        args.fetch = args.validate = args.categorize = args.generate = True
    
    # Initialize orchestrator
    orchestrator = SOPOrchestrator(config_path=args.config)
    
    # Run pipeline
    if all([args.fetch, args.validate, args.categorize, args.generate]):
        # Run full pipeline
        result = orchestrator.run_full_pipeline(
            days_back=args.days,
            limit=args.limit
        )
        
        if result["status"] == "success":
            print("\n✓ SOP generation completed successfully!")
            print(f"  Generated {result['sops_generated']} SOPs from {result['valid_incidents']} incidents")
            print(f"  Duration: {result['duration_seconds']:.2f} seconds")
        else:
            print(f"\n✗ Pipeline failed: {result.get('message', 'Unknown error')}")
            sys.exit(1)
    else:
        # Run individual steps (for advanced usage)
        print("Individual step execution not yet implemented.")
        print("Use without flags to run full pipeline.")


if __name__ == "__main__":
    main()
