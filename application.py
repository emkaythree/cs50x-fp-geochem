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
        totals = db.execute("SELECT SUM(solution_master_species), SUM(solution_species), SUM(phases) FROM db_meta")
        total_SMS = totals[0].get("SUM(solution_master_species)")
        total_SS = totals[0].get("SUM(solution_species)")
        total_PH = totals[0].get("SUM(phases)")

        flask.flash("Hello!")
        return flask.render_template("index.html", total_SMS=total_SMS, total_SS=total_SS, total_PH=total_PH)
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

    summary = db.execute("SELECT * FROM db_meta")
    

    return flask.render_template("summary.html", summary=summary)

