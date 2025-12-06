"""Reminder System for Atom AI.

Handles natural language reminder creation and management.
Examples:
- "Remind me to call mom in 5 minutes"
- "Set alarm for 7am tomorrow"
- "Remind me every day at 9am to check emails"
"""

import re
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple
from atom.tasks.scheduler import Scheduler, ScheduledTask, get_scheduler
from atom.utils.logger import setup_logger

logger = setup_logger(__name__, 'atom.log')


class ReminderManager:
    """Manages reminders with natural language parsing."""
    
    def __init__(self, scheduler: Scheduler = None):
        self.scheduler = scheduler or get_scheduler()
    
    def create_reminder(self, text: str, speak_callback=None) -> Optional[ScheduledTask]:
        """Create a reminder from natural language.
        
        Args:
            text: Natural language like "call mom in 5 minutes"
            speak_callback: Function to call for voice response
            
        Returns:
            Created task or None if parsing failed
        """
        # Parse the reminder text
        title, scheduled_time, recurrence = self._parse_reminder(text)
        
        if not title or not scheduled_time:
            logger.warning(f"Could not parse reminder: {text}")
            return None
        
        # Create task
        task = ScheduledTask(
            task_id=str(uuid.uuid4())[:8],
            title=title,
            scheduled_time=scheduled_time,
            task_type="reminder",
            recurrence=recurrence
        )
        
        # Add to scheduler
        if self.scheduler.add_task(task):
            response = self._format_confirmation(task)
            logger.info(f"Reminder created: {task.title} at {task.scheduled_time}")
            
            if speak_callback:
                speak_callback(response)
            
            return task
        
        return None
    
    def _parse_reminder(self, text: str) -> Tuple[Optional[str], Optional[datetime], Optional[str]]:
        """Parse reminder text into components.
        
        Returns:
            Tuple of (title, scheduled_time, recurrence)
        """
        text = text.lower().strip()
        
        # Remove common prefixes
        prefixes = ["remind me to ", "reminder ", "remind me ", "set a reminder to ", 
                   "set reminder ", "alarm ", "set alarm for ", "wake me up at "]
        for prefix in prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):]
                break
        
        # Check for recurrence
        recurrence = None
        if "every day" in text or "daily" in text:
            recurrence = "daily"
            text = text.replace("every day", "").replace("daily", "")
        elif "every week" in text or "weekly" in text:
            recurrence = "weekly"
            text = text.replace("every week", "").replace("weekly", "")
        
        # Parse time
        scheduled_time = None
        title = text
        
        # Pattern: "in X minutes/hours"
        match = re.search(r"in (\d+)\s*(minutes?|mins?|hours?|hrs?|seconds?|secs?)", text)
        if match:
            amount = int(match.group(1))
            unit = match.group(2)
            
            if "min" in unit:
                scheduled_time = datetime.now() + timedelta(minutes=amount)
            elif "hour" in unit or "hr" in unit:
                scheduled_time = datetime.now() + timedelta(hours=amount)
            elif "sec" in unit:
                scheduled_time = datetime.now() + timedelta(seconds=amount)
            
            title = text[:match.start()].strip()
        
        # Pattern: "at X:XX" or "at Xam/pm"
        if not scheduled_time:
            match = re.search(r"at (\d{1,2}):?(\d{2})?\s*(am|pm)?", text)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2)) if match.group(2) else 0
                ampm = match.group(3)
                
                if ampm == "pm" and hour < 12:
                    hour += 12
                elif ampm == "am" and hour == 12:
                    hour = 0
                
                now = datetime.now()
                scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # If time is in the past, schedule for tomorrow
                if scheduled_time < now:
                    scheduled_time += timedelta(days=1)
                
                title = text[:match.start()].strip()
        
        # Pattern: "tomorrow"
        if not scheduled_time and "tomorrow" in text:
            tomorrow = datetime.now() + timedelta(days=1)
            scheduled_time = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
            title = text.replace("tomorrow", "").strip()
        
        # Default: 1 hour from now
        if not scheduled_time:
            scheduled_time = datetime.now() + timedelta(hours=1)
        
        # Clean up title
        title = re.sub(r"\s+", " ", title).strip()
        if not title:
            title = "Reminder"
        
        return title, scheduled_time, recurrence
    
    def _format_confirmation(self, task: ScheduledTask) -> str:
        """Format confirmation message for a reminder."""
        time_str = task.scheduled_time.strftime("%I:%M %p")
        date_str = task.scheduled_time.strftime("%B %d")
        
        now = datetime.now()
        if task.scheduled_time.date() == now.date():
            date_part = f"today at {time_str}"
        elif task.scheduled_time.date() == (now + timedelta(days=1)).date():
            date_part = f"tomorrow at {time_str}"
        else:
            date_part = f"on {date_str} at {time_str}"
        
        if task.recurrence:
            return f"I'll remind you {task.recurrence} {date_part}: {task.title}"
        else:
            return f"I'll remind you {date_part}: {task.title}"
    
    def get_pending_reminders(self) -> list:
        """Get all pending reminders."""
        return self.scheduler.get_pending_tasks()
    
    def get_overdue_reminders(self) -> list:
        """Get overdue reminders that haven't been notified."""
        return self.scheduler.get_overdue_tasks()
    
    def announce_pending(self, speak_callback) -> int:
        """Announce all pending/overdue reminders on startup.
        
        Returns:
            Number of pending reminders announced
        """
        overdue = self.get_overdue_reminders()
        pending = self.get_pending_reminders()
        
        count = len(overdue)
        
        if overdue:
            speak_callback(f"You have {len(overdue)} missed reminder{'s' if len(overdue) > 1 else ''}.")
            
            for task in overdue[:3]:  # Announce max 3
                speak_callback(f"Reminder: {task.title}")
                self.scheduler.mark_notified(task.task_id)
        
        elif pending:
            next_task = pending[0]
            time_str = next_task.scheduled_time.strftime("%I:%M %p")
            speak_callback(f"You have {len(pending)} upcoming reminder{'s' if len(pending) > 1 else ''}. Next one at {time_str}.")
        
        return count
    
    def cancel_reminder(self, keyword: str) -> bool:
        """Cancel a reminder by keyword match."""
        pending = self.get_pending_reminders()
        
        for task in pending:
            if keyword.lower() in task.title.lower():
                self.scheduler.remove_task(task.task_id)
                logger.info(f"Cancelled reminder: {task.title}")
                return True
        
        return False


# Singleton
_reminder_manager = None

def get_reminder_manager() -> ReminderManager:
    global _reminder_manager
    if _reminder_manager is None:
        _reminder_manager = ReminderManager()
    return _reminder_manager


if __name__ == "__main__":
    print("Reminder Manager Test")
    print("=" * 50)
    
    def speak(text):
        print(f"🔊 {text}")
    
    manager = ReminderManager()
    
    # Test parsing
    tests = [
        "call mom in 5 minutes",
        "check emails at 9am",
        "wake me up at 7:30 am tomorrow",
        "exercise every day at 6pm"
    ]
    
    for test in tests:
        print(f"\nInput: '{test}'")
        task = manager.create_reminder(test, speak)
        if task:
            print(f"  → {task.title} | {task.scheduled_time} | Recur: {task.recurrence}")
