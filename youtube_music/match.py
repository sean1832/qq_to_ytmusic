import difflib
import re
from typing import Dict, List, Optional


class Track:
    def __init__(
        self,
        title: str,
        artists: List[str],
        album: str,
        duration: int | str,
        type: Optional[str] = None,
        id: Optional[str] = None,
        isYT: bool = False,
        isTopResult: bool = False,
    ):
        self.title = title
        self.artists = artists
        self.album = album
        self.id = id
        self.type = type
        self.isYT = isYT
        self.isTopResult = isTopResult
        self.score = 0.0
        if isinstance(duration, str):
            self.duration = self._minutes_to_seconds(duration)
        else:
            self.duration = duration

    def _minutes_to_seconds(self, minutes_str: str) -> int:
        minutes, seconds = map(int, minutes_str.split(":"))
        return minutes * 60 + seconds

    def __str__(self) -> str:
        return f"Track(title: {self.title}, artists: {self.artists}, album: {self.album}, duration: {self.duration}, type:{self.type}, id: {self.id})"


class MusicMatcher:
    def __init__(
        self,
        tolerance: float = 0.3,
        duration_threshold: int = 3,
        top_result_multiplier: float = 1.2,
        special_keywords: Optional[List[str]] = [
            "instrumental",
            "remix",
            "live",
            "cover",
        ],
    ):
        """
        :param tolerance: Similarity tolerance for matching (0.0 to 1.0) higher = stricter
        :param duration_threshold: Allowed difference in duration between tracks (in seconds) higher = stricter
        :param top_result_multiplier: Multiplier for top result tracks to increase their similarity score
        :param special_keywords: List of keywords that should increase or decrease similarity scores.
        """
        self.tolerance = tolerance
        self.duration_threshold = duration_threshold
        self.top_result_multiplier = top_result_multiplier
        self.special_keywords = [
            keyword.lower() for keyword in special_keywords
        ]  # Normalize to lowercase
        self._skip = False  # flag to skip the current track

    def _normalize_string(self, s: str) -> str:
        """Normalize strings by stripping, lowering case, and removing special characters."""
        return re.sub(r"\s+", " ", s.strip().lower())

    def _clean_title(self, title: str) -> str:
        """Remove text inside parentheses or brackets unless they contain special keywords."""
        # Normalize title
        title_lower = title.lower()

        # Function to decide whether to keep or remove parentheses/brackets content
        def replace_func(match):
            content = match.group(0)  # Includes the parentheses/brackets
            inner_content = match.group(1)  # Inside the parentheses/brackets

            if inner_content and any(keyword in inner_content for keyword in self.special_keywords):
                return content  # Keep it if it contains a special keyword
            else:
                return ""  # Remove it if no special keyword is found

        # Adjusted pattern to capture inner content of parentheses or brackets
        pattern = re.compile(r"\((.*?)\)|\[(.*?)\]")
        title_cleaned = pattern.sub(replace_func, title_lower)
        return title_cleaned.strip()


        # Adjusted pattern to capture inner content
        pattern = re.compile(r"\((.*?)\)|\[(.*?)\]")
        title_cleaned = pattern.sub(replace_func, title_lower)
        return title_cleaned.strip()

    def _keyword_in_title(self, title: str) -> bool:
        """Check if any special keyword is present in the title, ignoring case."""
        title_lower = title.lower()  # Convert title to lowercase
        return any(keyword in title_lower for keyword in self.special_keywords)

    def _split_title(self, title: str) -> List[str]:
        """Splits the title into phrases, prioritizing quoted sections."""
        # Clean up irrelevant parts in parentheses or brackets
        title_cleaned = self._clean_title(title)

        # Extract content inside quotation marks (Japanese or English style)
        phrases = re.findall(r'"(.*?)"|「(.*?)」', title_cleaned)  # Handle both types of quotes
        if phrases:
            # Flatten list of phrases extracted from quotes
            phrases = [p for sublist in phrases for p in sublist if p]
        else:
            # Split by spaces and special characters if no quotes are found
            phrases = re.split(r"[\s\-\(\)]+", title_cleaned)

        # Normalize the phrases (lowercasing, etc.)
        return [self._normalize_string(p) for p in phrases if p]

    def _similar_strings(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings, adjusting score for keyword presence."""
        if str1 == str2:
            return 1.0

        # Split and clean both strings
        parts1 = self._split_title(str1)
        parts2 = self._split_title(str2)

        best_similarity = 0.0
        for part1 in parts1:
            for part2 in parts2:
                similarity = difflib.SequenceMatcher(None, part1, part2).ratio()
                best_similarity = max(best_similarity, similarity)

        # Adjust score based on keyword presence
        keyword_in_original = self._keyword_in_title(str1)
        keyword_in_candidate = self._keyword_in_title(str2)

        if keyword_in_candidate and not keyword_in_original:
            best_similarity = 0  # Set score to 0 if keyword is only in the candidate
            self._skip = True
        elif keyword_in_original and keyword_in_candidate:
            best_similarity *= 1.5  # Increase score if both have the same keyword

        if best_similarity < 0.3:  # threshold to return 0.0 for low similarity
            best_similarity = 0.0

        return best_similarity

    def _similar_duration(self, dur1: float, dur2: float) -> float:
        """
        Return a score between 0 and 1 based on how similar two durations are.
        A score of 1 means identical durations, and the score decreases as the
        difference increases, reaching 0 when the difference exceeds the threshold.
        """
        duration_difference = abs(dur1 - dur2)

        if duration_difference > self.duration_threshold:
            return 0.0  # Completely different if difference exceeds threshold

        # Calculate a score inversely proportional to the difference, normalized to [0, 1]
        return 1.0 - (duration_difference / self.duration_threshold)

    def _similar_artists(self, artists1: List[str], artists2: List[str]) -> float:
        """Calculate the similarity between two lists of artists."""
        best_similarity = 0.0
        for artist1 in artists1:
            for artist2 in artists2:
                similarity = self._similar_strings(artist1, artist2)
                best_similarity = max(best_similarity, similarity)
        return best_similarity

    def match_track_one_to_one(self, track1: Track, track2: Track) -> bool:
        """
        Match two tracks based on title, artists, album, and duration.
        The similarity of strings should be above the tolerance, and the duration score
        should contribute to the overall match decision.
        """
        title_similarity = self._similar_strings(track1.title, track2.title)
        artist_similarity = self._similar_artists(track1.artists, track2.artists)
        album_similarity = self._similar_strings(track1.album, track2.album)
        duration_similarity = self._similar_duration(track1.duration, track2.duration)
        if self._skip:
            self._skip = False
            return False
        # We can now also use the duration_similarity score (a float) in this logic
        return (
            title_similarity >= self.tolerance
            and artist_similarity >= self.tolerance
            and album_similarity >= self.tolerance
            and duration_similarity > 0.0  # Ensure some duration similarity
        )

    def match_tracks_one_to_many(self, track: Track, track_list: List[Track]) -> Optional[Track]:
        """
        Find the best match for a given track from a list of tracks.
        Returns the most similar track or None if no match is found.
        """
        best_match = None
        best_score = 0.0

        for candidate in track_list:
            title_similarity = (
                self._similar_strings(track.title, candidate.title) * 1.1  # title weight
            )
            artist_similarity = self._similar_artists(track.artists, candidate.artists)
            album_similarity = (
                self._similar_strings(track.album, candidate.album) * 1.5  # album weight
            )
            duration_similarity = (
                self._similar_duration(track.duration, candidate.duration) * 0.8  # duration weight
            )
            if self._skip:
                self._skip = False
                continue

            top_result_multiplier = self.top_result_multiplier if candidate.isTopResult else 1.0

            # Calculate an overall similarity score including duration similarity as a factor
            overall_similarity = (
                title_similarity + artist_similarity + album_similarity + duration_similarity
            ) / 4.0

            overall_similarity *= top_result_multiplier

            if overall_similarity >= self.tolerance:
                if overall_similarity > best_score:
                    best_score = overall_similarity
                    best_match = candidate
        if best_match:
            best_match.score = best_score
        return best_match

    def match_tracks_many_to_many(
        self, list1: List[Track], list2: List[Track]
    ) -> Dict[Track, Optional[Track]]:
        """
        Match tracks from two lists and return a dictionary of matched tracks.
        Keys are tracks from list1, and values are the best matches from list2.
        """
        matches = {}

        for track1 in list1:
            best_match = self.match_tracks_one_to_many(track1, list2)
            if best_match:
                matches[track1] = best_match

        return matches
