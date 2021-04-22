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
    db.execute("CREATE TABLE IF NOT EXISTS solution_species (id INTEGER, equation TEXT, reactants TEXT, defined_species TEXT, primary_master_species INTEGER DEFAULT 0, secondary_master_species INTEGER DEFAULT 0, other_products TEXT, log_k REAL, delta_h REAL, delta_h_units TEXT DEFAULT [kJ/mol], analytic TEXT, gamma TEXT, llnl_gamma REAL, co2_llnl_gamma INTEGER DEFAULT 0, dw REAL DEFAULT 0, Vm TEXT, millero TEXT, activity_water INTEGER DEFAULT 0, add_logk TEXT, erm_ddl REAL DEFAULT 0, no_check INTEGER DEFAULT 0, mole_balance TEXT, db_id INTEGER, PRIMARY KEY(id), FOREIGN KEY(db_id) REFERENCES db_meta(id))")

    # table for storing information about phases
    db.execute("CREATE TABLE IF NOT EXISTS phases (id INTEGER, name TEXT, equation TEXT, defined_phase TEXT, other_reactants TEXT, dissolved_products TEXT, log_k REAL, add_log_k TEXT, delta_h REAL, delta_h_units TEXT DEFAULT [kJ/mol], analytic TEXT, Vm REAL DEFAULT 0, Vm_units TEXT DEFAULT [cm^3/mol], T_c REAL, P_c REAL, omega REAL, db_id INTEGER, PRIMARY KEY(id), FOREIGN KEY(db_id) REFERENCES db_meta(id))")

    # for database in databases, load file - from https://stackoverflow.com/questions/10377998/how-can-i-iterate-over-files-in-a-given-directory

    #for filename in glob.glob("databases/*"):
    #    load(filename)
    #load("databases/MINTEQ.DAT")

    #load("databases/ColdChem.dat")
    #load("databases/core10.dat")
    load("databases/PHREEQC.DAT")
    #load("databases/iso.dat")
    #load("databases/sit.dat")
    #load("databases/frezchem.dat")

# function for loading geochemical database files (i.e. .dat files) into the SQL database
def load(datfile):

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
            # search for the solution master species keyword data block
            if "SOLUTION_MASTER_SPECIES" in (item.upper() for item in row):
                print("SOLUTION MASTER SPECIES FOUND")
                # search through data block - if there is data on a line, then assume it is a master species, if a line is blank, then assume have reached end of data block - also build in protection in case there is no space between SOLUTION_MASTER_SPECIES and SOLUTION_SPECIES
                for row in reader:
                    if row and row[0].upper() not in DATABLOCK:
                        # ignore comments
                        if "#" in row[0]:
                            continue
                        # convert space separated values to tab separated values, and remove additional tabs where necesary, and import into a new list
                        elif len(db.execute("SELECT * FROM solution_master_species WHERE element = ? AND db_id = ?", row[0], current_dat[0]["id"])) == 0:
                            newrow = []
                            temprow = (" ".join(row)).split(" ")
                            for item in temprow:
                                if item != "":
                                    newrow.append(item)

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
                # initialise a variable to store solution species equations
                current_eqn = False
                # search through solution species to find equations
                for row in reader:
                    # assume that if an equals sign is in a line, a new species has been found - use variable to keep track of current equation
                    if row and "=" in row[0] and row[0].upper() not in DATABLOCK:
                        current_eqn = row
                        #print(current_eqn)
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
                        if len(db.execute("SELECT * FROM solution_species WHERE equation = ? AND db_id = ?", current_eqn, current_dat[0]["id"])) == 0:
                            db.execute("INSERT INTO solution_species (equation, reactants, defined_species, primary_master_species, secondary_master_species, other_products, db_id) VALUES (?, ?, ?, ?, ?, ?, ?)", current_eqn, reactants, defined_species, primary_ms, secondary_ms, other_products, current_dat[0]["id"])
                        # TODO: update table
                        #else:
                        #    db.execute("UPDATE solution_species SET equation = ? WHERE db_id = ?", current_eqn, current_dat[0]["id"])
                    elif not row:
                        continue

                    # for the current equation, search for a defined log K value - add to a variable
                    elif "log_k" in row:
                        # get rid of tabs/spaces
                        log_k = []
                        for item in row:
                            if item != "":
                                log_k.append(item)
                        #print(log_k)
                        # add log K into table
                        db.execute("UPDATE solution_species SET log_k = ? WHERE equation = ? AND db_id = ?", log_k[1], current_eqn, current_dat[0]["id"])

                    # search for a defined delta H value
                    elif "delta_h" in row or "-delta_H" in row:
                        # get rid of tabs/spaces
                        delta_h = []
                        for item in row:
                            if item != "":
                                delta_h.append(item)
                        #print(delta_h[1], delta_h[2])
                        # add delta H to table
                        db.execute("UPDATE solution_species SET delta_h = ?, delta_h_units = ? WHERE equation = ? AND db_id = ?", delta_h[1], delta_h[2], current_eqn, current_dat[0]["id"])

                    # search for analytical expressions
                    elif "-analytic" in row or "-analytical_expression" in row:
                        # get rid of tabs
                        analytic = []
                        for item in row:
                            if item != "":
                                analytic.append(item)
                        #print(analytic)
                        # add analytical expression to table
                        db.execute("UPDATE solution_species SET analytic = ? WHERE equation = ? AND db_id = ?", analytic[1], current_eqn, current_dat[0]["id"])

                    # if encounter another keyword data block, that indicates the end of the solution species data block
                    elif row and row[0] in DATABLOCK:
                        print("end of block")
                        break

            # search for phases keyword data block
            if "PHASES" in (item.upper() for item in row):
                print("PHASES FOUND")
                phase_count = 0
                for row in reader:
                    # search for a phase name - indicated by a row containing a single item with no spaces in it - also ignore comments
                        #                                                           #
                        # Flawed because ignores phases with comments in same line  #
                        #                                                           #
                    if row and len(row) == 1 and not "#" in row[0][0] and not " " in row[0] and not row[0] in DATABLOCK:
                        # SQL doesn't like colons, so change to a period
                        #if ":" in row[0]:
                        current_phase = row[0].replace(":", ".")
                        #else:
                        #    current_phase = row[0]
                        phase_count += 1
                        print(current_phase, phase_count)


                        # add to table
                        if len(db.execute("SELECT * FROM phases WHERE name = ? and db_id = ?", current_phase, current_dat[0]["id"])) == 0:
                            db.execute("INSERT INTO phases (name, db_id) VALUES (?, ?)", current_phase, current_dat[0]["id"])

                        # for the current phase, find the following:
                        for row in reader:
                            # find the dissolution reaction
                            if row and "=" in row[1]:
                                equation = []
                                for item in row:
                                    if item != "":
                                        equation.append(item)
                                print(equation)
                                
                                # split equation to left hand side and right hand side
                                neweqn = equation[0].split("=")
                                print(neweqn)
                                
                                # get the phase being defined i.e. the first species defined on a line including an = sign
                                defined_phase = ""
                                for i in range(len(neweqn[0])):
                                    if neweqn[0][i] != " ":
                                        defined_phase += neweqn[0][i]
                                    else:
                                        break
                                print(defined_phase)
                                # get other reactants - i.e. any other species on the left hand side of the equation
                                other_reactants = ""
                                other_reactants_active = False
                                for i in range(len(neweqn[0])):
                                    if neweqn[0][i-1] == "+":
                                        other_reactants_active = True
                                        
                                    if other_reactants_active == True:
                                        other_reactants += equation[0][i]
                                print(other_reactants)
                                
                                # get dissolved products - i.e. everything on right hand side of equation
                                dissolved_products = neweqn[1]
                                print(dissolved_products)                                
                                
                                # add to database
                                db.execute("UPDATE phases SET equation = ?, defined_phase = ?, other_reactants = ?, dissolved_products = ? WHERE name = ? AND db_id = ?", equation, defined_phase, other_reactants, dissolved_products, current_phase, current_dat[0]["id"])
                                
                                # get log K value if present
                                if row and "log_k" in row or "-log_k" in row or "logk" in row or "-l" in row:
                                    # get rid of tabs/spaces
                                    log_k = []
                                    for item in row:
                                        if item != "":
                                            log_k.append(item)
                                    print(log_k)
                            
                                # get delta H value
                                elif row and "-delta_h" in row:
                                    continue
                                
                                # get analytical expression
                                elif row and "-analytic" in row:
                                    continue
                                
                                #get Vm value
                                elif row and "-Vm" in row:
                                    continue
                            
                            else:
                                break





                    # if encounter another keyword data block, that indicates the end of the phases data block
                    elif row and row[0] in DATABLOCK:
                        print("end of block")
                        break




if __name__ == "__main__":
    main()