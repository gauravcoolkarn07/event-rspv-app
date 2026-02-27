from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("events.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            date TEXT,
            max_seats INTEGER,
            admin_password TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS rsvps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            user_name TEXT,
            email TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()
@app.route('/')
def index():
    conn = sqlite3.connect('events.db')
    events = conn.execute("SELECT * FROM events").fetchall()

    event_data = []

    for event in events:
        rsvp_count = conn.execute(
            "SELECT COUNT(*) FROM rsvps WHERE event_id = ?",
            (event[0],)
        ).fetchone()[0]

        attendees = conn.execute(
            "SELECT user_name FROM rsvps WHERE event_id = ?",
            (event[0],)
        ).fetchall()

        event_data.append({
            "id": event[0],
            "name": event[1],
            "date": event[2],
            "max_seats": event[3],
            "rsvp_count": rsvp_count,
            "attendees": attendees
        })

    conn.close()
    return render_template('index.html', events=event_data)
@app.route('/create', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        name = request.form['name']
date = request.form['date']
max_seats = request.form['max_seats']
admin_password = request.form['admin_password']

conn = sqlite3.connect('events.db')
conn.execute("""
    INSERT INTO events (name, date, max_seats, admin_password)
    VALUES (?, ?, ?, ?)
""", (name, date, max_seats, admin_password))
        conn.commit()
        conn.close()
        return redirect('/')

    return render_template('create_event.html')
@app.route('/rsvp/<int:event_id>', methods=['POST'])
def rsvp(event_id):
    user_name = request.form['user_name']
    email = request.form['email']

    conn = sqlite3.connect('events.db')
    conn.execute("INSERT INTO rsvps (event_id, user_name, email) VALUES (?, ?, ?)",
                 (event_id, user_name, email))
    conn.commit()
    conn.close()

    return redirect('/')
@app.route("/admin/<int:event_id>", methods=["GET", "POST"])
def admin_dashboard(event_id):
    conn = sqlite3.connect("events.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == "POST":
        password = request.form["password"]

        cursor.execute("SELECT admin_password FROM events WHERE id = ?", (event_id,))
        event = cursor.fetchone()

        if event and event["admin_password"] == password:
            cursor.execute("SELECT * FROM attendees WHERE event_id = ?", (event_id,))
            attendees = cursor.fetchall()
            return render_template("admin.html", attendees=attendees)

        else:
            return "Wrong Password"

    return render_template("admin_login.html", event_id=event_id)


if __name__ == '__main__':
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port)
