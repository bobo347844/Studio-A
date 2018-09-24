#Proximity Occupation Sensor
#HTML Server
#Version 1.4
#13197963
#
#
#14/9/18
#
#
#
#

#Libraries

#system libraries
import os

#time libraries
import time
import datetime

#sql
import sqlite3
#connect to sql database
sqlDB = sqlite3.connect("seating.db", check_same_thread=False)
cursor = sqlDB.cursor()

#flask
from flask import Flask, render_template, redirect,url_for, send_from_directory
app = Flask(__name__)

#send seating page + database info
@app.route("/seating")
def seating():
    cursor.execute("SELECT * FROM seating ORDER BY location ASC")
    return render_template("seating.html", seats = cursor.fetchall())

#send about page + nothing
@app.route("/about")
def about():
    return render_template("about.html")

#send index page + nothing
@app.route("/index")
def index():
    return render_template("index.html")

#send howto page + nothing
@app.route("/howto")
def howto():
    return render_template("howto.html")

#catches requests for favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

#catches requests for pages that dont exit/bad redirects
@app.route("/")
def redirection():
    return redirect(url_for('index'))


#run the program on the localhost
if __name__ == "__main__":
    app.run(host="0.0.0.0")






