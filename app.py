from flask import Flask, request, render_template_string, send_from_directory
import instaloader
import requests
import os

app = Flask(__name__)

HTML_TEMPLATE = '''
<!doctype html>
<html>
 <style>
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: #f3f0f5;
      margin: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
    }

    .bmi-container {
      background: #fff;
      padding: 2rem;
      border-radius: 1.5rem;
      box-shadow: 0 10px 25px rgba(146, 57, 206, 0.2);
      width: 100%;
      max-width: 75%;
    }

    h1 {
      color: #9239CE;
      text-align: center;
      margin-bottom: 1rem;
    }

    .input-group {
      display: flex;
      flex-direction: column;
      gap: 1rem;
      margin-bottom: 1.5rem;
    }

    label {
      font-weight: bold;
      color: #9239CE;
    }

    input[type="text"] {
      padding: 0.75rem;
      border: 2px solid #9239CE;
      border-radius: 1rem;
      outline: none;
      font-size: 1rem;
    }

    button {
      background: #FF12C4;
      color: #fff;
      border: none;
      padding: 0.75rem 1.25rem;
      border-radius: 1rem;
      cursor: pointer;
      font-size: 1rem;
      transition: background 0.3s ease;
    }

    button:hover {
      background: #e010b5;
    }

    .result {
      margin-top: 1.5rem;
      padding: 1rem;
      border-radius: 1rem;
      background-color: #f9f4fc;
      border: 1px solid #9239CE;
      color: #333;
      text-align: center;
    }

    .result span {
      display: block;
      margin-top: 0.5rem;
      font-size: 1.2rem;
      font-weight: bold;
      color: #FF12C4;
    }

    @media (max-width: 500px) {
      .bmi-container {
        padding: 1.25rem;
      }
    }
</style>
<body>
<div class="bmi-container">
<h1>Instagram Video Downloader</h1>
  <div class="input-group">
  <form method="POST">
    <input type="text" name="url" id="ig-url" placeholder="Enter Instagram video URL" style="width: 80%; padding: 8px;" required />
    <button type="submit">Get Video</button>
    
  </form>
  {% if video_path %}
    <div class="result" id="result">
      <h3>Download link:</h3>
      <a href="{{ url_for('download_file', filename=video_filename) }}"><button type="button">Click Me!</button></a>
    </div>
  {% elif error %}
    <div class="result" id="result">
      <p style="color:red;">{{ error }}</p>
    </div>
  {% endif %}
  </div>
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
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
