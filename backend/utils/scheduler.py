"""
Backup scheduling utilities for automated MikroTik backups
"""
import logging
import schedule
import time
import threading
from datetime import datetime, timedelta
from .mikrotik import BackupManager
from models import Router, Backup, Schedule, db

logger = logging.getLogger(__name__)

class BackupScheduler:
    """Automated backup scheduler using the schedule library"""

    def __init__(self):
        self.running = False
        self.scheduler_thread = None
        self.backup_manager = BackupManager()

    def start(self):
        """Start the backup scheduler"""
        if self.running:
            logger.warning("Scheduler is already running")
            return

        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("Backup scheduler started")

    def stop(self):
        """Stop the backup scheduler"""
        if not self.running:
            logger.warning("Scheduler is not running")
            return

        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Backup scheduler stopped")

    def _run_scheduler(self):
        """Main scheduler loop"""
        logger.info("Scheduler loop started")

        while self.running:
            try:
                # Run pending scheduled tasks
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)

    def schedule_backup(self, router_id, schedule_time, backup_type='full'):
        """Schedule a one-time backup for a specific router"""
        def job():
            self._execute_backup(router_id, backup_type)

        # Schedule the job
        schedule_time_str = schedule_time.strftime('%H:%M')
        schedule.every().day.at(schedule_time_str).do(job)

        logger.info(f"Scheduled {backup_type} backup for router {router_id} at {schedule_time_str}")

    def schedule_recurring_backup(self, router_id, cron_expression, backup_type='full'):
        """Schedule a recurring backup using cron-like expression"""
        # Parse cron expression (simplified)
        # Format: "minute hour day month weekday"
        # Example: "0 2 * * *" for daily at 2:00 AM

        def job():
            self._execute_backup(router_id, backup_type)

        try:
            # Simple cron parsing (can be enhanced with croniter library)
            parts = cron_expression.split()
            if len(parts) >= 2:
                minute = parts[0]
                hour = parts[1]

                if minute == '*' and hour != '*':
                    # Every minute during specific hour (simplified: run once at HH:00)
                    schedule.every().day.at(f"{hour}:00").do(job)
                elif hour == '*' and minute != '*':
                    # Every hour at specific minute
                    schedule.every().hour.at(f":{minute}").do(job)
                elif hour != '*' and minute != '*':
                    # Specific time daily
                    schedule.every().day.at(f"{hour}:{minute}").do(job)
                else:
                    logger.error(f"Unsupported cron expression: {cron_expression}")
                    return False

                logger.info(f"Scheduled recurring {backup_type} backup for router {router_id} with cron: {cron_expression}")
                return True

        except Exception as e:
            logger.error(f"Failed to parse cron expression '{cron_expression}': {e}")
            return False

    def _execute_backup(self, router_id, backup_type='full'):
        """Execute backup for a router"""
        try:
            # Get router from database
            router = Router.query.get(router_id)
            if not router:
                logger.error(f"Router {router_id} not found")
                return False

            if not router.enabled:
                logger.info(f"Router {router.name} is disabled, skipping backup")
                return False

            logger.info(f"Starting scheduled backup for router: {router.name}")

            # Create backup
            result = self.backup_manager.create_router_backup(router, backup_type=backup_type)

            if result['success']:
                # Save backup record to database
                backup = Backup(
                    router_id=router.id,
                    filename=result['filename'],
                    file_path=result['file_path'],
                    file_size=result['file_size'],
                    backup_type=backup_type,
                    status='success'
                )

                # Update router stats
                router.last_backup = datetime.utcnow()
                router.backup_count += 1

                db.session.add(backup)
                db.session.commit()

                logger.info(f"Scheduled backup completed successfully for router: {router.name}")
                return True
            else:
                # Save failed backup record
                backup = Backup(
                    router_id=router.id,
                    filename='',
                    file_path='',
                    file_size=0,
                    backup_type=backup_type,
                    status='failed',
                    error_message=result.get('error', 'Unknown error')
                )

                db.session.add(backup)
                db.session.commit()

                logger.error(f"Scheduled backup failed for router {router.name}: {result.get('error')}")
                return False

        except Exception as e:
            logger.error(f"Error executing scheduled backup for router {router_id}: {e}")
            return False

    def load_schedules_from_db(self):
        """Load and activate all schedules from database"""
        try:
            schedules = Schedule.query.filter_by(enabled=True).all()

            for sched in schedules:
                success = self.schedule_recurring_backup(
                    sched.router_id,
                    sched.cron_expression,
                    sched.backup_type
                )

                if success:
                    logger.info(f"Activated schedule: {sched.name} for router {sched.router.name}")
                else:
                    logger.error(f"Failed to activate schedule: {sched.name}")

        except Exception as e:
            logger.error(f"Error loading schedules from database: {e}")

    def cleanup_old_backups(self):
        """Clean up old backup files based on retention settings"""
        try:
            from models import SystemSettings

            retention_days = SystemSettings.get_setting('backup_retention_days', 30)
            auto_delete = SystemSettings.get_setting('auto_delete_old_backups', True)

            # Ensure retention_days is an integer
            if not isinstance(retention_days, int):
                retention_days = 30

            if auto_delete:
                self.backup_manager.cleanup_old_backups(retention_days)
                logger.info(f"Cleaned up backups older than {retention_days} days")

        except Exception as e:
            logger.error(f"Error during backup cleanup: {e}")

    def get_next_runs(self):
        """Get information about next scheduled runs"""
        # This is a simplified version - in a real implementation,
        # you'd want to use a more sophisticated scheduling library
        next_runs = []

        try:
            schedules = Schedule.query.filter_by(enabled=True).all()

            for sched in schedules:
                # Parse cron expression to estimate next run
                next_run = self._estimate_next_run(sched.cron_expression)
                if next_run:
                    next_runs.append({
                        'schedule_id': sched.id,
                        'schedule_name': sched.name,
                        'router_name': sched.router.name,
                        'next_run': next_run.isoformat(),
                        'cron_expression': sched.cron_expression
                    })

        except Exception as e:
            logger.error(f"Error getting next runs: {e}")

        return next_runs

    def _estimate_next_run(self, cron_expression):
        """Estimate next run time from cron expression"""
        try:
            parts = cron_expression.split()
            if len(parts) >= 2:
                now = datetime.now()

                # Simple estimation - in production, use croniter library
                if parts[1] != '*':  # Specific hour
                    hour = int(parts[1])
                    next_run = now.replace(hour=hour, minute=int(parts[0]) if parts[0] != '*' else 0,
                                         second=0, microsecond=0)

                    if next_run <= now:
                        next_run += timedelta(days=1)

                    return next_run

        except Exception as e:
            logger.error(f"Error estimating next run for cron '{cron_expression}': {e}")

        return None

# Global scheduler instance
scheduler = BackupScheduler()

def start_scheduler():
    """Start the global scheduler instance"""
    scheduler.start()
    scheduler.load_schedules_from_db()

def stop_scheduler():
    """Stop the global scheduler instance"""
    scheduler.stop()

def schedule_router_backup(router_id, cron_expression, backup_type='full', schedule_name=None):
    """Schedule a recurring backup for a router"""
    try:
        router = Router.query.get(router_id)
        if not router:
            return False

        # Create schedule record
        schedule = Schedule(
            router_id=router_id,
            name=schedule_name or f"Auto-backup {router.name}",
            cron_expression=cron_expression,
            backup_type=backup_type,
            enabled=True
        )

        db.session.add(schedule)
        db.session.commit()

        # Activate the schedule
        success = scheduler.schedule_recurring_backup(router_id, cron_expression, backup_type)

        if success:
            logger.info(f"Created and activated schedule for router: {router.name}")
            return True
        else:
            # Remove from database if activation failed
            db.session.delete(schedule)
            db.session.commit()
            return False

    except Exception as e:
        logger.error(f"Error creating backup schedule: {e}")
        return False

def get_scheduler_status():
    """Get scheduler status and information"""
    return {
        'running': scheduler.running,
        'next_runs': scheduler.get_next_runs(),
        'active_schedules': len(scheduler.get_next_runs())
    }