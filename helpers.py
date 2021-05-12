# functions to import
import chardet
import cs50
import csv
import flask
import glob
import os
import sys

# function to create a SQLite database in the instance directory
def create(path):
    # create SQLite database file
    open(os.path.join(path, 'database.db'), "w").close()

    # create tables in database
    db = cs50.SQL("sqlite:///instance/database.db")

    # table for storing metadata about geochemical databases - name and number of species
    db.execute("CREATE TABLE IF NOT EXISTS db_meta (id INTEGER, name TEXT NOT NULL, solution_master_species INTEGER, solution_species INTEGER, phases INTEGER, PRIMARY KEY(id))")

    # table for storing information about solution master species
    db.execute("CREATE TABLE IF NOT EXISTS solution_master_species (id INTEGER, element TEXT NOT NULL, master_species TEXT, primary_master_species INTEGER DEFAULT 0, secondary_master_species INTEGER DEFAULT 0, alkalinity REAL, gfw_formula TEXT, element_gfw REAL, db_id INTEGER, PRIMARY KEY(id), FOREIGN KEY(db_id) REFERENCES db_meta(id))")

    # table for storing information about solution species
    db.execute("CREATE TABLE IF NOT EXISTS solution_species (id INTEGER, equation TEXT, reactants TEXT, defined_species TEXT, primary_master_species INTEGER DEFAULT 0, secondary_master_species INTEGER DEFAULT 0, other_products TEXT, log_k REAL, delta_h REAL, delta_h_units TEXT DEFAULT [kJ/mol], analytic_1 REAL, analytic_2 REAL, analytic_3 REAL, analytic_4 REAL, analytic_5 REAL, analytic_6 REAL, gamma_a REAL, gamma_b REAL, llnl_gamma REAL, co2_llnl_gamma INTEGER DEFAULT 0, dw REAL DEFAULT 0, Vm TEXT, millero TEXT, activity_water INTEGER DEFAULT 0, add_log_k_named_expression TEXT, add_log_k_coefficient REAL, erm_ddl REAL DEFAULT 1.0, no_check INTEGER DEFAULT 0, mole_balance TEXT, db_id INTEGER, PRIMARY KEY(id), FOREIGN KEY(db_id) REFERENCES db_meta(id))")

    # table for storing information about phases
    db.execute("CREATE TABLE IF NOT EXISTS phases (id INTEGER, name TEXT, equation TEXT, defined_phase TEXT, other_reactants TEXT, dissolved_products TEXT, log_k REAL, add_log_k_named_expression TEXT, add_log_k_coefficient REAL, delta_h REAL, delta_h_units TEXT DEFAULT [kJ/mol], analytic_1 REAL, analytic_2 REAL, analytic_3 REAL, analytic_4 REAL, analytic_5 REAL, analytic_6 REAL, Vm REAL DEFAULT 0, Vm_units TEXT DEFAULT [cm^3/mol], T_c REAL, P_c REAL, omega REAL, db_id INTEGER, PRIMARY KEY(id), FOREIGN KEY(db_id) REFERENCES db_meta(id))")

# function to load PHREEQC database files into the SQLite database
def load(datfile):
    print(datfile.filename)

    # access sqlite database
    db = cs50.SQL("sqlite:///instance/database.db")

    # create an entry in the db_meta table for the current .dat file if it doesn't already exist
    if len(db.execute("SELECT * FROM db_meta WHERE name = ?", datfile.filename)) != 1:
        db.execute("INSERT INTO db_meta (name) VALUES (?)", datfile.filename)

    # set a variable to keep track of current .dat file
    """TODO"""