"""Core podcast management functionality."""

import json
import os
from typing import List, Optional
import feedparser
import requests
from models import Podcast, Episode


class PodcastManager:
    """Manages podcast subscriptions and feed parsing."""

    def __init__(self, storage_file='subscriptions.json'):
        self.storage_file = storage_file
        self.subscriptions: List[Podcast] = []
        self.load_subscriptions()

    def load_subscriptions(self):
        """Load subscriptions from JSON file."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.subscriptions = [Podcast.from_dict(p) for p in data]
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error loading subscriptions: {e}")
                self.subscriptions = []

    def save_subscriptions(self):
        """Save subscriptions to JSON file."""
        with open(self.storage_file, 'w') as f:
            data = [p.to_dict() for p in self.subscriptions]
            json.dump(data, f, indent=2)

    def subscribe(self, feed_url: str) -> bool:
        """Subscribe to a podcast feed."""
        # Check if already subscribed
        if any(p.feed_url == feed_url for p in self.subscriptions):
            print("Already subscribed to this podcast.")
            return False

        # Parse feed to get podcast info
        feed = feedparser.parse(feed_url)

        if not feed.entries and not feed.feed:
            print("Invalid feed URL or unable to parse feed.")
            return False

        # Extract podcast information
        feed_info = feed.feed
        podcast = Podcast(
            title=feed_info.get('title', 'Unknown Podcast'),
            feed_url=feed_url,
            description=feed_info.get('subtitle', feed_info.get('description', 'No description')),
            author=feed_info.get('author', feed_info.get('itunes_author'))
        )

        self.subscriptions.append(podcast)
        self.save_subscriptions()
        print(f"Successfully subscribed to: {podcast.title}")
        return True

    def unsubscribe(self, podcast_title: str) -> bool:
        """Unsubscribe from a podcast."""
        original_count = len(self.subscriptions)
        self.subscriptions = [p for p in self.subscriptions if p.title != podcast_title]

        if len(self.subscriptions) < original_count:
            self.save_subscriptions()
            print(f"Unsubscribed from: {podcast_title}")
            return True
        else:
            print(f"Podcast not found: {podcast_title}")
            return False

    def list_subscriptions(self) -> List[Podcast]:
        """Return list of all subscriptions."""
        return self.subscriptions

    def get_episodes(self, podcast_title: str, limit: int = 10) -> List[Episode]:
        """Get recent episodes for a podcast."""
        podcast = next((p for p in self.subscriptions if p.title == podcast_title), None)

        if not podcast:
            print(f"Podcast not found: {podcast_title}")
            return []

        feed = feedparser.parse(podcast.feed_url)
        episodes = []

        for entry in feed.entries[:limit]:
            # Find audio enclosure
            audio_url = None
            for enclosure in entry.get('enclosures', []):
                if 'audio' in enclosure.get('type', ''):
                    audio_url = enclosure.get('href')
                    break

            if not audio_url:
                audio_url = entry.get('link', '')

            episode = Episode(
                title=entry.get('title', 'Unknown Episode'),
                description=entry.get('summary', 'No description'),
                url=audio_url,
                pub_date=entry.get('published', 'Unknown date'),
                duration=entry.get('itunes_duration')
            )
            episodes.append(episode)

        return episodes

    def download_episode(self, episode_url: str, filename: str) -> bool:
        """Download an episode to a file."""
        try:
            print(f"Downloading episode to: {filename}")
            response = requests.get(episode_url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\rProgress: {percent:.1f}%", end='', flush=True)

            print(f"\nDownload complete: {filename}")
            return True

        except requests.RequestException as e:
            print(f"Error downloading episode: {e}")
            return False
