# functions to import
import cs50
import csv
import os
import sys

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
                        #if current_eqn and len(db.execute("SELECT * FROM solution_species WHERE equation = ? AND db_id = ?", current_eqn, current_dat[0]["id"])) == 0:
                         #   db.execute("INSERT INTO solution_species (equation, reactants, defined_species, other_products, log_k, delta_h, delta_h_units, db_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", current_eqn, reactants, defined_species, other_products, log_k, delta_h, delta_h_units, current_dat[0]["id"])
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







if __name__ == "__main__":
    main()