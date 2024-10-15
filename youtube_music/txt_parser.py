import json
import os
from enum import Enum


class FileType(Enum):
    PLAINTEXT = 0
    JSON = 1


class TxtParser:
    def __init__(self, txt_file: str, file_type: FileType):
        self.txt_file: str = txt_file
        self.file_type: FileType = file_type

    def parse(self):
        if self.file_type == FileType.JSON:
            return self._parse_json()
        elif self.file_type == FileType.PLAINTEXT:
            return self._parse_plaintext()
        else:
            raise ValueError(f"Invalid file type: {self.file_type}")

    def to_json(self, parsed_data: dict, output_file: str):
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(parsed_data, indent=4))

    def _parse_json(self):
        with open(self.txt_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    def _parse_plaintext(self) -> dict:
        playlist_name = os.path.basename(self.txt_file).split(".")[0]
        songs = []
        with open(self.txt_file, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()

        for line in lines:
            if line:
                song_seg = line.split(" - ")
                if len(song_seg) != 2:
                    print(f"Invalid song format: {self.txt_file}: {line}")
                    continue
                songs.append(
                    {
                        "name": song_seg[0],
                        "artist": song_seg[1],
                    }
                )

        return {"name": playlist_name, "songs": songs}