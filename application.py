# functions to import
import chardet
import cs50
import csv
import flask
import flask_session
import glob
import helpers
import os
import sys
import tempfile
import werkzeug

app = flask.Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = "arbitraryvalue1234567890-="

# define the path to the upload folder - https://pythonbasics.org/flask-upload-file/
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# specifies the maximum size (in bytes) of the files to be uploaded
#app.config['MAX_CONTENT_PATH']

# create upload folder https://stackoverflow.com/questions/42424853/saving-upload-in-flask-only-saves-to-project-root
os.makedirs(os.path.join(app.instance_path, 'databases'), exist_ok=True)

# Configue SQL database
db = cs50.SQL("sqlite:///instance/database.db")

# Configure session to use filesystem (instead of signed cookies) from finance problem set
#app.config["SESSION_FILE_DIR"] = tempfile.mkdtemp()
#app.config["SESSION_PERMANENT"] = False
#app.config["SESSION_TYPE"] = "filesystem"
#flask_session.Session(app)

# index page
@app.route("/", methods=["GET", "POST"])
def index():
    if flask.request.method == "GET":
        
        # check if a SQLite database exists to store data, create if not
        if not os.path.isfile(os.path.join(app.instance_path, 'database.db')):
            helpers.create(app.instance_path)
        
        # summarise current status
        totals = db.execute("SELECT SUM(solution_master_species), SUM(solution_species), SUM(phases) FROM db_meta")
        total_SMS = totals[0].get("SUM(solution_master_species)")
        total_SS = totals[0].get("SUM(solution_species)")
        total_PH = totals[0].get("SUM(phases)")

        flask.flash("Hello!")
        return flask.render_template("index.html", total_SMS=total_SMS, total_SS=total_SS, total_PH=total_PH)
    else:
        if flask.request.form.get("load"):


            # upload a file from a user's computer and store
            #https://pythonbasics.org/flask-upload-file/
            #https://stackoverflow.com/questions/42424853/saving-upload-in-flask-only-saves-to-project-root
            #https://stackoverflow.com/questions/11817182/uploading-multiple-files-with-flask

            # get the list of files uploaded
            files = flask.request.files.getlist("file")
            # cycle through each file
            for file in files:
                #print(file)
                #print(file.filename)
                # upload to server
                file.save(os.path.join(app.instance_path, 'databases', werkzeug.utils.secure_filename(file.filename)))
                # if a file in the databases folder has the same name as one that was just uploaded (i.e. was not uploaded on a previous occasion) then load it
                for database in glob.glob(os.path.join(app.instance_path, 'databases','*')):
                    if os.path.basename(database) == file.filename:
                        #print(os.path.basename(database))
                        helpers.load(database)



            #print(os.path.join(app.instance_path, 'databases'))

            flask.flash("loaded!")
            return flask.redirect("/")

        elif flask.request.form.get("overview"):
            return flask.redirect("/overview")

        elif flask.request.form.get("search"):
            return flask.redirect("/search")

        else:
            return flask.redirect("/")

# summary page
@app.route("/overview")
def summary():
    flask.flash("overviewed!")

    summary = db.execute("SELECT * FROM db_meta")


    return flask.render_template("summary.html", summary=summary)

@app.route("/search", methods=["GET", "POST"])
def search():
    if flask.request.method == "GET":
        flask.flash("Search!")
        return flask.render_template("search.html")
    else:

        searchtype = flask.request.form.get("type")
        print(searchtype)
        if searchtype == "solution_master_species":
            element = flask.request.form.get("element")
            species = flask.request.form.get("species")

            if flask.request.form.get("primary") == "all":
                primary_ms = 1
                secondary_ms = 1
            elif flask.request.form.get("primary") == "primary":
                primary_ms = 1
                secondary_ms = -1
            elif flask.request.form.get("primary") == "secondary":
                primary_ms = -1
                secondary_ms = 1

            if element:
                print(flask.request.form.get("element"))
                results = db.execute(
                    "SELECT solution_master_species.id AS ID, element AS Element, master_species AS Species, primary_master_species AS 'Primary Master Species', secondary_master_species AS 'Secondary Master Species', alkalinity AS Alkalinity, element_gfw AS 'Gram Formula Weight', db_meta.name AS Database FROM solution_master_species JOIN db_meta ON solution_master_species.db_id = db_meta.id WHERE element GLOB ? AND (primary_master_species = ? OR secondary_master_species = ?)", "*" + element + "*", primary_ms, secondary_ms)
                # replace 1s and 0s with ticks and crosses
                for i in range(len(results)):
                    for old, new in [("0", "\u2716"), ("1", "\u2714")]:
                        results[i]["Primary Master Species"] = str(results[i]["Primary Master Species"]).replace(old, new)
                        results[i]["Secondary Master Species"] = str(results[i]["Secondary Master Species"]).replace(old, new)

                return flask.render_template("results.html", results=results)
            elif species:
                results = db.execute(
                    "SELECT solution_master_species.id AS ID, element AS Element, master_species AS Species, primary_master_species AS 'Primary Master Species', secondary_master_species AS 'Secondary Master Species',alkalinity AS Alkalinity, element_gfw AS 'Gram Formula Weight', db_meta.name AS Database FROM solution_master_species JOIN db_meta ON solution_master_species.db_id = db_meta.id WHERE master_species = ? AND (primary_master_species = ? OR secondary_master_species = ?)", species, primary_ms, secondary_ms)
                # replace 1s and 0s with ticks and crosses
                for i in range(len(results)):
                    for old, new in [("0", "\u2716"), ("1", "\u2714")]:
                        results[i]["Primary Master Species"] = str(results[i]["Primary Master Species"]).replace(old, new)
                        results[i]["Secondary Master Species"] = str(results[i]["Secondary Master Species"]).replace(old, new)

                return flask.render_template("results.html", results=results)
            elif element and species:
                results = db.execute(
                    "SELECT solution_master_species.id AS ID, element AS Element, master_species AS Species,primary_master_species AS 'Primary Master Species', secondary_master_species AS 'Secondary Master Species', alkalinity AS Alkalinity, element_gfw AS 'Gram Formula Weight', db_meta.name AS Database FROM solution_master_species JOIN db_meta ON solution_master_species.db_id = db_meta.id WHERE element GLOB ? AND master_species = ? AND (primary_master_species = ? OR secondary_master_species = ?)", "*" + element + "*", species, primary_ms, secondary_ms)
                # replace 1s and 0s with ticks and crosses
                for i in range(len(results)):
                    for old, new in [("0", "\u2716"), ("1", "\u2714")]:
                        results[i]["Primary Master Species"] = str(results[i]["Primary Master Species"]).replace(old, new)
                        results[i]["Secondary Master Species"] = str(results[i]["Secondary Master Species"]).replace(old, new)

                    return flask.render_template("results.html", results=results)
            else:
                flask.flash("Must specify element and/or species.")

        elif searchtype == "solution_species":
            flask.flash("Solution species!!")
            print(flask.request.form.get("defined_species"))
            results = db.execute(
                "SELECT solution_species.id AS ID, defined_species AS 'Defined Species', equation AS Equation, primary_master_species AS 'Primary Master Species', secondary_master_species AS 'Secondary Master Species', log_k AS 'log K', delta_h AS 'ΔH', delta_h_units AS '(units)', db_meta.name AS Database FROM solution_species JOIN db_meta ON solution_species.db_id = db_meta.id WHERE defined_species = ?", flask.request.form.get("defined_species"))
            # replace 1s and 0s with ticks and crosses
            for i in range(len(results)):
                for old, new in [("0", "\u2716"), ("1", "\u2714")]:
                    results[i]["Primary Master Species"] = str(results[i]["Primary Master Species"]).replace(old, new)
                    results[i]["Secondary Master Species"] = str(results[i]["Secondary Master Species"]).replace(old, new)

            return flask.render_template("results.html", results=results)

        elif searchtype == "phases":
            flask.flash("Phases!!")
            phase_name = flask.request.form.get("name")
            formula = flask.request.form.get("formula")
            if phase_name:
                print(phase_name)
                results = db.execute(
                    "SELECT phases.id AS ID, phases.name AS Name, defined_phase AS Formula, equation AS Equation, log_k AS 'log K', delta_h AS 'ΔH', delta_h_units AS '(units)', db_meta.name AS Database FROM phases JOIN db_meta ON phases.db_id = db_meta.id WHERE phases.name = ?", phase_name)
                return flask.render_template("results.html", results=results)
            elif formula:
                print(formula)
                results = db.execute(
                    "SELECT phases.id AS ID, phases.name AS Name, defined_phase AS Formula, equation AS Equation, log_k AS 'log K', delta_h AS 'ΔH', delta_h_units AS '(units)', db_meta.name AS Database FROM phases JOIN db_meta ON phases.db_id = db_meta.id WHERE defined_phase = ?", formula)
                return flask.render_template("results.html", results=results)
            else:
                flask.flash("Must specify phase name or formula.")
        else:
            flask.flash("Must specify a valid selection of data to search")

        return flask.render_template("search.html")