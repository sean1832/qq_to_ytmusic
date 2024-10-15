# QQ-Music to YT-Music 🎶➡️🎵
Easily transfer your QQ-Music playlist to a Youtube Music playlist.


**[English](readme_en.md) | [中文说明](readme.md)**

## Overview 🚀
Fetch QQ-Music playlists, search & match songs with Youtube Music using [`ytmusicapi`](https://github.com/sigma67/ytmusicapi), and transfer them to Youtube Music.

## Requirements 📋
- Python 3
- Google Account

## Quick Start ⚡
1. **Get your QQ-Music Playlist URL**: Share your QQ-Music playlist and copy the link.
2. **Add URL to File**: Paste it into [`qqmusic-urls.txt`](qqmusic-urls.txt); each new URL on a new line.
3. **Fetch Songs**: Run `fetch_qq.bat` to save playlist data as JSON files in `data/qqmusic-raw/`.
4. **Transfer to YT-Music**: Use `import_ytmusic.bat` to import songs to YT-Music.

> [!WARNING]
> When you run the script for the first time, it will ask you to login to your Google account. 
> After logging in, it will generate a `oauth.json` under the root directory. **Go back to the terminal and press `Enter` to continue.**

> [!NOTE]
> Copy and paste the links in the [`qqmusic-urls.txt`](qqmusic-urls.txt) file.
> Add multiple links in new lines:
> ```txt
> https://y.qq.com/n/ryqq/playlist/2065383105
> https://y.qq.com/n/ryqq/playlist/7451573651
> ```

## Command Line Usage 🖥️
Modify the scripts for customized configuration before executing.

### Extract QQ-Music Playlist:
```bash
python qq_music/fetch.py
```

### Merge JSON Playlist Files:
```bash
python qq_music/merge.py
```

### Import to YT-Music:
```bash
python youtube_music/main.py
```

## Disclaimer ⚠️
For educational purposes only. Misuse responsibility lies with the user.

## References 📚
- [ytmusicapi](https://github.com/sigma67/ytmusicapi) - Unofficial Youtube Music API.
- [spotify_to_ytmusic](https://github.com/sigma67/spotify_to_ytmusic) - Inspiration for transferring to youtube music.
- [qq_music_list](https://github.com/loikein/qq_music_list/) - Fetching QQ-Music playlists.

## License 📜
Licensed under Apache-2.0. See the [LICENSE](LICENSE) file for more details.