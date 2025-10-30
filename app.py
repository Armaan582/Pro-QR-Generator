import os
import uuid
from flask import Flask, render_template_string, request, send_file, url_for, send_from_directory
from werkzeug.utils import secure_filename
import qrcode
from io import BytesIO

app = Flask(__name__)

# Upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load HTML
with open("index.html", "r", encoding="utf-8") as f:
    html_content = f.read()

def allowed_file(filename):
    # support common images + videos
    allowed_exts = {"png", "jpg", "jpeg", "gif", "webp", "mp4", "mov", "avi", "mkv", "webm"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_exts

@app.route("/")
def home():
    return render_template_string(html_content)

@app.route("/generate", methods=["POST"])
def generate_qr():
    text = request.form.get("text", "").strip()
    file = request.files.get("image")

    if file and allowed_file(file.filename):
        # secure and unique filename
        safe_name = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{safe_name}"
        path = os.path.join(UPLOAD_FOLDER, unique_name)
        file.save(path)

        # Create an absolute URL that points to the uploaded file route
        # _external=True ensures the full URL (http(s)://host:port/...) is embedded in the QR
        data = url_for("uploaded_file", filename=unique_name, _external=True)

    elif text:
        data = text
    else:
        return "No text or image provided", 400

    try:
        img = qrcode.make(data)
    except Exception as e:
        return f"Failed to generate QR: {e}", 500

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

# Serve uploaded files at /uploads/<filename>
# Browsers will open the file directly (images will display, videos will play)
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=False)

# ---------------- Render-friendly / local run ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # For local testing on LAN: host="0.0.0.0" makes it reachable from other devices on your network
    app.run(host="0.0.0.0", port=port, debug=True)
