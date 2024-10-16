# Modified by: @sean1832
# From the original source:
# https://github.com/sigma67/spotify_to_ytmusic/blob/main/spotify_to_ytmusic/ytmusic.py
import datetime
import json
import re
from collections import OrderedDict
from typing import List, Optional

from match import MusicMatcher, Track
from utils.terminal_col import Color, TermCol
from ytmusicapi import YTMusic


class TYMusicOp:
    def __init__(self, oauth_path: str, language: str = "en"):
        self.api = YTMusic(oauth_path, language=language)

    def create_playlist(
        self,
        name: str,
        description: str = "",
        privacy: str = "PRIVATE",
        tracks: Optional[List[str]] = None,
    ) -> str:
        """
        Create a YouTube Music playlist.
        """
        return self.api.create_playlist(name, description, privacy, video_ids=tracks)

    def search_songs(
        self, external_tracks: List[dict], tolerance: float, playlist_name: str
    ) -> List[str]:
        """
        Search YouTube Music for external tracks and return their video IDs.
        First, perform a simple query (track title only). If no match is found,
        perform a detailed query (track title and artist names).
        """
        video_ids = []
        not_found_tracks = []
        total_tracks = len(external_tracks)

        print("Searching YouTube...")

        for index, track in enumerate(external_tracks):
            external_track = self._build_external_track(track)
            matched_track = None

            # Try simple query first
            query = self._build_query(track, query_type="detailed")
            yt_results = self.api.search(query)

            # # Save results for debugging
            # with open(f"yt_results_{track['name']}_detail.json", "w", encoding="utf-8") as f:
            #     f.write(json.dumps(yt_results, indent=4, ensure_ascii=False))

            if yt_results:
                yt_tracks = self._extract_yt_tracks(yt_results)
                matched_track = self._find_best_match(external_track, yt_tracks, tolerance)
                if matched_track:
                    print(
                        f"[{index+1}/{total_tracks}] Matched (detail query): {external_track.title} -> {matched_track.title} (ytid: {matched_track.id}) (score: {matched_track.score})"
                    )
                    video_ids.append(matched_track.id)
                    continue  # Proceed to the next track

            # If no match with detail query, try simple query
            query = self._build_query(track, query_type="simple")
            yt_results = self.api.search(query)

            # # Save results for debugging
            # with open(f"yt_results_{track['name']}_simple.json", "w", encoding="utf-8") as f:
            #     f.write(json.dumps(yt_results, indent=4, ensure_ascii=False))

            if yt_results:
                yt_tracks = self._extract_yt_tracks(yt_results)
                matched_track = self._find_best_match(external_track, yt_tracks, tolerance)
                if matched_track:
                    print(
                        f"[{index+1}/{total_tracks}] Matched (simple query): {external_track.title} -> {matched_track.title} (ytid: {matched_track.id}) (score: {matched_track.score})"
                    )
                    video_ids.append(matched_track.id)
                    continue  # Proceed to the next track

            # If still no match found
            TermCol.print(
                f"[{index+1}/{total_tracks}] Failed: {external_track.title}",
                Color.YELLOW,
            )
            track["query"] = query
            track["end_reason"] = "No match found after detail and simple queries"
            not_found_tracks.append(track)

        self._handle_not_found_tracks(not_found_tracks, playlist_name)

        return video_ids

    def add_playlist_items(self, playlist_id: str, video_ids: List[str]):
        """
        Add songs to an existing YouTube Music playlist.
        """
        unique_video_ids = list(OrderedDict.fromkeys(video_ids))
        self.api.add_playlist_items(playlist_id, unique_video_ids)
        print(f"{len(unique_video_ids)} songs added to playlist.")

    def get_playlist_id(self, name: str) -> str:
        """
        Retrieve the playlist ID by name.
        """
        playlists = self.api.get_library_playlists(10000)
        for playlist in playlists:
            if name in playlist["title"]:
                return playlist["playlistId"]
        raise ValueError(f"Playlist '{name}' not found.")

    def remove_songs(self, playlist_id: str):
        """
        Remove all songs from a given playlist.
        """
        playlist_items = self.api.get_playlist(playlist_id, 10000)
        if "tracks" in playlist_items:
            self.api.remove_playlist_items(playlist_id, playlist_items["tracks"])

    def remove_playlists_by_pattern(self, pattern: str):
        """
        Remove all playlists that match a given pattern.
        """
        playlists = self.api.get_library_playlists(10000)
        matching_playlists = [pl for pl in playlists if re.match(pattern, pl["title"])]

        if not matching_playlists:
            print("No playlists matched the pattern.")
            return

        print("The following playlists will be removed:")
        print("\n".join([pl["title"] for pl in matching_playlists]))

        confirmation = input("Please confirm (y/n): ").lower()
        if confirmation.startswith("y"):
            for playlist in matching_playlists:
                self.api.delete_playlist(playlist["playlistId"])
            print(f"{len(matching_playlists)} playlists deleted.")
        else:
            print("Aborted. No playlists were deleted.")

    def remove_playlists(self, playlist_id: str):
        """Remove a playlist by its ID."""
        print(f"Deleting playlist with ID: {playlist_id}")
        confirmation = input("Please confirm (y/n): ").lower()
        if confirmation.startswith("y"):
            self.api.delete_playlist(playlist_id)
            print(f"Playlist with ID {playlist_id} deleted.")

    def _build_query(self, track: dict, query_type: str = "detailed") -> str:
        """
        Build a search query from the external track data.
        The query_type parameter determines the type of query:
        - 'simple': search by track title only
        - 'detailed': search by track title and artist names
        """
        # Remove text inside parentheses for the track name (feat. artists)
        track_name = re.sub(r" \(feat.*\..+\)", "", track["name"])

        if query_type == "simple":
            # Simple query: only the track name
            return track_name
        elif query_type == "detailed":
            # Remove any content inside brackets from artist names
            clean_artists = [
                re.sub(r"\s*\(.*?\)", "", artist).strip() for artist in track["artists"]
            ]

            # Remove special characters but keep Unicode letters, digits, and spaces
            clean_artists = [
                re.sub(r"[^\w\s]", "", artist, flags=re.UNICODE) for artist in clean_artists
            ]

            # Join artists' names and remove any "&" symbols
            artists = " ".join(clean_artists).replace(" &", "")

            # Combine track name and artist names into a search query
            return f"{track_name} {artists}"
        else:
            raise ValueError(f"Unknown query_type: {query_type}")

    def _extract_yt_tracks(self, yt_results: List[dict]) -> List[Track]:
        """
        Extract valid YouTube tracks from search results.
        """
        yt_tracks = []
        for result in yt_results:
            if result.get("resultType") not in ["song", "video"]:
                continue

            yt_track = Track(
                title=result.get("title", ""),
                artists=[artist["name"] for artist in result.get("artists", [])],
                album=result.get("album", {}).get("name", ""),
                duration=result.get("duration_seconds", 0),
                type=result.get("resultType"),
                id=result.get("videoId"),
                isYT=True,
                isTopResult=result.get("category") == "Top result"
                or result.get("category") == "上位の検索結果",
            )
            yt_tracks.append(yt_track)

        return yt_tracks

    def _build_external_track(self, track: dict) -> Track:
        """
        Build a Track object from external track data.
        """
        return Track(
            title=track["name"],
            artists=track["artists"],
            album=track["album"],
            duration=track["duration"],
        )

    def _find_best_match(
        self, external_track: Track, yt_tracks: List[Track], tolerance: float
    ) -> Optional[Track]:
        """
        Use the MusicMatcher to find the best matching YouTube track for an external track.
        """
        matcher = MusicMatcher(tolerance=tolerance)
        match = matcher.match_tracks_one_to_many(external_track, yt_tracks)
        return match

    def _handle_not_found_tracks(self, not_found_tracks: List[dict], playlist_name: str):
        """
        Handle tracks that were not found on YouTube Music.
        """
        if not not_found_tracks:
            return

        not_found_query = [track["query"] for track in not_found_tracks]

        print("")
        TermCol.print("===============WARNING==============", Color.YELLOW)
        TermCol.print(
            f"No results found for the following queries ({len(not_found_query)}):", Color.YELLOW
        )
        TermCol.print("\n".join(not_found_query), Color.YELLOW)
        TermCol.print("===============WARNING==============", Color.YELLOW)

        data = {
            "name": playlist_name,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "songs": not_found_tracks,
        }

        with open(f"noresults_yt_{playlist_name}.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(data, indent=4, ensure_ascii=False))
