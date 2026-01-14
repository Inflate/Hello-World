# Podcast Application

A podcast management application available in both graphical (GUI) and command-line (CLI) interfaces. Subscribe to podcasts, browse episodes, and download audio files with ease.

## Features

- **Two Interfaces**: Choose between a user-friendly GUI or powerful CLI
- **Subscribe to podcasts**: Add podcasts using their RSS feed URLs
- **Manage subscriptions**: View all subscribed podcasts and unsubscribe when needed
- **Browse episodes**: View recent episodes for any subscribed podcast
- **Download episodes**: Download podcast episodes to listen offline with progress tracking
- **Persistent storage**: Your subscriptions are saved automatically
- **Episode details**: View descriptions and metadata for each episode

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd Hello-World
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Graphical Interface (GUI)

For a user-friendly graphical interface, run:

```bash
python podcast_gui.py
```

The GUI provides:
- **Left Panel**: Subscribe to new podcasts and view your subscription list
- **Right Panel**: Browse episodes and view detailed descriptions
- **Download Manager**: Download episodes with a single click

Simply paste a podcast feed URL, click Subscribe, then select podcasts and episodes from the lists.

### Command-Line Interface (CLI)

For command-line usage, use `podcast_app.py`:

#### Subscribe to a Podcast

```bash
python podcast_app.py subscribe <feed_url>
```

Example:
```bash
python podcast_app.py subscribe https://feeds.npr.org/510318/podcast.xml
```

### List Your Subscriptions

```bash
python podcast_app.py list
```

### View Episodes

```bash
python podcast_app.py episodes "Podcast Title"
```

You can optionally specify the number of episodes to show:
```bash
python podcast_app.py episodes "Podcast Title" 20
```

### Download an Episode

First, view the episodes, then download by number:
```bash
python podcast_app.py episodes "Podcast Title"
python podcast_app.py download 1
```

Episodes are downloaded to the `downloads/` directory.

### Unsubscribe from a Podcast

```bash
python podcast_app.py unsubscribe "Podcast Title"
```

### Get Help

```bash
python podcast_app.py help
```

## Popular Podcast Feeds

Here are some popular podcast RSS feeds to get started:

- **NPR News Now**: https://feeds.npr.org/500005/podcast.xml
- **The Daily (NY Times)**: https://feeds.simplecast.com/54nAGcIl
- **Radiolab**: https://feeds.wnyc.org/radiolab
- **99% Invisible**: https://feeds.99percentinvisible.org/99percentinvisible
- **Planet Money**: https://feeds.npr.org/510289/podcast.xml

## File Structure

```
podcast_gui.py         # Graphical user interface (GUI)
podcast_app.py         # Command-line interface (CLI)
podcast_manager.py     # Core podcast management logic
models.py              # Data models for podcasts and episodes
requirements.txt       # Python dependencies
subscriptions.json     # Your saved subscriptions (auto-generated)
downloads/             # Downloaded episodes (auto-generated)
```

## Requirements

- Python 3.6 or higher
- Tkinter (included with most Python installations)
- Internet connection for fetching feeds and downloading episodes

## How It Works

1. **Feed Parsing**: Uses the `feedparser` library to parse RSS feeds from podcast providers
2. **Storage**: Subscriptions are stored locally in a JSON file
3. **Downloads**: Episodes are downloaded using streaming requests to handle large audio files efficiently

## Troubleshooting

**Problem**: "Invalid feed URL or unable to parse feed"
- Ensure the URL is a valid RSS feed (not a website URL)
- Check your internet connection
- Some feeds may have access restrictions

**Problem**: Episode download fails
- The audio file URL may be expired or restricted
- Check your internet connection
- Try a different episode

## License

This project is open source and available for educational purposes.
