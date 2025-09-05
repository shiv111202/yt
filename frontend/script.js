async function getVideo() {
  const url = document.getElementById("url").value;
  const res = await fetch(`/api/video?url=${encodeURIComponent(url)}`);
  const data = await res.json();
  const resultDiv = document.getElementById("result");

  if (data.error) {
    resultDiv.innerHTML = `<p style="color:red;">Error: ${data.error}</p>`;
  } else {
    resultDiv.innerHTML = `
      <h3>${data.title}</h3>
      <video src="${data.video_url}" controls width="480"></video><br>
      <a href="${data.video_url}" download>Download MP4</a>
    `;
  }
}

async function getPlaylist() {
  const url = document.getElementById("url").value;
  const res = await fetch(`/api/playlist?url=${encodeURIComponent(url)}`);
  const data = await res.json();
  const resultDiv = document.getElementById("result");

  if (data.error) {
    resultDiv.innerHTML = `<p style="color:red;">Error: ${data.error}</p>`;
  } else {
    let html = `<h2>${data.playlist_title}</h2>`;
    data.videos.forEach(v => {
      html += `
        <div>
          <p>${v.title}</p>
          <video src="${v.url}" controls width="320"></video><br>
          <a href="${v.url}" download>Download MP4</a>
        </div>
        <hr>
      `;
    });
    resultDiv.innerHTML = html;
  }
}
