import requests
import time
import schedule
import json
from datetime import datetime
base_cowin_url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict"
now = datetime.now()
today_date = now.strftime("%d-%m-%Y")
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'

headers={'User-Agent':user_agent,} 
def fetch_data_from_cowin(district_id):
  query_params = f"?district_id={district_id}&date={today_date}"
  final_url = base_cowin_url+query_params
  response = requests.get(final_url,headers)
  extract_availability_data(response)


def fetch_state_id():
  info = open('states.json')
  res = json.load(info)
  statelist = res["states"]
  statenames ="State Names"
  for eachstate in statelist:
    statenames+=eachstate["state_name"]+"\n"
  return statenames


def fetch_district_id():
  url = "https://cdn-api.co-vin.in/api/v2/admin/location/districts/31"
  response = requests.get(url,headers)
  response_json = response.json()
  print(response_json.text)


  


def fetch_data_for_states(district_ids):
  for district_id in district_ids:
    fetch_data_from_cowin(district_id)

group_id = "get_real_time_cowin_data"
telegram_api_url = "https://api.telegram.org/bot1915986506:AAHQlIRQw_u1jdVI5Z2X8mfTcKisQkeLo0w/sendMessage?chat_id=@__groupid__&text="
def send_message_telegram(message):
  final_url = telegram_api_url.replace("__groupid__",group_id)
  final_url = final_url + message
  response = requests.get(final_url)
  if response.status_code == 429:
    time.sleep(int(response.headers["Retry-After"]))
  print(response)

def extract_availability_data(response):
  response_json = response.json()
  for center in response_json["centers"]:  
    message =""
    for session in center["sessions"]:
      if session["available_capacity_dose1"]>0:
        message += "Pincode: {} \n Center Name: {} \n Minimum Age Limit : {} \n Vaccine :{}\n Fee:{}\n Dose 1 available capacity: {} \n Dose 2 available capacity:{} \n----\n".format(center["center_id"],center["name"],session["min_age_limit"],session["vaccine"],center["fee_type"],session["available_capacity_dose1"],session["available_capacity_dose2"])
    send_message_telegram(message)
    


