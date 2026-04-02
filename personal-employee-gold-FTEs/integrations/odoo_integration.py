#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo Integration - Gold Tier
Complete Odoo ERP integration for CRM, Sales, Inventory, and Automation.

Features:
- CRM and Lead Management
- Sales Order Automation
- Customer Management
- Product and Inventory
- Invoice Management
- Automated Workflows
- Docker-based deployment

Author: Gold Tier FTE System
Version: 1.0.0
"""

import os
import sys
import json
import time
import hashlib
import re
import xmlrpc.client
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# ============================================================================
# CONFIGURATION
# ============================================================================

class OdooConfig:
    """Odoo Integration Configuration"""

    # Paths
    SCRIPT_DIR = Path(__file__).parent
    PROJECT_ROOT = SCRIPT_DIR.parent
    LOG_PATH = PROJECT_ROOT / 'AI_Employee_Vault' / 'Logs' / 'odoo.log'
    NEEDS_ACTION_PATH = PROJECT_ROOT / 'Needs_Action'
    SYNC_PATH = PROJECT_ROOT / 'odoo-sync'

    # Odoo Connection
    ODOO_URL = os.getenv('ODOO_URL', 'http://localhost:8069')
    ODOO_DB = os.getenv('ODOO_DB', 'odoo')
    ODOO_USERNAME = os.getenv('ODOO_USERNAME', 'admin')
    ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'admin_secret_123')
    
    # Docker settings
    DOCKER_COMPOSE_PATH = SCRIPT_DIR.parent / 'odoo-docker' / 'docker-compose.yml'
    
    # Sync settings
    SYNC_INTERVAL = int(os.getenv('ODOO_SYNC_INTERVAL', '300'))  # seconds
    AUTO_CREATE_LEADS = os.getenv('ODOO_AUTO_CREATE_LEADS', 'true').lower() == 'true'
    
    # Sales keywords (consistent with other integrations)
    SALES_KEYWORDS = [
        'interested', 'interest', 'demo', 'pricing', 'price', 'buy',
        'purchase', 'quote', 'proposal', 'contract', 'deal', 'opportunity',
        'budget', 'decision', 'timeline', 'requirements', 'rfp', 'rfi',
        'vendor', 'solution', 'partnership', 'collaboration', 'meeting',
        'call', 'discuss', 'explore', 'services', 'product', 'enterprise'
    ]


# ============================================================================
# LOGGER
# ============================================================================

class Logger:
    """Simple file and console logger"""

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


# ============================================================================
# ODOO XML-RPC CLIENT
# ============================================================================

class OdooClient:
    """Odoo XML-RPC client for API communication"""

    def __init__(self, url: str = None, db: str = None, username: str = None, password: str = None):
        self.config = OdooConfig()
        self.logger = Logger(self.config.LOG_PATH)
        
        self.url = url or self.config.ODOO_URL
        self.db = db or self.config.ODOO_DB
        self.username = username or self.config.ODOO_USERNAME
        self.password = password or self.config.ODOO_PASSWORD
        
        self.uid = None
        self.common = None
        self.models = None
        
        self._connect()

    def _connect(self):
        """Connect to Odoo server"""
        try:
            # Common endpoint for authentication
            self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            
            # Authenticate
            self.uid = self.common.authenticate(db=self.db, login=self.username, password=self.password)
            
            if not self.uid:
                raise Exception("Authentication failed. Check credentials.")
            
            # Models endpoint for operations
            self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            
            self.logger.success(f"Connected to Odoo: {self.url} (User ID: {self.uid})")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Odoo: {e}")
            raise

    def execute(self, model: str, method: str, *args, **kwargs):
        """Execute a method on a model"""
        try:
            return self.models.execute_kw(
                self.db, self.uid, self.password,
                model, method,
                args, kwargs
            )
        except Exception as e:
            self.logger.error(f"Error executing {method} on {model}: {e}")
            raise

    def search(self, model: str, domain: List, limit: int = 80, offset: int = 0) -> List:
        """Search records"""
        return self.execute(model, 'search', domain, limit=limit, offset=offset)

    def search_read(self, model: str, domain: List, fields: List = None, limit: int = 80) -> List[Dict]:
        """Search and read records"""
        return self.execute(model, 'search_read', domain, fields=fields, limit=limit)

    def create(self, model: str, values: Dict) -> int:
        """Create a record"""
        record_id = self.execute(model, 'create', values)
        self.logger.info(f"Created {model} record with ID: {record_id}")
        return record_id

    def write(self, model: str, ids: List, values: Dict) -> bool:
        """Update records"""
        return self.execute(model, 'write', ids, values)

    def unlink(self, model: str, ids: List) -> bool:
        """Delete records"""
        return self.execute(model, 'unlink', ids)

    def call_method(self, model: str, id: int, method: str, *args):
        """Call a method on a specific record"""
        return self.execute(model, method, [id], *args)


# ============================================================================
# ODOO CRM INTEGRATION
# ============================================================================

class OdooCRM:
    """Odoo CRM integration for lead and opportunity management"""

    def __init__(self, client: OdooClient):
        self.client = client
        self.config = OdooConfig()
        self.logger = Logger(self.config.LOG_PATH)

    def create_lead(self, name: str, email: str = None, phone: str = None,
                   company: str = None, description: str = None,
                   source: str = 'Website', priority: str = '3') -> int:
        """Create a new lead in Odoo CRM"""
        
        values = {
            'name': name,
            'contact_name': name,
            'email_from': email,
            'phone': phone,
            'partner_name': company or name,
            'description': description,
            'source_id': self._get_or_create_source(source),
            'priority': priority,
            'stage_id': self._get_default_stage_id()
        }
        
        # Remove None values
        values = {k: v for k, v in values.items() if v is not None}
        
        lead_id = self.client.create('crm.lead', values)
        self.logger.success(f"Lead created: {name} (ID: {lead_id})")
        
        return lead_id

    def create_opportunity(self, lead_id: int, opportunity_name: str = None,
                          expected_revenue: float = 0.0, probability: float = 10.0) -> bool:
        """Convert lead to opportunity"""
        
        values = {}
        if opportunity_name:
            values['name'] = opportunity_name
        if expected_revenue > 0:
            values['expected_revenue'] = expected_revenue
        if probability > 0:
            values['probability'] = probability
        
        # Convert to opportunity
        self.client.call_method('crm.lead', lead_id, 'action_new_opportunity')
        
        # Update with additional values
        if values:
            self.client.write('crm.lead', [lead_id], values)
        
        self.logger.success(f"Lead {lead_id} converted to opportunity")
        return True

    def get_leads(self, stage: str = None, limit: int = 50) -> List[Dict]:
        """Get leads from CRM"""
        domain = []
        
        if stage:
            stage_ids = self.client.search('crm.stage', [('name', 'ilike', stage)])
            if stage_ids:
                domain.append(('stage_id', 'in', stage_ids))
        
        fields = ['id', 'name', 'contact_name', 'email_from', 'phone',
                 'partner_name', 'description', 'priority', 'stage_id',
                 'create_date', 'user_id']
        
        leads = self.client.search_read('crm.lead', domain, fields=fields, limit=limit)
        return leads

    def update_lead_stage(self, lead_id: int, stage_name: str) -> bool:
        """Update lead stage"""
        stage_ids = self.client.search('crm.stage', [('name', 'ilike', stage_name)])
        
        if stage_ids:
            self.client.write('crm.lead', [lead_id], {'stage_id': stage_ids[0]})
            self.logger.success(f"Lead {lead_id} stage updated to {stage_name}")
            return True
        
        self.logger.warning(f"Stage {stage_name} not found")
        return False

    def _get_or_create_source(self, source_name: str) -> int:
        """Get or create lead source"""
        source_ids = self.client.search('crm.team', [('name', '=', source_name)])
        
        if source_ids:
            return source_ids[0]
        
        # Create if doesn't exist
        try:
            return self.client.create('crm.team', {'name': source_name})
        except:
            return 1  # Default to first available

    def _get_default_stage_id(self) -> int:
        """Get default stage ID"""
        stage_ids = self.client.search('crm.stage', [('sequence', '=', 0)], limit=1)
        return stage_ids[0] if stage_ids else 1


# ============================================================================
# ODOO SALES INTEGRATION
# ============================================================================

class OdooSales:
    """Odoo Sales integration for order management"""

    def __init__(self, client: OdooClient):
        self.client = client
        self.config = OdooConfig()
        self.logger = Logger(self.config.LOG_PATH)

    def create_quotation(self, partner_name: str, partner_email: str = None,
                        products: List[Dict] = None, notes: str = None) -> int:
        """Create a sales quotation"""
        
        # Find or create partner
        partner_id = self._get_or_create_partner(partner_name, partner_email)
        
        # Create quotation
        values = {
            'partner_id': partner_id,
            'state': 'draft',
            'origin': 'Gold Tier FTE - Auto Generated',
            'note': notes
        }
        
        quotation_id = self.client.create('sale.order', values)
        
        # Add products
        if products:
            for product in products:
                self._add_quotation_line(quotation_id, product)
        
        self.logger.success(f"Quotation created: ID {quotation_id}")
        return quotation_id

    def confirm_quotation(self, quotation_id: int) -> bool:
        """Confirm quotation and convert to sales order"""
        try:
            self.client.call_method('sale.order', quotation_id, 'action_confirm')
            self.logger.success(f"Quotation {quotation_id} confirmed")
            return True
        except Exception as e:
            self.logger.error(f"Failed to confirm quotation: {e}")
            return False

    def create_invoice(self, order_id: int) -> int:
        """Create invoice from sales order"""
        try:
            invoice_ids = self.client.call_method('sale.order', order_id, '_create_invoices')
            self.logger.success(f"Invoice created from order {order_id}")
            return invoice_ids[0] if isinstance(invoice_ids, list) else invoice_ids
        except Exception as e:
            self.logger.error(f"Failed to create invoice: {e}")
            return 0

    def get_orders(self, state: str = None, limit: int = 50) -> List[Dict]:
        """Get sales orders"""
        domain = []
        
        if state:
            domain.append(('state', '=', state))
        
        fields = ['id', 'name', 'partner_id', 'amount_total', 'state',
                 'date_order', 'validity_date', 'note']
        
        orders = self.client.search_read('sale.order', domain, fields=fields, limit=limit)
        return orders

    def _get_or_create_partner(self, name: str, email: str = None) -> int:
        """Get or create business partner"""
        partner_ids = self.client.search('res.partner', [('name', '=', name)])
        
        if partner_ids:
            return partner_ids[0]
        
        # Create partner
        values = {
            'name': name,
            'email': email,
            'customer_rank': 1
        }
        
        return self.client.create('res.partner', {k: v for k, v in values.items() if v})

    def _add_quotation_line(self, quotation_id: int, product_info: Dict):
        """Add product line to quotation"""
        product_id = product_info.get('product_id')
        
        # If product_id is a name, find or create it
        if isinstance(product_id, str):
            product_ids = self.client.search('product.product', [('name', '=', product_id)])
            
            if product_ids:
                product_id = product_ids[0]
            else:
                product_id = self.client.create('product.product', {
                    'name': product_id,
                    'type': 'service',
                    'list_price': product_info.get('price', 0.0)
                })
        
        line_values = {
            'order_id': quotation_id,
            'product_id': product_id,
            'product_uom_qty': product_info.get('qty', 1),
            'product_uom': product_info.get('uom', 1)
        }
        
        self.client.create('sale.order.line', line_values)


# ============================================================================
# ODOO INVENTORY INTEGRATION
# ============================================================================

class OdooInventory:
    """Odoo Inventory integration"""

    def __init__(self, client: OdooClient):
        self.client = client
        self.config = OdooConfig()
        self.logger = Logger(self.config.LOG_PATH)

    def get_product_quantity(self, product_name: str) -> float:
        """Get quantity on hand for a product"""
        product_ids = self.client.search('product.product', [('name', '=', product_name)])
        
        if not product_ids:
            self.logger.warning(f"Product {product_name} not found")
            return 0.0
        
        product = self.client.search_read('product.product', [('id', '=', product_ids[0])],
                                         fields=['qty_available'], limit=1)
        
        return product[0]['qty_available'] if product else 0.0

    def update_product_quantity(self, product_name: str, quantity: float) -> bool:
        """Update product quantity (requires stock adjustment)"""
        product_ids = self.client.search('product.product', [('name', '=', product_name)])
        
        if not product_ids:
            self.logger.warning(f"Product {product_name} not found")
            return False
        
        # Create stock adjustment
        location_ids = self.client.search('stock.location', [('usage', '=', 'internal')], limit=1)
        
        if not location_ids:
            return False
        
        adjustment_id = self.client.create('stock.inventory', {
            'name': f'Auto Adjustment - {product_name}',
            'location_ids': [(6, 0, location_ids)]
        })
        
        # Add product line
        self.client.create('stock.inventory.line', {
            'inventory_id': adjustment_id,
            'product_id': product_ids[0],
            'product_uom_id': 1,  # Units
            'product_qty': quantity
        })
        
        # Validate adjustment
        self.client.call_method('stock.inventory', adjustment_id, 'action_validate')
        
        self.logger.success(f"Updated {product_name} quantity to {quantity}")
        return True

    def get_products(self, category: str = None, limit: int = 100) -> List[Dict]:
        """Get products from inventory"""
        domain = []
        
        if category:
            category_ids = self.client.search('product.category', [('name', 'ilike', category)])
            if category_ids:
                domain.append(('categ_id', 'in', category_ids))
        
        fields = ['id', 'name', 'default_code', 'list_price', 'qty_available',
                 'virtual_available', 'type']
        
        products = self.client.search_read('product.product', domain, fields=fields, limit=limit)
        return products


# ============================================================================
# MAIN ODOO INTEGRATION CLASS
# ============================================================================

class OdooIntegration:
    """Main Odoo Integration - combines all modules"""

    def __init__(self):
        self.config = OdooConfig()
        self.logger = Logger(self.config.LOG_PATH)
        self.client: Optional[OdooClient] = None
        self.crm: Optional[OdooCRM] = None
        self.sales: Optional[OdooSales] = None
        self.inventory: Optional[OdooInventory] = None
        
        self.seen_items: set = set()
        self.stats = {
            'leads_created': 0,
            'orders_created': 0,
            'invoices_created': 0,
            'products_synced': 0,
            'errors': 0
        }

    def connect(self) -> bool:
        """Connect to Odoo"""
        try:
            self.client = OdooClient()
            self.crm = OdooCRM(self.client)
            self.sales = OdooSales(self.client)
            self.inventory = OdooInventory(self.client)
            
            self.logger.success("Odoo modules initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Odoo: {e}")
            return False

    def create_lead_from_source(self, source: str, sender: str, content: str,
                               email: str = None, phone: str = None) -> int:
        """Create lead from external source (LinkedIn, Facebook, etc.)"""
        
        # Check if already created
        item_id = f"{source}:{sender}:{hashlib.md5(content.encode()).hexdigest()[:8]}"
        
        if item_id in self.seen_items:
            self.logger.info(f"Lead already created: {item_id}")
            return 0
        
        self.seen_items.add(item_id)
        
        # Create lead
        lead_id = self.crm.create_lead(
            name=sender,
            email=email,
            phone=phone,
            description=f"From {source}:\n{content[:500]}",
            source=source
        )
        
        self.stats['leads_created'] += 1
        return lead_id

    def create_quotation_from_lead(self, lead_id: int, products: List[Dict] = None) -> int:
        """Create quotation from lead"""
        
        # Get lead details
        leads = self.client.search_read('crm.lead', [('id', '=', lead_id)],
                                       fields=['partner_name', 'contact_name', 'email_from', 'phone'])
        
        if not leads:
            self.logger.error(f"Lead {lead_id} not found")
            return 0
        
        lead = leads[0]
        
        # Create quotation
        quotation_id = self.sales.create_quotation(
            partner_name=lead.get('partner_name') or lead.get('contact_name'),
            partner_email=lead.get('email_from'),
            products=products or [{'product_id': 'Consulting Service', 'qty': 1, 'price': 1000}]
        )
        
        self.stats['orders_created'] += 1
        return quotation_id

    def sync_leads_from_sources(self, leads_data: List[Dict]) -> int:
        """Sync leads from external sources"""
        created = 0
        
        for lead_data in leads_data:
            source = lead_data.get('source', 'Unknown')
            sender = lead_data.get('sender', 'Unknown')
            content = lead_data.get('content', '')
            email = lead_data.get('email')
            phone = lead_data.get('phone')
            
            lead_id = self.create_lead_from_source(source, sender, content, email, phone)
            
            if lead_id:
                created += 1
        
        self.logger.success(f"Synced {created} leads from external sources")
        return created

    def start_monitoring(self):
        """Start continuous monitoring and sync"""
        self.logger.info("="*70)
        self.logger.info("ODOO MONITOR - GOLD TIER")
        self.logger.info("="*70)
        self.logger.info(f"Sync interval: {self.config.SYNC_INTERVAL}s")
        self.logger.info(f"Auto-create leads: {self.config.AUTO_CREATE_LEADS}")
        self.logger.info("="*70)
        
        if not self.connect():
            self.logger.error("Failed to connect to Odoo. Exiting.")
            return
        
        try:
            check_count = 0
            
            while True:
                check_count += 1
                self.logger.info(f"\n{'='*50}")
                self.logger.info(f"Check #{check_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Get current stats from Odoo
                leads = self.crm.get_leads(limit=10)
                orders = self.sales.get_orders(limit=10)
                
                self.logger.info(f"Recent leads: {len(leads)}")
                self.logger.info(f"Recent orders: {len(orders)}")
                
                # Print stats
                self.logger.info(f"\n📊 Stats: Leads={self.stats['leads_created']}, "
                               f"Orders={self.stats['orders_created']}, "
                               f"Invoices={self.stats['invoices_created']}")
                
                next_check = datetime.now().strftime('%H:%M:%S')
                self.logger.info(f"⏳ Next check at {next_check} ({self.config.SYNC_INTERVAL}s)")
                time.sleep(self.config.SYNC_INTERVAL)
                
        except KeyboardInterrupt:
            self.logger.info("\n\n👋 Stopping Odoo Monitor...")
        finally:
            # Print final stats
            self.logger.info("="*70)
            self.logger.info("FINAL STATS")
            self.logger.info("="*70)
            self.logger.info(f"Leads created: {self.stats['leads_created']}")
            self.logger.info(f"Orders created: {self.stats['orders_created']}")
            self.logger.info(f"Invoices created: {self.stats['invoices_created']}")
            self.logger.info(f"Products synced: {self.stats['products_synced']}")
            self.logger.info(f"Errors: {self.stats['errors']}")


# ============================================================================
# DOCKER MANAGEMENT
# ============================================================================

class OdooDockerManager:
    """Manage Odoo Docker containers"""

    def __init__(self):
        self.config = OdooConfig()
        self.logger = Logger(self.config.LOG_PATH)
        self.compose_path = self.config.DOCKER_COMPOSE_PATH

    def start(self):
        """Start Odoo Docker containers"""
        self.logger.info("Starting Odoo Docker containers...")
        
        import subprocess
        
        try:
            result = subprocess.run(
                ['docker-compose', '-f', str(self.compose_path), 'up', '-d'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.logger.success("Odoo containers started successfully")
                self.logger.info(result.stdout)
            else:
                self.logger.error(f"Failed to start containers: {result.stderr}")
                
        except FileNotFoundError:
            self.logger.error("docker-compose not found. Please install Docker Desktop.")
        except Exception as e:
            self.logger.error(f"Error starting containers: {e}")

    def stop(self):
        """Stop Odoo Docker containers"""
        self.logger.info("Stopping Odoo Docker containers...")
        
        import subprocess
        
        try:
            result = subprocess.run(
                ['docker-compose', '-f', str(self.compose_path), 'down'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.logger.success("Odoo containers stopped successfully")
            else:
                self.logger.error(f"Failed to stop containers: {result.stderr}")
                
        except Exception as e:
            self.logger.error(f"Error stopping containers: {e}")

    def status(self):
        """Check Odoo Docker containers status"""
        self.logger.info("Checking Odoo Docker containers status...")
        
        import subprocess
        
        try:
            result = subprocess.run(
                ['docker-compose', '-f', str(self.compose_path), 'ps'],
                capture_output=True,
                text=True
            )
            
            print(result.stdout)
            
        except Exception as e:
            self.logger.error(f"Error checking status: {e}")

    def logs(self, service: str = 'odoo'):
        """View Odoo logs"""
        self.logger.info(f"Viewing logs for {service}...")
        
        import subprocess
        
        try:
            result = subprocess.run(
                ['docker-compose', '-f', str(self.compose_path), 'logs', '-f', service],
                capture_output=False,
                text=True
            )
        except Exception as e:
            self.logger.error(f"Error viewing logs: {e}")

    def backup(self):
        """Create database backup"""
        self.logger.info("Creating database backup...")
        
        import subprocess
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"odoo-backups/backup_{timestamp}.sql"
        
        try:
            # Create backup directory
            backup_dir = self.config.PROJECT_ROOT / 'odoo-docker' / 'odoo-backups'
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Run pg_dump
            result = subprocess.run(
                f'docker exec gold-tier-odoo-db pg_dump -U odoo -F c -f /backups/backup_{timestamp}.dump odoo',
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.logger.success(f"Backup created: {backup_file}")
            else:
                self.logger.error(f"Backup failed: {result.stderr}")
                
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """CLI interface for Odoo Integration"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Odoo Integration - Gold Tier')
    
    # Docker commands
    parser.add_argument('--docker-start', action='store_true', help='Start Odoo Docker containers')
    parser.add_argument('--docker-stop', action='store_true', help='Stop Odoo Docker containers')
    parser.add_argument('--docker-status', action='store_true', help='Check Docker containers status')
    parser.add_argument('--docker-backup', action='store_true', help='Create database backup')
    
    # CRM commands
    parser.add_argument('--create-lead', type=str, help='Create a new lead (name)')
    parser.add_argument('--lead-email', type=str, help='Lead email')
    parser.add_argument('--get-leads', action='store_true', help='Get all leads')
    
    # Sales commands
    parser.add_argument('--create-quotation', type=str, help='Create quotation (partner name)')
    parser.add_argument('--get-orders', action='store_true', help='Get all orders')
    
    # Inventory commands
    parser.add_argument('--get-products', action='store_true', help='Get all products')
    parser.add_argument('--product-qty', type=str, help='Get product quantity (product name)')
    
    # Monitoring
    parser.add_argument('--monitor', action='store_true', help='Start monitoring mode')
    
    args = parser.parse_args()
    
    odoo = OdooIntegration()
    docker_mgr = OdooDockerManager()
    
    if args.docker_start:
        docker_mgr.start()
    
    elif args.docker_stop:
        docker_mgr.stop()
    
    elif args.docker_status:
        docker_mgr.status()
    
    elif args.docker_backup:
        docker_mgr.backup()
    
    elif args.create_lead:
        if not odoo.connect():
            return
        lead_id = odoo.crm.create_lead(args.create_lead, args.lead_email)
        print(f"Lead created with ID: {lead_id}")
    
    elif args.get_leads:
        if not odoo.connect():
            return
        leads = odoo.crm.get_leads()
        print(json.dumps(leads, indent=2, default=str))
    
    elif args.create_quotation:
        if not odoo.connect():
            return
        quotation_id = odoo.sales.create_quotation(args.create_quotation)
        print(f"Quotation created with ID: {quotation_id}")
    
    elif args.get_orders:
        if not odoo.connect():
            return
        orders = odoo.sales.get_orders()
        print(json.dumps(orders, indent=2, default=str))
    
    elif args.get_products:
        if not odoo.connect():
            return
        products = odoo.inventory.get_products()
        print(json.dumps(products, indent=2, default=str))
    
    elif args.product_qty:
        if not odoo.connect():
            return
        qty = odoo.inventory.get_product_quantity(args.product_qty)
        print(f"Quantity on hand: {qty}")
    
    elif args.monitor:
        odoo.start_monitoring()
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
