from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import csv
import io

app = Flask(__name__)

DB = "calls.db"


def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT,
            date TEXT,
            time TEXT,
            duration TEXT,
            call_type TEXT
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def home():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    calls = conn.execute(
        "SELECT * FROM calls ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return render_template("index.html", calls=calls)


@app.route("/api/calls", methods=["POST"])
def receive_calls():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({"error": "Expected a list of call records"}), 400

    conn = sqlite3.connect(DB)

    for call in data:
        conn.execute("""
            INSERT INTO calls
            (number, date, time, duration, call_type)
            VALUES (?, ?, ?, ?, ?)
        """, (
            call.get("number", ""),
            call.get("date", ""),
            call.get("time", ""),
            call.get("duration", ""),
            call.get("type", "")
        ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "saved": len(data)
    })


@app.route("/export.csv")
def export_csv():
    conn = sqlite3.connect(DB)
    cursor = conn.execute("""
        SELECT number, date, time, duration, call_type
        FROM calls
        ORDER BY id DESC
    """)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Number",
        "Date",
        "Time",
        "Duration",
        "Call Type"
    ])

    writer.writerows(cursor.fetchall())
    conn.close()

    file_data = io.BytesIO(output.getvalue().encode("utf-8-sig"))

    return send_file(
        file_data,
        mimetype="text/csv",
        as_attachment=True,
        download_name="call_history.csv"
    )


init_db()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
