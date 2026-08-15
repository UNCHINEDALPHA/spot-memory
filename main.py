from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "spots.db")
UPLOAD_FOLDER= os.path.join(BASE_DIR, "static", "uploads")

app = Flask("location")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            caption TEXT NOT NULL,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            photo_path TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db() 

@app.route("/")
def home():
    conn= sqlite3.connect(DB_PATH)
    conn.row_factory= sqlite3.Row
    memories= conn.execute("SELECT * FROM memories ORDER BY created_at DESC"). fetchall()
    conn.close()
    return render_template("index.html", memories= memories)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        caption = request.form.get("caption")
        lat = request.form.get("lat")
        lng = request.form.get("lng")

        photo_path= None
        file= request.files.get("photo")
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            photo_path = filename

        conn = sqlite3.connect(DB_PATH)
        conn.execute(

         "INSERT INTO memories (caption, lat, lng, photo_path, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
         (caption, lat, lng, photo_path)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("home"))

    return render_template("add.html")
