import json
import requests
import urllib
from dbhelpercopy import DBHelper
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
    send_message("Sorry, unable to fetch data at this moment", chat)

def extract_availability_data(response,chat):
  response_json = response.json()
  i = 0
  j = 0
  k = 0 
  message ="Vaccine data: "
  for center in response_json["centers"]:  
    for session in center["sessions"]:
      send_message("Fetching center no "+str(j),chat)
      if session["available_capacity_dose1"]>0 or session["available_capacity_dose2"]>0:
        send_message("Awesome , center "+str(j)+" has doses " ,chat)
        message += "Pincode: {} \n Center Name: {} \n Minimum Age Limit : {} \n Vaccine :{}\n Fee:{}\n Dose 1 available capacity: {} \n Dose 2 available capacity:{} \n----\n".format(center["center_id"],center["name"],session["min_age_limit"],session["vaccine"],center["fee_type"],session["available_capacity_dose1"],session["available_capacity_dose2"])
        j = j+1
        k = k+1
      else:
        send_message("Available capacity is none (0) for center no "+str(j),chat)
        j = j + 1
    i = i +1
    # if j>10:
    #   break
    send_message(message+str(i+1),chat)
  send_message("Finished collecting data, found "+str(k)+" centers with available vaccines,"+ "type /start to get other data",chat)


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

validstateslist = []
def getstates():
  info = open('states.json')
  res = json.load(info)
  statelist = res["states"]
  if (len(validstateslist)<2):
    for everystate in statelist:
        validstateslist.append(everystate["state_name"])
  return statelist

validdistrict = []
def validatedistrict(statename):
    info = open('district.json')
    res = json.load(info)
    districtlist = res[statename]["districts"]
    for district in districtlist:
        validdistrict.append(district["district_name"])
    return districtlist

def handle_updates(updates):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        print(chat)
        if text == "/start":
            db.delete_all_items(chat)
            db.setup()
            db.addowner(chat)
            send_message("Welcome ,Alisha bot here, to help you retrieve vaccine availability data", chat)
            statelist = getstates()
            keyboard = [[eachstate["state_name"]] for eachstate in statelist]
            reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
            keyboard2 = json.dumps(reply_markup)
            send_message("Please select the state from dropdown ",chat,keyboard2)     
        elif text in validstateslist:
            # if (db.check_if_id_exists(chat)==1):
            #   print("yes")
            #   db.update_state(text,chat)
            # else:
            db.add_state(text,chat)
            statename = text
            districtlist = validatedistrict(statename)
            keyboard = [[eachdistrict["district_name"]] for eachdistrict in districtlist]
            reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
            keyboard2 = json.dumps(reply_markup)
            send_message("Please select district from drop down",chat,keyboard2)
        elif text in validdistrict:
            #db.setup() 
            try:
              statename = db.get_state(chat)
              print("entering district:  " + statename)
              db.update_district(text,chat)
              districtname = text
              districtlist = validatedistrict(statename)
              for district in districtlist:
                if district["district_name"]==districtname:
                  district_id = district["district_id"]
                  send_message("Matched,fetching your data, please be patient",chat)
                  fetch_data_from_cowin(district_id,chat)
                  break
            except Exception as e:
                print(e)
        elif text =="/delete":
            db.delete_all_items(chat)
        elif text =="/testing":
            try:
              print(db.get_all_Data())
              statename = db.get_state(chat)
              districtname = db.get_district(chat)
              print(statename,districtname)
            except Exception as e:
              print(e)
        elif text =="/stop":
            db.stop()
            send_message("Stopping fecthing data, to fetch another data type /start")
            db.delete_all_items(chat)
            # districtlist = validatedistrict(statename)
            # for district in districtlist:
            #     if district["district_name"]==districtname:
            #         district_id = district["district_id"]
            #         send_message("Matched,fetching your data, please be patient",chat)
            #         fetch_data_from_cowin(district_id,chat)
            #         break   
        elif text.startswith("/"):
            db.delete_all_items(chat)
            send_message("Bots of our planet understand /start for now :), trying to become smart like humans, meanwhile press /start to talk to me",chat)
            continue
        else:
            #db.delete_all_items(chat)
            send_message("Received your message ,I Need to become human to understand "+text+ " :), meanwhile please type /start for starting again :)", chat)
        

