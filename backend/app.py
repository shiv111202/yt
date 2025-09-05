from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import yt_dlp
import os

app = FastAPI()

# ---------------- API ----------------
def get_video_info(url: str, playlist: bool = False):
    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "noplaylist": not playlist,
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return info

@app.get("/api/video")
async def get_single_video(url: str):
    try:
        info = get_video_info(url, playlist=False)
        return {"title": info["title"], "video_url": info["url"]}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/playlist")
async def get_playlist(url: str):
    try:
        info = get_video_info(url, playlist=True)
        videos = []
        if "entries" in info:
            for entry in info["entries"]:
                if entry:
                    videos.append({
                        "title": entry.get("title"),
                        "id": entry.get("id"),
                        "url": entry.get("url")
                    })
        return {"playlist_title": info.get("title", "Untitled Playlist"), "videos": videos}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ---------------- Frontend ----------------
# Serve static frontend
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
