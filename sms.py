#
# Send an sms message to all phone numbers listed in the input csv file.
# The Twilio API gateway is used.
# Note that the status of the Twilio messages needs to be polled an
# hour later to retrieve messages that have failed to be received by
# a mobile phone. These clients are notified by mail instead.
#
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import sys
import csv


sender_phone = os.environ['SMS_PHONE']
account_sid  = os.environ['SMS_KEY']
auth_token   = os.environ['SMS_TOKEN']
client = Client(account_sid, auth_token)

if len(sys.argv) != 2:
    print("Usage: python3 sms.py <file.csv>")
    exit (1)
infile = sys.argv[1]

# batch3
# batch-26
with open(infile, "r") as f:
    reader = csv.DictReader(f, delimiter=',')
    for row in reader:
        first = row['FirstName']
        family = row['FamilyName']
        phone = row['Phone']
        body = f"""
Dear {first},

Your COVID-19 test result is NEGATIVE.

Your test has shown that you did not have corona virus when tested.  Please continue to physically distance, wear a mask outside, wash hands regularly and avoid touching your face.

Please consult your doctor for advice if needed.

This message is from Star Health. No Reply.
"""

        try:
            message = client.messages \
                .create(from_=sender_phone, to=phone, body=body)

            print(f"{message.sid} {phone}, {first}, {family}")
        except TwilioRestException as err:
            print(f"Invalid phone number {phone}, {first}, {family}")
