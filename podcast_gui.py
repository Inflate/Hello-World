#!/usr/bin/env python3
"""
Podcast Application GUI - Graphical interface for podcast management.

A user-friendly desktop application for managing podcast subscriptions
and downloading episodes.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os
from podcast_manager import PodcastManager
from models import Podcast, Episode


class PodcastGUI:
    """Main GUI application class."""

    def __init__(self, root):
        self.root = root
        self.root.title("Podcast Manager")
        self.root.geometry("900x600")

        self.manager = PodcastManager()
        self.current_episodes = []
        self.selected_podcast = None

        self.setup_ui()
        self.refresh_podcast_list()

    def setup_ui(self):
        """Set up the user interface."""
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Left panel - Podcast list
        self.setup_podcast_panel(main_frame)

        # Right panel - Episode list
        self.setup_episode_panel(main_frame)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))

    def setup_podcast_panel(self, parent):
        """Set up the left panel with podcast list."""
        # Podcast panel
        podcast_frame = ttk.LabelFrame(parent, text="Subscribed Podcasts", padding="5")
        podcast_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        podcast_frame.columnconfigure(0, weight=1)
        podcast_frame.rowconfigure(1, weight=1)

        # Subscribe section
        subscribe_frame = ttk.Frame(podcast_frame)
        subscribe_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        subscribe_frame.columnconfigure(0, weight=1)

        ttk.Label(subscribe_frame, text="Feed URL:").grid(row=0, column=0, sticky=tk.W)

        self.feed_url_var = tk.StringVar()
        feed_entry = ttk.Entry(subscribe_frame, textvariable=self.feed_url_var)
        feed_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(2, 5))

        subscribe_btn = ttk.Button(subscribe_frame, text="Subscribe", command=self.subscribe_podcast)
        subscribe_btn.grid(row=2, column=0, sticky=(tk.W, tk.E))

        # Podcast listbox
        listbox_frame = ttk.Frame(podcast_frame)
        listbox_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        self.podcast_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, width=30)
        self.podcast_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.podcast_listbox.bind('<<ListboxSelect>>', self.on_podcast_select)

        scrollbar.config(command=self.podcast_listbox.yview)

        # Unsubscribe button
        unsubscribe_btn = ttk.Button(podcast_frame, text="Unsubscribe", command=self.unsubscribe_podcast)
        unsubscribe_btn.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

    def setup_episode_panel(self, parent):
        """Set up the right panel with episode list and details."""
        # Episode panel
        episode_frame = ttk.LabelFrame(parent, text="Episodes", padding="5")
        episode_frame.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        episode_frame.columnconfigure(0, weight=1)
        episode_frame.rowconfigure(1, weight=1)

        # Podcast info
        self.podcast_info_var = tk.StringVar(value="Select a podcast to view episodes")
        info_label = ttk.Label(episode_frame, textvariable=self.podcast_info_var,
                              wraplength=500, justify=tk.LEFT)
        info_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        # Episode list with Treeview
        tree_frame = ttk.Frame(episode_frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Treeview for episodes
        self.episode_tree = ttk.Treeview(tree_frame, columns=("date", "duration"),
                                        yscrollcommand=vsb.set, selectmode="browse")
        self.episode_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.config(command=self.episode_tree.yview)

        # Configure columns
        self.episode_tree.heading("#0", text="Episode Title")
        self.episode_tree.heading("date", text="Published")
        self.episode_tree.heading("duration", text="Duration")

        self.episode_tree.column("#0", width=300)
        self.episode_tree.column("date", width=150)
        self.episode_tree.column("duration", width=80)

        self.episode_tree.bind('<<TreeviewSelect>>', self.on_episode_select)

        # Episode details
        details_frame = ttk.LabelFrame(episode_frame, text="Episode Details", padding="5")
        details_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        details_frame.columnconfigure(0, weight=1)

        self.episode_details = scrolledtext.ScrolledText(details_frame, height=6, wrap=tk.WORD)
        self.episode_details.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.episode_details.config(state=tk.DISABLED)

        # Download button
        self.download_btn = ttk.Button(episode_frame, text="Download Selected Episode",
                                       command=self.download_episode, state=tk.DISABLED)
        self.download_btn.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

    def refresh_podcast_list(self):
        """Refresh the podcast listbox."""
        self.podcast_listbox.delete(0, tk.END)
        subscriptions = self.manager.list_subscriptions()

        for podcast in subscriptions:
            self.podcast_listbox.insert(tk.END, podcast.title)

        self.status_var.set(f"Loaded {len(subscriptions)} podcasts")

    def subscribe_podcast(self):
        """Subscribe to a new podcast."""
        feed_url = self.feed_url_var.get().strip()

        if not feed_url:
            messagebox.showwarning("Input Required", "Please enter a feed URL")
            return

        self.status_var.set("Subscribing to podcast...")
        self.root.update()

        # Run in thread to avoid blocking UI
        def subscribe_thread():
            try:
                success = self.manager.subscribe(feed_url)

                # Update UI in main thread
                self.root.after(0, lambda: self.after_subscribe(success))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to subscribe: {str(e)}"))
                self.root.after(0, lambda: self.status_var.set("Ready"))

        threading.Thread(target=subscribe_thread, daemon=True).start()

    def after_subscribe(self, success):
        """Handle post-subscription UI updates."""
        if success:
            self.feed_url_var.set("")
            self.refresh_podcast_list()
            self.status_var.set("Successfully subscribed!")
        else:
            self.status_var.set("Ready")

    def unsubscribe_podcast(self):
        """Unsubscribe from selected podcast."""
        selection = self.podcast_listbox.curselection()

        if not selection:
            messagebox.showwarning("No Selection", "Please select a podcast to unsubscribe")
            return

        podcast_title = self.podcast_listbox.get(selection[0])

        result = messagebox.askyesno("Confirm Unsubscribe",
                                    f"Are you sure you want to unsubscribe from '{podcast_title}'?")

        if result:
            self.manager.unsubscribe(podcast_title)
            self.refresh_podcast_list()
            self.clear_episode_list()
            self.status_var.set(f"Unsubscribed from {podcast_title}")

    def on_podcast_select(self, event):
        """Handle podcast selection."""
        selection = self.podcast_listbox.curselection()

        if not selection:
            return

        podcast_title = self.podcast_listbox.get(selection[0])
        self.selected_podcast = podcast_title

        # Find podcast details
        podcast = next((p for p in self.manager.list_subscriptions() if p.title == podcast_title), None)

        if podcast:
            info_text = f"{podcast.title}\n"
            if podcast.author:
                info_text += f"By: {podcast.author}\n"
            info_text += f"{podcast.description[:200]}..."
            self.podcast_info_var.set(info_text)

        self.load_episodes(podcast_title)

    def load_episodes(self, podcast_title):
        """Load episodes for selected podcast."""
        self.status_var.set("Loading episodes...")
        self.root.update()

        def load_thread():
            try:
                episodes = self.manager.get_episodes(podcast_title, limit=20)
                self.current_episodes = episodes

                # Update UI in main thread
                self.root.after(0, lambda: self.display_episodes(episodes))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load episodes: {str(e)}"))
                self.root.after(0, lambda: self.status_var.set("Ready"))

        threading.Thread(target=load_thread, daemon=True).start()

    def display_episodes(self, episodes):
        """Display episodes in the treeview."""
        # Clear existing items
        for item in self.episode_tree.get_children():
            self.episode_tree.delete(item)

        # Add episodes
        for i, episode in enumerate(episodes):
            duration = episode.duration if episode.duration else "N/A"
            self.episode_tree.insert("", tk.END, text=episode.title,
                                    values=(episode.pub_date, duration),
                                    tags=(str(i),))

        self.status_var.set(f"Loaded {len(episodes)} episodes")

    def on_episode_select(self, event):
        """Handle episode selection."""
        selection = self.episode_tree.selection()

        if not selection:
            return

        item = self.episode_tree.item(selection[0])
        tags = self.episode_tree.item(selection[0], 'tags')

        if tags:
            episode_idx = int(tags[0])
            episode = self.current_episodes[episode_idx]

            # Display episode details
            self.episode_details.config(state=tk.NORMAL)
            self.episode_details.delete(1.0, tk.END)
            self.episode_details.insert(1.0, episode.description)
            self.episode_details.config(state=tk.DISABLED)

            # Enable download button
            self.download_btn.config(state=tk.NORMAL)

    def download_episode(self):
        """Download selected episode."""
        selection = self.episode_tree.selection()

        if not selection:
            messagebox.showwarning("No Selection", "Please select an episode to download")
            return

        tags = self.episode_tree.item(selection[0], 'tags')
        if not tags:
            return

        episode_idx = int(tags[0])
        episode = self.current_episodes[episode_idx]

        # Create downloads directory
        os.makedirs('downloads', exist_ok=True)

        # Generate filename
        safe_title = "".join(c for c in episode.title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')
        filename = f"downloads/{safe_title}.mp3"

        # Avoid overwriting
        counter = 1
        while os.path.exists(filename):
            filename = f"downloads/{safe_title}_{counter}.mp3"
            counter += 1

        # Disable button during download
        self.download_btn.config(state=tk.DISABLED)

        def download_thread():
            try:
                self.root.after(0, lambda: self.status_var.set(f"Downloading {episode.title}..."))
                success = self.manager.download_episode(episode.url, filename)

                if success:
                    self.root.after(0, lambda: messagebox.showinfo("Download Complete",
                                                                    f"Episode downloaded to:\n{filename}"))
                    self.root.after(0, lambda: self.status_var.set("Download complete"))
                else:
                    self.root.after(0, lambda: self.status_var.set("Download failed"))

            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Download Error", str(e)))
                self.root.after(0, lambda: self.status_var.set("Download failed"))
            finally:
                self.root.after(0, lambda: self.download_btn.config(state=tk.NORMAL))

        threading.Thread(target=download_thread, daemon=True).start()

    def clear_episode_list(self):
        """Clear the episode list."""
        for item in self.episode_tree.get_children():
            self.episode_tree.delete(item)

        self.episode_details.config(state=tk.NORMAL)
        self.episode_details.delete(1.0, tk.END)
        self.episode_details.config(state=tk.DISABLED)

        self.podcast_info_var.set("Select a podcast to view episodes")
        self.download_btn.config(state=tk.DISABLED)
        self.current_episodes = []


def main():
    """Main entry point."""
    root = tk.Tk()
    app = PodcastGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
