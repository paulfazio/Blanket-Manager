from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_NAME = "database.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Create tables
with get_db_connection() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS horses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS blankets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            horse_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            min_temp INTEGER,
            max_temp INTEGER,
            FOREIGN KEY (horse_id) REFERENCES horses (id) ON DELETE CASCADE
        )
    """)

@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db_connection()
    if request.method == "POST":
        horse_name = request.form["horse_name"]
        if horse_name:
            conn.execute("INSERT INTO horses (name) VALUES (?)", (horse_name,))
            conn.commit()
        return redirect(url_for("index"))

    # Fetch horses and their associated blankets
    horses = conn.execute("SELECT * FROM horses").fetchall()
    
    # We'll create a dictionary where keys are horse IDs and values are lists of blankets
    horse_data = []
    for horse in horses:
        blankets = conn.execute("SELECT * FROM blankets WHERE horse_id = ?", (horse['id'],)).fetchall()
        horse_data.append({'horse': horse, 'blankets': blankets})

    conn.close()
    return render_template("index.html", horse_data=horse_data)

@app.route("/add_blanket/<int:horse_id>", methods=["POST"])
def add_blanket(horse_id):
    name = request.form["blanket_name"]
    min_t = request.form["min_temp"]
    max_t = request.form["max_temp"]
    
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO blankets (horse_id, name, min_temp, max_temp) VALUES (?, ?, ?, ?)",
        (horse_id, name, min_t, max_t)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/delete/<int:horse_id>")
def delete(horse_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM horses WHERE id = ?", (horse_id,))
    # SQLite foreign keys need PRAGMA foreign_keys = ON to cascade, 
    # or we delete manually:
    conn.execute("DELETE FROM blankets WHERE horse_id = ?", (horse_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)