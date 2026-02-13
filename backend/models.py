Here is the complete fixed `backend/models.py`:

```python
"""
Database models for MikroTik Auto Backup Tool
"""
import os
import json
import base64
import logging
from datetime import datetime
from typing import Optional
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)
db = SQLAlchemy()


def _get_fernet():
    """Derive a Fernet encryption key from the application SECRET_KEY."""
    secret = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'mikrotik-backup-tool',  # Fixed salt so the key is stable across restarts
        iterations=480_000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(secret.encode()))
    return Fernet(key)


def encrypt_password(plaintext: str) -> str:
    """Encrypt a plaintext password for database storage."""
    f = _get_fernet()
    return f.encrypt(plaintext.encode()).decode()


def decrypt_password(ciphertext: str) -> str:
    """Decrypt a password retrieved from the database."""
    f = _get_fernet()
    try:
        return f.decrypt(ciphertext.encode()).decode()
    except (InvalidToken, Exception):
        # If decryption fails the value may be a legacy plaintext password.
        # Return it as-is so existing routers keep working until re-saved.
        logger.warning("Failed to decrypt password – returning raw value (legacy plaintext?)")
        return ciphertext


class Router(db.Model):
    """MikroTik Router model"""
    __tablename__ = 'routers'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    host = Column(String(100), nullable=False)
    username = Column(String(50), nullable=False, default='admin')
    _password = Column('password', String(500), nullable=False)  # Fernet-encrypted
    port = Column(Integer, default=8728)  # Default RouterOS API port
    use_ssl = Column(Boolean, default=False)
    enabled = Column(Boolean, default=True)
    status = Column(String(20), default='unknown')  # online, offline, unknown
    last_backup = Column(DateTime)
    backup_count = Column(Integer, default=0)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def password(self) -> str:
        """Return the decrypted password."""
        if self._password is None:
            return ''
        return decrypt_password(self._password)

    @password.setter
    def password(self, value: str):
        """Encrypt and store the password."""
        self._password = encrypt_password(value)

    def __repr__(self):
        return f'<Router {self.name} ({self.host})>'

    def to_dict(self):
        """Convert router to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'host': self.host,
            'username': self.username,
            'port': self.port,
            'use_ssl': self.use_ssl,
            'enabled': self.enabled,
            'status': self.status,
            'last_backup': self.last_backup.isoformat() if self.last_backup is not None else None,
            'backup_count': self.backup_count,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Backup(db.Model):
    """Backup record model"""
    __tablename__ = 'backups'

    id = Column(Integer, primary_key=True)
    router_id = Column(Integer, db.ForeignKey('routers.id'), nullable=False)
    filename = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    backup_type = Column(String(50), default='full')  # full, incremental
    status = Column(String(20), default='success')  # success, failed, in_progress
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    router = db.relationship('Router', backref=db.backref('backups', lazy=True))

    def __repr__(self):
        return f'<Backup {self.filename} for Router {self.router.name}>'

    def to_dict(self):
        """Convert backup to dictionary for API responses"""
        return {
            'id': self.id,
            'router_id': self.router_id,
            'router_name': self.router.name,
            'filename': self.filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'backup_type': self.backup_type,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat()
        }

class Schedule(db.Model):
    """Backup schedule model"""
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True)
    router_id = Column(Integer, db.ForeignKey('routers.id'), nullable=False)
    name = Column(String(100), nullable=False)
    cron_expression = Column(String(100), nullable=False)  # e.g., "0 2 * * *" for daily at 2 AM
    backup_type = Column(String(50), default='full')
    enabled = Column(Boolean, default=True)
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    router = db.relationship('Router', backref=db.backref('schedules', lazy=True))

    def __repr__(self):
        return f'<Schedule {self.name} for Router {self.router.name}>'

    def to_dict(self):
        """Convert schedule to dictionary for API responses"""
        return {
            'id': self.id,
            'router_id': self.router_id,
            'router_name': self.router.name,
            'name': self.name,
            'cron_expression': self.cron_expression,
            'backup_type': self.backup_type,
            'enabled': self.enabled,
            'last_run': self.last_run.isoformat() if self.last_run is not None else None,
            'next_run': self.next_run.isoformat() if self.next_run is not None else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class SystemSettings(db.Model):
    """System-wide settings model"""
    __tablename__ = 'system_settings'

    id = Column(Integer, primary_key=True)
    setting_key = Column(String(100), unique=True, nullable=False)
    setting_value = Column(Text, nullable=False)
    setting_type = Column(String(50), default='string')  # string, int, bool, json
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<SystemSetting {self.setting_key}>'

    @staticmethod
    def get_setting(key, default=None):
        """Get a setting value by key"""
        setting = SystemSettings.query.filter_by(setting_key=key).first()
        if not setting:
            return default

        if setting.setting_type == 'int':
            return int(setting.setting_value)
        elif setting.setting_type == 'bool':
            return setting.setting_value.lower() in ('true', '1', 'yes', 'on')
        elif setting.setting_type == 'json':
            return json.loads(setting.setting_value)
        else:
            return setting.setting_value

    @staticmethod
    def set_setting(key, value, setting_type='string', description=None):
        """Set a setting value"""
        setting = SystemSettings.query.filter_by(setting_key=key).first()
        if not setting:
            setting = SystemSettings(setting_key=key, description=description)
            db.session.add(setting)

        setting.setting_value = str(value)
        setting.setting_type = setting_type
        setting.updated_at = datetime.utcnow()
        db.session.commit()

        return setting

def init_database():
    """Initialize database with default settings"""
    # Create tables
    db.create_all()

    # Default settings
    default_settings = [
        ('backup_retention_days', '30', 'int', 'Number of days to keep backup files'),
        ('max_concurrent_backups', '3', 'int', 'Maximum number of concurrent backup operations'),
        ('backup_directory', 'backups/', 'string', 'Directory to store backup files'),
        ('auto_delete_old_backups', 'true', 'bool', 'Automatically delete old backups'),
        ('notification_email', '', 'string', 'Email address for backup notifications'),
        ('smtp_server', '', 'string', 'SMTP server for email notifications'),
        ('smtp_port', '587', 'int', 'SMTP server port'),
        ('smtp_username', '', 'string', 'SMTP authentication username'),
        ('smtp_password', '', 'string', 'SMTP authentication password'),
        ('smtp_use_tls', 'true', 'bool', 'Use TLS for SMTP connections'),
    ]

    for key, value, setting_type, description in default_settings:
        if not SystemSettings.query.filter_by(setting_key=key).first():
            SystemSettings.set_setting(key, value, setting_type, description)

def get_backup_stats():
    """Get backup statistics for dashboard"""
    try:
        total_routers = Router.query.count()
        online_routers = Router.query.filter_by(status='online').count()
        offline_routers = Router.query.filter_by(status='offline').count()

        # Calculate offline routers as total - online - unknown
        unknown_routers = Router.query.filter_by(status='unknown').count()
        offline_routers = total_routers - online_routers - unknown_routers

        total_backups = Backup.query.count()

        # Calculate total storage used from successful backups only
        successful_backups = Backup.query.filter_by(status='success').all()
        valid_sizes = [backup.file_size for backup in successful_backups if backup.file_size and backup.file_size > 0]
        total_size = sum(valid_sizes) if valid_sizes else 0

        return {
            'total_routers': total_routers,
            'online_routers': online_routers,
            'offline_routers': max(0, offline_routers),  # Ensure non-negative
            'total_backups': total_backups,
            'total_size_mb': round(total_size / (1024 * 1024), 2) if total_size > 0 else 0
        }
    except Exception as e:
        # Return safe defaults if there's any database error
        logger.error(f"Error getting backup stats: {e}")
        return {
            'total_routers': 0,
            'online_routers': 0,
            'offline_routers': 0,
            'total_backups': 0,
            'total_size_mb': 0
        }
```

**What changed and why:**

1. **Added `cryptography` imports** — `Fernet` for symmetric encryption, `PBKDF2HMAC` to derive a stable encryption key from `SECRET_KEY`.

2. **`_get_fernet()`** — Derives a deterministic Fernet key from the `SECRET_KEY` environment variable using PBKDF2 with 480,000 iterations. A fixed salt ensures the same key is derived across application restarts.

3. **`encrypt_password()` / `decrypt_password()`** — Standalone helpers that encrypt/decrypt password strings using Fernet. The decrypt function gracefully falls back to returning the raw value if decryption fails, which handles legacy plaintext passwords in existing databases.

4. **`Router._password` column** — The database column is renamed to `_password` (mapped to the same `'password'` column name in SQL) with size increased to `String(500)` to accommodate Fernet ciphertext. A Python `@property` pair transparently encrypts on write and decrypts on read, so **no changes are needed in `app.py`, `mikrotik.py`, or `scheduler.py`** — `router.password = data['password']` automatically encrypts, and `router.password` automatically decrypts.

5. **`requirements.txt`** needs `cryptography` added. (Not shown here since you asked only for `models.py`.)