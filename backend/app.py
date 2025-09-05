# from fastapi import FastAPI, Form
# from fastapi.responses import JSONResponse
# from fastapi.staticfiles import StaticFiles
# import yt_dlp
# import tempfile
# import os

# app = FastAPI()

# # ---------------- Helper ----------------
# def run_yt_dlp(url: str, playlist: bool, cookies: str = None):
#     # Create yt-dlp options
#     ydl_opts = {
#         "format": "best[ext=mp4]/best",
#         "noplaylist": not playlist,
#         "quiet": True,
#     }

#     # If cookies provided, save them in a temp Netscape file
#     if cookies:
#         tmp_file = tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt")
#         tmp_file.write("# Netscape HTTP Cookie File\n")
#         for cookie in cookies.split(";"):
#             if "=" in cookie:
#                 key, value = cookie.strip().split("=", 1)
#                 # Minimal Netscape format: domain, flag, path, secure, expiry, name, value
#                 tmp_file.write(f".youtube.com\tTRUE\t/\tFALSE\t2147483647\t{key}\t{value}\n")
#         tmp_file.close()
#         ydl_opts["cookiefile"] = tmp_file.name

#     try:
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = ydl.extract_info(url, download=False)
#         return info
#     finally:
#         # Clean up temp cookie file
#         if cookies:
#             os.remove(tmp_file.name)

# # ---------------- API ----------------
# @app.post("/api/video")
# async def get_single_video(url: str = Form(...), cookies: str = Form(None)):
#     try:
#         info = run_yt_dlp(url, playlist=False, cookies=cookies)
#         return {"title": info["title"], "video_url": info["url"]}
#     except Exception as e:
#         return JSONResponse({"error": str(e)}, status_code=500)


# @app.post("/api/playlist")
# async def get_playlist(url: str = Form(...), cookies: str = Form(None)):
#     try:
#         info = run_yt_dlp(url, playlist=True, cookies=cookies)
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
# frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
# app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")



from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import yt_dlp
import tempfile
import os

app = FastAPI()

# ---------------- Helper ----------------
def clean_cookie_text(cookie_text: str) -> str:
    cleaned = []
    for line in cookie_text.splitlines():
        if line.startswith("#HttpOnly_"):
            # strip the HttpOnly_ prefix
            cleaned.append(line.replace("#HttpOnly_", "", 1))
        elif line.startswith("#") and "Netscape" not in line:
            # skip normal comments
            continue
        else:
            cleaned.append(line)
    return "\n".join(cleaned)


def run_yt_dlp(url: str, playlist: bool, cookies: str = None):
    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "noplaylist": not playlist,
        "quiet": True,
    }

    tmp_file = None
    if cookies:
        tmp_file = tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt")
        # clean and write proper Netscape cookies
        tmp_file.write(clean_cookie_text(cookies))
        tmp_file.close()
        ydl_opts["cookiefile"] = tmp_file.name

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return info
    finally:
        if tmp_file:
            os.remove(tmp_file.name)

# ---------------- API ----------------
@app.post("/api/video")
async def get_single_video(url: str = Form(...), cookies: str = Form(None)):
    try:
        info = run_yt_dlp(url, playlist=False, cookies=cookies)
        return {"title": info["title"], "video_url": info["url"]}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/playlist")
async def get_playlist(url: str = Form(...), cookies: str = Form(None)):
    try:
        info = run_yt_dlp(url, playlist=True, cookies=cookies)
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
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
