from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_NAME = "database.db"


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# Create table if it doesn't exist
with get_db_connection() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)


@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db_connection()

    if request.method == "POST":
        item_name = request.form["name"]
        if item_name:
            conn.execute("INSERT INTO items (name) VALUES (?)", (item_name,))
            conn.commit()
        return redirect(url_for("index"))

    items = conn.execute("SELECT * FROM items").fetchall()
    conn.close()
    return render_template("index.html", items=items)


@app.route("/delete/<int:item_id>")
def delete(item_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
