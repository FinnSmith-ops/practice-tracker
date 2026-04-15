from flask import Flask, request, render_template, session
import sqlite3

app = Flask(__name__)
app.secret_key = "devkey"

DB_PATH = "database.db"

def get_db():
    return sqlite3.connect(DB_PATH)

@app.route("/")
def index():
    return render_template("hello.html")

@app.route("/login")
def login():
    return render_template("login_form.html")

@app.route("/logged_in", methods=["POST"])
def logged_in():
    Username = request.form["Username"]
    Password = request.form["Password"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS User_info(
            User_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT NOT NULL UNIQUE,
            Password TEXT NOT NULL
        )
    """)

    cursor.execute(
        "SELECT User_ID FROM User_info WHERE Username=? AND Password=?",
        (Username, Password),
    )

    result = cursor.fetchone()
    conn.close()

    if result is None:
        return render_template("bad_login.html")

    session["User_ID"] = result[0]
    return render_template("good_login.html")

@app.route("/registration")
def registration():
    return render_template("registration_form.html")

@app.route("/registered", methods=["POST"])
def register():
    Username = request.form["Username"]
    Password = request.form["Password"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS User_info(
            User_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT NOT NULL UNIQUE,
            Password TEXT NOT NULL
        )
    """)

    try:
        cursor.execute(
            "INSERT INTO User_info (Username, Password) VALUES (?, ?)",
            (Username, Password),
        )
    except sqlite3.IntegrityError:
        conn.close()
        return render_template("username_taken.html")

    cursor.execute(
        "SELECT User_ID FROM User_info WHERE Username=? AND Password=?",
        (Username, Password),
    )
    result = cursor.fetchone()

    conn.commit()
    conn.close()

    session["User_ID"] = result[0]
    return render_template("good_login.html")

@app.route("/add_song")
def add_song():
    return render_template("add_song.html")

@app.route("/add_goal")
def add_goal():
    return render_template("add_goal.html")

@app.route("/song", methods=["POST"])
def show_song():
    if not session.get("User_ID"):
        return render_template("not_logged_in.html")

    song = request.form["song"].strip()
    date = request.form["date"]
    time = int(request.form["time"])

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS User_Songs(
            User_ID INT,
            song TEXT,
            date TEXT,
            time INTEGER
        )
    """)

    cursor.execute(
        "INSERT INTO User_Songs VALUES (?, ?, ?, ?)",
        (session["User_ID"], song, date, time),
    )

    conn.commit()
    conn.close()

    return render_template("home.html")

@app.route("/goal", methods=["POST"])
def goal():
    if not session.get("User_ID"):
        return render_template("not_logged_in.html")

    song = request.form["song"].strip()
    date = request.form["date"]
    time = int(request.form["time"])

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS User_Goals(
            User_ID INT,
            song TEXT,
            date TEXT,
            time INTEGER
        )
    """)

    cursor.execute(
        "SELECT 1 FROM User_Goals WHERE User_ID=? AND song=?",
        (session["User_ID"], song),
    )

    if cursor.fetchone():
        conn.close()
        return render_template("already_goal.html")

    cursor.execute(
        "INSERT INTO User_Goals VALUES (?, ?, ?, ?)",
        (session["User_ID"], song, date, time),
    )

    conn.commit()
    conn.close()

    return render_template("home.html")

@app.route("/all_songs")
def all_songs():
    if not session.get("User_ID"):
        return render_template("not_logged_in.html")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS User_Songs(
            User_ID INT,
            song TEXT,
            date TEXT,
            time INTEGER
        )
    """)

    cursor.execute("""
        SELECT song, SUM(time)
        FROM User_Songs
        WHERE User_ID=?
        GROUP BY song
    """, (session["User_ID"],))

    data = cursor.fetchall()
    conn.close()

    if not data:
        return render_template("add_song.html")

    return render_template("all_songs.html", quant=len(data), data=data)

@app.route("/goals")
def see_goal():
    if not session.get("User_ID"):
        return render_template("not_logged_in.html")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS User_Songs(
            User_ID INT,
            song TEXT,
            date TEXT,
            time INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS User_Goals(
            User_ID INT,
            song TEXT,
            date TEXT,
            time INTEGER
        )
    """)

    cursor.execute("""
        SELECT g.song, IFNULL(SUM(s.time), 0), g.time
        FROM User_Goals g
        LEFT JOIN User_Songs s
        ON g.User_ID = s.User_ID AND g.song = s.song
        WHERE g.User_ID = ?
        GROUP BY g.song
    """, (session["User_ID"],))

    data = cursor.fetchall()
    conn.close()

    if not data:
        return render_template("add_goal.html")

    song_names = []
    goal_percents = []
    goals = []

    for song, total_time, goal_time in data:
        total_time = int(total_time)
        goal_time = int(goal_time)
        print(goal_time)
        print(total_time)
        percent = 0 if goal_time == 0 else round((total_time / (goal_time*60)) * 100, 2)

        song_names.append(song)
        goal_percents.append(percent)
        goals.append(goal_time)

    return render_template(
        "show_goal.html",
        goals=goals,
        goal_percents=goal_percents,
        song_names=song_names
    )

if __name__ == "__main__":
    app.run(debug=True)