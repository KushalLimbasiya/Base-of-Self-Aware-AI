"""Task Scheduler for Atom AI.

Manages scheduled tasks, reminders, and recurring events.
Runs in a background thread and triggers voice notifications.
"""

import threading
import time
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Callable
from atom.utils.logger import setup_logger

logger = setup_logger(__name__, 'atom.log')


class ScheduledTask:
    """Represents a scheduled task or reminder."""
    
    def __init__(
        self,
        task_id: str,
        title: str,
        scheduled_time: datetime,
        task_type: str = "reminder",  # reminder, event, recurring
        recurrence: Optional[str] = None,  # daily, weekly, monthly
        completed: bool = False,
        notified: bool = False,
        metadata: Optional[Dict] = None
    ):
        self.task_id = task_id
        self.title = title
        self.scheduled_time = scheduled_time
        self.task_type = task_type
        self.recurrence = recurrence
        self.completed = completed
        self.notified = notified
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "scheduled_time": self.scheduled_time.isoformat(),
            "task_type": self.task_type,
            "recurrence": self.recurrence,
            "completed": self.completed,
            "notified": self.notified,
            "metadata": json.dumps(self.metadata)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ScheduledTask":
        return cls(
            task_id=data["task_id"],
            title=data["title"],
            scheduled_time=datetime.fromisoformat(data["scheduled_time"]),
            task_type=data.get("task_type", "reminder"),
            recurrence=data.get("recurrence"),
            completed=data.get("completed", False),
            notified=data.get("notified", False),
            metadata=json.loads(data.get("metadata", "{}"))
        )
    
    def is_due(self) -> bool:
        """Check if task is due now."""
        return datetime.now() >= self.scheduled_time and not self.notified
    
    def is_overdue(self) -> bool:
        """Check if task is past due time."""
        return datetime.now() > self.scheduled_time


class Scheduler:
    """Background scheduler for tasks and reminders.
    
    Features:
    - Persistent storage in SQLite
    - Background thread for checking tasks
    - Natural language time parsing
    - Recurring tasks support
    - Voice notifications via callback
    """
    
    def __init__(
        self,
        db_path: str = "data/scheduler.db",
        check_interval: int = 30,  # seconds
        notification_callback: Optional[Callable] = None
    ):
        self.db_path = db_path
        self.check_interval = check_interval
        self.notification_callback = notification_callback
        
        self._running = False
        self._thread = None
        
        self._init_db()
        logger.info("Scheduler initialized")
    
    def _init_db(self):
        """Initialize SQLite database for tasks."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                scheduled_time TEXT NOT NULL,
                task_type TEXT DEFAULT 'reminder',
                recurrence TEXT,
                completed INTEGER DEFAULT 0,
                notified INTEGER DEFAULT 0,
                metadata TEXT DEFAULT '{}'
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_task(self, task: ScheduledTask) -> bool:
        """Add a new scheduled task."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            data = task.to_dict()
            cursor.execute("""
                INSERT OR REPLACE INTO tasks 
                (task_id, title, scheduled_time, task_type, recurrence, completed, notified, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["task_id"], data["title"], data["scheduled_time"],
                data["task_type"], data["recurrence"], 
                int(data["completed"]), int(data["notified"]),
                data["metadata"]
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Task added: {task.title} at {task.scheduled_time}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add task: {e}")
            return False
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a task by ID."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to remove task: {e}")
            return False
    
    def get_pending_tasks(self) -> List[ScheduledTask]:
        """Get all pending (not notified) tasks."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT task_id, title, scheduled_time, task_type, recurrence, 
                   completed, notified, metadata
            FROM tasks
            WHERE notified = 0 AND completed = 0
            ORDER BY scheduled_time
        """)
        
        tasks = []
        for row in cursor.fetchall():
            tasks.append(ScheduledTask.from_dict({
                "task_id": row[0],
                "title": row[1],
                "scheduled_time": row[2],
                "task_type": row[3],
                "recurrence": row[4],
                "completed": bool(row[5]),
                "notified": bool(row[6]),
                "metadata": row[7]
            }))
        
        conn.close()
        return tasks
    
    def get_overdue_tasks(self) -> List[ScheduledTask]:
        """Get tasks that are past their scheduled time but not notified."""
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT task_id, title, scheduled_time, task_type, recurrence,
                   completed, notified, metadata
            FROM tasks
            WHERE scheduled_time < ? AND notified = 0 AND completed = 0
            ORDER BY scheduled_time
        """, (now,))
        
        tasks = []
        for row in cursor.fetchall():
            tasks.append(ScheduledTask.from_dict({
                "task_id": row[0],
                "title": row[1],
                "scheduled_time": row[2],
                "task_type": row[3],
                "recurrence": row[4],
                "completed": bool(row[5]),
                "notified": bool(row[6]),
                "metadata": row[7]
            }))
        
        conn.close()
        return tasks
    
    def mark_notified(self, task_id: str):
        """Mark a task as notified."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET notified = 1 WHERE task_id = ?", (task_id,))
        conn.commit()
        conn.close()
    
    def mark_completed(self, task_id: str):
        """Mark a task as completed."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET completed = 1 WHERE task_id = ?", (task_id,))
        conn.commit()
        conn.close()
    
    def _handle_recurring(self, task: ScheduledTask):
        """Create next occurrence for recurring tasks."""
        if not task.recurrence:
            return
        
        if task.recurrence == "daily":
            next_time = task.scheduled_time + timedelta(days=1)
        elif task.recurrence == "weekly":
            next_time = task.scheduled_time + timedelta(weeks=1)
        elif task.recurrence == "monthly":
            next_time = task.scheduled_time + timedelta(days=30)
        else:
            return
        
        import uuid
        new_task = ScheduledTask(
            task_id=str(uuid.uuid4())[:8],
            title=task.title,
            scheduled_time=next_time,
            task_type=task.task_type,
            recurrence=task.recurrence,
            metadata=task.metadata
        )
        self.add_task(new_task)
        logger.info(f"Created next occurrence: {new_task.title} at {next_time}")
    
    def _check_tasks(self):
        """Check for due tasks and trigger notifications."""
        now = datetime.now()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT task_id, title, scheduled_time, task_type, recurrence,
                   completed, notified, metadata
            FROM tasks
            WHERE scheduled_time <= ? AND notified = 0 AND completed = 0
        """, (now.isoformat(),))
        
        for row in cursor.fetchall():
            task = ScheduledTask.from_dict({
                "task_id": row[0],
                "title": row[1],
                "scheduled_time": row[2],
                "task_type": row[3],
                "recurrence": row[4],
                "completed": bool(row[5]),
                "notified": bool(row[6]),
                "metadata": row[7]
            })
            
            # Trigger notification
            if self.notification_callback:
                try:
                    self.notification_callback(task)
                except Exception as e:
                    logger.error(f"Notification failed: {e}")
            
            # Mark as notified
            self.mark_notified(task.task_id)
            
            # Handle recurring
            if task.recurrence:
                self._handle_recurring(task)
        
        conn.close()
    
    def start(self):
        """Start background scheduler thread."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("Scheduler started")
    
    def stop(self):
        """Stop scheduler thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        logger.info("Scheduler stopped")
    
    def _run_loop(self):
        """Background loop checking for tasks."""
        while self._running:
            try:
                self._check_tasks()
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
            
            time.sleep(self.check_interval)


# Singleton instance
_scheduler = None

def get_scheduler(notification_callback: Callable = None) -> Scheduler:
    """Get or create scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = Scheduler(notification_callback=notification_callback)
    return _scheduler


if __name__ == "__main__":
    import uuid
    
    print("Scheduler Test")
    print("=" * 50)
    
    def notify(task):
        print(f"\n🔔 REMINDER: {task.title}")
        print(f"   Scheduled: {task.scheduled_time}")
    
    scheduler = Scheduler(notification_callback=notify, check_interval=5)
    
    # Add test task
    task = ScheduledTask(
        task_id=str(uuid.uuid4())[:8],
        title="Test reminder",
        scheduled_time=datetime.now() + timedelta(seconds=10)
    )
    scheduler.add_task(task)
    print(f"Added task: {task.title} in 10 seconds")
    
    scheduler.start()
    
    try:
        print("\nWaiting for notification... (Ctrl+C to exit)")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.stop()
        print("\nDone!")
