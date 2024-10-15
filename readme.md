# QQ-Music to YT-Music
This is a simple tool to transfer your QQ-Music playlist to YT-Music playlist.

## Requirements
- Python 3
- Google account

## Basic Usage
1. Get your QQ-Music playlist url. You can do so by sharing your playlist and copying the link.
2. Paste the link in the [`qqmusic-urls.txt`](qqmusic-urls.txt) file. You can add multiple links, each in a new line.
> [!NOTE] Example:
> ```txt
> https://y.qq.com/n/ryqq/playlist/2065383105
> https://y.qq.com/n/ryqq/playlist/7451573651
> ```

3. Run `fetch_qq.bat` to fetch the songs from the QQ-Music playlist. It will save the playlist data into `data/qqmusic-raw/` folder as json files.
4. Run `import_ytmusic.bat` to import the songs to YT-Music.
> [!WARNING]
> When you run the script for the first time, it will ask you to login to your Google account. 
> **After logging in, go back to the terminal and press `Enter` to continue.**

## Use from Command Line
You can also invoke the scripts from the command line. Note that 
at the moment, you need to modify the scripts to change configuration.

**Extract the QQ-Music playlist data:**
```bash
python qq_music/fetch.py
```

**Merge multiple json playlist files into one:**
```bash
python qq_music/merge.py
```

**Import the QQ-Music playlist to YT-Music:**
```bash
python youtube_music/main.py
```


## Disclaimer
This tool is for educational purposes only. I do not take any responsibility for the misuse of this tool.

## Credits
- [ytmusicapi](https://github.com/sigma67/ytmusicapi) *(for the unofficial YT-Music API.)*
- [spotify_to_ytmusic](https://github.com/sigma67/spotify_to_ytmusic) *(for the inspiration and the base code for adding songs to YT-Music playlist.)*
- [qq_music_list](https://github.com/loikein/qq_music_list/) *(for the base code for fetching songs from QQ-Music playlist.)*

## License
This project is licensed under the Apache-2.0 License - see the [LICENSE](LICENSE) file for details.
