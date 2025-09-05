# from fastapi import FastAPI, Query
# from fastapi.responses import JSONResponse
# from fastapi.staticfiles import StaticFiles
# import yt_dlp
# import os

# app = FastAPI()

# # ---------------- API ----------------
# def get_video_info(url: str, playlist: bool = False):
#     ydl_opts = {
#         "format": "best[ext=mp4]/best",
#         "noplaylist": not playlist,
#         "quiet": True,
#     }
#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         info = ydl.extract_info(url, download=False)
#     return info

# @app.get("/api/video")
# async def get_single_video(url: str):
#     try:
#         info = get_video_info(url, playlist=False)
#         return {"title": info["title"], "video_url": info["url"]}
#     except Exception as e:
#         return JSONResponse({"error": str(e)}, status_code=500)

# @app.get("/api/playlist")
# async def get_playlist(url: str):
#     try:
#         info = get_video_info(url, playlist=True)
#         videos = []
#         if "entries" in info:
#             for entry in info["entries"]:
#                 if entry:
#                     videos.append({
#                         "title": entry.get("title"),
#                         "id": entry.get("id"),
#                         "url": entry.get("url")
#                     })
#         return {"playlist_title": info.get("title", "Untitled Playlist"), "videos": videos}
#     except Exception as e:
#         return JSONResponse({"error": str(e)}, status_code=500)

# # ---------------- Frontend ----------------
# # Serve static frontend
# # app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
# # Serve frontend from inside backend/frontend
# frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
# app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


import requests
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

API_BASE = "https://pipedapi.kavin.rocks"

@app.get("/api/video")
async def get_video(url: str):
    # Extract video_id safely
    video_id = None
    if "youtube.com" in url or "youtu.be" in url:
        if "v=" in url:
            video_id = url.split("v=")[1].split("&")[0]
        else:
            video_id = url.split("/")[-1].split("?")[0]
    else:
        video_id = url

    try:
        res = requests.get(f"{API_BASE}/streams/{video_id}", timeout=10)
        if res.status_code != 200:
            return {"error": f"Piped API failed with {res.status_code}"}

        try:
            data = res.json()
        except Exception:
            return {"error": "Invalid JSON from Piped API", "raw": res.text[:200]}

        if not data.get("videoStreams"):
            return {"error": "No video streams found"}

        return {
            "title": data.get("title", "Unknown"),
            "video_url": data["videoStreams"][0]["url"]
        }

    except Exception as e:
        return {"error": str(e)}


@app.get("/api/playlist")
async def get_playlist(url: str):  # match frontend param
    # Extract playlist_id (after "list=")
    if "list=" in url:
        playlist_id = url.split("list=")[1].split("&")[0]
    else:
        playlist_id = url

    res = requests.get(f"{API_BASE}/playlists/{playlist_id}")
    data = res.json()

    return {
        "playlist_title": data.get("name"),
        "videos": [
            {"title": v["title"], "url": f"{API_BASE}/streams/{v['url'].split('v=')[1]}"}
            for v in data.get("relatedStreams", [])
        ]
    }


# Path to frontend folder (inside backend)
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")

# Serve frontend files (index.html at "/")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")