import subprocess
import threading
import time
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KerberosRenewer:
    """Handles automatic Kerberos ticket renewal using keytab"""
    
    def __init__(self, principal=None, keytab=None, interval=1800):
        """
        Initialize Kerberos renewer
        
        Args:
            principal: Kerberos principal (e.g., 'user@REALM.COM')
            keytab: Path to keytab file
            interval: Renewal interval in seconds (default: 30 minutes)
        """
        self.principal = principal or os.getenv('KRB5_PRINCIPAL')
        self.keytab = keytab or os.getenv('KRB5_KTNAME', '/etc/kerberos/krb5.keytab')
        self.interval = interval
        self._running = False
        self._thread = None
        
        if not self.principal:
            raise ValueError("KRB5_PRINCIPAL must be set either as parameter or environment variable")
    
    def _renew_ticket(self):
        """Attempt to renew or obtain a new Kerberos ticket"""
        try:
            # Try to renew existing ticket first
            result = subprocess.run(
                ['kinit', '-R'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully renewed Kerberos ticket for {self.principal}")
                return True
            
            # If renewal failed, get a new ticket using keytab
            result = subprocess.run(
                ['kinit', '-kt', self.keytab, self.principal],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully obtained new Kerberos ticket for {self.principal}")
                return True
            else:
                logger.error(f"Failed to obtain Kerberos ticket: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Kerberos ticket renewal timed out")
            return False
        except FileNotFoundError:
            logger.error("kinit command not found. Is krb5-user installed?")
            return False
        except Exception as e:
            logger.error(f"Error renewing Kerberos ticket: {e}")
            return False
    
    def _renewal_loop(self):
        """Background loop that renews tickets periodically"""
        # Get initial ticket
        logger.info("Obtaining initial Kerberos ticket...")
        self._renew_ticket()
        
        while self._running:
            time.sleep(self.interval)
            if self._running:
                logger.info("Renewing Kerberos ticket...")
                self._renew_ticket()
    
    def start(self):
        """Start the automatic renewal background thread"""
        if self._running:
            logger.warning("Kerberos renewer is already running")
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._renewal_loop, daemon=True, name="KerberosRenewer")
        self._thread.start()
        logger.info(f"Started Kerberos ticket renewal (interval: {self.interval}s)")
    
    def stop(self):
        """Stop the automatic renewal thread"""
        if not self._running:
            return
        
        logger.info("Stopping Kerberos ticket renewal...")
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Kerberos ticket renewal stopped")
    
    def get_ticket_info(self):
        """Get current ticket information"""
        try:
            result = subprocess.run(
                ['klist'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout if result.returncode == 0 else None
        except Exception as e:
            logger.error(f"Failed to get ticket info: {e}")
            return None


# Convenience function for easy integration
def start_auto_renewal(principal=None, keytab=None, interval=1800):
    """
    Start automatic Kerberos ticket renewal
    
    Args:
        principal: Kerberos principal
        keytab: Path to keytab file
        interval: Renewal interval in seconds (default: 30 minutes)
    
    Returns:
        KerberosRenewer instance
    """
    renewer = KerberosRenewer(principal=principal, keytab=keytab, interval=interval)
    renewer.start()
    return renewer
