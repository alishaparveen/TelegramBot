import json
import requests
import urllib
from dbhelper import DBHelper
from datetime import datetime
db = DBHelper()

TOKEN = "1915986506:AAHQlIRQw_u1jdVI5Z2X8mfTcKisQkeLo0w"
URL = f"https://api.telegram.org/bot{TOKEN}/"

base_cowin_url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict"
now = datetime.now()
today_date = now.strftime("%d-%m-%Y")
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'

headers={'User-Agent':user_agent,} 
def fetch_data_from_cowin(district_id,chat):
  query_params = f"?district_id={district_id}&date={today_date}"
  final_url = base_cowin_url+query_params
  response = requests.get(final_url,headers)
  #print(response.text)
  if response.ok:
    send_message("Fetched data, parsing & bringing to you", chat)
    extract_availability_data(response,chat)
  else:
    send_message("Sorry, unable to fetch data at this moment")

def extract_availability_data(response,chat):
  response_json = response.json()
  i = 0
  message ="Vaccine data: "+str(i+1)
  for center in response_json["centers"]:
    if i>5:
      break  
    for session in center["sessions"]:
      if session["available_capacity_dose1"]>0 or session["available_capacity_dose2"]>0:
        message += "Pincode: {} \n Center Name: {} \n Minimum Age Limit : {} \n Vaccine :{}\n Fee:{}\n Dose 1 available capacity: {} \n Dose 2 available capacity:{} \n----\n".format(center["center_id"],center["name"],session["min_age_limit"],session["vaccine"],center["fee_type"],session["available_capacity_dose1"],session["available_capacity_dose2"])
        i = i + 1
    send_message(message,chat)


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)

def handle_updates(updates):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        items = db.get_items(chat)
        if text == "/start":
            send_message("Welcome ,Alisha bot here, to help you retrieve vaccine availability data, please type 1 to continue, for new session type new", chat)
        elif text =="1":
            info = open('states.json')
            res = json.load(info)
            statelist = res["states"]
            # for everystate in statelist:
            #   db.add_item(everystate["state_name"],chat)
            keyboard = [[eachstate["state_name"]] for eachstate in statelist]
            reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
            keyboard2 = json.dumps(reply_markup)
            send_message("Please select the state from dropdown & then type 2, for new session type new",chat,keyboard2)
        elif text=="2":
            items = db.get_items(chat)
            if(len(items)>0):
              statename = items[0]
              info = open('district.json')
              res = json.load(info)
              districtlist = res[statename]["districts"]
              keyboard = [[eachdistrict["district_name"]] for eachdistrict in districtlist]
              reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
              keyboard2 = json.dumps(reply_markup)
              send_message("Thanks, please type 3 and it will retieve your data, for new session type new",chat,keyboard2)
        elif text =="3":
            items = db.get_items(chat)
            if(len(items)>0):
              statename = items[0]
              districtname = items[1]
              info = open('district.json')
              res = json.load(info)
              districtlist = res[statename]["districts"]
              for district in districtlist:
                if district["district_name"]==districtname:
                  district_id = district["district_id"]
                  send_message("Matched,fetching your data, please be patient",chat)
                  fetch_data_from_cowin(district_id,chat)
                  break
        elif text=="new":
            db.delete_all_items(chat)
            send_message("Let's start again, type 1 to start", chat)
        elif text.startswith("/"):
            continue
        elif text in items:
            #db.delete_item(text,chat)
            send_message("Thanks, you had already selected this, type new", chat)
        else:
            db.add_item(text,chat)
            items = db.get_items(chat)
            message = "\n".join(items)
            send_message(message, chat)



def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)