#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gold Tier Orchestrator - Main Controller
Unified orchestration for all Gold Tier integrations:
- LinkedIn (from Silver Tier)
- Facebook Integration
- Odoo ERP Integration
- Cross-platform automation and sync

Features:
- Unified monitoring across all platforms
- Automatic lead sync to Odoo CRM
- Cross-platform posting
- Centralized logging and stats
- Automated workflows

Author: Gold Tier FTE System
Version: 1.0.0
"""

import os
import sys
import json
import time
import signal
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add integrations to path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR / 'integrations'))

# Import integrations
try:
    from facebook_integration import FacebookIntegration, FacebookConfig
except ImportError as e:
    print(f"⚠️ Facebook integration not available: {e}")
    FacebookIntegration = None

try:
    from odoo_integration import OdooIntegration, OdooDockerManager
except ImportError as e:
    print(f"⚠️ Odoo integration not available: {e}")
    OdooIntegration = None
    OdooDockerManager = None


# ============================================================================
# CONFIGURATION
# ============================================================================

class GoldTierConfig:
    """Gold Tier Configuration"""

    # Paths
    PROJECT_ROOT = Path(__file__).parent
    LOG_PATH = PROJECT_ROOT / 'AI_Employee_Vault' / 'Logs' / 'gold_tier.log'
    NEEDS_ACTION_PATH = PROJECT_ROOT / 'Needs_Action'
    SYNC_PATH = PROJECT_ROOT / 'sync-data'

    # Monitoring intervals (seconds)
    LINKEDIN_INTERVAL = int(os.getenv('LINKEDIN_CHECK_INTERVAL', '120'))
    FACEBOOK_INTERVAL = int(os.getenv('FACEBOOK_CHECK_INTERVAL', '120'))
    ODOO_SYNC_INTERVAL = int(os.getenv('ODOO_SYNC_INTERVAL', '300'))

    # Enable/Disable integrations
    ENABLE_LINKEDIN = os.getenv('GOLD_ENABLE_LINKEDIN', 'true').lower() == 'true'
    ENABLE_FACEBOOK = os.getenv('GOLD_ENABLE_FACEBOOK', 'true').lower() == 'true'
    ENABLE_ODOO = os.getenv('GOLD_ENABLE_ODOO', 'true').lower() == 'true'

    # Auto-sync settings
    AUTO_SYNC_LEADS_TO_ODOO = os.getenv('GOLD_AUTO_SYNC_LEADS', 'true').lower() == 'true'
    AUTO_CREATE_QUOTATIONS = os.getenv('GOLD_AUTO_CREATE_QUOTATIONS', 'false').lower() == 'true'

    # Cross-platform posting
    CROSS_POST_ENABLED = os.getenv('GOLD_CROSS_POST', 'false').lower() == 'true'
    POST_TO_LINKEDIN = os.getenv('GOLD_POST_LINKEDIN', 'true').lower() == 'true'
    POST_TO_FACEBOOK = os.getenv('GOLD_POST_FACEBOOK', 'true').lower() == 'true'


# ============================================================================
# LOGGER
# ============================================================================

class Logger:
    """Unified logger for Gold Tier"""

    def __init__(self, log_path: Path):
        self.log_path = log_path
        self._ensure_log_file()

    def _ensure_log_file(self):
        """Create log file if it doesn't exist"""
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            self.log_path.touch()

    def _timestamp(self) -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def log(self, message: str, level: str = 'INFO'):
        """Log message to file and console"""
        timestamp = self._timestamp()
        log_line = f"[{timestamp}] [{level}] {message}"

        # Console output with colors
        if level == 'ERROR':
            print(f"\033[91m{log_line}\033[0m")  # Red
        elif level == 'WARNING':
            print(f"\033[93m{log_line}\033[0m")  # Yellow
        elif level == 'SUCCESS':
            print(f"\033[92m{log_line}\033[0m")  # Green
        elif level == 'SALES':
            print(f"\033[94m{log_line}\033[0m")  # Blue
        elif level == 'SYNC':
            print(f"\033[95m{log_line}\033[0m")  # Magenta
        else:
            print(log_line)

        # File output
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')

    def info(self, message: str):
        self.log(message, 'INFO')

    def warning(self, message: str):
        self.log(message, 'WARNING')

    def error(self, message: str):
        self.log(message, 'ERROR')

    def success(self, message: str):
        self.log(message, 'SUCCESS')

    def sales(self, message: str):
        self.log(message, 'SALES')

    def sync(self, message: str):
        self.log(message, 'SYNC')


# ============================================================================
# GOLD TIER ORCHESTRATOR
# ============================================================================

class GoldTierOrchestrator:
    """Main Gold Tier Orchestrator"""

    def __init__(self):
        self.config = GoldTierConfig()
        self.logger = Logger(self.config.LOG_PATH)
        
        # Integration instances
        self.facebook: Optional[Any] = None
        self.odoo: Optional[Any] = None
        self.odoo_docker: Optional[Any] = None
        
        # Sync data
        self.pending_leads: List[Dict] = []
        self.synced_leads: set = set()
        
        # Stats
        self.stats = {
            'linkedin_checks': 0,
            'facebook_checks': 0,
            'odoo_syncs': 0,
            'leads_synced': 0,
            'posts_created': 0,
            'quotations_created': 0,
            'errors': 0
        }
        
        # Control flags
        self.running = False
        self.threads: List[threading.Thread] = []
        
        # Ensure directories exist
        self.config.NEEDS_ACTION_PATH.mkdir(parents=True, exist_ok=True)
        self.config.SYNC_PATH.mkdir(parents=True, exist_ok=True)

    def initialize(self) -> bool:
        """Initialize all integrations"""
        self.logger.info("="*70)
        self.logger.info("GOLD TIER ORCHESTRATOR - INITIALIZING")
        self.logger.info("="*70)
        
        success = True
        
        # Initialize Facebook
        if self.config.ENABLE_FACEBOOK and FacebookIntegration:
            try:
                self.facebook = FacebookIntegration()
                self.logger.success("✓ Facebook Integration initialized")
            except Exception as e:
                self.logger.error(f"✗ Facebook Integration failed: {e}")
                success = False
        elif self.config.ENABLE_FACEBOOK:
            self.logger.warning("⚠ Facebook Integration not available")
        else:
            self.logger.info("○ Facebook Integration disabled")
        
        # Initialize Odoo
        if self.config.ENABLE_ODOO and OdooIntegration:
            try:
                self.odoo = OdooIntegration()
                self.odoo_docker = OdooDockerManager()
                if self.odoo.connect():
                    self.logger.success("✓ Odoo Integration connected")
                else:
                    self.logger.warning("⚠ Odoo Integration not connected (server may not be running)")
            except Exception as e:
                self.logger.error(f"✗ Odoo Integration failed: {e}")
                success = False
        elif self.config.ENABLE_ODOO:
            self.logger.warning("⚠ Odoo Integration not available")
        else:
            self.logger.info("○ Odoo Integration disabled")
        
        self.logger.info("="*70)
        return success

    def _generate_lead_id(self, source: str, sender: str, content: str) -> str:
        """Generate unique lead ID"""
        import hashlib
        unique_str = f"{source}:{sender}:{hashlib.md5(content.encode()).hexdigest()[:8]}"
        return unique_str

    def _is_sales_lead(self, content: str) -> bool:
        """Check if content is sales-related"""
        keywords = [
            'interested', 'interest', 'demo', 'pricing', 'price', 'buy',
            'purchase', 'quote', 'proposal', 'contract', 'deal', 'opportunity',
            'budget', 'decision', 'timeline', 'requirements', 'rfp', 'rfi'
        ]
        content_lower = content.lower()
        return any(kw in content_lower for kw in keywords)

    def sync_lead_to_odoo(self, source: str, sender: str, content: str,
                         email: str = None, phone: str = None) -> bool:
        """Sync a lead to Odoo CRM"""
        
        if not self.odoo:
            return False
        
        lead_id = self._generate_lead_id(source, sender, content)
        
        if lead_id in self.synced_leads:
            self.logger.info(f"Lead already synced: {lead_id}")
            return False
        
        try:
            # Create lead in Odoo
            odoo_lead_id = self.odoo.create_lead_from_source(
                source=source,
                sender=sender,
                content=content,
                email=email,
                phone=phone
            )
            
            if odoo_lead_id:
                self.synced_leads.add(lead_id)
                self.stats['leads_synced'] += 1
                
                self.logger.sync(f"📌 Lead synced to Odoo: {sender} from {source}")
                
                # Auto-create quotation if enabled and sales lead
                if self.config.AUTO_CREATE_QUOTATIONS and self._is_sales_lead(content):
                    quotation_id = self.odoo.create_quotation_from_lead(odoo_lead_id)
                    if quotation_id:
                        self.stats['quotations_created'] += 1
                        self.logger.sync(f"💼 Quotation auto-created: {quotation_id}")
                
                return True
            
        except Exception as e:
            self.logger.error(f"Failed to sync lead to Odoo: {e}")
            self.stats['errors'] += 1
        
        return False

    def cross_post(self, message: str, link: str = None) -> Dict:
        """Post to multiple platforms"""
        results = {}
        
        if not self.config.CROSS_POST_ENABLED:
            self.logger.info("Cross-posting disabled")
            return results
        
        # Post to LinkedIn (if Silver Tier available)
        if self.config.POST_TO_LINKEDIN:
            try:
                # Try to import and use LinkedIn poster
                from importlib.util import spec_from_file_location, module_from_spec
                
                linkedin_path = self.config.PROJECT_ROOT.parent / 'personal-employe-bronze-FTEs' / 'linkedin_post.py'
                if linkedin_path.exists():
                    spec = spec_from_file_location("linkedin_post", linkedin_path)
                    linkedin_module = module_from_spec(spec)
                    spec.loader.exec_module(linkedin_module)
                    
                    # Use LinkedIn poster
                    if hasattr(linkedin_module, 'LinkedInPoster'):
                        poster = linkedin_module.LinkedInPoster()
                        result = poster.post_update(message)
                        results['linkedin'] = result
                        self.stats['posts_created'] += 1
                        self.logger.success(f"✓ Posted to LinkedIn")
            except Exception as e:
                self.logger.error(f"LinkedIn post failed: {e}")
                self.stats['errors'] += 1
        
        # Post to Facebook
        if self.config.POST_TO_FACEBOOK and self.facebook:
            try:
                result = self.facebook.post_update(message, link)
                results['facebook'] = result
                self.stats['posts_created'] += 1
                self.logger.success(f"✓ Posted to Facebook")
            except Exception as e:
                self.logger.error(f"Facebook post failed: {e}")
                self.stats['errors'] += 1
        
        return results

    def monitor_facebook(self):
        """Monitor Facebook in background thread"""
        self.logger.info("Starting Facebook monitor thread...")
        
        if not self.facebook:
            return
        
        check_count = 0
        
        while self.running:
            try:
                check_count += 1
                self.stats['facebook_checks'] += 1
                
                # Monitor comments and messages
                comments = self.facebook.monitor_comments()
                messages = self.facebook.monitor_messages()
                
                # Sync sales leads to Odoo
                if self.config.AUTO_SYNC_LEADS_TO_ODOO and self.odoo:
                    for comment in comments:
                        if comment.get('is_sales'):
                            self.sync_lead_to_odoo(
                                source='Facebook Comment',
                                sender=comment.get('sender', 'Unknown'),
                                content=comment.get('message', ''),
                            )
                    
                    for message in messages:
                        if message.get('is_sales'):
                            self.sync_lead_to_odoo(
                                source='Facebook Message',
                                sender=message.get('sender', 'Unknown'),
                                content=message.get('message', ''),
                            )
                
                time.sleep(self.config.FACEBOOK_INTERVAL)
                
            except Exception as e:
                self.logger.error(f"Facebook monitor error: {e}")
                self.stats['errors'] += 1
                time.sleep(10)

    def sync_odoo(self):
        """Sync Odoo in background thread"""
        self.logger.info("Starting Odoo sync thread...")
        
        if not self.odoo:
            return
        
        check_count = 0
        
        while self.running:
            try:
                check_count += 1
                self.stats['odoo_syncs'] += 1
                
                # Get recent leads from Odoo
                if self.odoo.crm:
                    leads = self.odoo.crm.get_leads(limit=10)
                    self.logger.sync(f"Odoo CRM: {len(leads)} recent leads")
                
                # Get recent orders
                if self.odoo.sales:
                    orders = self.odoo.sales.get_orders(limit=10)
                    self.logger.sync(f"Odoo Sales: {len(orders)} recent orders")
                
                time.sleep(self.config.ODOO_SYNC_INTERVAL)
                
            except Exception as e:
                self.logger.error(f"Odoo sync error: {e}")
                self.stats['errors'] += 1
                time.sleep(10)

    def start(self):
        """Start the Gold Tier Orchestrator"""
        self.logger.info("="*70)
        self.logger.info("🏆 GOLD TIER ORCHESTRATOR - STARTING")
        self.logger.info("="*70)
        self.logger.info(f"LinkedIn: {'Enabled' if self.config.ENABLE_LINKEDIN else 'Disabled'}")
        self.logger.info(f"Facebook: {'Enabled' if self.config.ENABLE_FACEBOOK else 'Disabled'}")
        self.logger.info(f"Odoo ERP: {'Enabled' if self.config.ENABLE_ODOO else 'Disabled'}")
        self.logger.info(f"Auto-sync leads: {'Yes' if self.config.AUTO_SYNC_LEADS_TO_ODOO else 'No'}")
        self.logger.info(f"Cross-posting: {'Yes' if self.config.CROSS_POST_ENABLED else 'No'}")
        self.logger.info("="*70)
        
        if not self.initialize():
            self.logger.warning("Some integrations failed to initialize. Continuing with available services...")
        
        self.running = True
        
        # Start background threads
        if self.config.ENABLE_FACEBOOK and self.facebook:
            fb_thread = threading.Thread(target=self.monitor_facebook, daemon=True)
            fb_thread.start()
            self.threads.append(fb_thread)
        
        if self.config.ENABLE_ODOO and self.odoo:
            odoo_thread = threading.Thread(target=self.sync_odoo, daemon=True)
            odoo_thread.start()
            self.threads.append(odoo_thread)
        
        self.logger.success("✅ All monitor threads started")
        self.logger.info("Press Ctrl+C to stop")
        
        # Main loop
        try:
            while self.running:
                # Print periodic status
                self.logger.info(f"\n{'='*50}")
                self.logger.info(f"Status Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                self.logger.info(f"FB Checks: {self.stats['facebook_checks']}")
                self.logger.info(f"Odoo Syncs: {self.stats['odoo_syncs']}")
                self.logger.info(f"Leads Synced: {self.stats['leads_synced']}")
                self.logger.info(f"Posts Created: {self.stats['posts_created']}")
                self.logger.info(f"Quotations: {self.stats['quotations_created']}")
                self.logger.info(f"Errors: {self.stats['errors']}")
                
                time.sleep(60)
                
        except KeyboardInterrupt:
            self.logger.info("\n\n👋 Shutting down Gold Tier Orchestrator...")
            self.running = False
        
        # Wait for threads to finish
        for thread in self.threads:
            thread.join(timeout=5)
        
        # Print final stats
        self.logger.info("="*70)
        self.logger.info("FINAL STATS")
        self.logger.info("="*70)
        self.logger.info(f"Facebook checks: {self.stats['facebook_checks']}")
        self.logger.info(f"Odoo syncs: {self.stats['odoo_syncs']}")
        self.logger.info(f"Leads synced to CRM: {self.stats['leads_synced']}")
        self.logger.info(f"Posts created: {self.stats['posts_created']}")
        self.logger.info(f"Quotations created: {self.stats['quotations_created']}")
        self.logger.info(f"Errors: {self.stats['errors']}")
        self.logger.info("="*70)

    def stop(self):
        """Stop the orchestrator"""
        self.running = False


# ============================================================================
# QUICK START FUNCTIONS
# ============================================================================

def start_odoo_docker():
    """Start Odoo Docker containers"""
    if OdooDockerManager:
        docker_mgr = OdooDockerManager()
        docker_mgr.start()
    else:
        print("Odoo integration not available")

def stop_odoo_docker():
    """Stop Odoo Docker containers"""
    if OdooDockerManager:
        docker_mgr = OdooDockerManager()
        docker_mgr.stop()
    else:
        print("Odoo integration not available")

def post_to_all(message: str, link: str = None):
    """Post message to all platforms"""
    orchestrator = GoldTierOrchestrator()
    orchestrator.initialize()
    results = orchestrator.cross_post(message, link)
    print(f"Post results: {json.dumps(results, indent=2)}")
    return results

def sync_leads(leads: List[Dict]):
    """Sync leads to Odoo"""
    orchestrator = GoldTierOrchestrator()
    orchestrator.initialize()
    
    synced = 0
    for lead in leads:
        if orchestrator.sync_lead_to_odoo(
            source=lead.get('source', 'Manual'),
            sender=lead.get('sender', 'Unknown'),
            content=lead.get('content', ''),
            email=lead.get('email'),
            phone=lead.get('phone')
        ):
            synced += 1
    
    print(f"Synced {synced} leads to Odoo")
    return synced


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """CLI interface for Gold Tier Orchestrator"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Gold Tier Orchestrator - Unified AI Employee System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gold_tier_orchestrator.py --start              Start full orchestrator
  python gold_tier_orchestrator.py --odoo-start         Start Odoo Docker
  python gold_tier_orchestrator.py --post "Hello"       Post to all platforms
  python gold_tier_orchestrator.py --status             Check system status
        """
    )
    
    parser.add_argument('--start', action='store_true', help='Start Gold Tier Orchestrator')
    parser.add_argument('--odoo-start', action='store_true', help='Start Odoo Docker containers')
    parser.add_argument('--odoo-stop', action='store_true', help='Stop Odoo Docker containers')
    parser.add_argument('--odoo-status', action='store_true', help='Check Odoo Docker status')
    parser.add_argument('--odoo-backup', action='store_true', help='Create Odoo backup')
    
    parser.add_argument('--post', type=str, help='Post message to all platforms')
    parser.add_argument('--link', type=str, help='Link to include in post')
    
    parser.add_argument('--status', action='store_true', help='Check system status')
    parser.add_argument('--test-connections', action='store_true', help='Test all connections')
    
    args = parser.parse_args()
    
    if args.start:
        orchestrator = GoldTierOrchestrator()
        orchestrator.start()
    
    elif args.odoo_start:
        start_odoo_docker()
    
    elif args.odoo_stop:
        stop_odoo_docker()
    
    elif args.odoo_status:
        if OdooDockerManager:
            docker_mgr = OdooDockerManager()
            docker_mgr.status()
    
    elif args.odoo_backup:
        if OdooDockerManager:
            docker_mgr = OdooDockerManager()
            docker_mgr.backup()
    
    elif args.post:
        post_to_all(args.post, args.link)
    
    elif args.status:
        orchestrator = GoldTierOrchestrator()
        print("\n🏆 GOLD TIER STATUS")
        print("="*50)
        print(f"Facebook: {'✓' if orchestrator.facebook else '✗'}")
        print(f"Odoo: {'✓' if orchestrator.odoo else '✗'}")
        print(f"Config: {orchestrator.config.PROJECT_ROOT}")
        print("="*50)
    
    elif args.test_connections:
        orchestrator = GoldTierOrchestrator()
        print("\n🔌 TESTING CONNECTIONS")
        print("="*50)
        orchestrator.initialize()
        print("="*50)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
