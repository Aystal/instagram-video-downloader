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
  <title></title>
  <style>
     #body_div {
      margin: 0;
      font-family: 'Segoe UI', sans-serif;
      background: #f8f8ff;
      color: #333;
    }
    #tool_header {
      background: linear-gradient(90deg, #9239CE, #FF12C4);
      color: white;
      text-align: center;
      padding: 2rem 1rem;
      margin-bottom: 1rem;
      border-radius: 2rem;
    }
    .flex-container {
      display: flex;
      flex-direction: column;
      max-width: 600px;
      margin: 2rem auto;
      padding: 1rem;
      background: white;
      border-radius: 1rem;
      box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    input, select, button {
      width: 90%;
      padding: 0.75rem;
      margin: auto;
      border: 1px solid #ccc;
      border-radius: 0.5rem;
      margin-bottom: 1rem;
    }
    #label1{
      color: #9239CE;
      font: sans-serif;
      margin-bottom: 0.5rem;
    }
    button {
      background: #9239CE;
      color: white;
      border: none;
      cursor: pointer;
      margin-top: 1rem;
    }
    .input-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.input-group input,
.input-group button {
  width: 100%;
  max-width: 500px;
  box-sizing: border-box;
}
    button:hover {
      background: #7c2bbd;
    }
    #result {
      font-size: 1.2rem;
      margin-top: 1rem;
      font-weight: bold;
      text-align: center;
    }
    #tool_footer {
      text-align: center;
      font-size: 0.9rem;
      padding: 1rem;
      color: #888;
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
</head>
<div id="body_div">
   <div class="flex-container">
    <header id="tool_header">
      <h1>Free IG video Downloader</h1>
      <p>no se que poner jeje</p>
    </header>
    <form method="POST">
    
      <div class="input-group">
      <label for="ig-url" id="label1">Enter Instagram video URL:</label>
      <input type="text" name="url" id="ig-url" placeholder="https://www.instagram.com/reel/..." required />
      <button type="submit">Get Video</button>
    </div>
      </form>
      {% if video_path %}
      <div class="result" id="result">
        <h3 id="label1">Download link:</h3>
        <a href="{{ url_for('download_file', filename=video_filename) }}"><button type="button">Click Me!</button></a>
      </div>
      {% elif error %}
      <div class="result" id="result">
        <p style="color:red;">{{ error }}</p>
      </div>
      {% endif %}
    
    </div>
  <footer id="tool_footer">
    &copy; 2025 BMI Tools | <a href="#">Privacy</a> | <a href="#">Contact</a>
  </footer>
</div>
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
