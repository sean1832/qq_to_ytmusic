# Modified by: @sean1832
# From the original source:
# https://github.com/sigma67/spotify_to_ytmusic/blob/main/spotify_to_ytmusic/ytmusic.py
import re
from collections import OrderedDict
from typing import List

from match import get_best_fit_song_id
from ytmusicapi import YTMusic


class TYMusicOp:
    def __init__(self, oauth_path):
        self.api = YTMusic(oauth_path)

    def create_playlist(self, name, info="", privacy="PRIVATE", tracks=None):
        return self.api.create_playlist(name, info, privacy, video_ids=tracks)

    def search_songs(self, tracks: List[dict]):
        videoIds = []
        songs = list(tracks)
        notFound = list()
        print("Searching YouTube...")
        for i, song in enumerate(songs):
            name = re.sub(r" \(feat.*\..+\)", "", song["name"])
            artists = song["artists"]
            joinedArtists = " ".join(artists)
            query = joinedArtists + " " + name
            query = query.replace(" &", "")
            result = self.api.search(query)
            if len(result) == 0:
                notFound.append(query)
            else:
                targetSong = get_best_fit_song_id(result, song)
                if targetSong is None:
                    notFound.append(query)
                else:
                    videoIds.append(targetSong)

            if i > 0 and i % 10 == 0:
                print(f"YouTube tracks: {i}/{len(songs)}")
        if len(notFound) > 0:
            print("===============WARNING==============")
            print("No results found for the following songs:")
            print("\n ".join(notFound))
            print("===============WARNING==============")
            with open("noresults_youtube.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(notFound))
                f.write("\n")

        return videoIds

    def add_playlist_items(self, playlistId, videoIds):
        videoIds = OrderedDict.fromkeys(videoIds)
        self.api.add_playlist_items(playlistId, videoIds)
        print(str(len(videoIds)) + " songs added to playlist.")

    def get_playlist_id(self, name):
        pl = self.api.get_library_playlists(10000)
        try:
            playlist = next(x for x in pl if x["title"].find(name) != -1)["playlistId"]
            return playlist
        except StopIteration:
            raise ValueError("Playlist title not found in playlists")

    def remove_songs(self, playlistId):
        items = self.api.get_playlist(playlistId, 10000)
        if "tracks" in items:
            self.api.remove_playlist_items(playlistId, items["tracks"])

    def remove_playlists(self, pattern):
        playlists = self.api.get_library_playlists(10000)
        p = re.compile("{0}".format(pattern))
        matches = [pl for pl in playlists if p.match(pl["title"])]
        print("The following playlists will be removed:")
        print("\n".join([pl["title"] for pl in matches]))
        print("Please confirm (y/n):")

        choice = input().lower()
        if choice[:1] == "y":
            [self.api.delete_playlist(pl["playlistId"]) for pl in matches]
            print(str(len(matches)) + " playlists deleted.")
        else:
            print("Aborted. No playlists were deleted.")
