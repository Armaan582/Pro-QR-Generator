import os
import uuid
from flask import Flask, render_template_string, request, send_file
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
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"png","jpg","jpeg","gif","webp"}

@app.route("/")
def home():
    return render_template_string(html_content)

@app.route("/generate", methods=["POST"])
def generate_qr():
    text = request.form.get("text", "").strip()
    file = request.files.get("image")

    if file and allowed_file(file.filename):
        unique_name = f"{uuid.uuid4().hex}_{file.filename}"
        path = os.path.join(UPLOAD_FOLDER, unique_name)
        file.save(path)
        data = path  # QR for uploaded file path
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

if __name__ == "__main__":
    app.run(debug=True)
