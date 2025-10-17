from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
from db import init_db, insert_bill, get_user_bills

app = Flask(__name__)
app.secret_key = "medi_alarm_secret"
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Initialize Database ---
init_db()


# --- Routes ---

@app.route('/')
def home():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route('/login', methods=['POST'])
def login():
    login_id = request.form.get("login")
    if not login_id:
        return "Enter email or phone!", 400
    session["user"] = login_id
    return redirect(url_for("dashboard"))


@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))


@app.route('/dashboard1')
def dashboard():
    if "user" not in session:
        return redirect(url_for("home"))
    return render_template("dashboard1.html", user=session["user"])


@app.route('/upload_bill', methods=['POST'])
def upload_bill():
    if "user" not in session:
        return redirect(url_for("home"))

    file = request.files.get("bill")
    if not file:
        return "No file uploaded", 400

    filename = secure_filename(file.filename)
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(path)

    # OCR with pytesseract
    text = pytesseract.image_to_string(Image.open(path))

    # Basic parsing
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    pharmacy = next((l for l in lines if "pharmacy" in l.lower() or "chemist" in l.lower()), "")
    doctor = next((l for l in lines if "dr." in l.lower() or "doctor" in l.lower()), "")
    meds = [l for l in lines if any(x in l.lower() for x in ["mg", "tablet", "tab", "ml", "dose"])]

    insert_bill(session["user"], pharmacy, doctor, "\n".join(meds), text)

    return jsonify({
        "pharmacy": pharmacy,
        "doctor": doctor,
        "medicines": meds,
        "raw_text": text
    })


@app.route('/get_bills')
def get_bills():
    if "user" not in session:
        return jsonify([])
    rows = get_user_bills(session["user"])
    return jsonify(rows)


if __name__ == "__main__":
    app.run(debug=True)