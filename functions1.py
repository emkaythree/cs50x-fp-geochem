# functions to import
import chardet
import cs50
import csv
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

def main():
    # check if a database file exists for storing data about the geochemical databases
    if not os.path.isfile("database1.db"):
        open ("database1.db", "w").close()

    # create tables in database
    db = cs50.SQL("sqlite:///database1.db")

    # table for storing metadata about geochemical databases - name and number of species
    db.execute("CREATE TABLE IF NOT EXISTS db_meta (id INTEGER, name TEXT NOT NULL, solution_master_species INTEGER, solution_species INTEGER, phases INTEGER, PRIMARY KEY(id))")

    # table for storing information about solution master species
    db.execute("CREATE TABLE IF NOT EXISTS solution_master_species (id INTEGER, element TEXT NOT NULL, master_species TEXT, primary_master_species INTEGER DEFAULT 0, secondary_master_species INTEGER DEFAULT 0, alkalinity REAL, gfw_formula TEXT, element_gfw REAL, db_id INTEGER, PRIMARY KEY(id), FOREIGN KEY(db_id) REFERENCES db_meta(id))")

    # table for storing information about solution species
    db.execute("CREATE TABLE IF NOT EXISTS solution_species (id INTEGER, equation TEXT, reactants TEXT, defined_species TEXT, primary_master_species INTEGER DEFAULT 0, secondary_master_species INTEGER DEFAULT 0, other_products TEXT, log_k REAL, delta_h REAL, delta_h_units TEXT DEFAULT [kJ/mol], analytic_1 REAL, analytic_2 REAL, analytic_3 REAL, analytic_4 REAL, analytic_5 REAL, analytic_6 REAL, gamma_a REAL, gamma_b REAL, llnl_gamma REAL, co2_llnl_gamma INTEGER DEFAULT 0, dw REAL DEFAULT 0, Vm TEXT, millero TEXT, activity_water INTEGER DEFAULT 0, add_log_k_named_expression TEXT, add_log_k_coefficient REAL, erm_ddl REAL DEFAULT 1.0, no_check INTEGER DEFAULT 0, mole_balance TEXT, db_id INTEGER, PRIMARY KEY(id), FOREIGN KEY(db_id) REFERENCES db_meta(id))")

    # table for storing information about phases
    db.execute("CREATE TABLE IF NOT EXISTS phases (id INTEGER, name TEXT, equation TEXT, defined_phase TEXT, other_reactants TEXT, dissolved_products TEXT, log_k REAL, add_log_k_named_expression TEXT, add_log_k_coefficient REAL, delta_h REAL, delta_h_units TEXT DEFAULT [kJ/mol], analytic_1 REAL, analytic_2 REAL, analytic_3 REAL, analytic_4 REAL, analytic_5 REAL, analytic_6 REAL, Vm REAL DEFAULT 0, Vm_units TEXT DEFAULT [cm^3/mol], T_c REAL, P_c REAL, omega REAL, db_id INTEGER, PRIMARY KEY(id), FOREIGN KEY(db_id) REFERENCES db_meta(id))")

    # for database in databases, load file - from https://stackoverflow.com/questions/10377998/how-can-i-iterate-over-files-in-a-given-directory

    for filename in glob.glob("databases/*"):
       load(filename)
    #load("databases/MINTEQ.DAT")

    #load("databases/ColdChem.dat")
    #load("databases/core10.dat")
    #load("databases/PHREEQC.DAT")
    #load("databases/iso.dat")
    #load("databases/sit.dat")
    #load("databases/frezchem.dat")
    #load("databases/PITZER.DAT")
    #load("databases/test.dat")
    #load("databases/tkmullan_v1-08.DAT")




    if len(sys.argv) != 2:
        ######## testing getting sums from database #########
        #summary = db.execute("SELECT SUM(solution_master_species), SUM(solution_species), SUM(phases) FROM db_meta")
        #total_SMS = summary[0].get("SUM(solution_master_species)")
        #total_SS = summary[0].get("SUM(solution_species)")
        #total_PH = summary[0].get("SUM(phases)")
        #print(summary, total_SMS, total_SS, total_PH)

        ########testing getting summary table##############
        print(db.execute("SELECT * FROM db_meta"))


        #print("Usage: functions1.py <folder or file>")
    elif ".dat" in sys.argv[1].lower():
    #elif ".dat" in sys.argv[1].lower() and sys.argv[1] in (filename for filename in glob.glob("databases/*")):
        try:
            load(sys.argv[1])
        except ValueError as e:
            print(e)
    elif sys.argv[1] in (folder for folder in glob.glob("*")):
        print("valid folder found")
        for filename in glob.glob(sys.argv[1] + "/*"):
            try:
                load(filename)
            except ValueError as e:
                print(e)
    else:
        print("not a valid file or folder")
        #load(sys.argv[1])

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

# function for loading geochemical database files (i.e. .dat files) into the SQL database
def load(datfile):

    # check specified file is valid
    if not os.path.isfile(datfile):
        raise ValueError("File not found")

    # access sqlite database
    db = cs50.SQL("sqlite:///database1.db")

    # create an entry in the db_meta table for the current .dat file if it doesn't already exist
    if len(db.execute("SELECT * FROM db_meta WHERE name = ?", os.path.basename(datfile))) != 1:
        db.execute("INSERT INTO db_meta (name) VALUES (?)", os.path.basename(datfile))

    # set a variable to keep track of current .dat file
    current_dat = db.execute("SELECT id FROM db_meta WHERE name = ?", os.path.basename(datfile))

    print(os.path.basename(datfile))

    # tool to detect encoding of files - https://chardet.readthedocs.io/en/latest/usage.html
    detector = chardet.universaldetector.UniversalDetector()
    detector.reset()
    with open(datfile, "rb") as file:
        for row in file:
            detector.feed(row)
            if detector.done: break
        detector.close()
        encoding = detector.result["encoding"]
        #print(encoding)

    # open file using detected encoding

    with open(datfile, "r", encoding=encoding) as file:
        reader = csv.reader(file, delimiter="\t")

        # scroll throug file searching for keyword data blocks
        for row in reader:
            # Phreeqc databases can be inconsistent in terms of separating values with tabs or spaces so need to convert into a consistent format where anything separated by a space or a tab is a separate list item
            # join all items in row into a string, and then split into a new list based upon the position of spaces
            #temprow = (" ".join(row)).split(" ")

            # add not-empty list items to a new list
            #newrow = []
            #for item in temprow:
            #    if any(temprow) and item != "":
            #        newrow.append(item)
            #print(newrow)

            # search for the solution master species keyword data block
            if "SOLUTION_MASTER_SPECIES" in (item.upper() for item in row):
                print("SOLUTION MASTER SPECIES FOUND")

            # search through data block - if there is data on a line, then assume it is a master species, if a line is blank, then assume have reached end of data block - also build in protection in case there is no space between SOLUTION_MASTER_SPECIES and SOLUTION_SPECIES
                for row in reader:

                    # convert rows to consistent formatting
                    newrow = convert(row)

                    if newrow and newrow[0].upper() not in DATABLOCK:
                        # ignore comments
                        if "#" in newrow[0]:
                            continue
                        # convert space separated values to tab separated values, and remove additional tabs where necesary, and import into a new list
                        elif len(db.execute("SELECT * FROM solution_master_species WHERE element = ? AND db_id = ?", newrow[0], current_dat[0]["id"])) == 0:

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
                    elif not row:
                        continue
                    else:
                        print("end of block")
                        break

            # search for solution species keyword data block
            if "SOLUTION_SPECIES" in (item.upper() for item in row):
                print("SOLUTION SPECIES FOUND")

                # search through solution species to find equations
                for row in reader:

                    # convert rows to consistent formatting
                    newrow = convert(row)
                    #print(newrow)

                    #if newrow:
                    #    if not newrow[0].lower() in [value for items in KEYWORDS.values() for value in items]:
                        #if not newrow[0].lower() in KEYWORDS_SLNS:
                    #        print(newrow)

                    # assume that if an equals sign is in a line, a new species has been found - use variable to keep track of current equation
                    if newrow and "=" in newrow and newrow[0][0] != "#" and not newrow[0].lower() in [item for value in KEYWORDS.values() for item in value] and not newrow[0].upper() in DATABLOCK:

                        # combine equation into a single list item and get rid of trailing comments
                        current_eqn = (" ".join(newrow)).split("#")

                        print("newrow:", newrow)
                        print("currenteqn:", current_eqn)

                        # get reactants
                        reactants = ""
                        for i in range(len(current_eqn[0])):
                            # get everything on the left hand side of the equation
                            if current_eqn[0][i] != "=":
                                reactants += current_eqn[0][i]
                            else:
                                break

                        # get defined species
                        defined_species = ""
                        defined_species_active = False
                        for i in range(len(current_eqn[0])):
                            # search for equals sign as start of right hand side of equation - the defined species is the first species, so add everything until first + sign encountered (except where indicating charge)
                            if current_eqn[0][i-1] == "=":
                                defined_species_active = True
                            elif current_eqn[0][i-1] == " " and current_eqn[0][i] == "+" and current_eqn[0][i+1] == " ":
                                defined_species_active = False

                            if defined_species_active == True:
                                defined_species += current_eqn[0][i]

                        # get other products
                        other_products = ""
                        other_products_active = False
                        for i in range(len(current_eqn[0])):
                            # search for a + sign on the right hand side of the equation - everything after this will be "other products" of the reaction
                            if current_eqn[0][i-2] == " " and current_eqn[0][i-1] == "+" and current_eqn[0][i] == " " and current_eqn[0].find("=", 0, i) != -1:
                                other_products_active = True

                            if other_products_active == True:
                                other_products += current_eqn[0][i]

                        # check if primary master species - assume if reactants = defined species
                        primary_ms, secondary_ms = False, False

                        if reactants.strip() == defined_species.strip():
                            primary_ms = True

                        # check if secondary master species - if there are electrons in the equation
                        elif "e-" in current_eqn[0].lower() and not primary_ms:
                            secondary_ms = True

                        # add the mandatory fields of the current equation to solution species table
                        if len(db.execute("SELECT * FROM solution_species WHERE equation = ? AND db_id = ?", current_eqn[0], current_dat[0]["id"])) == 0:
                            db.execute("INSERT INTO solution_species (equation, reactants, defined_species, primary_master_species, secondary_master_species, other_products, db_id) VALUES (?, ?, ?, ?, ?, ?, ?)", current_eqn[0], reactants, defined_species.strip(), primary_ms, secondary_ms, other_products, current_dat[0]["id"])
                        # TODO: update table
                        #else:
                        #    db.execute("UPDATE solution_species SET equation = ? WHERE db_id = ?", current_eqn, current_dat[0]["id"])

                    #skip blank rows
                    elif not newrow:
                        continue

                    # for the current equation, search for a defined log K value - add to a variable
                    elif newrow[0].lower() in KEYWORDS["log_k"]:
                        print("logknewrow:", newrow)

                        # add log K into table
                        db.execute("UPDATE solution_species SET log_k = ? WHERE equation = ? AND db_id = ?", newrow[1], current_eqn[0], current_dat[0]["id"])

                    # search for a defined delta H value
                    elif newrow[0].lower() in KEYWORDS["delta_h"]:
                        print("deltaH: ", newrow)

                        # check for units
                        if len(newrow) == 3:
                            delta_h_units = newrow[2]
                        else:
                            delta_h_units = "kJ/mol"
                        # add delta H to table
                        db.execute("UPDATE solution_species SET delta_h = ?, delta_h_units = ? WHERE equation = ? AND db_id = ?", newrow[1], delta_h_units, current_eqn[0], current_dat[0]["id"])

                    # search for analytical expressions
                    elif newrow[0].lower() in KEYWORDS["analytical_expression"]:
                        print("AE:", newrow)

                        # check if all six analytical expression values are given
                        if len(newrow) < 7:
                            while len(newrow) < 7:
                                newrow.append(0)
                        print("analytic:", newrow)
                        # add analytical expression to table
                        db.execute("UPDATE solution_species SET analytic_1 = ?, analytic_2 = ?, analytic_3 = ?, analytic_4 = ?, analytic_5 = ?, analytic_6 = ? WHERE equation = ? AND db_id = ?", newrow[1], newrow[2], newrow[3], newrow[4], newrow[5], newrow[6], current_eqn[0], current_dat[0]["id"])

                    # check for gamma values
                    elif newrow[0].lower() in KEYWORDS["gamma"]:
                        print("gamma:", newrow)

                        # add gamma to table
                        db.execute("UPDATE solution_species SET gamma_a = ?, gamma_b = ? WHERE equation = ? AND db_id = ?", newrow[1], newrow[2], current_eqn[0], current_dat[0]["id"])

                    # search for llnl gamma values
                    elif newrow[0].lower() in KEYWORDS["llnl_gamma"]:
                        print("llnl", newrow)

                        # add llnl gamma to  table
                        db.execute("UPDATE solution_species SET llnl_gamma = ? WHERE equation = ? AND db_id = ?", newrow[1], current_eqn[0], current_dat[0]["id"])

                    # search for CO2 llnl gamma
                    elif newrow[0].lower() in KEYWORDS["co2_llnl_gamma"]:
                        print("CO2", newrow)

                        db.execute("UPDATE solution_species SET co2_llnl_gamma = 1 WHERE equation = ? AND db_id = ?", current_eqn[0], current_dat[0]["id"])

                    # search for Vm values
                    elif newrow[0].lower() in KEYWORDS["Vm"]:
                        print("Vm:", newrow)
                        # join into a single string for simplicity
                        Vm = ""
                        for i in range(1, len(newrow), 1):
                            if newrow[i] != "#":
                                Vm += " " + newrow[i]
                            else:
                                break
                        print(Vm)
                        db.execute("UPDATE solution_species SET Vm = ? WHERE equation = ? AND db_id = ?", Vm, current_eqn[0], current_dat[0]["id"])

                    # search for Millero values
                    elif newrow[0].lower() in KEYWORDS["Millero"]:
                        print("Millero:", newrow)
                        # join into a single string for simplicity
                        Millero = ""
                        for i in range(1, len(newrow), 1):
                            if newrow[i] != "#":
                                Millero += " " + newrow[i]
                            else:
                                break
                        print(Millero)
                        db.execute("UPDATE solution_species SET millero = ? WHERE equation = ? AND db_id = ?", Millero, current_eqn[0], current_dat[0]["id"])

                    # search for activity water specifier
                    elif newrow[0].lower() in KEYWORDS["activity_water"]:
                        print(newrow)
                        db.execute("UPDATE solution_species SET activity_water = 1 WHERE equation = ? AND db_id = ?", current_eqn[0], current_dat[0]["id"])

                    # search for add log K values
                    elif newrow[0].lower() in KEYWORDS["add_log_k"]:
                        print("addlogk:", newrow)
                        db.execute("UPDATE solution_species SET add_log_k_named_expression = ?, add_log_k_coefficient = ? WHERE equation = ? AND db_id = ?", newrow[1], newrow[2], current_eqn[0], current_dat[0]["id"])

                    # search for erm_ddl
                    elif newrow[0].lower() in KEYWORDS["erm_ddl"]:
                        print("erm_ddl:", newrow)
                        db.execute("UPDATE solution_species SET erm_ddl = ? WHERE equation = ? AND db_id = ?", newrow[1], current_eqn[0], current_dat[0]["id"])

                    # search for no check
                    elif newrow[0].lower() in KEYWORDS["no_check"]:
                        print("no check", newrow)
                        db.execute("UPDATE solution_species SET no_check = 1 WHERE equation = ? AND db_id = ?", current_eqn[0], current_dat[0]["id"])

                    # search for mole balance
                    elif newrow[0].lower() in KEYWORDS["mole_balance"]:
                        print("MB", newrow)
                        db.execute("UPDATE solution_species SET mole_balance = ? WHERE equation = ? AND db_id = ?", newrow[1], current_eqn[0], current_dat[0]["id"])

                    # if encounter another keyword data block, that indicates the end of the solution species data block
                    elif newrow[0].upper() in DATABLOCK:
                        print("END OF SOLUTION SPECIES")
                        break

            # search for phases keyword data block
            if "PHASES" in (item.upper() for item in row):
                print("PHASES FOUND")
                phase_count = 0
                #cycle through each line in phases data block
                for row in reader:
                    # convert rows to consistent formatting
                    newrow = convert(row)
                    #print(newrow)

                    # search for a phase name - single word that is not a keyword
                    if newrow and not "=" in newrow and newrow[0][0] != "#" and not newrow[0].lower() in [item for value in KEYWORDS.values() for item in value] and not newrow[0].upper() in DATABLOCK:
                        phase_count += 1

                        # get rid of trailing comments and convert ":" to "."
                        current_phase = newrow[0].replace(":", ".")
                        print(current_phase, phase_count)

                        # add to table
                        if len(db.execute("SELECT * FROM phases WHERE name = ? and db_id = ?", current_phase, current_dat[0]["id"])) == 0:
                            db.execute("INSERT INTO phases (name, db_id) VALUES (?, ?)", current_phase, current_dat[0]["id"])

                    # skip blank rows
                    elif not newrow:
                        continue

                    elif newrow[0][0] == "#":
                        continue

                    # search for an equation based upon an = sign being in the relevant row
                    elif "=" in newrow:
                        print("equation:", newrow)
                        #recombine equation and split into left hand and right hand sides
                        equation = (" ".join(newrow).replace(":", ".")).split("=")
                        print("eqn:", equation)

                        # get the phase being defined i.e. the first species defined on a line including an = sign
                        defined_phase = ""
                        for i in range(len(equation[0])):
                            if equation[0][i] != " ":
                                defined_phase += equation[0][i]
                            else:
                                break
                        print("defined phase:", defined_phase)

                        # get other reactants - i.e. any other species on the left hand side of the equation
                        other_reactants = ""
                        other_reactants_active = False
                        for i in range(len(equation[0])):
                            if equation[0][i-2] == " " and equation[0][i-1] == "+" and equation[0][i] == " ":
                                other_reactants_active = True

                            if other_reactants_active == True:
                                other_reactants += equation[0][i]
                        if other_reactants:
                            print("Other reactants:", other_reactants)

                        # get dissolved products - i.e. everything on right hand side of equation
                        dissolved_products = equation[1]
                        print("dissolved:", dissolved_products)

                        # add to database
                        db.execute("UPDATE phases SET equation = ?, defined_phase = ?, other_reactants = ?, dissolved_products = ? WHERE name = ? AND db_id = ?", equation[0] + "=" + equation[1], defined_phase, other_reactants, dissolved_products, current_phase, current_dat[0]["id"])

                    # get log K value if present
                    elif newrow[0].lower() in KEYWORDS["log_k"]:
                        print("logknewrow:", newrow)
                        db.execute("UPDATE phases SET log_k = ? WHERE name = ? AND db_id = ?", newrow[1], current_phase, current_dat[0]["id"])

                    # search for add log K values
                    elif newrow[0].lower() in KEYWORDS["add_log_k"]:
                        print("addlogk:", newrow)
                        db.execute("UPDATE phases SET add_log_k_named_expression = ?, add_log_k_coefficient = ? WHERE name = ? AND db_id = ?", newrow[1], newrow[2], current_phase, current_dat[0]["id"])

                    # search for a defined delta H value
                    elif newrow[0].lower() in KEYWORDS["delta_h"]:
                        print("deltaH: ", newrow)

                        # check for units
                        if len(newrow) == 3:
                            delta_h_units = newrow[2].strip("#")
                        else:
                            delta_h_units = "kJ/mol"

                        db.execute("UPDATE phases SET delta_h = ?, delta_h_units = ? WHERE name = ? AND db_id = ?", newrow[1], delta_h_units, current_phase, current_dat[0]["id"])

                    # search for analytical expressions
                    elif newrow[0].lower() in KEYWORDS["analytical_expression"]:
                        print("AE:", newrow)

                        # check if all six analytical expression values are given
                        if len(newrow) < 7:
                            while len(newrow) < 7:
                                newrow.append(0)
                        print("analytic:", newrow)

                        db.execute("UPDATE phases SET analytic_1 = ?, analytic_2 = ?, analytic_3 = ?, analytic_4 = ?, analytic_5 = ?, analytic_6 = ? WHERE name = ? AND db_id = ?", newrow[1], newrow[2], newrow[3], newrow[4], newrow[5], newrow[6], current_phase, current_dat[0]["id"])

                    # search for Vm value
                    elif newrow[0].lower() in KEYWORDS["Vm"]:
                        print("Vm:", newrow)

                        # get units if specified, otherwise use default
                        if len(newrow) == 3:
                            Vm_units = newrow[2]
                        else:
                            Vm_units = "cm^3/mol"

                        db.execute("UPDATE phases SET Vm = ?, Vm_units = ? WHERE name = ? AND db_id = ?", newrow[1], Vm_units, current_phase, current_dat[0]["id"])

                    # get critical temperature value
                    elif newrow[0].lower() in KEYWORDS["t_c"]:
                        print("T_c:", newrow)
                        db.execute("UPDATE phases SET T_c = ? WHERE name = ? AND db_id = ?", newrow[1], current_phase, current_dat[0]["id"])

                    # get critical pressure value
                    elif newrow[0].lower() in KEYWORDS["p_c"]:
                        print("P_c:", newrow)
                        db.execute("UPDATE phases SET P_c = ? WHERE name = ? AND db_id = ?", newrow[1], current_phase, current_dat[0]["id"])

                    # get acentic factor of the gas
                    elif newrow[0].lower() in KEYWORDS["omega"]:
                        print("Omega:", newrow)
                        db.execute("UPDATE phases SET omega = ? WHERE name = ? AND db_id = ?", newrow[1], current_phase, current_dat[0]["id"])

                    # if encounter another keyword data block, that indicates the end of the solution species data block
                    elif newrow[0].upper() in DATABLOCK:
                        print("END OF PHASES")
                        break

    # count items in database

    db.execute("UPDATE db_meta SET solution_master_species = (SELECT count(element) FROM solution_master_species WHERE db_id = ?), solution_species = (SELECT count(equation) FROM solution_species WHERE db_id = ?), phases = (SELECT count(name) FROM phases WHERE db_id = ?) WHERE id = ?", current_dat[0]["id"], current_dat[0]["id"], current_dat[0]["id"], current_dat[0]["id"])

if __name__ == "__main__":
    main()