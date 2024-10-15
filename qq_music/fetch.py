# Fetch QQ Music playlist data and save it as JSON files.

# Modified by: @sean1832
# From the original source:
# https://github.com/loikein/qq_music_list/blob/master/export.py
import json
import os
import re
import time

import requests


class QQMusicList:
    def __init__(self, id):
        self.id = id
        self.headers = {
            "user-agent": "Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.170816.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Mobile Safari/537.36",
            "referer": f"https://y.qq.com/w/taoge.html?ADTAG=profile_h5&id={self.id}",
        }
        self.session = requests.Session()

    def total_song_num(self):
        url = "https://y.qq.com/n/m/detail/taoge/index.html"
        params = {"ADTAG": "profile_h5", "id": self.id}
        method = "GET"
        resp = self.session.request(method, url, params=params, headers=self.headers, timeout=10)
        if resp.status_code != 200:
            print("get song num error.")
            return 0
        total_song_num = re.search(r"共(\d+)首", resp.text).group(1)
        if not isinstance(total_song_num, int):
            total_song_num = int(total_song_num)
        return total_song_num

    def get_list(self, song_num=15):
        song_list = []
        url = "https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg"
        params = {"_": int(time.time() * 1000)}
        method = "POST"
        postdata = {
            "format": "json",
            "inCharset": "utf-8",
            "outCharset": "utf-8",
            "notice": "0",
            "platform": "h5",
            "needNewCode": "1",
            "new_format": "1",
            "pic": "500",
            "disstid": self.id,
            "type": "1",
            "json": "1",
            "utf8": "1",
            "onlysong": "0",
            "nosign": "1",
            "song_begin": 0,
            "song_num": f"{song_num}",
        }
        total_song_num = self.total_song_num()
        for song_begin in range(0, total_song_num, song_num):
            postdata["song_begin"] = str(song_begin)
            params["_"] = int(time.time() * 1000)
            resp = self.session.request(
                method, url, headers=self.headers, params=params, data=postdata
            )
            if resp.status_code != 200:
                print(f"{song_begin} page fetch failed.")
                continue
            # fetch data
            data = resp.json()

            # with open("data.json", "w", encoding="utf-8") as f:
            #     f.write(json.dumps(data, indent=4, ensure_ascii=False))
            # break

            cdlist = data.get("cdlist")[0]
            playlist_name = cdlist.get("dissname")
            songlist = cdlist.get("songlist")
            for song in songlist:
                name = song.get("name")
                artists = [s.get("name") for s in song.get("singer")]
                interval = song.get("interval")
                album = song.get("album").get("name")
                song_dict = {
                    "name": name,
                    "artists": artists,
                    "album": album,
                    "duration": interval,
                }
                print(song_dict)
                song_list.append(song_dict)

        return {
            "id": self.id,
            "name": playlist_name,
            "songs": song_list,
        }, playlist_name

    def start(self, output_dir="."):
        data, playlist_name = self.get_list()
        file_name = f"{playlist_name}.json"
        output_path = os.path.join(output_dir, file_name)
        # if output dir not exists, create it
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(json.dumps(data, indent=4))
        print(f"file saved at: {file_name}, " f"songs: {len(data['songs'])}")


def read_lines(file):
    with open(file, "r") as f:
        return f.read().splitlines()


def validate_url(url):
    if not url.startswith("https://y.qq.com/n/ryqq/playlist/"):
        raise ValueError(
            f"Invalid QQ Music playlist URL '{url}'. It should be started with 'https://y.qq.com/n/ryqq/playlist/'"
        )
    return url


def parse_id(url):
    return url.split("/")[-1]


if __name__ == "__main__":
    # Make sure you have place your playlist url inside qqmusic-urls.txt
    lines = read_lines("qqmusic-urls.txt")
    if not lines or not any(lines):
        raise ValueError("No URL found in qqmusic-urls.txt")
    id_list = []
    for line in lines:
        if not line or not line.strip() or line.startswith("#") or line == "":
            continue
        url = validate_url(line)
        id_list.append(parse_id(url))
    print(f"Found {len(id_list)} playlist(s) to fetch.")
    for id in id_list:
        print("\n" + "=" * 50)
        print(f"Fetching playlist: {id}\n")
        qq_list = QQMusicList(id)
        qq_list.start("data/qqmusic-raw")
        time.sleep(0.5)  # avoid being blocked

    print("\n\nCompleted.")
