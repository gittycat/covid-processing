# Reads the grey-st.csv, simmons.csv, ... files and outputs master.csv
#

import os
import csv
import re
from datetime import datetime


# Get filenames in the 'csv' dir
(_, _, filenames) = next(os.walk('./csv'))


def t(date):
    # try:
        date = date.strip()
        if date == '':
            return ''
        if date == '1/1/00':
            return ''
        dt = datetime.strptime(date, '%d/%m/%Y')
        dtf = dt.strftime('%Y-%m-%d')
        return dtf

def clean_postcode(suburb):
    if suburb == "South Melbourne":
        return "3205"
    elif suburb == "Brunswick":
        return "3056"
    else:
        return ""


# Remove \n and strip()
def clean(str):
    str = str.strip()
    if str == 'N/A' or str == 'n/a':
        return ''
    return str.replace('\r\n', ' ').replace('\n', ' ').strip('\r\n').strip('\n')

# TODO: Refactor. Use a proper date validator
def clean_date(date):
    date = clean(date)
    if date == '':
        return ''

    # Add the century for two digits years
    d = date.split('/')
    if len(d) < 3:
#        print("Invalid Date: ", d, " Removing it and continuing...")
        return ''

    year = int(d[2])
    # Assume centenarians for years > "20"
    if year > 20 and year < 100:
        return f"{d[0]}/{d[1]}/19{d[2]}"
    elif year >= 0 and year <= 20:
        return f"{d[0]}/{d[1]}/20{d[2]}"
    else:
        return date

# header
buf = []
buf.append(['CollectionDate','FirstName','FamilyName','Phone','DOB','Address','Suburb','State','Postcode','Contacted','ContactDate','ContactMethod'])

for filename in filenames:
    with open('./csv/'+filename, newline='', encoding="latin-1") as file:
        print(f"parsing {filename}...")
        recs = csv.DictReader(file, delimiter=',')
        for c in recs:
            # Some csv are in UTF-8... some not. This removes the UTF-8 prefix if present.
            # if '\ufeffDate' in c.keys():
            #     c['Date'] = c.pop('\ufeffDate')

            date  = t(clean_date(c['Date']))
            firstName  =  clean(c['First Name'])
            familyName = clean(c['Family Name'])
            dob        = t(clean_date(c['DOB']))
            nfyd  = (c['Notification Method'] != '' )
            nfyMethod  = clean(c['Notification Method'].replace("'d", ""))
            nfyDate = t(clean_date(c['Notification Sent Date']))
            phone = clean(re.sub(r" ",'', c['Phone'], flags=re.UNICODE))
            addr = clean(c['Address'])
            suburb = c['Suburb'].strip()
            postcode = c['Postcode'] or clean_postcode(suburb)

            if date == '' and c['First Name'] == '':
                continue
            buf.append([date,firstName,familyName,phone,dob,addr,suburb,'VIC',postcode,nfyd,nfyDate,nfyMethod])

with open('master.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerows(buf)
#        f.write(','.join(rec))


# TODO: Add missing files in master.csv