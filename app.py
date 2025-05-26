from flask import Flask, request, render_template_string, send_from_directory
import instaloader
import requests
import os

app = Flask(__name__)

HTML_TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Instagram Video Downloader</title>
  <style>
    :root {
      --primary: #9239CE;
      --secondary: #FF12C4;
      --text: #000000;
      --bg: #ffffff;
      --card-bg: #f5f5f5;
    }
    body {
      font-family: Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      margin: 0;
      padding: 20px;
      scroll-behavior: smooth;
    }
    .container {
      max-width: 700px;
      margin: auto;
      text-align: center;
      padding: 30px;
      border-radius: 10px;
      background-color: var(--card-bg);
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
      animation: fadeIn 0.7s ease-in-out;
    }
    h1 {
      color: var(--primary);
    }
    input[type="text"] {
      width: 90%;
      padding: 12px;
      margin-top: 20px;
      border: 2px solid var(--secondary);
      border-radius: 6px;
      font-size: 16px;
    }
    button {
      margin-top: 15px;
      padding: 12px 24px;
      background-color: var(--primary);
      border: none;
      border-radius: 6px;
      font-size: 16px;
      color: #fff;
      cursor: pointer;
      transition: background-color 0.3s ease;
    }
    button:hover {
      background-color: #6e28a6;
    }
    .thumbnail-results {
      margin-top: 30px;
    }
    .thumb {
      margin-bottom: 20px;
    }
    img {
      max-width: 100%;
      border-radius: 8px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .actions {
      margin-top: 10px;
    }
    a.download-btn {
      display: inline-block;
      margin: 6px;
      background-color: var(--secondary);
      color: #fff;
      padding: 8px 15px;
      text-decoration: none;
      border-radius: 5px;
      font-size: 15px;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: scale(0.98); }
      to { opacity: 1; transform: scale(1); }
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Instagram Video Downloader</h1>
    <p>Paste the Instagram video URL below to download it.</p>

    <form method="POST">
      <input type="text" name="url" placeholder="https://www.instagram.com/reel/..." required />
      <button type="submit">Download Video</button>
    </form>

    {% if video_path %}
    <div class="thumbnail-results">
      <div class="actions">
        <p><strong>Your download is ready:</strong></p>
        <a href="{{ url_for('download_file', filename=video_filename) }}" class="download-btn">Download Video</a>
      </div>
    </div>
    {% elif error %}
    <div class="thumbnail-results">
      <p style="color:red;"><strong>{{ error }}</strong></p>
    </div>
    {% endif %}
  </div>
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
            shortcode = url.rstrip('/').split("/")[-1]
            L = instaloader.Instaloader()
            post = instaloader.Post.from_shortcode(L.context, shortcode)

            if post.is_video:
                video_url = post.video_url
                video_filename = f"{shortcode}.mp4"
                download_path = os.path.join("downloads", video_filename)
                os.makedirs("downloads", exist_ok=True)

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
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
