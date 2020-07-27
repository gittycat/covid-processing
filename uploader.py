#
# Upload covid test collection data and lab result data to the 
# database.
#
# The collection and lab-result data need to be provided in csv form
# to this script.
#
# For lab result data, a match is made based on the "labcode" field,
# which is unique for each test.
#
# For the collection data from Star Health (master.csv), we overwrite the previous
# content *for some fields only*: firstName, familyName, ContactDate
# and ContactMethod.
# The match between database row and csv line is done based on the
# dob, collectDate and any one word of the firstName and familyName.
# Eg: Jane K O'Neil Rogan, the words 'jane,o'neil,rogan' are used for
# matches.
#
# Validation and Cleanup of data
# ------------------------------
# Some serious cleanup must be done on the csv generated from Excel.
# This is done in a separate script, genmaster.py.
# The csv from the lab result also needs some work on its date.
# We convert them to a canonical ISO date (YYYY-MM-DD) before upload.
# 

import sys
import os
import csv
import psycopg2
from datetime import datetime
import re

if len(sys.argv) != 2:
    print("Usage: python3 uploader.py <input-file.csv>")
    exit (1)

# Detects whether it's the lab result or the master csv based on the header
filetype = ""
with open(sys.argv[1], 'r') as f:
    header = f.readline()
    if header[0:20] == 'CollectionDate,First':
        filetype = 'collection'
    elif header[0:20] == 'LABNAME,PROC,DATA_ST':
        filetype = 'labresult'
    else:
        print("Unrecognized file. Only lab result csv OR collection csv are valid")
        exit()

infile = sys.argv[1]

fields = []
tr = {}
if filetype == 'labresult':
    # Lab result csv
    tableName = 'lab_results'
    tableConstraint = 'lab_results_labcode_key'
    tableAction = 'DO NOTHING'
    fields = ['labcode','servicedate','pat_idno','pat_surname','pat_given_name','sex','dateofbirth','pat_add1','pat_add2','pat_add3','pat_pcode','clinical_data_line_1','clinical_data_line_2','specimen_collection_date','labname','proc','data_status','specimendate','ageindays','ageinyears','senderscode','senders_surname','senders_initials','sendersadd1','sendersadd2','sendersadd3','senders_pc','doc_idnumber','doc_surname','doc_initials','doc_provnumber','senders_ref','their_ref','vidrl_lab_no','specimen_type','specimen_site','wuhpcr','wuhpcr1','wuhpcr2','wuhpcr3','wuhpcr4','wuhpcr5']
    # translation between tricky database and csv fields.
    # As a rule, the database fields are the labresult.csv fields lowercased.
    tr = {
        'specimen_type': 'SPECIMEN TYPE',
        'specimen_site': 'SPECIMEN SITE',
        'clinical_data_line_1': 'CLINICAL DATA LINE 1',
        'clinical_data_line_2': 'CLINICAL DATA LINE 2',
        'specimen_collection_date': 'SPECIMEN COLLECTION DATE',
        'vidrl_lab_no': 'VIDRL LAB NO.'
    }
    def translate(key):
        if key in tr:
            return tr[key]
        return key.upper()

else:
    # Collection csv
    tableName = 'collections'
    tableConstraint = 'collections_collect_date_dob_first_name_family_name_key'
    tableAction = "DO UPDATE SET contacted=EXCLUDED.contacted, contact_date=EXCLUDED.contact_date"
    fields = ['collect_date','first_name','family_name','phone','dob','address','suburb','state','postcode','contacted', 'contact_date','contact_method']
    # translation between database and csv fields.
    tr = {
        'collect_date': 'CollectionDate',
        'first_name': 'FirstName',
        'family_name': 'FamilyName',
        'phone': 'Phone',
        'dob': 'DOB',
        'address': 'Address',
        'suburb': 'Suburb',
        'state': 'State',
        'postcode': 'Postcode',
        'contacted': 'Contacted',
        'contact_date': 'ContactDate',
        'contact_method': 'ContactMethod'
    }
    def translate(key):
        return tr[key]

dateFields = ['collect_date', 'dob', 'contact_date', 'servicedate', 'dateofbirth', 'specimen_collection_date', 'specimendate']


# TODO: Use a proper date validator
def clean_date(date):
    #                 unknown
    if date == '' or ('unk' in date.lower()) or date == '1/1/00':
        return 'NULL'

    # Check for valid iso dates
    if re.match(r"\d{4}-\d{2}-\d{2}", date):
        return date

    # Add the century for two digits years
    d = date.split('/')
    if len(d) < 3:
        print("Error: Invalid date: ", d)
        exit()
    year = int(d[2])
    # Assume 19xx for years > "20"
    if year > 20 and year < 100:
        date = f"19{d[2]}-{int(d[1]):02d}-{int(d[0]):02d}"
    elif year >=0 and year <= 20:
        date = f"20{d[2]}-{int(d[1]):02d}-{int(d[0]):02d}"
    return date.strip("'")

def value(rec, k):
    val = rec[translate(k)]
    if k in dateFields:
        # Date values must not be empty strings. Replace by NULL.
        if val == '':
            val = 'NULL'
        else:
            val = clean_date(val)
    return val

with open(infile, newline='',  encoding='ISO-8859-1') as file:
    buf = []
    counter = 0
    for rec in csv.DictReader(file, delimiter=','):
        counter += 1
        # For each record, add the values together into "(value1, value2,...)"
        buf.append("(" + str(list(map(lambda k: value(rec,k), fields)))[1:-1] + ")")

    # Build the SQL command
    # We use an "upsert": ignore (labresults) or update (collections) if the insert fails
    cmd = "INSERT INTO " + tableName + "(" + ",".join(fields) + ") VALUES " + ",".join(buf)
    cmd += " ON CONFLICT ON CONSTRAINT " + tableConstraint + " " + tableAction + ";"

    # Some more cleanup
    cmd = cmd.replace("'NULL'", "NULL")
    # Replace "O'Neil" by 'O''Neil'  (sql syntax)
    cmd = re.sub(r"\"(\w+)\'(\w+)\"", r"'\1''\2'", cmd)
 
    # # For testing
    # print(cmd)
    # exit()
 
    # Execute the SQL command on the db
    try:
        print("connecting...")
        conn = psycopg2.connect(user = os.environ['POSTGRES_USER'],
                            password = os.environ['POSTGRES_PASSWORD'],
                            host = "localhost",
                            port = "5432",
                            database = "covid")

        cursor = conn.cursor()
        cursor.execute(cmd)
        print("committing...")
        conn.commit()
        print(f"uploaded {counter} records")
        print("done")

    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        #closing database connection.
            if conn is not None:
                cursor.close()
                conn.close()
