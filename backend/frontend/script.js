async function getVideo() {
  const url = document.getElementById("url").value;
  const cookies = document.getElementById("cookies").value;

  const formData = new FormData();
  formData.append("url", url);
  if (cookies) formData.append("cookies", cookies);

  const res = await fetch(`/api/video`, {
    method: "POST",
    body: formData
  });

  const data = await res.json();
  const resultDiv = document.getElementById("result");

  if (data.error) {
    resultDiv.innerHTML = `<p style="color:red;">Error: ${data.error}</p>`;
  } else {
    // Render video container
    resultDiv.innerHTML = `
      <h3>${data.title}</h3>
      <video id="player" controls width="480"></video><br>
      <a href="${data.video_url}" download>Download MP4</a>
    `;

    // Decide how to play
    if (data.video_url.endsWith(".m3u8")) {
      playVideo(data.video_url);
    } else {
      document.getElementById("player").src = data.video_url;
    }
  }
}


async function getPlaylist() {
  const url = document.getElementById("url").value;
  const cookies = document.getElementById("cookies").value;

  const formData = new FormData();
  formData.append("url", url);
  if (cookies) formData.append("cookies", cookies);

  const res = await fetch(`/api/playlist`, {
    method: "POST",
    body: formData
  });

  const data = await res.json();
  const resultDiv = document.getElementById("result");

  if (data.error) {
    resultDiv.innerHTML = `<p style="color:red;">Error: ${data.error}</p>`;
  } else {
    let html = `<h2>${data.playlist_title}</h2>`;
    data.videos.forEach((v, i) => {
      const playerId = `player-${i}`;
      html += `
        <div>
          <p>${v.title}</p>
          <video id="${playerId}" controls width="320"></video><br>
          <a href="${v.url}" download>Download MP4</a>
        </div>
        <hr>
      `;
    });
    resultDiv.innerHTML = html;

    // Init players
    data.videos.forEach((v, i) => {
      const videoEl = document.getElementById(`player-${i}`);
      if (v.url.endsWith(".m3u8")) {
        const hls = new Hls();
        hls.loadSource(v.url);
        hls.attachMedia(videoEl);
      } else {
        videoEl.src = v.url;
      }
    });
  }
}



function playVideo(url) {
  const video = document.getElementById("player");
  if (Hls.isSupported()) {
    const hls = new Hls();
    hls.loadSource(url);
    hls.attachMedia(video);
  } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
    // Safari
    video.src = url;
  }
}