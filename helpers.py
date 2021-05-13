# functions to import
import chardet
import cs50
import csv
import flask
import glob
import os
import sys

# global variable to store the standard Phreeqc keyword data blocks
DATABLOCK = [
    "CALCULATE_VALUES",
    "EXCHANGE_MASTER_SPECIES",
    "EXCHANGE_SPECIES",
    "ISOTOPE_ALPHAS",
    "ISOTOPE_RATIOS",
    "ISOTOPES",
    "LLNL_AQUEOUS_MODEL_PARAMETERS",
    "NAMED_EXPRESSIONS",
    "PHASES",
    "PITZER",
    "RATES",
    "SIT",
    "SOLUTION_MASTER_SPECIES",
    "SOLUTION_SPECIES",
    "SURFACE_MASTER_SPECIES",
    "SURFACE_SPECIES",
    ]

# global dict to hold keywords
KEYWORDS = {
    # keywords used in solution species and phases data blocks
    "log_k": ["log_k", "-log_k", "logk", "-l", "-lo", "-log", "-log_", "-log_k", "-logk"],
    "add_log_k": ["-add_logk", "add_logk", "add_log_k", "-ad", "-add", "-add_", "-add_l", "-add_lo", "-add_log", "-add_log_", "-add_log_k"],
    "delta_h": ["delta_h", "-delta_h", "deltah", "-d", "-de", "-del", "-delt", "-delta", "-delta_", "-deltah"],
    "analytical_expression": [ "analytical_expression", "a_e", "ae" , "-a", "-a_", "-a_e", "-ae" ,"-an", "-ana", "-anal", "-analy", "-analyt", "-analyti", "-analytic", "-analytica", "-analytical", "-analytical_",
                                "-analytical_e", "-analytical_ex", "-analytical_exp", "-analytical_expr", "-analytical_expre", "-analytical_expres", "-analytical_express", "-analytical_expressi", "-analytical_expressio",
                                "-analytical_expression",],
    "Vm": ["-vm", "vm"],

    # keywords used in solution species data block only
    "dw": ["-dw", "dw",],
    "gamma": ["-gamma", "-g", "-ga", "-gam", "-gamm"],
    "Millero": ["millero", "-millero", "-mi", "-mil", "-mill", "-mille", "-miller"],
    "activity_water": ["activity_water", "-activity_water", "-ac", "-act", "-acti", "-activ", "-activi", "-activit", "-activity", "-activity_", "-activity_w", "-activity_wa", "-activity_wat", "-activity_wate"],
    "llnl_gamma": ["llnl_gamma", "-llnl_gamma", "-ll", "-lln", "-llnl", "-llnl_", "-llnl_g", "-llnl_ga", "-llnl_gam", "-llnl_gamm"],
    "co2_llnl_gamma": ["co2_llnl_gamma", "-co2_llnl_gamma", "-co", "-co2", "-co2_", "-co2_l", "-co2_ll", "-co2_lln", "-co2_llnl", "-co2_llnl_", "-co2_llnl_g", "-co2_llnl_ga", "-co2_llnl_gam", "-co2_llnl_gamm"],
    "erm_ddl": ["erm_ddl", "-erm_ddl", "-e", "-er", "-erm", "-erm_", "-erm_d", "-erm_dd"],
    "no_check": ["no_check", "-no_check", "-n", "-no", "-no_", "-no_c", "-no_ch", "-no_che", "-no_chec"],
    "mole_balance": ["mole_balance", "mass_balance", "mb", "-mass_balance", "-mb", "-mole_balance", "-m", "-mo", "-mol", "-mole", "-mole_", "-mole_b", "-mole_ba", "-mole_bal", "-mole_bala", "-mole_balan", "-mole_balanc"],

    # keywords used in phases data block only
    "t_c": ["-t_c", "t_c"],
    "p_c": ["-p_c", "p_c"],
    "omega": ["-omega", "omega"]

}

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

# Phreeqc databases can be inconsistent in terms of separating values with tabs or spaces so need to convert into a consistent format where anything separated by a space or a tab is a separate list item
def convert(row):
    # join all items in row into a string, and then split into a new list based upon the position of spaces
    temprow = (" ".join(row)).split(" ")

    # add not-empty list items to a new list
    newrow = []
    for item in temprow:
        if any(temprow) and item != "":
            newrow.append(item)

    return newrow

# function to load PHREEQC database files into the SQLite database
def load(datfile):
    print(datfile)

    # access sqlite database
    db = cs50.SQL("sqlite:///instance/database.db")

    # create an entry in the db_meta table for the current .dat file if it doesn't already exist
    if len(db.execute("SELECT * FROM db_meta WHERE name = ?", os.path.basename(datfile))) != 1:
        db.execute("INSERT INTO db_meta (name) VALUES (?)", os.path.basename(datfile))

    # set a variable to keep track of current .dat file
    current_dat = db.execute("SELECT id FROM db_meta WHERE name = ?", os.path.basename(datfile))
    print(current_dat)

    # tool to detect encoding of files - https://chardet.readthedocs.io/en/latest/usage.html
    detector = chardet.universaldetector.UniversalDetector()
    detector.reset()
    with open(datfile, "rb") as file:
        for row in file:
            detector.feed(row)
            if detector.done: break
        detector.close()
        encoding = detector.result["encoding"]
        print(encoding)

    # open file using detected encoding
    with open(datfile, "r", encoding=encoding) as file:
        reader = csv.reader(file, delimiter="\t")

        # scroll through file searching for keyword data blocks
        for row in reader:
            #print(row)
            # search for the solution master species keyword data block
            if "SOLUTION_MASTER_SPECIES" in (item.upper() for item in row):
                print("SOLUTION MASTER SPECIES FOUND")
                # search through data block
                for row in reader:
                    # convert rows to consistent formatting
                    newrow = convert(row)
                    # check that data exists on the current row
                    if newrow:
                        # ignore comments
                        if "#" in newrow[0]:
                            #print(newrow)
                            continue

                        # if encouner another keyword data block, then exit loop
                        elif newrow[0].upper() in DATABLOCK:
                            print("end of block", newrow)
                            break

                        # else assume have encountered master species
                        else:
                            # check if primary or secondary master species
                            if "(" and ")" not in newrow[0]:
                                primary = True
                                secondary = False
                            else:
                                primary = False
                                secondary = True

                            print(newrow, primary, secondary)
                            # add species to the solution_master_species table
                            # element_gfw only needs to be specified for primary master species, so check whether or not it is present in a particular row to see whether it needs to be added to the SQL database
                            if len(newrow) < 5:
                                db.execute("INSERT INTO solution_master_species (element, master_species, primary_master_species, secondary_master_species, alkalinity, gfw_formula, db_id) VALUES (?, ?, ?, ?, ?, ?, ?)", newrow[0], newrow[1], primary, secondary, newrow[2], newrow[3], current_dat[0]["id"])
                            else:
                                db.execute("INSERT INTO solution_master_species (element, master_species, primary_master_species, secondary_master_species, alkalinity, gfw_formula, element_gfw, db_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", newrow[0], newrow[1], primary, secondary, newrow[2], newrow[3], newrow[4], current_dat[0]["id"])

            # search for solution species keyword data block
            if "SOLUTION_SPECIES" in (item.upper() for item in row):
                print("SOLUTION SPECIES FOUND")
                for row in reader:
                    # convert rows to consistent formatting
                    newrow = convert(row)
                    #print(newrow)

                    # ignore blank rows
                    if not newrow:
                        continue

                    # if encounter another keyword data block, that indicates the end of the solution species data block
                    elif newrow[0].upper() in DATABLOCK:
                        print("END OF SOLUTION SPECIES", newrow)
                        break

                    # assume that if an equals sign is in a line, a new species has been found, but ignore if a comment or if the equals sign is in the same row as a keyword
                    elif "=" in newrow and newrow[0][0] != "#" and not newrow[0].lower() in [item for value in KEYWORDS.values() for item in value]:
                        print(newrow)
                        # combine equation into a single list item and get rid of trailing comments
                        """TODO"""
