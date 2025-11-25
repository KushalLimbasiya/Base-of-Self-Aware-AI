"""User Profile Management for Atom.

Manages user personal information including name, location, interests, and preferences.
Stores data in SQLite database for persistence across sessions.
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path
from Logger import setup_logger

logger = setup_logger(__name__, 'atom.log')


@dataclass
class UserProfile:
    """User profile data structure.
    
    Attributes:
        user_name: User's name (detected from conversation)
        location: User's location/city
        occupation: User's job/profession
        interests: List of user interests
        preferences: Dict of user preferences
        timezone: User's timezone
        language: Preferred language (default: 'en')
        first_interaction: First time user interacted
        last_interaction: Last time user interacted
        total_conversations: Total number of conversations
    """
    user_name: Optional[str] = None
    location: Optional[str] = None
    occupation: Optional[str] = None
    interests: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    timezone: Optional[str] = None
    language: str = "en"
    first_interaction: Optional[str] = None
    last_interaction: Optional[str] = None
    total_conversations: int = 0
    
    def to_dict(self) -> dict:
        """Convert profile to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UserProfile':
        """Create profile from dictionary."""
        # Convert JSON strings back to lists/dicts
        if 'interests' in data and isinstance(data['interests'], str):
            data['interests'] = json.loads(data['interests'])
        if 'preferences' in data and isinstance(data['preferences'], str):
            data['preferences'] = json.loads(data['preferences'])
        return cls(**data)


class UserProfileManager:
    """Manages user profile storage and retrieval.
    
    Uses SQLite database to persist user information across sessions.
    """
    
    def __init__(self, db_path: str = "data/memory.db"):
        """Initialize profile manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Create table if not exists
        self._create_table()
        logger.info(f"UserProfileManager initialized with database: {db_path}")
    
    def _create_table(self):
        """Create user_profile table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_profile (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_name TEXT,
                    location TEXT,
                    occupation TEXT,
                    interests TEXT,
                    preferences TEXT,
                    timezone TEXT,
                    language TEXT DEFAULT 'en',
                    first_interaction TEXT,
                    last_interaction TEXT,
                    total_conversations INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            logger.debug("User profile table created/verified")
    
    def get_profile(self) -> UserProfile:
        """Get current user's profile.
        
        Returns:
            UserProfile object (creates new if doesn't exist)
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get first profile (single user system for now)
            cursor.execute('SELECT * FROM user_profile ORDER BY id DESC LIMIT 1')
            row = cursor.fetchone()
            
            if row:
                data = dict(row)
                # Remove SQLite-specific fields
                data.pop('id', None)
                data.pop('created_at', None)
                data.pop('updated_at', None)
                
                profile = UserProfile.from_dict(data)
                logger.debug(f"Loaded profile for user: {profile.user_name or 'Unknown'}")
                return profile
            else:
                # Create new profile
                logger.info("No existing profile found, creating new one")
                return UserProfile()
    
    def save_profile(self, profile: UserProfile):
        """Save or update user profile.
        
        Args:
            profile: UserProfile object to save
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Update last interaction
            profile.last_interaction = datetime.now().isoformat()
            
            # Check if profile exists
            cursor.execute('SELECT id FROM user_profile LIMIT 1')
            exists = cursor.fetchone()
            
            # Convert lists/dicts to JSON
            interests_json = json.dumps(profile.interests)
            preferences_json = json.dumps(profile.preferences)
            
            if exists:
                # Update existing
                cursor.execute('''
                    UPDATE user_profile SET
                        user_name = ?,
                        location = ?,
                        occupation = ?,
                        interests = ?,
                        preferences = ?,
                        timezone = ?,
                        language = ?,
                        last_interaction = ?,
                        total_conversations = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = (SELECT id FROM user_profile LIMIT 1)
                ''', (
                    profile.user_name,
                    profile.location,
                    profile.occupation,
                    interests_json,
                    preferences_json,
                    profile.timezone,
                    profile.language,
                    profile.last_interaction,
                    profile.total_conversations
                ))
                logger.info(f"Updated profile for: {profile.user_name or 'User'}")
            else:
                # Insert new
                if not profile.first_interaction:
                    profile.first_interaction = datetime.now().isoformat()
                
                cursor.execute('''
                    INSERT INTO user_profile (
                        user_name, location, occupation, interests,
                        preferences, timezone, language, first_interaction,
                        last_interaction, total_conversations
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    profile.user_name,
                    profile.location,
                    profile.occupation,
                    interests_json,
                    preferences_json,
                    profile.timezone,
                    profile.language,
                    profile.first_interaction,
                    profile.last_interaction,
                    profile.total_conversations
                ))
                logger.info(f"Created new profile for: {profile.user_name or 'User'}")
            
            conn.commit()
    
    def update_name(self, name: str):
        """Update user's name.
        
        Args:
            name: User's name
        """
        profile = self.get_profile()
        profile.user_name = name
        self.save_profile(profile)
        logger.info(f"User name updated to: {name}")
    
    def update_location(self, location: str):
        """Update user's location.
        
        Args:
            location: User's location/city
        """
        profile = self.get_profile()
        profile.location = location
        self.save_profile(profile)
        logger.info(f"User location updated to: {location}")
    
    def update_occupation(self, occupation: str):
        """Update user's occupation.
        
        Args:
            occupation: User's job/profession
        """
        profile = self.get_profile()
        profile.occupation = occupation
        self.save_profile(profile)
        logger.info(f"User occupation updated to: {occupation}")
    
    def add_interest(self, interest: str):
        """Add an interest to user's profile.
        
        Args:
            interest: Interest to add
        """
        profile = self.get_profile()
        if interest not in profile.interests:
            profile.interests.append(interest)
            self.save_profile(profile)
            logger.info(f"Added interest: {interest}")
    
    def set_preference(self, key: str, value: Any):
        """Set a user preference.
        
        Args:
            key: Preference key
            value: Preference value
        """
        profile = self.get_profile()
        profile.preferences[key] = value
        self.save_profile(profile)
        logger.debug(f"Set preference {key} = {value}")
    
    def increment_conversations(self):
        """Increment total conversation count."""
        profile = self.get_profile()
        profile.total_conversations += 1
        self.save_profile(profile)
    
    def delete_profile(self):
        """Delete all user profile data."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM user_profile')
            conn.commit()
        logger.warning("User profile deleted")
    
    def get_profile_summary(self) -> str:
        """Get formatted profile summary for speech.
        
        Returns:
            String summary of user profile
        """
        profile = self.get_profile()
        
        if not profile.user_name:
            return "I don't know your name yet. You can introduce yourself by saying 'My name is' followed by your name."
        
        summary = f"Your name is {profile.user_name}."
        
        if profile.location:
            summary += f" You live in {profile.location}."
        
        if profile.occupation:
            summary += f" You work as {profile.occupation}."
        
        if profile.interests:
            interests_str = ", ".join(profile.interests[:3])
            summary += f" You're interested in {interests_str}."
        
        if profile.total_conversations > 0:
            summary += f" We've had {profile.total_conversations} conversations."
        
        return summary


# Example usage and testing
if __name__ == "__main__":
    print("UserProfile Demo")
    print("=" * 50)
    
    # Initialize manager
    manager = UserProfileManager("data/test_memory.db")
    
    # Get profile
    profile = manager.get_profile()
    print(f"\nCurrent profile: {profile.user_name or 'No name set'}")
    
    # Update name
    manager.update_name("Alice")
    print("Name updated to: Alice")
    
    # Update location
    manager.update_location("New York")
    print("Location updated to: New York")
    
    # Add interests
    manager.add_interest("programming")
    manager.add_interest("AI")
    print("Added interests: programming, AI")
    
    # Get summary
    summary = manager.get_profile_summary()
    print(f"\nProfile Summary:\n{summary}")
    
    # Get updated profile
    profile = manager.get_profile()
    print(f"\nFull Profile:")
    print(f"  Name: {profile.user_name}")
    print(f"  Location: {profile.location}")
    print(f"  Interests: {profile.interests}")
    print(f"  Conversations: {profile.total_conversations}")
    
    print("\n" + "=" * 50)
    print("Demo complete!")
