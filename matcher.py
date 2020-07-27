#
# Link the collection records with corresponding lab_results records,
# when a match if found.
#
# We use the collection.labcode field as a foreign key to lab_results.
#
# The match is on the dob and a fuzzy search of the first and family names.
#

import os
import psycopg2

# Link up the two tables on the labcode field, based on dob + first + family names 
# using fuzzy search
cmd = "UPDATE collections AS c SET labcode = l.labcode FROM lab_results as l WHERE c.dob = l.dateofbirth AND SIMILARITY(UPPER(c.first_name),l.pat_given_name) > 0.4 and SIMILARITY(UPPER(c.family_name),l.pat_surname) > 0.4;"

try:
    print("connecting...")
    conn = psycopg2.connect(user = os.environ['POSTGRES_USER'],
                        password = os.environ['POSTGRES_PASSWORD'],
                        host = "localhost",
                        port = "5432",
                        database = "covid")

    cursor = conn.cursor()
    cursor.execute(cmd)
    print("linking entries...")
    conn.commit()
    print("done")

except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)
finally:
    #closing database connection.
    if conn is not None:
        cursor.close()
        conn.close()
