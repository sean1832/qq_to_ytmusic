# Modified by: @sean1832
# From the original source:
# https://github.com/sigma67/spotify_to_ytmusic/blob/main/spotify_to_ytmusic/utils/match.py

import difflib
from typing import Dict, List


def get_best_fit_song_id(ytm_results: List[Dict], external_tracks: List[Dict]) -> str | None:
    """
    Find the best match for track spoti in a list of ytmusicapi results

    :param ytm_results: List of ytmusicapi search results
    :param external_tracks: external track
    :return: videoId of best matching result
    """
    match_score = {}
    title_score = {}
    for ytm in ytm_results:
        if (
            "resultType" not in ytm
            or ytm["resultType"] not in ["song", "video"]
            or not ytm["title"]
        ):
            continue

        duration_match_score = None
        if "duration" in ytm and ytm["duration"] and external_tracks["duration"]:
            # convert duration to seconds
            duration_items = ytm["duration"].split(":")
            duration_sec = int(duration_items[0]) * 60 + int(duration_items[1])
            duration_match_score = (
                1
                - abs(duration_sec - external_tracks["duration"]) * 2 / external_tracks["duration"]
            )

        title = ytm["title"]
        # for videos,
        if ytm["resultType"] == "video":
            title_split = title.split("-")
            if len(title_split) == 2:
                title = title_split[1]

        artists = " ".join([a["name"] for a in ytm["artists"]])

        title_score[ytm["videoId"]] = difflib.SequenceMatcher(
            a=title.lower(), b=external_tracks["name"].lower()
        ).ratio()

        # get artist with highest score
        artist_scores = []
        for artist in external_tracks["artists"]:
            artist_score = difflib.SequenceMatcher(a=artists.lower(), b=artist.lower()).ratio()
            artist_scores.append(artist_score)
        artist_score_max = max(artist_scores)

        # calculate score
        scores = [
            title_score[ytm["videoId"]],
            artist_score_max,
        ]
        if duration_match_score:
            scores.append(duration_match_score * 5)

        # add album for songs only
        if ytm["resultType"] == "song" and ytm.get("album", None) is not None:
            scores.append(
                difflib.SequenceMatcher(
                    a=ytm["album"]["name"].lower(), b=external_tracks["album"].lower()
                ).ratio()
            )

        match_score[ytm["videoId"]] = (
            sum(scores) / len(scores) * max(1, int(ytm["resultType"] == "song") * 2)
        )

    if len(match_score) == 0:
        return None

    max_score_video_id = max(match_score, key=match_score.get)

    return max_score_video_id
