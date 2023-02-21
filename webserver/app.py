import os, uuid
import datetime as dt
import json
from flask import Flask, request, jsonify, redirect 
import base64
import subprocess,argparse
import logging
import re

from config import twilio_auth, groupme_auth

from twilio.rest import Client 
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        fname = "API/responces/" + str(uuid.uuid1())+".json"
        msg = request.values.get('Body', '').lower()
        phone_num = request.values.get('From','')
        city = request.values.get('FromCity','')
        print(msg)
        print(phone_num)
        print(city)
        send_message(msg, phone_num, city)

        return '', 200 
    else:
        abort(400)


import requests
from requests.structures import CaseInsensitiveDict
import json

def send_message(msg,num, city):
    name = get_name_from_num(num)
    url = "https://api.groupme.com/v3/bots/post"
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"


    data_dict = {
    "bot_id"  : groupme_auth["prod"]["bot_id"],
    "text"    : f"Message from: {num}\nName: {name}\nCity: {city} \nMessage: {msg}"
    }


    data = json.dumps(data_dict)

    resp = requests.post(url, headers=headers, data=data)

    print(resp.status_code)


def get_name_from_num(num):
    import csv

    numeric_filter = filter(str.isdigit, num)
    parsed_num = "".join(numeric_filter)
    parsed_num = parsed_num[1:]
    
    with open("full_name_number.csv", newline='\n') as f:
        name_reader = csv.reader(f, delimiter=',')
        for row in name_reader:
            try:
                if row[2] == parsed_num:
                    return row[0] + " " + row[1]
            except:
                return "N/A"
                

@app.route("/callback", methods=["POST", "GET"])
def call_back():
    if request.method == 'POST':

        now = dt.datetime.now().strftime("%m%d%I%M%S")
        logfile = 'logs/real_' + now + '.log'
        logging.basicConfig(filename=logfile, encoding='utf-8', level=logging.DEBUG)
        logging.debug(f'I was called on: {now}')

        data = request.stream.read()

        callback = json.loads(data)
        handle_callback(callback)


        return "thanks"


@app.route("/testcallback", methods=["POST", "GET"])
def test_call_back():
    if request.method == 'POST':

        now = dt.datetime.now().strftime("%m_%d_%I:%M:%S")
        logfile = 'logs/test_' + now + '.log'
        logging.basicConfig(filename=logfile, encoding='utf-8', level=logging.DEBUG)
        logging.debug(f'I was called on: {now}')

        data = request.stream.read()
        callback = json.loads(data)

        handle_callback(callback)

        return "thanks"

# don't fuck this up
def handle_callback(callback):

    # verify the message is not coming from the bot
    if callback['sender_type'] == 'bot':
        return 

    # exit if attachments is empty 
    if len(callback['attachments']) == 0: 
        return 

    # only continue if atachment type is reply  
    if callback['attachments'][0]['type'] == 'reply':

        # message id we are replying to 
        reply_id = callback['attachments'][0]['reply_id'] 
        base_reply_id = callback['attachments'][0]['base_reply_id'] 

        # don't reply to replies
        if reply_id != base_reply_id:
            return


        # fetch the past 75 messages 
        token = groupme_auth["prod"]["token"]
        group_id = groupme_auth["prod"]["group_id"]
        url = f"https://api.groupme.com/v3/groups/{group_id}/messages?limit=75&token={token}"

        res = requests.get(url)
        res_dict = json.loads(res.text)
        messages = res_dict['response']['messages']

        for msg in messages: 
            if msg['id'] == reply_id:

                foo = re.search("Message from\: \+(.*)\n",msg['text'])
                bar = foo.group(1)                
                number = "+" + bar
                responce = callback['text']
                send_reply(responce, number)
                break


def send_reply(responce, phone_number):
    account_sid = twilio_auth["account_sid"] 
    auth_token = twilio_auth["auth_token"] 
    client = Client(account_sid, auth_token)
    message = client.messages.create(
            body=responce,
            messaging_service_sid=twilio_auth["messaging_service_sid"], 
            to=phone_number
            )



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
