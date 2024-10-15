# QQ音乐转Youtube music 🎶➡️🎵
轻松将您的QQ音乐播放列表转移到YT音乐播放列表。

**[English](readme_en.md) | [中文说明](readme.md)**

## 概述 🚀
抓取QQ音乐播放列表，使用 [`ytmusicapi`](https://github.com/sigma67/ytmusicapi) 搜索并匹配歌曲，并将其转移到YT音乐。

## 需求 📋
- Python 3
- Google帐户

## 快速开始 ⚡
1. **获取你的QQ音乐播放列表URL**：分享你的QQ音乐播放列表并复制链接。
2. **添加URL到文件**：将其粘贴到 [`qqmusic-urls.txt`](qqmusic-urls.txt) 文件中，每个新URL占一行。
3. **获取歌曲**：运行 `fetch_qq.bat` 将播放列表数据保存为JSON文件到 `data/qqmusic-raw/`。
4. **转移到YT音乐**：使用 `import_ytmusic.bat` 将歌曲导入YT音乐。

> [!WARNING]
> 第一次运行脚本时，会要求你登录你的Google帐户。登录后，它将在根目录下生成`oauth.json`。
> **这时候回到终端并按 `Enter` 继续。**

> [!NOTE]
> 将链接复制粘贴到 [`qqmusic-urls.txt`](qqmusic-urls.txt) 文件中。
> 在新行中添加多个链接：
> ```txt
> https://y.qq.com/n/ryqq/playlist/2065383105
> https://y.qq.com/n/ryqq/playlist/7451573651
> ```

## 命令行使用 🖥️
在执行之前修改脚本以进行自定义配置。

### 提取QQ音乐播放列表：
```bash
python qq_music/fetch.py
```

### 合并JSON播放列表文件：
```bash
python qq_music/merge.py
```

### 导入到YT音乐：
```bash
python youtube_music/main.py
```

## 免责声明 ⚠️
仅用于教育目的。责任由用户自行承担。

## 参考资料 📚
- [ytmusicapi](https://github.com/sigma67/ytmusicapi) - 非官方的YT音乐API。
- [spotify_to_ytmusic](https://github.com/sigma67/spotify_to_ytmusic) - 转移歌曲的灵感来源。
- [qq_music_list](https://github.com/loikein/qq_music_list/) - 抓取QQ音乐播放列表。

## 许可证 📜
根据Apache-2.0许可。详情见 [LICENSE](LICENSE) 文件。