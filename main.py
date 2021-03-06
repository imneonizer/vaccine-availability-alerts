# python-dotenv==0.17.0
# requests==2.25.1
# fake-useragent==0.1.11
import requests
import json, os
import datetime, time
from os.path import join, dirname
from dotenv import load_dotenv
from fake_useragent import UserAgent

load_dotenv(join(dirname(__file__), '.env'))

"""
# search for @PushitBot on Telegram to get token
# Contents of .env file

PINCODES=201301, 121003, 500081
MIN_AGE_LIMIT=53
TOKEN=<your-token>
INTERVAL=60
"""

EMOJIS = {
    "center_id" : "π",
    "name" : "π₯",
    "state_name" : "πΎ",
    "district_name" : "ποΈ",
    "block_name" : "π",
    "pincode" : "π’",
    "from" : "π",
    "to" : "π",
    "lat" : "πΊοΈ",
    "long" : "πΊοΈ",
    "fee_type" : "π°",
    "session_id" : "π",
    "date" : "π",
    "available_capacity" : "πΊ",
    "fee" : "π°",
    "min_age_limit" : "πΎ",
    "vaccine" : "π",
    "slots" : "π°"
}

PINCODES = [p.strip() for p in os.environ.get("PINCODES").split(",")]
MIN_AGE = int(os.environ.get("MIN_AGE_LIMIT"))
TOKEN = os.environ.get("TOKEN")
DATES = lambda r: [(datetime.datetime.today() + datetime.timedelta(days=d)).strftime("%d-%m-%Y") for d in range(0, r)]
INTERVAL = int(os.environ.get("INTERVAL"))
UA = UserAgent()

def get_sessions(pincode, date):
    try:
        # request cowin portal API for available sessions
        res = requests.get("https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin?pincode={}&date={}".format(pincode, date), headers={'User-Agent':str(UA.random)})
        if res.status_code == 403:
            print("[{}][ERROR] 403 Cowin portal is blocking your IP address".format(datetime.datetime.now()))
        return json.loads(res.text).get("sessions") if res.ok else []
    except Exception as e:
        print(e)
        return []    


def push(string):
    # push data to telegram bot
    requests.get("https://tgbots.skmobi.com/pushit/{}?msg={}".format(TOKEN, string))


def emojify(d):
    try:
        # remove unnecessary data
        for k in ["session_id", "lat", "long", "fee_type"]:
            d.pop(k)
    except: pass
    
    # parse dict to readable message
    string = ""
    for (k,v) in d.items():
        if k == "slots":
            v = ", ".join(v).replace("-", " - ")
        string += "{} {} = {}\n".format(EMOJIS.get(k), k.replace("_", " ").title(), v)
    return string

# Event Loop
while True:
    for pincode in PINCODES:
        # check for next 2 days
        for date in DATES(2):
            print("[{}][INFO] fetching data for date: {}, PINCODE: {}".format(datetime.datetime.now(), date, pincode))
            # fetch data from cowin portal
            sessions = get_sessions(pincode, date)
            
            # parse session details
            for s in sessions:
                try:
                    if MIN_AGE >= s.get("min_age_limit"):
                        message = emojify(s)
                        print(message)
                        # send message to telegram
                        push(message)
                except Exception as e:
                    print(e)
    print("[{}][INFO] sleeping for {} seconds".format(datetime.datetime.now(), INTERVAL))
    time.sleep(INTERVAL)

"""
# sample output

π Center Id = 605831
π₯ Name = UPHC BHANGEL
πΎ State Name = Uttar Pradesh
ποΈ District Name = Gautam Buddha Nagar
π Block Name = Bisrakh
π’ Pincode = 201301
π From = 09:00:00
π To = 17:00:00
π Date = 03-05-2021
πΊ Available Capacity = 12
π° Fee = 0
π Min Age Limit = 45
π Vaccine = COVISHIELD
π° Slots = 09:00AM - 11:00AM, 11:00AM - 01:00PM, 01:00PM - 03:00PM, 03:00PM - 05:00PM
"""
