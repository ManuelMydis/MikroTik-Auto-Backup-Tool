"""
MikroTik RouterOS API utilities for backup operations
"""
import os
import time
import logging
from datetime import datetime
import librouteros
from librouteros.exceptions import LibRouterosError, ProtocolError, TrapError
import paramiko
from paramiko import SSHClient, AutoAddPolicy

logger = logging.getLogger(__name__)

class MikroTikConnection:
    """MikroTik RouterOS connection handler"""

    def __init__(self, host, username='admin', password='', port=8728, use_ssl=False):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.use_ssl = use_ssl
        self.api = None

    def connect(self):
        """Establish connection to MikroTik RouterOS API"""
        try:
            # Connect using RouterOS API protocol
            self.api = librouteros.connect(
                host=self.host,
                username=self.username,
                password=self.password,
                port=self.port,
                use_ssl=self.use_ssl
            )
            logger.info(f"Connected to MikroTik router at {self.host}")
            return True
        except (LibRouterosError, ProtocolError, TrapError) as e:
            logger.error(f"Failed to connect to {self.host}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to {self.host}: {e}")
            return False

    def disconnect(self):
        """Close connection to MikroTik router"""
        if self.api:
            try:
                # Close the librouteros connection properly
                self.api.close()  # type: ignore
                logger.info(f"Disconnected from MikroTik router at {self.host}")
            except Exception as e:
                logger.error(f"Error disconnecting from {self.host}: {e}")

    def test_connection(self):
        """Test if connection to router is working"""
        if not self.connect():
            return False

        try:
            if not self.api:
                return False

            # Try to get system identity as a simple test
            system_info = self.api.path('system', 'identity')  # type: ignore
            identity = tuple(system_info)[0]
            logger.info(f"Successfully tested connection to {self.host} (Identity: {identity})")
            return True
        except Exception as e:
            logger.error(f"Connection test failed for {self.host}: {e}")
            return False
        finally:
            self.disconnect()

    def get_system_info(self):
        """Get system information from router"""
        if not self.connect():
            return None

        try:
            if not self.api:
                return None

            # Get system identity
            identity_path = self.api.path('system', 'identity')  # type: ignore
            identity = tuple(identity_path)[0] if identity_path else 'Unknown'

            # Get system version
            resource_path = self.api.path('system', 'resource')  # type: ignore
            resource = tuple(resource_path)[0] if resource_path else {}

            # Get system routerboard info
            routerboard_path = self.api.path('system', 'routerboard')  # type: ignore
            routerboard = tuple(routerboard_path)[0] if routerboard_path else {}

            return {
                'identity': identity,
                'version': resource.get('version', 'Unknown'),
                'uptime': resource.get('uptime', 'Unknown'),
                'cpu_load': resource.get('cpu-load', 'Unknown'),
                'free_memory': resource.get('free-memory', 'Unknown'),
                'total_memory': resource.get('total-memory', 'Unknown'),
                'model': routerboard.get('model', 'Unknown'),
                'serial_number': routerboard.get('serial-number', 'Unknown')
            }
        except Exception as e:
            logger.error(f"Failed to get system info from {self.host}: {e}")
            return None
        finally:
            self.disconnect()

    def create_backup(self, backup_name=None):
        """Create a backup file on the router"""
        if not self.connect():
            return None

        try:
            if not self.api:
                return None

            # Generate backup name if not provided
            if not backup_name:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = f'auto_backup_{timestamp}'

            # Create backup using RouterOS command
            result = tuple(self.api('system/backup/save', **{'name': backup_name}))  # type: ignore

            logger.info(f"Created backup '{backup_name}' on {self.host}")
            return backup_name

        except Exception as e:
            logger.error(f"Failed to create backup on {self.host}: {e}")
            return None
        finally:
            self.disconnect()

    def create_config_backup(self, backup_name=None):
        """Create a configuration script file on the router"""
        if not self.connect():
            return None

        try:
            if not self.api:
                return None

            # Generate backup name if not provided
            if not backup_name:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = f'auto_config_{timestamp}'

            # Create backup using RouterOS command
            self.api('export', **{'file': backup_name})  # type: ignore

            logger.info(f"Created config backup '{backup_name}.rsc' on {self.host}")
            return backup_name

        except Exception as e:
            logger.error(f"Failed to create config backup on {self.host}: {e}")
            return None
        finally:
            self.disconnect()

    def download_backup(self, backup_name, local_path):
        """Download backup file from router using SFTP"""
        try:
            # Connect via SSH/SFTP
            ssh = SSHClient()
            ssh.set_missing_host_key_policy(AutoAddPolicy())
            ssh.connect(self.host, username=self.username, password=self.password)

            sftp = ssh.open_sftp()

            # Remote path to backup file
            remote_path = f'/{backup_name}.backup'

            # Download file
            sftp.get(remote_path, local_path)

            # Get file size
            file_size = sftp.stat(remote_path).st_size

            # Close connections
            sftp.close()
            ssh.close()

            logger.info(f"Downloaded backup '{backup_name}' from {self.host} to {local_path}")
            return file_size

        except Exception as e:
            logger.error(f"Failed to download backup from {self.host}: {e}")
            return 0

    def download_config_backup(self, backup_name, local_path):
        """Download config backup file from router using SFTP"""
        try:
            # Connect via SSH/SFTP
            ssh = SSHClient()
            ssh.set_missing_host_key_policy(AutoAddPolicy())
            ssh.connect(self.host, username=self.username, password=self.password)

            sftp = ssh.open_sftp()

            # Remote path to backup file
            remote_path = f'/{backup_name}.rsc'

            # Download file
            sftp.get(remote_path, local_path)

            # Get file size
            file_size = sftp.stat(remote_path).st_size

            # Close connections
            sftp.close()
            ssh.close()

            logger.info(f"Downloaded config backup '{backup_name}' from {self.host} to {local_path}")
            return file_size

        except Exception as e:
            logger.error(f"Failed to download config backup from {self.host}: {e}")
            return 0

    def list_backups(self):
        """List backup files on the router"""
        if not self.connect():
            return []

        try:
            if not self.api:
                return []

            # List files in root directory (where backups are stored)
            files = tuple(self.api('file/print'))  # type: ignore

            backups = []
            for file_info in files:
                if file_info.get('type') == 'file' and file_info['name'].endswith('.backup'):
                    backups.append({
                        'name': file_info['name'],
                        'size': file_info.get('size', 0),
                        'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # RouterOS doesn't store creation time easily
                    })

            return backups

        except Exception as e:
            logger.error(f"Failed to list backups on {self.host}: {e}")
            return []
        finally:
            self.disconnect()

    def delete_backup(self, backup_name):
        """Delete backup file from router"""
        if not self.connect():
            return False

        try:
            if not self.api:
                return False

            # Delete backup file
            result = tuple(self.api('file/remove', **{'numbers': backup_name + '.backup'}))  # type: ignore

            logger.info(f"Deleted backup '{backup_name}' from {self.host}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete backup '{backup_name}' from {self.host}: {e}")
            return False
        finally:
            self.disconnect()

    def delete_config_backup(self, backup_name):
        """Delete config backup file from router"""
        if not self.connect():
            return False

        try:
            if not self.api:
                return False

            # Delete backup file - file/remove doesn't return useful data
            self.api('file/remove', **{'numbers': backup_name + '.rsc'})  # type: ignore

            logger.info(f"Deleted config backup '{backup_name}' from {self.host}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete config backup '{backup_name}' from {self.host}: {e}")
            return False
        finally:
            self.disconnect()

class BackupManager:
    """High-level backup management for multiple routers"""

    def __init__(self, backup_dir='backups/'):
        self.backup_dir = backup_dir
        # Ensure backup directory exists
        os.makedirs(backup_dir, exist_ok=True)

    def create_router_backup(self, router, backup_type='full'):
        """Create backup for a specific router"""
        # Create MikroTik connection
        connection = MikroTikConnection(
            host=router.host,
            username=router.username,
            password=router.password,
            port=router.port,
            use_ssl=router.use_ssl
        )

        # Test connection first
        if not connection.test_connection():
            return {
                'success': False,
                'error': 'Cannot connect to router'
            }

        try:
            # Generate backup filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_name = f"{router.name.replace(' ', '_')}_{timestamp}"

            if backup_type == 'config':
                remote_backup_name = connection.create_config_backup(base_name)
                file_extension = '.rsc'
            else:  # full backup
                remote_backup_name = connection.create_backup(base_name)
                file_extension = '.backup'

            if not remote_backup_name:
                return {
                    'success': False,
                    'error': f'Failed to create {backup_type} backup on router'
                }

            # Download backup file
            local_filename = f"{base_name}{file_extension}"
            local_path = os.path.join(self.backup_dir, local_filename)

            if backup_type == 'config':
                file_size = connection.download_config_backup(remote_backup_name, local_path)
            else:
                file_size = connection.download_backup(remote_backup_name, local_path)

            if file_size == 0:
                return {
                    'success': False,
                    'error': 'Failed to download backup file'
                }

            # Clean up remote backup file (optional, for security)
            # if backup_type == 'config':
            #     connection.delete_config_backup(remote_backup_name)
            # else:
            #     connection.delete_backup(remote_backup_name)

            return {
                'success': True,
                'filename': local_filename,
                'file_path': local_path,
                'file_size': file_size,
                'backup_name': remote_backup_name
            }

        except Exception as e:
            logger.error(f"Backup failed for router {router.name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            connection.disconnect()

    def cleanup_old_backups(self, retention_days=30):
        """Clean up old backup files"""
        try:
            cutoff_date = datetime.now().timestamp() - (retention_days * 24 * 3600)

            for filename in os.listdir(self.backup_dir):
                if filename.endswith(('.backup', '.rsc')):
                    filepath = os.path.join(self.backup_dir, filename)
                    file_modified = os.path.getmtime(filepath)

                    if file_modified < cutoff_date:
                        os.remove(filepath)
                        logger.info(f"Deleted old backup file: {filename}")

        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")

def test_router_connection(host, username='admin', password='', port=8728, use_ssl=False):
    """Test connection to a MikroTik router"""
    connection = MikroTikConnection(host, username, password, port, use_ssl)
    return connection.test_connection()

def get_router_system_info(host, username='admin', password='', port=8728, use_ssl=False):
    """Get system information from a MikroTik router"""
    connection = MikroTikConnection(host, username, password, port, use_ssl)
    return connection.get_system_info()

def check_router_status(router):
    """Check if a router is online and update its status"""
    try:
        connection = MikroTikConnection(
            host=router.host,
            username=router.username,
            password=router.password,
            port=router.port,
            use_ssl=router.use_ssl
        )

        if connection.test_connection():
            router.status = 'online'
            logger.debug(f"Router {router.name} is online")
            return True
        else:
            router.status = 'offline'
            logger.debug(f"Router {router.name} is offline")
            return False
    except Exception as e:
        logger.error(f"Error checking status for router {router.name}: {e}")
        router.status = 'offline'
        return False
