from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import psycopg2.extras
import os
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
DATABASE_URL = os.environ.get("DATABASE_URL")

app = Flask("location")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id SERIAL PRIMARY KEY,
            caption TEXT NOT NULL,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            photo_path TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

@app.route("/")
def home():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM memories ORDER BY created_at DESC")
    memories = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", memories=memories)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        caption = request.form.get("caption")
        lat = request.form.get("lat")
        lng = request.form.get("lng")

        photo_path = None
        file = request.files.get("photo")
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            photo_path = filename

        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO memories (caption, lat, lng, photo_path) VALUES (%s, %s, %s, %s)",
            (caption, lat, lng, photo_path)
        )
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("home"))

    return render_template("add.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)