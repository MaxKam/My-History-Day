from get_events import GetEvents
from configparser import ConfigParser
from db_connect import DBConnect
import requests
import datetime
import pickle

def format_message(message):
    return_string = "Your events on this day:\n"
    for key in message:
        split_key = key.split("-")
        return_string += split_key[0] + " : " + message[key] + "\n"
    return return_string

def send_events(sms_url, to_number, events_list):
    data = {'ToNumber': to_number,
            'Message': events_list}
    
    r = requests.post(url = sms_url, data = data)
    if r.status_code == 200:
        return "Success!"
    else:
        return "Failed to send"


def schedule():
    config = ConfigParser()
    config.read("./app_config.ini")

    gcal_events = GetEvents(config.get("APP_SETTINGS", "rpc_server"))
    dbcon = DBConnect(config.get("APP_SETTINGS", "db_path"))
    users = dbcon.get_sms_users()
    today = datetime.date.today()

    for user in users:
        creds = pickle.loads(user[4])
        events_list = gcal_events.get_gcal_events(creds, "calendar", "v3", today.strftime("%m/%d/%Y"))
        if events_list != "No events":
            message = format_message(events_list)
            send_events(config.get("APP_SETTINGS", "sms_url"), user[6], message)


if __name__ == '__main__':
    schedule()