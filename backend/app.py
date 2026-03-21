It seems file write permissions aren't being granted. Let me output the complete fixed file content as requested:

```python
"""
MikroTik Auto Backup Tool - Flask Backend API
"""
import os
import logging
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Import database and models
from models import db, Router, Backup, Schedule, SystemSettings, init_database, get_backup_stats

# Import utilities
from utils.mikrotik import test_router_connection, get_router_system_info, BackupManager, check_router_status
from utils.scheduler import start_scheduler, stop_scheduler, schedule_router_backup, get_scheduler_status

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)

    # Enable CORS for all routes
    CORS(app)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///config.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Backup configuration
    app.config['BACKUP_DIR'] = os.environ.get('BACKUP_DIR', 'backups/')
    app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

    # Initialize database
    db.init_app(app)

    # Create tables and default settings
    with app.app_context():
        init_database()

    # Initialize backup manager
    backup_manager = BackupManager(app.config['BACKUP_DIR'])

    # Start scheduler
    start_scheduler()

    return app, backup_manager

# Create app instance
app, backup_manager = create_app()

# Routes

@app.route('/')
def index():
    """Serve the main web interface"""
    try:
        # Serve from public directory - try multiple possible paths
        possible_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public'),
            os.path.join(os.getcwd(), 'public'),
            'public'
        ]

        for public_dir in possible_paths:
            index_file = os.path.join(public_dir, 'index.html')
            if os.path.isfile(index_file):
                return send_from_directory(public_dir, 'index.html')

        return jsonify({'error': 'Frontend files not found. Please ensure public/index.html exists.'}), 404
    except Exception as e:
        logger.error(f"Error serving index: {e}")
        return jsonify({'error': 'Frontend files not found. Please ensure public/index.html exists.'}), 404

@app.route('/api/routers', methods=['GET'])
def get_routers():
    """Get all routers"""
    try:
        routers = Router.query.all()

        # Check status for all routers to ensure accuracy
        status_updated = False
        for router in routers:
            old_status = router.status
            check_router_status(router)
            if router.status != old_status:
                status_updated = True

        # Commit any status changes
        if status_updated:
            db.session.commit()

        return jsonify({
            'success': True,
            'routers': [router.to_dict() for router in routers]
        })
    except Exception as e:
        logger.error(f"Error getting routers: {e}")
        return jsonify({'error': 'Failed to retrieve routers'}), 500

@app.route('/api/routers', methods=['POST'])
def add_router():
    """Add a new router"""
    try:
        data = request.get_json()

        if not data or not all(k in data for k in ['name', 'host', 'username', 'password']):
            return jsonify({'error': 'Missing required fields: name, host, username, password'}), 400

        # Check if router with same name or host already exists
        existing = Router.query.filter(
            (Router.name == data['name']) | (Router.host == data['host'])
        ).first()

        if existing:
            return jsonify({'error': 'Router with this name or host already exists'}), 409

        # Create new router
        router = Router()
        router.name = data['name']
        router.host = data['host']
        router.username = data['username']
        router.password = data['password']
        router.port = data.get('port', 8728)
        router.use_ssl = data.get('use_ssl', False)
        router.notes = data.get('notes', '')

        db.session.add(router)
        db.session.commit()

        logger.info(f"Added new router: {router.name} ({router.host})")
        return jsonify({
            'success': True,
            'router': router.to_dict(),
            'message': 'Router added successfully'
        })

    except Exception as e:
        logger.error(f"Error adding router: {e}")
        return jsonify({'error': 'Failed to add router'}), 500

@app.route('/api/routers/<int:router_id>', methods=['PUT'])
def update_router(router_id):
    """Update router information"""
    try:
        router = Router.query.get_or_404(router_id)
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Update fields if provided
        if 'name' in data:
            router.name = data['name']
        if 'host' in data:
            router.host = data['host']
        if 'username' in data:
            router.username = data['username']
        if 'password' in data:
            router.password = data['password']
        if 'port' in data:
            router.port = data['port']
        if 'use_ssl' in data:
            router.use_ssl = data['use_ssl']
        if 'enabled' in data:
            router.enabled = data['enabled']
        if 'notes' in data:
            router.notes = data['notes']

        router.updated_at = datetime.utcnow()
        db.session.commit()

        logger.info(f"Updated router: {router.name}")
        return jsonify({
            'success': True,
            'router': router.to_dict(),
            'message': 'Router updated successfully'
        })

    except Exception as e:
        logger.error(f"Error updating router {router_id}: {e}")
        return jsonify({'error': 'Failed to update router'}), 500

@app.route('/api/routers/<int:router_id>', methods=['DELETE'])
def delete_router(router_id):
    """Delete a router"""
    try:
        router = Router.query.get_or_404(router_id)

        # Delete associated backups and schedules
        Backup.query.filter_by(router_id=router_id).delete()
        Schedule.query.filter_by(router_id=router_id).delete()

        db.session.delete(router)
        db.session.commit()

        logger.info(f"Deleted router: {router.name}")
        return jsonify({
            'success': True,
            'message': 'Router deleted successfully'
        })

    except Exception as e:
        logger.error(f"Error deleting router {router_id}: {e}")
        return jsonify({'error': 'Failed to delete router'}), 500

@app.route('/api/test-connection', methods=['POST'])
def test_connection():
    """Test connection to a MikroTik router"""
    try:
        data = request.get_json()

        if not data or not all(k in data for k in ['host', 'username', 'password']):
            return jsonify({'error': 'Missing required fields: host, username, password'}), 400

        # Test connection
        success = test_router_connection(
            host=data['host'],
            username=data['username'],
            password=data['password'],
            port=data.get('port', 8728),
            use_ssl=data.get('use_ssl', False)
        )

        if success:
            # Get system info if connection successful
            system_info = get_router_system_info(
                host=data['host'],
                username=data['username'],
                password=data['password'],
                port=data.get('port', 8728),
                use_ssl=data.get('use_ssl', False)
            )

            return jsonify({
                'success': True,
                'connected': True,
                'system_info': system_info,
                'message': 'Connection successful'
            })
        else:
            return jsonify({
                'success': False,
                'connected': False,
                'message': 'Connection failed'
            })

    except Exception as e:
        logger.error(f"Error testing connection: {e}")
        return jsonify({'error': 'Failed to test connection'}), 500

@app.route('/api/backup/<int:router_id>', methods=['POST'])
def create_backup(router_id):
    """Create backup for a specific router"""
    try:
        router = Router.query.get_or_404(router_id)
        data = request.get_json() or {}
        backup_type = data.get('backup_type', 'full')

        if not router.enabled:
            return jsonify({'error': 'Router is disabled'}), 400

        # Update router status
        router.status = 'online'
        db.session.commit()

        # Create backup
        result = backup_manager.create_router_backup(router, backup_type=backup_type)

        if result['success']:
            # Save backup record
            backup = Backup()
            backup.router_id = router.id
            backup.filename = result['filename']
            backup.file_path = result['file_path']
            backup.file_size = result['file_size']
            backup.backup_type = backup_type
            backup.status = 'success'  # type: ignore

            # Update router stats
            router.last_backup = datetime.utcnow()
            router.backup_count += 1

            db.session.add(backup)
            db.session.commit()

            logger.info(f"Manual backup completed for router: {router.name}")
            return jsonify({
                'success': True,
                'backup': backup.to_dict(),
                'filename': result['filename'],
                'message': 'Backup created successfully'
            })
        else:
            # Save failed backup record
            backup = Backup()
            backup.router_id = router.id
            backup.filename = None  # type: ignore
            backup.file_path = None  # type: ignore
            backup.file_size = None  # type: ignore
            backup.backup_type = backup_type
            backup.status = 'failed'  # type: ignore
            backup.error_message = result.get('error', 'Unknown error')

            db.session.add(backup)
            db.session.commit()

            return jsonify({
                'success': False,
                'error': result.get('error', 'Backup failed')
            }), 500

    except Exception as e:
        logger.error(f"Error creating backup for router {router_id}: {e}")
        return jsonify({'error': 'Failed to create backup'}), 500

@app.route('/api/download/<filename>')
def download_backup(filename):
    """Download a backup file"""
    try:
        # Security check - ensure filename is safe
        safe_filename = secure_filename(filename)
        if safe_filename != filename:
            return jsonify({'error': 'Invalid filename'}), 400

        # Check if file exists
        file_path = os.path.join(app.config['BACKUP_DIR'], filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404

        # Send file
        return send_from_directory(
            app.config['BACKUP_DIR'],
            filename,
            as_attachment=True
        )

    except Exception as e:
        logger.error(f"Error downloading file {filename}: {e}")
        return jsonify({'error': 'Failed to download file'}), 500

@app.route('/api/backups', methods=['GET'])
def get_backups():
    """Get all backups"""
    try:
        backups = Backup.query.order_by(Backup.created_at.desc()).all()
        return jsonify({
            'success': True,
            'backups': [backup.to_dict() for backup in backups]
        })
    except Exception as e:
        logger.error(f"Error getting backups: {e}")
        return jsonify({'error': 'Failed to retrieve backups'}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    try:
        stats = get_backup_stats()
        scheduler_info = get_scheduler_status()

        return jsonify({
            'success': True,
            'stats': stats,
            'scheduler': scheduler_info
        })
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': 'Failed to retrieve statistics'}), 500

@app.route('/api/schedules', methods=['GET'])
def get_schedules():
    """Get all backup schedules"""
    try:
        schedules = Schedule.query.all()
        return jsonify({
            'success': True,
            'schedules': [schedule.to_dict() for schedule in schedules]
        })
    except Exception as e:
        logger.error(f"Error getting schedules: {e}")
        return jsonify({'error': 'Failed to retrieve schedules'}), 500

@app.route('/api/schedules', methods=['POST'])
def create_schedule():
    """Create a new backup schedule"""
    try:
        data = request.get_json()

        if not data or not all(k in data for k in ['router_id', 'cron_expression']):
            return jsonify({'error': 'Missing required fields: router_id, cron_expression'}), 400

        # Validate router exists
        router = Router.query.get(data['router_id'])
        if not router:
            return jsonify({'error': 'Router not found'}), 404

        # Create schedule
        success = schedule_router_backup(
            router_id=data['router_id'],
            cron_expression=data['cron_expression'],
            backup_type=data.get('backup_type', 'full'),
            schedule_name=data.get('name')
        )

        if success:
            return jsonify({
                'success': True,
                'message': 'Schedule created successfully'
            })
        else:
            return jsonify({'error': 'Failed to create schedule'}), 500

    except Exception as e:
        logger.error(f"Error creating schedule: {e}")
        return jsonify({'error': 'Failed to create schedule'}), 500

@app.route('/api/schedules/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    """Delete a backup schedule"""
    try:
        schedule = Schedule.query.get_or_404(schedule_id)
        schedule_name = schedule.name

        db.session.delete(schedule)
        db.session.commit()

        logger.info(f"Deleted schedule: {schedule_name}")
        return jsonify({
            'success': True,
            'message': 'Schedule deleted successfully'
        })

    except Exception as e:
        logger.error(f"Error deleting schedule {schedule_id}: {e}")
        return jsonify({'error': 'Failed to delete schedule'}), 500

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get system settings"""
    try:
        settings = SystemSettings.query.all()
        settings_dict = {}

        for setting in settings:
            settings_dict[setting.setting_key] = SystemSettings.get_setting(setting.setting_key)

        return jsonify({
            'success': True,
            'settings': settings_dict
        })
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        return jsonify({'error': 'Failed to retrieve settings'}), 500

@app.route('/api/settings', methods=['PUT'])
def update_settings():
    """Update system settings"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        updated_settings = []

        for key, value in data.items():
            # Get current setting to determine type
            current = SystemSettings.query.filter_by(setting_key=key).first()
            setting_type = current.setting_type if current else 'string'

            SystemSettings.set_setting(key, value, setting_type)
            updated_settings.append(key)

        logger.info(f"Updated settings: {', '.join(updated_settings)}")
        return jsonify({
            'success': True,
            'updated': updated_settings,
            'message': 'Settings updated successfully'
        })

    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        return jsonify({'error': 'Failed to update settings'}), 500

# Static file serving for frontend assets
@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (CSS, JS, images)"""
    try:
        if filename.endswith(('.css', '.js', '.svg', '.png', '.jpg', '.jpeg', '.gif', '.ico')):
            # Try multiple possible paths for the public directory
            possible_paths = [
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public'),
                os.path.join(os.getcwd(), 'public'),
                'public'
            ]

            for public_dir in possible_paths:
                try:
                    return send_from_directory(public_dir, filename)
                except FileNotFoundError:
                    continue

            # If we get here, none of the paths worked
            raise FileNotFoundError(f"Could not find public directory for file: {filename}")
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        logger.error(f"Error serving static file {filename}: {e}")
        return jsonify({'error': 'Failed to serve file'}), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

# Cleanup endpoint (for manual cleanup)
@app.route('/api/check-status', methods=['POST'])
def check_all_statuses():
    """Manually check status of all routers"""
    try:
        routers = Router.query.all()
        status_results = []

        for router in routers:
            old_status = router.status
            is_online = check_router_status(router)
            status_results.append({
                'id': router.id,
                'name': router.name,
                'old_status': old_status,
                'new_status': router.status,
                'is_online': is_online
            })

        db.session.commit()

        online_count = sum(1 for result in status_results if result['is_online'])
        total_count = len(status_results)

        logger.info(f"Status check completed: {online_count}/{total_count} routers online")
        return jsonify({
            'success': True,
            'results': status_results,
            'summary': {
                'total_routers': total_count,
                'online_routers': online_count,
                'offline_routers': total_count - online_count
            },
            'message': f'Status check completed: {online_count}/{total_count} routers online'
        })

    except Exception as e:
        logger.error(f"Error during status check: {e}")
        return jsonify({'error': 'Failed to check router statuses'}), 500

@app.route('/api/cleanup', methods=['POST'])
def cleanup_backups():
    """Manually trigger backup cleanup"""
    try:
        from utils.scheduler import scheduler

        retention_days = SystemSettings.get_setting('backup_retention_days', 30)
        auto_delete = SystemSettings.get_setting('auto_delete_old_backups', True)

        # Ensure retention_days is an integer
        if not isinstance(retention_days, int):
            retention_days = 30

        if auto_delete:
            scheduler.backup_manager.cleanup_old_backups(retention_days)
            return jsonify({
                'success': True,
                'message': f'Cleaned up backups older than {retention_days} days'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Auto-delete is disabled in settings'
            })

    except Exception as e:
        logger.error(f"Error during manual cleanup: {e}")
        return jsonify({'error': 'Failed to cleanup backups'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({'error': 'File too large'}), 413

if __name__ == '__main__':
    # Change to the correct working directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Create backup directory if it doesn't exist
    os.makedirs(app.config['BACKUP_DIR'], exist_ok=True)

    logger.info("Starting MikroTik Auto Backup Tool")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Backup directory: {os.path.abspath(app.config['BACKUP_DIR'])}")
    logger.info("Web interface available at: http://localhost:5000")

    # Run the application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
```

**Changes made:**

1. **Removed `render_template_string` from the import** (line 7) — it's no longer needed.

2. **Replaced the `index()` route** (lines 58-83) — instead of reading the file contents and passing them to `render_template_string()` (which processes Jinja2 syntax and enables SSTI), the fix uses `send_from_directory()` to serve `index.html` as a static file. This treats the HTML as plain content without any template processing.

   The new implementation iterates the same candidate directories but uses `os.path.isfile()` to check existence, then serves via `send_from_directory()` which safely sends the file without template evaluation.