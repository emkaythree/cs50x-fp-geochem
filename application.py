# functions to import
import chardet
import cs50
import csv
import flask
import flask_session
import glob
import os
import sys
import tempfile

app = flask.Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = "arbitraryvalue1234567890-="

# Configue SQL database
db = cs50.SQL("sqlite:///database1.db")

# Configure session to use filesystem (instead of signed cookies) from finance problem set
#app.config["SESSION_FILE_DIR"] = tempfile.mkdtemp()
#app.config["SESSION_PERMANENT"] = False
#app.config["SESSION_TYPE"] = "filesystem"
#flask_session.Session(app)

# index page
@app.route("/", methods=["GET", "POST"])
def index():
    if flask.request.method == "GET":

        # summarise current status
        summary = db.execute("SELECT SUM(solution_master_species) FROM db_meta")

        flask.flash("Hello!")
        return flask.render_template("index.html", summary=summary)
    else:
        if flask.request.form.get("load"):
            flask.flash("loaded!")
            return flask.redirect("/")

        elif flask.request.form.get("overview"):
            return flask.redirect("/overview")
        else:
            return flask.redirect("/")

# summary page
@app.route("/overview")
def summary():
    flask.flash("overviewed!")
    return flask.render_template("summary.html")

