from flask import Flask, request
from flask import render_template
import sqlite3

from flask import session





app= Flask(__name__)
app.secret_key='key'
@app.route("/login")
def login():
    return render_template("login_form.html")
@app.route("/logged_in", methods=["POST", "GET"])
def logged_in():
    Username = request.form["Username"]
    Password = request.form["Password"]
    connection = sqlite3.connect(r"c:\Users\finns\OneDrive\Documents\SQLite\Flask_music.db")
    cursor = connection.cursor()
    sql = 'select User_ID from user_info where Username=? and Password=?'
    cursor.execute(sql, (Username, Password))
    result = cursor.fetchone()
    if result == None:
        return render_template("bad_login.html")
    if result:
        session["User_ID"] = result[0]
    connection.commit()
    connection.close()
    return render_template("good_login.html")
@app.route("/registration", methods=["POST", "GET"])
def registration():
    return render_template("registration_form.html")

@app.route("/registered", methods=["POST", "GET"])
def register():
    Username = request.form["Username"]
    Password = request.form["Password"]
    connection = sqlite3.connect(r"c:\Users\finns\OneDrive\Documents\SQLite\Flask_music.db")
    cursor = connection.cursor()
    sql = 'create table if not exists User_info(User_ID INTEGER PRIMARY KEY AUTOINCREMENT, Username varchar(50) not null, Password varchar(20) not null)'
    cursor.execute(sql)
    sql = 'insert into User_info(Username, Password) values(?, ?)' 
    try:
        cursor.execute(sql, (Username, Password))
    except sqlite3.IntegrityError:
        return render_template("username_taken.html")
    sql='select User_ID from User_info where Username=? and Password=?'
    cursor.execute(sql, (Username, Password))
    result = cursor.fetchone()
    if result:
        session["User_ID"] = result[0]
    connection.commit()
    connection.close()

    return render_template("good_login.html")
@app.route("/")
def index():
    return render_template("hello.html")

@app.route("/add_song", methods = ["GET", "POST"])
def add_song():
    return render_template('add_song.html') 

@app.route("/add_goal")
def add_goal(): 
    return render_template("add_goal.html")


@app.route("/goal", methods = ["POST"]) 
def goal():   
    song = request.form["song"]
    time = request.form["time"]
    date = request.form["date"]

    connection = sqlite3.connect(r"c:\Users\finns\OneDrive\Documents\SQLite\Flask_Music.db")
    cursor = connection.cursor()
    sql = 'create table if not exists User_Goals(User_ID INT not null, song varchar(50) not null, date varchar(20) not null, time varchar(20) not null, foreign key(User_ID) references users(User_ID))'
    cursor.execute(sql)
    sql = 'select song from User_goals'
    cursor.execute(sql)
    songs = cursor.fetchall()
    final = []
    print(len(songs))
    for i in range(len(songs)):
        if songs[i][0] == song:
            final.append(song)

    if song in final:
        return render_template('already_goal.html')
    sql = 'insert into User_Goals(User_ID, song, date, time) values(?, ?, ?, ?)'
    try: 
        cursor.execute(sql, (session.get("User_ID"), song, date, time))
    except sqlite3.IntegrityError:
        return render_template("not_logged_in.html")
    connection.commit()
    connection.close()
    return render_template("home.html")

@app.route("/song", methods = ["POST"])
def show_song():
    
    song = request.form["song"]
    date = request.form["date"]
    time = request.form["time"]

    connection = sqlite3.connect(r"c:\Users\finns\OneDrive\Documents\SQLite\Flask_Music.db")
    cursor = connection.cursor()
    sql = 'create table if not exists User_Songs(User_ID INT not null, song varchar(50) not null, date varchar(20) not null, time varchar(20) not null, foreign key(User_ID) references users(User_ID))'
    cursor.execute(sql)
    sql = 'insert into User_Songs(User_ID, song, date, time) values(?, ?, ?, ?)' 
    try:
        cursor.execute(sql, (session.get("User_ID"), song, date, time))
    except sqlite3.IntegrityError:
        return render_template("not_logged_in.html")
    connection.commit()
    connection.close()
    return render_template("home.html")

@app.route("/all_songs")
def all_songs():
    connection = sqlite3.connect(r"c:\Users\finns\OneDrive\Documents\SQLite\Flask_Music.db")
    cursor = connection.cursor()
    sql = 'select song, SUM(time) from User_Songs where User_ID = ? Group by song'
    cursor.execute(sql, (session.get("User_ID"),))
    data = cursor.fetchall()
    print(data)
    quant = len(data)
    return render_template("all_songs.html", quant = quant, data = data)

@app.route("/goals")
def see_goal(): 
    if session.get("User_ID") == None:
        return render_template("not_logged_in.html")
    connection = sqlite3.connect(r"c:\Users\finns\OneDrive\Documents\SQLite\Flask_Music.db")
    cursor = connection.cursor()
    sql = 'select * from User_Songs x join User_goals y on x.User_ID=y.User_ID and x.song = y.song where x.User_ID = ? '

    cursor.execute(sql, (session.get("User_ID"),))
    data = cursor.fetchall()
    print(data)

    time = 0
    total_time=[]
    song_names = []
    goals = []
    song = data[0][1]
    
    # percent_to_goal = (int(total_time/60))/int(goal)
    for i in range(len(data)):
        new_song = data[i][1]
        if i == len(data)-1:
            song_names.append(song)
            time+=data[i][3]
            total_time.append(time)
            goals.append(data[i][7])

        if new_song == song:
            
            time += data[i][3]

        else:
            goals.append(data[i][7])
            total_time.append(time)
            time = 0
            time += data[i][3]
            song_names.append(song)
            song = new_song
    goal_percents = []
    
    for i in total_time:
        print(i)
        goal_percents.append((i/60))
    print(goal_percents)
    for i in range(len(goal_percents)):
        goal_percents[i] = round(((float(goal_percents[i]))/float(goals[i])*100), 2)
    print(goals)
    print(goal_percents)
    print(song_names)     
    print(total_time)
    connection.commit()
    connection.close()
    return render_template("show_goal.html", goals = goals,  goal_percents = goal_percents, song_names = song_names)


if __name__ == '__main__':
    app.run()

