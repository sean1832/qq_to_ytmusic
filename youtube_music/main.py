# Read json files from data/qqmusic-raw and search for the corresponding songs on YouTube Music
# and add them to the playlist with the same name.
import os
from typing import List
import json

from ytm_ops import TYMusicOp


def scan_files(dir: str):
    files = []
    for root, _, filenames in os.walk(dir):
        for filename in filenames:
            if filename.endswith(".json"):
                files.append(os.path.join(root, filename))
    return files

def read_json(file: str):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    # >> Change this to the directory where your JSON files are stored. Default is "data/qqmusic-raw"
    files = scan_files("data/qqmusic-raw")
    print(f"Found {len(files)} files.")

    for file in files:
        qq_data = read_json(file)
        tracks: List[dict] = qq_data["songs"]
        playlist_name: str = qq_data["name"]
        print(f"Processing: {playlist_name}")

        yt_op = TYMusicOp("oauth.json")
        video_ids = yt_op.search_songs(tracks)

        # Search for existing playlist if exists
        playlist_id = None
        try:
            playlist_id = yt_op.get_playlist_id(playlist_name)
            print(f"Playlist '{playlist_name}' found. Appending songs...")
        except ValueError:
            print(f"Playlist {playlist_name} not found. Creating new playlist...")
            playlist_id = yt_op.create_playlist(playlist_name)

        yt_op.add_playlist_items(playlist_id, video_ids)
        print(f"Playlist '{playlist_name}' updated.")

    print("All playlists updated.")
