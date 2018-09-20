#Proximity Occupation Sensor
#HTML Server
#
#13197963
#
#
#9/8/18
#
# TODO: get information from sql database and display using flask on html
#
#

#Libraries

#time libraries
import time
import datetime

#sql
import sqlite3
sqlDB = sqlite3.connect("seating.db", check_same_thread=False)
cursor = sqlDB.cursor()

#flask
from flask import Flask, render_template, redirect,url_for



app = Flask(__name__)

@app.route("/seating")
def seating():
    cursor.execute("SELECT * FROM seating ORDER BY location ASC")
    return render_template("seating.html", seats = cursor.fetchall())

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/howto")
def howto():
    return render_template("howto.html")

@app.route("/")
def redirection():
    return redirect(url_for('index'))



if __name__ == "__main__":
    app.run(debug = True)






