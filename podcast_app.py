#!/usr/bin/env python3
"""
Podcast Application - Subscribe to and listen to podcasts.

A simple command-line application for managing podcast subscriptions
and downloading episodes.
"""

import sys
import os
from podcast_manager import PodcastManager


def print_help():
    """Print usage information."""
    help_text = """
Podcast Application - Manage your podcast subscriptions

Usage: python podcast_app.py <command> [arguments]

Commands:
  subscribe <feed_url>           Subscribe to a podcast feed
  unsubscribe <podcast_title>    Unsubscribe from a podcast
  list                           List all subscribed podcasts
  episodes <podcast_title>       Show recent episodes for a podcast
  download <episode_number>      Download an episode (use after 'episodes')
  help                           Show this help message

Examples:
  python podcast_app.py subscribe https://feeds.example.com/podcast.rss
  python podcast_app.py list
  python podcast_app.py episodes "My Favorite Podcast"
  python podcast_app.py download 1

Note: Use quotes around podcast titles with spaces.
"""
    print(help_text)


class PodcastApp:
    """Main application class."""

    def __init__(self):
        self.manager = PodcastManager()
        self.last_episodes = []

    def run(self, args):
        """Run the application with command-line arguments."""
        if len(args) < 1:
            print("Error: No command provided.")
            print_help()
            return 1

        command = args[0].lower()

        if command == 'subscribe':
            if len(args) < 2:
                print("Error: Feed URL required.")
                print("Usage: python podcast_app.py subscribe <feed_url>")
                return 1
            self.manager.subscribe(args[1])

        elif command == 'unsubscribe':
            if len(args) < 2:
                print("Error: Podcast title required.")
                print("Usage: python podcast_app.py unsubscribe <podcast_title>")
                return 1
            self.manager.unsubscribe(args[1])

        elif command == 'list':
            self.list_podcasts()

        elif command == 'episodes':
            if len(args) < 2:
                print("Error: Podcast title required.")
                print("Usage: python podcast_app.py episodes <podcast_title>")
                return 1
            limit = int(args[2]) if len(args) > 2 else 10
            self.show_episodes(args[1], limit)

        elif command == 'download':
            if len(args) < 2:
                print("Error: Episode number required.")
                print("Usage: python podcast_app.py download <episode_number>")
                return 1
            try:
                episode_num = int(args[1])
                self.download_episode(episode_num)
            except ValueError:
                print("Error: Episode number must be an integer.")
                return 1

        elif command == 'help':
            print_help()

        else:
            print(f"Error: Unknown command '{command}'")
            print_help()
            return 1

        return 0

    def list_podcasts(self):
        """List all subscribed podcasts."""
        subscriptions = self.manager.list_subscriptions()

        if not subscriptions:
            print("No podcast subscriptions found.")
            print("Use 'subscribe' command to add a podcast.")
            return

        print(f"\n{'='*60}")
        print(f"Subscribed Podcasts ({len(subscriptions)})")
        print(f"{'='*60}\n")

        for i, podcast in enumerate(subscriptions, 1):
            print(f"{i}. {podcast.title}")
            if podcast.author:
                print(f"   Author: {podcast.author}")
            print(f"   Description: {podcast.description[:100]}...")
            print(f"   Feed: {podcast.feed_url}")
            print()

    def show_episodes(self, podcast_title: str, limit: int = 10):
        """Show episodes for a podcast."""
        episodes = self.manager.get_episodes(podcast_title, limit)

        if not episodes:
            return

        self.last_episodes = episodes

        print(f"\n{'='*60}")
        print(f"Recent Episodes: {podcast_title}")
        print(f"{'='*60}\n")

        for i, episode in enumerate(episodes, 1):
            print(f"{i}. {episode.title}")
            print(f"   Published: {episode.pub_date}")
            if episode.duration:
                print(f"   Duration: {episode.duration}")
            print(f"   Description: {episode.description[:150]}...")
            print()

        print("To download an episode, use:")
        print(f"python podcast_app.py download <episode_number>")
        print()

    def download_episode(self, episode_num: int):
        """Download an episode."""
        if not self.last_episodes:
            print("Error: No episodes loaded.")
            print("Use 'episodes' command first to see available episodes.")
            return

        if episode_num < 1 or episode_num > len(self.last_episodes):
            print(f"Error: Invalid episode number. Choose 1-{len(self.last_episodes)}")
            return

        episode = self.last_episodes[episode_num - 1]

        # Create downloads directory
        os.makedirs('downloads', exist_ok=True)

        # Generate filename
        safe_title = "".join(c for c in episode.title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')
        filename = f"downloads/{safe_title}.mp3"

        # Avoid overwriting existing files
        counter = 1
        while os.path.exists(filename):
            filename = f"downloads/{safe_title}_{counter}.mp3"
            counter += 1

        self.manager.download_episode(episode.url, filename)


def main():
    """Main entry point."""
    app = PodcastApp()
    sys.exit(app.run(sys.argv[1:]))


if __name__ == '__main__':
    main()
