"""Data models for the podcast application."""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Episode:
    """Represents a podcast episode."""
    title: str
    description: str
    url: str
    pub_date: str
    duration: Optional[str] = None

    def __str__(self):
        return f"{self.title} ({self.pub_date})"


@dataclass
class Podcast:
    """Represents a podcast subscription."""
    title: str
    feed_url: str
    description: str
    author: Optional[str] = None

    def to_dict(self):
        """Convert to dictionary for JSON storage."""
        return {
            'title': self.title,
            'feed_url': self.feed_url,
            'description': self.description,
            'author': self.author
        }

    @classmethod
    def from_dict(cls, data):
        """Create Podcast from dictionary."""
        return cls(
            title=data['title'],
            feed_url=data['feed_url'],
            description=data['description'],
            author=data.get('author')
        )
