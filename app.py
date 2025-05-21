# Instagram Video Downloader
from flask import Flask, request, render_template_string, send_from_directory
import instaloader
import requests
import os

app = Flask(__name__)

HTML_TEMPLATE = '''
<!doctype html>
<html>
<head><title>Instagram Video Downloader</title></head>
<body>
  <h1>Instagram Video Downloader</h1>
  <form method="POST">
    <input type="text" name="url" placeholder="Enter Instagram video URL" style="width: 80%; padding: 8px;" required />
    <button type="submit">Get Video</button>
  </form>
  {% if video_path %}
    <h3>Download link:</h3>
    <a href="{{ url_for('download_file', filename=video_filename) }}"><button type="button">Click Me!</button></a>
  {% elif error %}
    <p style="color:red;">{{ error }}</p>
  {% endif %}
</body>
</html>
'''

@app.route("/", methods=["GET", "POST"])
def index():
    video_path = None
    video_filename = None
    error = None

    if request.method == "POST":
        url = request.form.get("url", "").strip()
        try:
            # Extraer shortcode del enlace
            shortcode = url.rstrip('/').split("/")[-1]
            L = instaloader.Instaloader()
            post = instaloader.Post.from_shortcode(L.context, shortcode)

            if post.is_video:
                video_url = post.video_url
                video_filename = f"{shortcode}.mp4"
                download_path = os.path.join("downloads", video_filename)
                os.makedirs("downloads", exist_ok=True)

                # Descargar el video
                r = requests.get(video_url)
                with open(download_path, "wb") as f:
                    f.write(r.content)

                video_path = download_path
            else:
                error = "The provided post is not a video."
        except Exception as e:
            error = "Could not retrieve video. Make sure the URL is a valid public Instagram post."

    return render_template_string(HTML_TEMPLATE, video_path=video_path, video_filename=video_filename, error=error)

@app.route("/downloads/<filename>")
def download_file(filename):
    return send_from_directory("downloads", filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
