import asyncio
import os
import re
from typing import Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
#from youtubesearchpython.__future__ import VideosSearch

import requests
import json

from ANNIEMUSIC.utils.database import is_on_off
from ANNIEMUSIC.utils.formatters import time_to_seconds


async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")


class YouTubeAPI:
    def __init__(self):
        self.base = "http://94.237.54.197:8443/song/?query="
        self.base2 = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        
    async def search(self, query):
        url = self.base + query
        response = requests.get(url)
        return response.json()

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if re.search(self.regex, link):
            return True
        else:
            return False

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset in (None,):
            return None
        return text[offset : offset + length]

    async def details(self, query: str):
        response_data = await self.search(query)
        if response_data:
            title = response_data.get("song", "")
            duration_min = response_data.get("duration", "")
            thumbnail = response_data.get("image", "")
            vidid = response_data.get("songl", "")
            duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
            return title, duration_min, duration_sec, thumbnail, vidid
        return None, None, None, None, None

    async def title(self, query: str):
        response_data = await self.search(query)
        if response_data:
            return response_data.get("song", "")
        return ""

    async def duration(self, query: str):
        response_data = await self.search(query)
        if response_data:
            return response_data.get("duration", "")
        return ""

    async def thumbnail(self, query: str):
        response_data = await self.search(query)
        if response_data:
            return response_data.get("image", "")
        return ""

    async def video(self, query: str):
        response_data = await self.search(query)
        if response_data:
            vid_url = response_data.get("media_url", "")
            if vid_url:
                return 1, vid_url
        return 0, ""

    async def track(self, query: str):
        response_data = await self.search(query)
        if response_data:
            title = response_data.get("song", "")
            duration_min = response_data.get("duration", "")
            vidid = response_data.get("song", "")
            yturl = response_data.get("media_url", "")
            thumbnail = response_data.get("image", "")
            track_details = {
                "title": title,
                "link": yturl,
                "vidid": vidid,
                "duration_min": duration_min,
                "thumb": thumbnail,
            }
            return track_details, vidid
        return {}, ""

    async def formats(self, query: str):
        response_data = await self.search(query)
        if response_data:
            link = response_data.get("media_url", "")
            ytdl_opts = {"quiet": True}
            ydl = yt_dlp.YoutubeDL(ytdl_opts)
            with ydl:
                formats_available = []
                r = ydl.extract_info(link, download=False)
                for format in r["formats"]:
                    try:
                        str(format["format"])
                    except:
                        continue
                    if not "dash" in str(format["format"]).lower():
                        try:
                            format["format"]
                            format["filesize"]
                            format["format_id"]
                            format["ext"]
                            format["format_note"]
                        except:
                            continue
                        formats_available.append(
                            {
                                "format": format["format"],
                                "filesize": format["filesize"],
                                "format_id": format["format_id"],
                                "ext": format["ext"],
                                "format_note": format["format_note"],
                                "yturl": link,
                            }
                        )
            return formats_available, link
        return [], ""

    async def slider(self, query: str, query_type: int):
        response_data = await self.search(query)
        if response_data:
            title = response_data.get("song", "")
            duration_min = response_data.get("duration", "")
            vidid = response_data.get("song", "")
            thumbnail = response_data.get("image", "")
            return title, duration_min, thumbnail, vidid
        return "", "", "", ""

    async def download(
        self,
        query: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        response_data = await self.search(query)
        if response_data:
            link = response_data.get("media_url", "")
            if videoid:
                link = response_data.get("media_url", "")
                #link = link
            loop = asyncio.get_running_loop()

            def audio_dl():
                ydl_optssx = {
                    "format": "bestaudio/best",
                    "outtmpl": "downloads/%(id)s.%(ext)s",
                    "geo_bypass": True,
                    "nocheckcertificate": True,
                    "quiet": True,
                    "no_warnings": True,
                }
                x = yt_dlp.YoutubeDL(ydl_optssx)
                info = x.extract_info(link, False)
                xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
                if os.path.exists(xyz):
                    return xyz
                x.download([link])
                return xyz

            def video_dl():
                ydl_optssx = {
                    "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])",
                    "outtmpl": "downloads/%(id)s.%(ext)s",
                    "geo_bypass": True,
                    "nocheckcertificate": True,
                    "quiet": True,
                    "no_warnings": True,
                }
                x = yt_dlp.YoutubeDL(ydl_optssx)
                info = x.extract_info(link, False)
                xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
                if os.path.exists(xyz):
                    return xyz
                x.download([link])
                return xyz

            def song_video_dl():
                formats = f"best"
                fpath = f"downloads/{title}"
                ydl_optssx = {
                    "format": formats,
                    "outtmpl": fpath,
                    "geo_bypass": True,
                    "nocheckcertificate": True,
                    "quiet": True,
                    "no_warnings": True,
                    "prefer_ffmpeg": True,
                    "merge_output_format": "mp4",
                }
                x = yt_dlp.YoutubeDL(ydl_optssx)
                x.download([link])

            def song_audio_dl():
                fpath = f"downloads/{title}.%(ext)s"
                ydl_optssx = {
                    "format": format_id,
                    "outtmpl": fpath,
                    "geo_bypass": True,
                    "nocheckcertificate": True,
                    "quiet": True,
                    "no_warnings": True,
                    "prefer_ffmpeg": True,
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }
                    ],
                }
                x = yt_dlp.YoutubeDL(ydl_optssx)
                x.download([link])

            if songvideo:
                await loop.run_in_executor(None, song_video_dl)
                fpath = f"downloads/{title}.mp4"
                return fpath
            elif songaudio:
                await loop.run_in_executor(None, song_audio_dl)
                fpath = f"downloads/{title}.mp3"
                return fpath
            elif video:
                if await is_on_off(1):
                    direct = True
                    downloaded_file = await loop.run_in_executor(None, video_dl)
                else:
                    proc = await asyncio.create_subprocess_exec(
                        "yt-dlp",
                        "-g",
                        "-6",
                        "-f",
                        "best[height<=?720][width<=?1280]",
                        f"{link}",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    stdout, stderr = await proc.communicate()
                    if stdout:
                        downloaded_file = stdout.decode().split("\n")[0]
                        direct = None
                    else:
                        return
            else:
                direct = True
                downloaded_file = await loop.run_in_executor(None, audio_dl)
            return downloaded_file, direct
        return "", ""
