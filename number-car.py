from __future__ import annotations

import os
import re
from datetime import datetime

import cv2
import numpy as np
import pytesseract
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# ---------------------------------------------------------------------------
# Database setup (SQLite)
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "plates.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Plate(db.Model):
    """A single license‑plate record."""

    plate_text: str = db.Column(db.String(16), primary_key=True)
    name: str = db.Column(db.String(128), nullable=False)
    first_seen: datetime = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:  # pragma: no cover – representation only.
        return f"<Plate {self.plate_text} – {self.name}>"


with app.app_context():
    db.create_all()  # create table if it doesn't exist (idempotent).


# ---------------------------------------------------------------------------
CYR_TO_LAT: dict[str, str] = {
    "А": "A",
    "В": "B",
    "Е": "E",
    "К": "K",
    "М": "M",
    "Н": "H",
    "О": "O",
    "Р": "P",
    "С": "C",
    "Т": "T",
    "Х": "X",
    "E": "E",  # sometimes OCR picks the Cyrillic YO; map to E for plates
}


def normalize_text(text: str) -> str:


    return "".join(CYR_TO_LAT.get(ch, ch) for ch in text)


PLATE_REGEX: re.Pattern[str] = re.compile(r"\b[A-Z]{1,3}\s*\d{1,4}\s*[A-Z]{0,2}\b")

# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------


@app.route("/recognize", methods=["POST"])
def recognize_plate():


    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file_storage = request.files["image"]
    img_bytes: bytes = file_storage.read()
    np_arr: np.ndarray[np.uint8] = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Basic preprocessing – convert to grayscale.
   # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)  # Премахване на шум
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 11, 2)  # Подобрена контрастност
    # Run OCR (pytesseract assumes RGB – but works fine on grayscale array).
    raw_text: str = pytesseract.image_to_string(gray)
    #text = normalize_text(raw_text.upper())
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    text = pytesseract.image_to_string(gray, config=custom_config)
    #print("RAW OCR TEXT:", raw_text)
    #print("NORMALIZED TEXT:", text)

    matches: list[str] = PLATE_REGEX.findall(text.replace("\n", " "))
    if not matches:
        return jsonify({"plate_text": "", "name": "Не е намерен номер"}), 200

    # Use the first match; for multiple plates in the image, you could iterate.
    plate_key: str = matches[0].replace(" ", "")
    print("MATCHES FOUND:", matches)
    # ---------------------------------------------------------------------
    # 1️⃣  Already stored? Return saved name.
    # ---------------------------------------------------------------------
    stored: Plate | None = Plate.query.filter_by(plate_text=plate_key).first()
    if stored:
        return jsonify({"plate_text": stored.plate_text, "name": stored.name}), 200

    # ---------------------------------------------------------------------
    # 2️⃣  New plate – determine name, save to DB, return.
    # ---------------------------------------------------------------------
    name: str = INITIAL_PLATE_NAMES.get(plate_key, "Няма съвпадение")

    new_entry = Plate(plate_text=plate_key, name=name)
    db.session.add(new_entry)
    db.session.commit()

    return jsonify({"plate_text": plate_key, "name": name}), 200


@app.route("/plates", methods=["GET"])
def list_plates():
    """Return all stored plates as JSON (dev helper)."""

    all_rows: list[Plate] = Plate.query.order_by(Plate.first_seen).all()
    return jsonify([
        {"plate_text": p.plate_text, "name": p.name, "first_seen": p.first_seen.isoformat()}
        for p in all_rows
    ])


# ---------------------------------------------------------------------------
# Entry‑point helper so `python license_plate_app.py` *just works*.
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    # Use 0.0.0.0 so it works in Docker / remote machines; remove if not needed.
    app.run(host="0.0.0.0", port=5000, debug=True)