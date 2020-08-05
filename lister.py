#
# Generates 3 CSV files containing contacts that need to be
# notified via sms, letters and phone calls.

import os
import psycopg2
import csv

smsfile = 'sms.csv'
letterfile = 'letters.csv'
callfile = 'calls.csv'

try:
    print("connecting...")
    conn = psycopg2.connect(user = os.environ['POSTGRES_USER'],
                        password = os.environ['POSTGRES_PASSWORD'],
                        host = "localhost",
                        port = "5432",
                        database = "covid")
    cursor = conn.cursor()

    #
    # SMS
    # -----------------------

    cmd = """
    SELECT c.first_name, c.family_name, c.phone
    FROM collections as c, lab_results as l 
    WHERE c.labcode = l.labcode 
      AND c.contacted = FALSE
      AND (substring(c.phone, 1,2) = '04' OR substring(c.phone, 1,1) = '4');
    """
    cursor.execute(cmd)

    with open(smsfile, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['first_name', 'family_name', 'phone'])
        rows = cursor.fetchall()
        for row in rows:
            writer.writerow(row)

    #
    # Letters
    # -----------------------

    cmd = """
    SELECT c.collect_date, c.first_name, c.family_name, c.address, c.suburb, c.state,
    c.postcode
    FROM collections as c, lab_results as l 
    WHERE c.labcode = l.labcode AND c.contacted = FALSE;
    """
    cursor.execute(cmd)

    with open(letterfile, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['collect_date', 'first_name', 'family_name', 'address', 'suburb', 'state', 'postcode'])
        rows = cursor.fetchall()
        for row in rows:
            writer.writerow(row)



    #
    # To Call list
    # -----------------------

    cmd = """
    SELECT c.phone, c.first_name, c.family_name, c.dob, c.collect_date
    FROM collections as c, lab_results as l 
    WHERE c.labcode = l.labcode 
      AND c.contacted = FALSE
      AND (substring(c.phone, 1,2) != '04' AND substring(c.phone, 1,1) != '4')
      AND c.phone != '' AND LOWER(c.phone) != 'nophone';
    """
    cursor.execute(cmd)

    with open(callfile, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['phone', 'first_name', 'family_name', 'dob', 'ollect_date'])
        rows = cursor.fetchall()
        for row in rows:
            writer.writerow(row)


    print("done")

except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)
finally:
    #closing database connection.
    if (conn):
        cursor.close()
        conn.close()
