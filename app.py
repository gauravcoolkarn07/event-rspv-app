from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('events.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    date TEXT,
                    max_seats INTEGER)''')

    conn.execute('''CREATE TABLE IF NOT EXISTS rsvps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER,
                    user_name TEXT,
                    email TEXT)''')
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

        conn = sqlite3.connect('events.db')
        conn.execute("INSERT INTO events (name, date, max_seats) VALUES (?, ?, ?)",
                     (name, date, max_seats))
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
if __name__ == '__main__':
    app.run(debug=True)