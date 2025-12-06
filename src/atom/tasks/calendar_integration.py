"""Calendar Integration for Atom AI.

Supports two modes:
1. Google Calendar API - Full sync with Google Calendar
2. Local Calendar - Offline calendar stored in SQLite

Features:
- View upcoming events
- Create/delete events
- Get reminders for upcoming events
- Time-based greetings
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from atom.utils.logger import setup_logger

logger = setup_logger(__name__, 'atom.log')


class CalendarEvent:
    """Represents a calendar event."""
    
    def __init__(
        self,
        event_id: str,
        title: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        description: str = "",
        location: str = "",
        source: str = "local"  # local or google
    ):
        self.event_id = event_id
        self.title = title
        self.start_time = start_time
        self.end_time = end_time or (start_time + timedelta(hours=1))
        self.description = description
        self.location = location
        self.source = source
    
    def to_dict(self) -> Dict:
        return {
            "event_id": self.event_id,
            "title": self.title,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "description": self.description,
            "location": self.location,
            "source": self.source
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "CalendarEvent":
        return cls(
            event_id=data["event_id"],
            title=data["title"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
            description=data.get("description", ""),
            location=data.get("location", ""),
            source=data.get("source", "local")
        )


class LocalCalendar:
    """Local calendar stored in SQLite."""
    
    def __init__(self, db_path: str = "data/calendar.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                description TEXT DEFAULT '',
                location TEXT DEFAULT '',
                source TEXT DEFAULT 'local'
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_event(self, event: CalendarEvent) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO events
                (event_id, title, start_time, end_time, description, location, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                event.event_id, event.title, event.start_time.isoformat(),
                event.end_time.isoformat() if event.end_time else None,
                event.description, event.location, event.source
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Event added: {event.title}")
            return True
        except Exception as e:
            logger.error(f"Failed to add event: {e}")
            return False
    
    def get_upcoming_events(self, hours: int = 24) -> List[CalendarEvent]:
        """Get events in the next N hours."""
        now = datetime.now()
        end = now + timedelta(hours=hours)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT event_id, title, start_time, end_time, description, location, source
            FROM events
            WHERE start_time >= ? AND start_time <= ?
            ORDER BY start_time
        """, (now.isoformat(), end.isoformat()))
        
        events = []
        for row in cursor.fetchall():
            events.append(CalendarEvent(
                event_id=row[0],
                title=row[1],
                start_time=datetime.fromisoformat(row[2]),
                end_time=datetime.fromisoformat(row[3]) if row[3] else None,
                description=row[4] or "",
                location=row[5] or "",
                source=row[6] or "local"
            ))
        
        conn.close()
        return events
    
    def get_today_events(self) -> List[CalendarEvent]:
        """Get all events for today."""
        now = datetime.now()
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT event_id, title, start_time, end_time, description, location, source
            FROM events
            WHERE start_time >= ? AND start_time < ?
            ORDER BY start_time
        """, (start.isoformat(), end.isoformat()))
        
        events = []
        for row in cursor.fetchall():
            events.append(CalendarEvent(
                event_id=row[0],
                title=row[1],
                start_time=datetime.fromisoformat(row[2]),
                end_time=datetime.fromisoformat(row[3]) if row[3] else None,
                description=row[4] or "",
                location=row[5] or "",
                source=row[6] or "local"
            ))
        
        conn.close()
        return events
    
    def delete_event(self, event_id: str) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM events WHERE event_id = ?", (event_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to delete event: {e}")
            return False


class GoogleCalendar:
    """Google Calendar integration using API."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self._service = None
        
        if api_key:
            logger.info("Google Calendar API initialized")
    
    def is_configured(self) -> bool:
        """Check if API is configured."""
        return bool(self.api_key)
    
    def get_upcoming_events(self, max_results: int = 10) -> List[CalendarEvent]:
        """Get upcoming events from Google Calendar.
        
        Note: For full functionality, need OAuth2 credentials.
        This is a simplified version using API key for public calendars.
        """
        if not self.api_key:
            return []
        
        try:
            import requests
            
            # Using Google Calendar API v3
            # Note: API key access is limited. Full access requires OAuth2.
            url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
            
            now = datetime.utcnow().isoformat() + "Z"
            params = {
                "key": self.api_key,
                "timeMin": now,
                "maxResults": max_results,
                "singleEvents": True,
                "orderBy": "startTime"
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Google Calendar API error: {response.status_code}")
                return []
            
            data = response.json()
            events = []
            
            for item in data.get("items", []):
                start = item.get("start", {})
                start_time = start.get("dateTime") or start.get("date")
                
                if start_time:
                    events.append(CalendarEvent(
                        event_id=item.get("id", ""),
                        title=item.get("summary", "Untitled"),
                        start_time=datetime.fromisoformat(start_time.replace("Z", "+00:00")),
                        description=item.get("description", ""),
                        location=item.get("location", ""),
                        source="google"
                    ))
            
            return events
            
        except Exception as e:
            logger.error(f"Google Calendar error: {e}")
            return []


class CalendarManager:
    """Unified calendar manager supporting local and Google calendars."""
    
    def __init__(self, google_api_key: str = None, db_path: str = "data/calendar.db"):
        self.local = LocalCalendar(db_path)
        self.google = GoogleCalendar(google_api_key) if google_api_key else None
        
        logger.info(f"CalendarManager initialized (Google: {bool(google_api_key)})")
    
    def get_upcoming_events(self, hours: int = 24) -> List[CalendarEvent]:
        """Get all upcoming events from all sources."""
        events = self.local.get_upcoming_events(hours)
        
        if self.google and self.google.is_configured():
            try:
                google_events = self.google.get_upcoming_events()
                events.extend(google_events)
            except Exception as e:
                logger.warning(f"Could not fetch Google events: {e}")
        
        # Sort by start time
        events.sort(key=lambda e: e.start_time)
        return events
    
    def get_today_events(self) -> List[CalendarEvent]:
        """Get today's events."""
        return self.local.get_today_events()
    
    def add_event(self, event: CalendarEvent) -> bool:
        """Add event to local calendar."""
        return self.local.add_event(event)
    
    def get_time_greeting(self) -> str:
        """Get appropriate greeting based on time of day."""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return "Good morning"
        elif 12 <= hour < 17:
            return "Good afternoon"
        elif 17 <= hour < 21:
            return "Good evening"
        else:
            return "Hello"
    
    def get_day_summary(self) -> str:
        """Get summary of today's events."""
        events = self.get_today_events()
        
        if not events:
            return "You have no events scheduled for today."
        
        if len(events) == 1:
            e = events[0]
            time_str = e.start_time.strftime("%I:%M %p")
            return f"You have one event today: {e.title} at {time_str}."
        
        summary = f"You have {len(events)} events today. "
        next_event = events[0]
        time_str = next_event.start_time.strftime("%I:%M %p")
        summary += f"Next up is {next_event.title} at {time_str}."
        
        return summary


# Singleton
_calendar_manager = None

def get_calendar_manager(api_key: str = None) -> CalendarManager:
    global _calendar_manager
    if _calendar_manager is None:
        _calendar_manager = CalendarManager(google_api_key=api_key)
    return _calendar_manager


if __name__ == "__main__":
    import uuid
    
    print("Calendar Manager Test")
    print("=" * 50)
    
    manager = CalendarManager()
    
    # Add test event
    event = CalendarEvent(
        event_id=str(uuid.uuid4())[:8],
        title="Team Meeting",
        start_time=datetime.now() + timedelta(hours=2),
        description="Weekly sync"
    )
    manager.add_event(event)
    print(f"Added: {event.title}")
    
    # Get greeting
    print(f"\n{manager.get_time_greeting()}!")
    
    # Get summary
    print(f"\n{manager.get_day_summary()}")
    
    # List upcoming
    print("\nUpcoming events:")
    for e in manager.get_upcoming_events(hours=48):
        print(f"  - {e.title} at {e.start_time.strftime('%I:%M %p')}")
