# Merge multiple playlists into a single playlist.
# This is useful when you want to merge multiple playlists into a single playlist before uploading to YouTube Music.
import json
import os


class JoinJSON:
    def __init__(self, json_files: list, new_playlist_name: str, dir: str = "."):
        self.json_files: list = json_files
        self.output_file: str = os.path.join(dir, f"{new_playlist_name}.json")
        self.new_playlist_name: str = new_playlist_name

    def join(self):
        result_songs = []
        ids = []
        for file in self.json_files:
            data = self._parse_json(file)
            ids.append(data.get("id"))
            songs = data.get("songs")
            for song in songs:
                if song not in result_songs:
                    result_songs.append(song)
                    print(song)

        return {"name": self.new_playlist_name, "id": ids, "songs": result_songs}

    def to_json(self, data: dict):
        if not os.path.exists(os.path.dirname(self.output_file)):
            os.makedirs(os.path.dirname(self.output_file))
        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, indent=4))

    def _parse_json(self, file):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data


if __name__ == "__main__":
    files = [
        "data/qqmusic-raw/「ACG神曲」动漫中二魂不灭！.json",
        "data/qqmusic-raw/注入灵魂丨B站大佬们的宝藏歌曲.json",
    ]
    joiner = JoinJSON(files, "anime", "data/qqmusic-joined")
    data = joiner.join()
    joiner.to_json(data)
    print(f"Joined playlists: {files} to {joiner.output_file}")
