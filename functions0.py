# functions to import
import cs50
import csv
import os
import sys

# global variable to store keywords used in PHASES data block
KEYWORDS_PHASES = [
    "log_k",
    "-log_k",
    "logk",
    "-l",
    "-lo",
    "-log",
    "-log_",
    "-log_k",
    "-logk",
    "-add_logk",
    "add_logk",
    "add_log_k",
    "-ad",
    "-add",
    "-add_",
    "-add_l",
    "-add_lo",
    "-add_log",
    "-add_log_",
    "-add_log_k",
    "delta_h",
    "-delta_h",
    "deltah",
    "-d",
    "-de",
    "-del",
    "-delt",
    "-delta",
    "-delta_",
    "-deltah"
    "analytical_expression",
    "a_e",
    "ae" ,
    "-a",
    "-a_",
    "-a_e",
    "-ae" ,"-an",
    "-ana",
    "-anal",
    "-analy",
    "-analyt",
    "-analyti",
    "-analytic",
    "-analytica",
    "-analytical",
    "-analytical_",
    "-analytical_e",
    "-analytical_ex",
    "-analytical_exp",
    "-analytical_expr",
    "-analytical_expre",
    "-analytical_expres",
    "-analytical_express",
    "-analytical_expressi",
    "-analytical_expressio",
    "-analytical_expression",
    "-vm",
    "-t_c",
    "-p_c",
    "-omega",
    ]

# global variable to store keywords used in SOLUTION_SPECIES data block
KEYWORDS_SLNS = [
    "log_k",
    "-log_k",
    "logk",
    "-l",
    "-lo",
    "-log",
    "-log_",
    "-log_k",
    "-logk",
    "-add_logk",
    "add_logk",
    "add_log_k",
    "-ad",
    "-add",
    "-add_",
    "-add_l",
    "-add_lo",
    "-add_log",
    "-add_log_",
    "-add_log_k",
    "delta_h",
    "-delta_h",
    "deltah",
    "-d",
    "-de",
    "-del",
    "-delt",
    "-delta",
    "-delta_",
    "-deltah"
    "analytical_expression",
    "a_e",
    "ae" ,
    "-a",
    "-a_",
    "-a_e",
    "-ae" ,"-an",
    "-ana",
    "-anal",
    "-analy",
    "-analyt",
    "-analyti",
    "-analytic",
    "-analytica",
    "-analytical",
    "-analytical_",
    "-analytical_e",
    "-analytical_ex",
    "-analytical_exp",
    "-analytical_expr",
    "-analytical_expre",
    "-analytical_expres",
    "-analytical_express",
    "-analytical_expressi",
    "-analytical_expressio",
    "-analytical_expression",
    "-dw",
    "dw",
    "-vm",
    "vm",
    "-gamma",
    "-g",
    "-ga",
    "-gam",
    "-gamm"
    "millero",
    "-millero",
    "-mi",
    "-mil",
    "-mill",
    "-mille",
    "-miller",
    "activity_water",
    "-ac",
    "-act",
    "-acti",
    "-activ",
    "-activi",
    "-activit",
    "-activity",
    "-activity_",
    "-activity_w",
    "-activity_wa",
    "-activity_wat",
    "-activity_wate",
    "llnl_gamma",
    "-llnl_gamma",
    "-ll",
    "-lln",
    "-llnl",
    "-llnl_",
    "-llnl_g",
    "-llnl_ga",
    "-llnl_gam",
    "-llnl_gamm",
    "co2_llnl_gamma",
    "-co2_llnl_gamma",
    "-co",
    "-co2",
    "-co2_",
    "-co2_l",
    "-co2_ll",
    "-co2_lln",
    "-co2_llnl",
    "-co2_llnl_",
    "-co2_llnl_g",
    "-co2_llnl_ga",
    "-co2_llnl_gam",
    "-co2_llnl_gamm",
    "erm_ddl",
    "-erm_ddl",
    "-e",
    "-er",
    "-erm",
    "-erm_",
    "-erm_d",
    "-erm_dd",
    "no_check",
    "-no_check",
    "-n",
    "-no",
    "-no_",
    "-no_c",
    "-no_ch",
    "-no_che",
    "-no_chec",
    "mole_balance",
    "mass_balance",
    "mb",
    "-mass_balance",
    "-mb",
    "-mole_balance",
    "-m",
    "-mo",
    "-mol",
    "-mole",
    "-mole_",
    "-mole_b",
    "-mole_ba",
    "-mole_bal",
    "-mole_bala",
    "-mole_balan",
    "-mole_balanc",
    ]



def main():
    # check if a database file exists for storing data about the geochemical databases
    if not os.path.isfile("database.db"):
        open ("database.db", "w").close()

    # create tables in database
    db = cs50.SQL("sqlite:///database.db")

    # table for storing metadata about geochemical databases - name and number of species
    db.execute("CREATE TABLE IF NOT EXISTS db_meta (id INTEGER, name TEXT NOT NULL, solution_master_species INTEGER, solution_species INTEGER, phases INTEGER, PRIMARY KEY(id))")

    # table for storing information about solution master species
    db.execute("CREATE TABLE IF NOT EXISTS solution_master_species (id INTEGER, element TEXT NOT NULL, master_species TEXT, alkalinity REAL, gfw_formula TEXT, element_gfw REAL, db_id INTEGER, PRIMARY KEY(id), FOREIGN KEY(db_id) REFERENCES db_meta(id))")

    # table for storing information about solution species
    db.execute("CREATE TABLE IF NOT EXISTS solution_species (id INTEGER, equation TEXT, reactants TEXT, defined_species TEXT, primary_master_species INTEGER DEFAULT 0, secondary_master_species INTEGER DEFAULT 0, other_products TEXT, log_k REAL, delta_h REAL, delta_h_units TEXT DEFAULT [kJ/mol], analytic TEXT, gamma TEXT, llnl_gamma REAL, co2_llnl_gamma INTEGER DEFAULT 0, dw REAL DEFAULT 0, Vm TEXT, millero TEXT, activity_water INTEGER DEFAULT 0, add_logk TEXT, erm_ddl REAL DEFAULT 0, no_check INTEGER DEFAULT 0, mole_balance TEXT, db_id INTEGER, PRIMARY KEY(id), FOREIGN KEY(db_id) REFERENCES db_meta(id))")

    # for database in databases, load file

    load("databases/ColdChem.dat")
    #load("databases/core10.dat")
    #load("databases/PHREEQC.DAT")
    #load("databases/iso.dat")
    #load("databases/sit.dat")
    #load("databases/frezchem.dat")

# function for loading geochemical database files (i.e. .dat files) into the SQL database
def load(datfile):

    # access sqlite database

    db = cs50.SQL("sqlite:///database.db")

    # create an entry in the db_meta table for the current .dat file if it doesn't already exist
    if len(db.execute("SELECT * FROM db_meta WHERE name = ?", os.path.basename(datfile))) != 1:
        db.execute("INSERT INTO db_meta (name) VALUES (?)", os.path.basename(datfile))

    # set a variable to keep track of current .dat file
    current_dat = db.execute("SELECT id FROM db_meta WHERE name = ?", os.path.basename(datfile))

    print(os.path.basename(datfile))

    with open(datfile, "r") as file:
        reader = csv.reader(file, delimiter="\t")

        for row in reader:
            # search for the solution master species keyword data block
            if "SOLUTION_MASTER_SPECIES" in row:

                # search through data block - if there is data on a line, then assume it is a master species, if a line is blank, then assume have reached end of data block - also build in protection in case there is no space between SOLUTION_MASTER_SPECIES and SOLUTION_SPECIES
                for row in reader:
                    if row and len(row[0]) > 0 and row[0] != "SOLUTION_SPECIES" and row[0] != "SIT":
                        print(row)
                        # insert row into SOLUTION_MASTER_SPECIES SQL table if doesn't already exist, ignoring comments
                        if len(db.execute("SELECT * FROM solution_master_species WHERE element = ? AND db_id = ?", row[0], current_dat[0]["id"])) == 0 and row[0] != "#":
                            # element_gfw only needs to be specified for primary master species, so check whether or not it is present in a particular row to see whether it needs to be added to the SQL database
                            if len(row) < 5:
                                print(row[0])
                                db.execute("INSERT INTO solution_master_species (element, species, alkalinity, gfw_formula, db_id) VALUES (?, ?, ?, ?, ?)", row[0], row[1], row[2], row[3], current_dat[0]["id"])
                            else:
                                db.execute("INSERT INTO solution_master_species (element, species, alkalinity, gfw_formula, element_gfw, db_id) VALUES (?, ?, ?, ?, ?, ?)", row[0], row[1], row[2], row[3], row[4], current_dat[0]["id"])
                    else:
                        print("end of block")
                        break

            ######################################################################
            # Find a way to check if all characters in a row are capital letters #
            ######################################################################


            # search for the solution species keyword data block
            if "SOLUTION_SPECIES" in row:
                # initialise a variable to store solution species equations
                current_eqn = False
                # search through solution species to find equations
                for row in reader:
                    # assume that if an equals sign is in a line, a new species has been found - use variable to keep track of current equation
                    if row and "=" in row[0] and row[0] != "PHASES":
                        # first check if a current equation already exists - if so, add to the database before looking at a new one
                        if current_eqn and len(db.execute("SELECT * FROM solution_species WHERE equation = ? AND db_id = ?", current_eqn, current_dat[0]["id"])) == 0:
                            db.execute("INSERT INTO solution_species (equation, reactants, defined_species, other_products, log_k, delta_h, delta_h_units, db_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", current_eqn, reactants, defined_species, other_products, log_k, delta_h, delta_h_units, current_dat[0]["id"])
                        # store new current equation
                        current_eqn = row
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

                        # check if primary master species


                        # check if secondary master species

                        # get other products
                        other_products = ""
                        other_products_active = False
                        for i in range(len(current_eqn[0])):
                            # search for a + sign on the right hand side of the equation - everything after this will be "other products" of the reaction
                            if current_eqn[0][i-2] == " " and current_eqn[0][i-1] == "+" and current_eqn[0][i] == " " and current_eqn[0].find("=", 0, i) != -1:
                                other_products_active = True

                            if other_products_active == True:
                                other_products += current_eqn[0][i]

                    # for the current equation, search for a defined log K value - add to a variable
                    elif "log_k" in row:
                        print(row)
                        if row[2]:
                            log_k = row[2]
                        else:
                            log_k = row[3]
                        print(row[1], log_k)
                    # search for a defined delta_h value
                    elif "delta_h" in row or "-delta_H" in row:
                        print(row[1], row[2], row[3])
                        delta_h = row[2]
                        if row[3]:
                            delta_h_units = row[3]
                        else:
                            delta_h_units = "kJ/mol"
                    # search for analytical expressions
                    elif "-analytic" in row or "-analytical_expression" in row:
                        print(row)

                    elif not row:
                        continue

                    # if encounter the word PHASES, then this indicates the end of the solution species keyword data block
                    elif row[0] == "PHASES":
                        if current_eqn and len(db.execute("SELECT * FROM solution_species WHERE equation = ? AND db_id = ?", current_eqn, current_dat[0]["id"])) == 0:
                            db.execute("INSERT INTO solution_species (equation, reactants, defined_species, other_products, log_k, delta_h, delta_h_units, db_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", current_eqn, reactants, defined_species, other_products, log_k, delta_h, delta_h_units, current_dat[0]["id"])
                        print("end of block")
                        break


            # search for phases keyword data block
            if "PHASES" in (item.upper() for item in row):
                print("PHASES FOUND")
                phase_count = 0
                for row in reader:

                    # convert space separated values into a list to correct for poorly formatted files
                    splitrow = (" ".join(row)).split(" ")
                    #print(splitrow)
                    # get rid of blank items in list
                    temprow = []
                    for item in splitrow:
                        if any(splitrow) and item != "":
                            temprow.append(item.strip())

                    #print("temprow:", temprow)
                    #print(len(temprow))

                    # search for a phase name - single word that is not a keyword
                    if temprow and not "=" in temprow and temprow[0][0] != "#" and not temprow[0].lower() in KEYWORDS_PHASES and not temprow[0].upper() in DATABLOCK:

                        # remove any trailing comments

                        newrow = temprow[0].split("#")
                        print("newrow:", newrow)

                        # SQL doesn't like colons, so change to a period
                        current_phase = newrow[0].replace(":", ".")

                        phase_count += 1
                        print(current_phase, phase_count)


                        # add to table
                        if len(db.execute("SELECT * FROM phases WHERE name = ? and db_id = ?", current_phase, current_dat[0]["id"])) == 0:
                            db.execute("INSERT INTO phases (name, db_id) VALUES (?, ?)", current_phase, current_dat[0]["id"])

                    # ignore comments
                    elif temprow and temprow[0] == "#":
                        #print("to ignore:", row)
                        continue


                    # search for an equation based upon an = sign being in the relevant row
                    elif temprow and "=" in temprow:
                        #recombine equation
                        #print("temprow:", temprow)
                        equation = " ".join(temprow).replace(":", ".")
                        #print("new temprow", equation)

                        neweqn = equation.split("=")
                        #print("neweqn:", neweqn)
                        #print("neweqnlenth = ", len(neweqn))

                        # get the phase being defined i.e. the first species defined on a line including an = sign
                        defined_phase = ""
                        for i in range(len(neweqn[0])):
                            if neweqn[0][i] != " ":
                                defined_phase += neweqn[0][i]
                            else:
                                break
                        print("defined phase:", defined_phase)

                        # get other reactants - i.e. any other species on the left hand side of the equation
                        other_reactants = ""
                        other_reactants_active = False
                        for i in range(len(neweqn[0])):
                            if neweqn[0][i-2] == " " and neweqn[0][i-1] == "+" and neweqn[0][i] == " ":
                                other_reactants_active = True

                            if other_reactants_active == True:
                                other_reactants += neweqn[0][i]
                        if other_reactants:
                            print("Other reactants", other_reactants)
                        
                        # get dissolved products - i.e. everything on right hand side of equation

                        dissolved_products = neweqn[1]
                        #print("dissolved:", dissolved_products)

                        # add to database
                        db.execute("UPDATE phases SET equation = ?, defined_phase = ?, other_reactants = ?, dissolved_products = ? WHERE name = ? AND db_id = ?", equation, defined_phase, other_reactants, dissolved_products, current_phase, current_dat[0]["id"])

                    # get log K value if present
                    elif temprow and temprow[0] in ["log_k", "-log_k", "logk", "-l", "-lo", "-log", "-log_", "-log_k", "-logk"]:
                        print("temprowlogk:", temprow)
                        db.execute("UPDATE phases SET log_k = ? WHERE name = ? AND db_id = ?", temprow[1], current_phase, current_dat[0]["id"])

                    # get add log K value if present
                    #elif row and "-add_logk" in row or "add_logk" in row or "add_log_k" in row or "-ad" in row:
                    elif temprow and temprow[0].lower() in ["-add_logk", "add_logk", "add_log_k", "-ad", "-add", "-add_", "-add_l", "-add_lo", "-add_log", "-add_log_", "-add_log_k", "-add_logk"]:
                        print("temprow_add", temprow)
                        db.execute("UPDATE phases SET add_log_k_named_expression = ?, add_log_k_coefficient = ? WHERE name = ? AND db_id = ?", temprow[1], temprow[2], current_phase, current_dat[0]["id"])


                    # get delta H value
                    elif temprow and temprow[0].lower() in ["delta_h", "deltah", "-delta_h"]:
                        print("delta H:", temprow)
                        if len(temprow) == 3:
                            delta_h_units = temprow[2]
                        else:
                            delta_h_units = "kJ/mol"
                        db.execute("UPDATE phases SET delta_h = ?, delta_h_units = ? WHERE name = ? AND db_id = ?", temprow[1], delta_h_units, current_phase, current_dat[0]["id"])

                    # get analytical expression
                    elif temprow and temprow[0].lower() in ["analytical_expression", "a_e", "ae", "-analytical_expression", "-a", "-a_", "-a_e", "-ae", "-an", "-ana", "-anal", "-analy", "-analyt", "-analyti", "-analytic", "-analytica", "-analytical", "-analytical_", "-analytical_e", "-analytical_ex", "-analytical_exp", "-analytical_expr", "-analytical_expre", "-analytical_expres", "-analytical_express", "-analytical_expressi", "-analytical_expressio"] and not "-ad" in temprow:
                        if len(temprow) < 7:
                            while len(temprow) < 7:
                                temprow.append(0)
                        print("analytic:", temprow)
                        db.execute("UPDATE phases SET analytic_1 = ?, analytic_2 = ?, analytic_3 = ?, analytic_4 = ?, analytic_5 = ?, analytic_6 = ? WHERE name = ? AND db_id = ?", temprow[1], temprow[2], temprow[3], temprow[4], temprow[5], temprow[6], current_phase, current_dat[0]["id"])

                    #get molar volume value
                    elif temprow and temprow[0].lower() in ["-vm", "vm"]:
                        print("Vm:", temprow)
                        # get units if specified, otherwise use default
                        if len(temprow) == 3:
                            Vm_units = temprow[2]
                        else:
                            Vm_units = "cm^3/mol"
                        db.execute("UPDATE phases SET Vm = ?, Vm_units = ? WHERE name = ? AND db_id = ?", temprow[1], Vm_units, current_phase, current_dat[0]["id"])


                    # get critical temperature value
                    elif temprow and temprow[0].lower() in ["-t_c", "t_c"]:
                        print("T_c:", temprow)
                        db.execute("UPDATE phases SET T_c = ? WHERE name = ? AND db_id = ?", temprow[1], current_phase, current_dat[0]["id"])


                    # get critical pressure value
                    elif temprow and temprow[0].lower() in ["-p_c", "p_c"]:
                        print("P_c:", temprow)
                        db.execute("UPDATE phases SET P_c = ? WHERE name = ? AND db_id = ?", temprow[1], current_phase, current_dat[0]["id"])

                    # get acentic factor of the gas
                    elif temprow and temprow[0].lower() in ["-omega", "omega"]:
                        print("Omega:", temprow)
                        db.execute("UPDATE phases SET omega = ? WHERE name = ? AND db_id = ?", temprow[1], current_phase, current_dat[0]["id"])

                    elif not temprow:
                        continue

                    elif temprow and temprow[0] in DATABLOCK:
                        print("end of block")
                        break














if __name__ == "__main__":
    main()