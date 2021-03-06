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

# check if a SQLite database exists to store data, create if not
if not os.path.isfile(os.path.join(app.instance_path, 'database.db')):
    helpers.create(app.instance_path)

# Configue SQL database
db = cs50.SQL("sqlite:///instance/database.db")

# Configure session to use filesystem (instead of signed cookies) from finance problem set
#app.config["SESSION_FILE_DIR"] = tempfile.mkdtemp()
#app.config["SESSION_PERMANENT"] = False
#app.config["SESSION_TYPE"] = "filesystem"
#flask_session.Session(app)

# index page and upload interface
@app.route("/", methods=["GET", "POST"])
def index():
    if flask.request.method == "GET":

        # summarise current status
        totals = db.execute("SELECT SUM(solution_master_species), SUM(solution_species), SUM(phases) FROM db_meta")
        total_SMS = totals[0].get("SUM(solution_master_species)")
        total_SS = totals[0].get("SUM(solution_species)")
        total_PH = totals[0].get("SUM(phases)")

        total_distinct_SMS = db.execute("SELECT COUNT(DISTINCT element) FROM solution_master_species")
        total_distinct_SS = db.execute("SELECT COUNT(DISTINCT defined_species) FROM solution_species")
        total_distinct_PH = db.execute("SELECT COUNT(DISTINCT name) FROM phases")


        return flask.render_template("index.html", total_SMS=total_SMS, total_SS=total_SS, total_PH=total_PH, total_distinct_SMS=total_distinct_SMS[0].get("COUNT(DISTINCT element)"), total_distinct_SS=total_distinct_SS[0].get("COUNT(DISTINCT defined_species)"), total_distinct_PH=total_distinct_PH[0].get("COUNT(DISTINCT name)"))
    else:
        if flask.request.form.get("load"):

            # upload a file from a user's computer and store
                #https://pythonbasics.org/flask-upload-file/
                #https://stackoverflow.com/questions/42424853/saving-upload-in-flask-only-saves-to-project-root
                #https://stackoverflow.com/questions/11817182/uploading-multiple-files-with-flask

            # check that a file was actually selected - https://stackoverflow.com/questions/23600059/check-flask-upload-if-user-does-not-selected-file
            if flask.request.files["file"].filename == "":
                flask.flash("Please select file(s) to upload")
                return flask.redirect("/")

            # get the list of files uploaded
            files = flask.request.files.getlist("file")
            # cycle through each file
            for file in files:
                # upload to server
                file.save(os.path.join(app.instance_path, 'databases', werkzeug.utils.secure_filename(file.filename)))
                # if a file in the databases folder has the same name as one that was just uploaded (i.e. was not uploaded on a previous occasion) then load it
                for database in glob.glob(os.path.join(app.instance_path, 'databases','*')):
                    if os.path.basename(database) == file.filename:
                        helpers.load(database)

            flask.flash("Loaded!")
            return flask.redirect("/")

        else:
            return flask.redirect("/")

# delete a database
@app.route("/delete")
def delete():

    # get the database to delete
    db_id = flask.request.args.get("id")
    db_name = db.execute("SELECT name FROM db_meta WHERE id = ?", db_id)

    # delete entry from db_meta table and, through ON DELETE CASCADE, delete any entries in the other tables with the corresponding db_id
    db.execute("DELETE FROM db_meta WHERE id = ?", db_id)

    flask.flash("Deleted " + db_name[0]["name"])
    return flask.redirect("/overview")

# page to look inside each individual database by master species/solution species/phases
@app.route("/details")
def details():

    # get the requested database and type of data being searched for
    db_id = flask.request.args.get("id")
    search_type = flask.request.args.get("type")

    if search_type == "solution_master_species":
        results = db.execute(
            "SELECT solution_master_species.id AS ID, element AS Element, master_species AS Species, primary_master_species AS 'Primary Master Species', secondary_master_species AS 'Secondary Master Species', alkalinity AS Alkalinity, element_gfw AS 'Gram Formula Weight', db_meta.name AS Database FROM solution_master_species JOIN db_meta ON solution_master_species.db_id = db_meta.id WHERE db_id = ?", db_id)

    elif search_type == "solution_species":
        results = db.execute(
            "SELECT solution_species.id AS ID, defined_species AS 'Defined Species', equation AS Equation, primary_master_species AS 'Primary Master Species', secondary_master_species AS 'Secondary Master Species', log_k AS 'log K', delta_h AS '??H', delta_h_units AS '(units)', db_meta.name AS Database FROM solution_species JOIN db_meta ON solution_species.db_id = db_meta.id WHERE db_id = ?", db_id)

    elif search_type == "phases":
        results = db.execute(
                    "SELECT phases.id AS ID, phases.name AS Name, defined_phase AS Formula, equation AS Equation, log_k AS 'log K', delta_h AS '??H', delta_h_units AS '(units)', db_meta.name AS Database FROM phases JOIN db_meta ON phases.db_id = db_meta.id WHERE db_id = ?", db_id)

    # replace 1s and 0s with ticks and crosses
    if search_type == "solution_master_species" or search_type == "solution_species":
        for i in range(len(results)):
            for old, new in [("0", "\u2716"), ("1", "\u2714")]:
                results[i]["Primary Master Species"] = str(results[i]["Primary Master Species"]).replace(old, new)
                results[i]["Secondary Master Species"] = str(results[i]["Secondary Master Species"]).replace(old, new)

    return flask.render_template("results.html", results=results)

# function to search by clicking on results from a search result
@app.route("/details2")
def details2():
    # get type of data to search and item being searched for
    search_item = flask.request.args.get("item")

    search_type = flask.request.args.get("type")

    #print(search_item, search_parameter, search_type)

    if search_type == "solution_master_species":
        search_parameter = flask.request.args.get("key").replace('Species', 'master_species')
        results = db.execute(
            "SELECT solution_master_species.id AS ID, element AS Element, master_species AS Species, primary_master_species AS 'Primary Master Species', secondary_master_species AS 'Secondary Master Species', alkalinity AS Alkalinity, element_gfw AS 'Gram Formula Weight', db_meta.name AS Database FROM solution_master_species JOIN db_meta ON solution_master_species.db_id = db_meta.id WHERE solution_master_species.? = ?", search_parameter, search_item)

    elif search_type == "solution_species":

        results = db.execute(
            "SELECT solution_species.id AS ID, defined_species AS 'Defined Species', equation AS Equation, primary_master_species AS 'Primary Master Species', secondary_master_species AS 'Secondary Master Species', log_k AS 'log K', delta_h AS '??H', delta_h_units AS '(units)', db_meta.name AS Database FROM solution_species JOIN db_meta ON solution_species.db_id = db_meta.id WHERE solution_species.? = ?", search_parameter, search_item)

    elif search_type == "phases":
        search_parameter = flask.request.args.get("key").replace('Formula', 'defined_phase')
        results = db.execute(
                    "SELECT phases.id AS ID, phases.name AS Name, defined_phase AS Formula, equation AS Equation, log_k AS 'log K', delta_h AS '??H', delta_h_units AS '(units)', db_meta.name AS Database FROM phases JOIN db_meta ON phases.db_id = db_meta.id WHERE phases.? = ?", search_parameter, search_item)


    return flask.render_template("results.html", results=results)

# summary page
@app.route("/overview")
def summary():

    summary = db.execute("SELECT * FROM db_meta")

    return flask.render_template("summary.html", summary=summary)

# search function
@app.route("/search", methods=["GET", "POST"])
def search():
    # show search page
    if flask.request.method == "GET":
        return flask.render_template("search.html")
    # search function
    else:
        searchtype = flask.request.form.get("type")

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
            # if searching by element
            if element:
                results = db.execute(
                    "SELECT solution_master_species.id AS ID, element AS Element, master_species AS Species, primary_master_species AS 'Primary Master Species', secondary_master_species AS 'Secondary Master Species', alkalinity AS Alkalinity, element_gfw AS 'Gram Formula Weight', db_meta.name AS Database FROM solution_master_species JOIN db_meta ON solution_master_species.db_id = db_meta.id WHERE (element = ? OR element GLOB ?) AND (primary_master_species = ? OR secondary_master_species = ?)", element, element + "(*)", primary_ms, secondary_ms)
                if len(results) == 0:
                    flask.flash("No master species found")
                # replace 1s and 0s with ticks and crosses
                for i in range(len(results)):
                    for old, new in [("0", "\u2716"), ("1", "\u2714")]:
                        results[i]["Primary Master Species"] = str(results[i]["Primary Master Species"]).replace(old, new)
                        results[i]["Secondary Master Species"] = str(results[i]["Secondary Master Species"]).replace(old, new)

                return flask.render_template("results.html", results=results)
            # if searching by species
            elif species:
                results = db.execute(
                    "SELECT solution_master_species.id AS ID, element AS Element, master_species AS Species, primary_master_species AS 'Primary Master Species', secondary_master_species AS 'Secondary Master Species',alkalinity AS Alkalinity, element_gfw AS 'Gram Formula Weight', db_meta.name AS Database FROM solution_master_species JOIN db_meta ON solution_master_species.db_id = db_meta.id WHERE master_species = ? AND (primary_master_species = ? OR secondary_master_species = ?)", species, primary_ms, secondary_ms)
                if len(results) == 0:
                    flask.flash("No master species found")
                # replace 1s and 0s with ticks and crosses
                for i in range(len(results)):
                    for old, new in [("0", "\u2716"), ("1", "\u2714")]:
                        results[i]["Primary Master Species"] = str(results[i]["Primary Master Species"]).replace(old, new)
                        results[i]["Secondary Master Species"] = str(results[i]["Secondary Master Species"]).replace(old, new)

                return flask.render_template("results.html", results=results)
            # if searching by both element and species
            elif element and species:
                results = db.execute(
                    "SELECT solution_master_species.id AS ID, element AS Element, master_species AS Species,primary_master_species AS 'Primary Master Species', secondary_master_species AS 'Secondary Master Species', alkalinity AS Alkalinity, element_gfw AS 'Gram Formula Weight', db_meta.name AS Database FROM solution_master_species JOIN db_meta ON solution_master_species.db_id = db_meta.id WHERE element GLOB ? AND master_species = ? AND (primary_master_species = ? OR secondary_master_species = ?)", "*" + element + "*", species, primary_ms, secondary_ms)
                if len(results) == 0:
                    flask.flash("No master species found")
                # replace 1s and 0s with ticks and crosses
                for i in range(len(results)):
                    for old, new in [("0", "\u2716"), ("1", "\u2714")]:
                        results[i]["Primary Master Species"] = str(results[i]["Primary Master Species"]).replace(old, new)
                        results[i]["Secondary Master Species"] = str(results[i]["Secondary Master Species"]).replace(old, new)

                    return flask.render_template("results.html", results=results)
            else:
                flask.flash("Must specify element and/or species.")

        elif searchtype == "solution_species":
            results = db.execute(
                "SELECT solution_species.id AS ID, defined_species AS 'Defined Species', equation AS Equation, primary_master_species AS 'Primary Master Species', secondary_master_species AS 'Secondary Master Species', log_k AS 'log K', delta_h AS '??H', delta_h_units AS '(units)', db_meta.name AS Database FROM solution_species JOIN db_meta ON solution_species.db_id = db_meta.id WHERE defined_species = ?", flask.request.form.get("defined_species"))
            if len(results) == 0:
                flask.flash("No solution species found")
            # replace 1s and 0s with ticks and crosses
            for i in range(len(results)):
                for old, new in [("0", "\u2716"), ("1", "\u2714")]:
                    results[i]["Primary Master Species"] = str(results[i]["Primary Master Species"]).replace(old, new)
                    results[i]["Secondary Master Species"] = str(results[i]["Secondary Master Species"]).replace(old, new)

            return flask.render_template("results.html", results=results)

        elif searchtype == "phases":
            phase_name = flask.request.form.get("name")
            formula = flask.request.form.get("formula")
            # if searching by phase name
            if phase_name:
                results = db.execute(
                    "SELECT phases.id AS ID, phases.name AS Name, defined_phase AS Formula, equation AS Equation, log_k AS 'log K', delta_h AS '??H', delta_h_units AS '(units)', db_meta.name AS Database FROM phases JOIN db_meta ON phases.db_id = db_meta.id WHERE phases.name LIKE ?", phase_name)
                if len(results) == 0:
                    flask.flash("No phases found")
                return flask.render_template("results.html", results=results)
            # if searching by formula
            elif formula:
                results = db.execute(
                    "SELECT phases.id AS ID, phases.name AS Name, defined_phase AS Formula, equation AS Equation, log_k AS 'log K', delta_h AS '??H', delta_h_units AS '(units)', db_meta.name AS Database FROM phases JOIN db_meta ON phases.db_id = db_meta.id WHERE defined_phase = ?", formula)
                if len(results) == 0:
                    flask.flash("No phases found")
                return flask.render_template("results.html", results=results)
            else:
                flask.flash("Must specify phase name or formula.")
        else:
            flask.flash("Must specify a valid selection of data to search")

        return flask.render_template("search.html")