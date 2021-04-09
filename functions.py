# functions to import
import cs50
import csv
import os.path
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
    db.execute("CREATE TABLE IF NOT EXISTS solution_master_species (id INTEGER, element TEXT NOT NULL, species TEXT, alkalinity REAL, gfw_formula TEXT, element_gfw REAL, db_id INTEGER, PRIMARY KEY(id), FOREIGN KEY(db_id) REFERENCES db_meta(id))")

    # for database in databases, load file

    load("databases/ColdChem.dat")

# function for loading geochemical database files (i.e. .dat files) into the SQL database
def load(datfile):
    # for each file in the /databases folder

    with open(datfile, "r") as file:
        reader = csv.reader(file, delimiter="\t")

        for row in reader:
            # search for the solution master species keyword data block
            if "SOLUTION_MASTER_SPECIES" in row:
                # search through data block - if there is data on a line, then assume it is a master species, if a line is blank, then assume have reached end of data block - also build in protection in case there is no space between SOLUTION_MASTER_SPECIES and SOLUTION_SPECIES
                for row in reader:
                    if len(row[0]) > 0 and row[0] != "SOLUTION_SPECIES":
                        print(row)
                    else:
                        print("end of block")
                        break
                    #if "SOLUTION_SPECIES" in row:
                    #    print("end of block")
                    #    break


            #if row[0] == "SOLUTION_MASTER_SPECIES":
            #    print(row[0])


if __name__ == "__main__":
    main()