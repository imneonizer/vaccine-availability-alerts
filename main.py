# python-dotenv==0.17.0
# requests==2.25.1
import requests
import json, os
import datetime, time
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(join(dirname(__file__), '.env'))
base = datetime.datetime.today()

"""
# search for @PushitBot on Telegram to get token
# Contents of .env file

PINCODES=201301, 121003, 500081
MIN_AGE_LIMIT=53
TOKEN=<your-token>
INTERVAL=60
"""

class API:
    EMOJIS = {
        "center_id" : "🆔",
        "name" : "🏥",
        "state_name" : "🗾",
        "district_name" : "🏘️",
        "block_name" : "📍",
        "pincode" : "🔢",
        "from" : "🕐",
        "to" : "🕒",
        "lat" : "🗺️",
        "long" : "🗺️",
        "fee_type" : "💰",
        "session_id" : "🚀",
        "date" : "📅",
        "available_capacity" : "🏺",
        "fee" : "💰",
        "min_age_limit" : "👾",
        "vaccine" : "💉",
        "slots" : "🎰"
    }
    
    PINCODES = [p.strip() for p in os.environ.get("PINCODES").split(",")]
    MIN_AGE = int(os.environ.get("MIN_AGE_LIMIT"))
    TOKEN = os.environ.get("TOKEN")
    DATES = lambda r: [(base + datetime.timedelta(days=d)).strftime("%d-%m-%Y") for d in range(0, r)]
    INTERVAL = int(os.environ.get("INTERVAL"))
    
    @staticmethod
    def get_sessions(pincode, date):
        try:
            # request cowin portal API for available sessions
            res = requests.get("https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin?pincode={}&date={}".format(pincode, date))
            return json.loads(res.text).get("sessions") if res.ok else []
        except Exception as e:
            print(e)
            return []    
    
    @staticmethod
    def push(string):
        # push data to telegram bot
        requests.get("https://tgbots.skmobi.com/pushit/{}?msg={}".format(API.TOKEN, string))
    
    @staticmethod
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
            string += "{} {} = {}\n".format(API.EMOJIS.get(k), k.replace("_", " ").title(), v)
        return string

# Event Loop
while True:
    for pincode in API.PINCODES:
        # check for next 7 days
        for date in API.DATES(7):
            print("[{}][INFO] fetching data for date: {}, PINCODE: {}".format(datetime.datetime.now(), date, pincode))
            # fetch data from cowin portal
            sessions = API.get_sessions(pincode, date)
            
            # parse session details
            for s in sessions:
                try:
                    if API.MIN_AGE >= s.get("min_age_limit"):
                        message = API.emojify(s)
                        print(message)
                        # send message to telegram
                        API.push(message)
                except Exception as e:
                    print(e)
    print("[{}][INFO] sleeping for {} seconds".format(datetime.datetime.now(), API.INTERVAL))
    time.sleep(API.INTERVAL)

"""
# sample output

🆔 Center Id = 605831
🏥 Name = UPHC BHANGEL
🗾 State Name = Uttar Pradesh
🏘️ District Name = Gautam Buddha Nagar
📍 Block Name = Bisrakh
🔢 Pincode = 201301
🕐 From = 09:00:00
🕒 To = 17:00:00
📅 Date = 03-05-2021
🏺 Available Capacity = 12
💰 Fee = 0
🎂 Min Age Limit = 45
💉 Vaccine = COVISHIELD
🎰 Slots = 09:00AM - 11:00AM, 11:00AM - 01:00PM, 01:00PM - 03:00PM, 03:00PM - 05:00PM
"""