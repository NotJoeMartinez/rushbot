from twilio.rest import Client 
import subprocess, time, csv, re, logging, sys, sqlite3
from config import twilio_credentals
import datetime

def main():


    msg_body = "Hey {}, this is a test" 

    blacklist = get_blacklist()

    campain_id = update_campains(msg_body)
    print(campain_id)
    print(f"running campain {campain_id}: {msg_body}")


    send_list = get_send_list(sys.argv[1])
    if len(send_list) > 10:
        ans = input(f"You are about to send {len(send_list)} messages are you sure? : Y/n ")
        if ans == "Y":
            rush_bot(send_list, msg_body, campain_id, blacklist)
        else:
            exit(0)
    else:
        rush_bot(send_list, msg_body, campain_id,blacklist)

def rush_bot(send_list, msg_body, campain_id, blacklist):
    for pnm in send_list:
        first_name = pnm[0].title()
        last_name = pnm[1].title()
        parsed_num = pnm[2]
        number = f"+1{pnm[2]}"

        fmt_msg = msg_body.format(first_name)

        if check_double_text(str(campain_id),parsed_num) == True:
            logging.error(f"{first_name} {last_name} {parsed_num} has recevied this message before, skipping")
            print(f"{first_name} {last_name} {parsed_num} has recevied this message before, skipping")
            continue
        elif parsed_num in blacklist:
            logging.error(f"{first_name} {last_name} {parsed_num} is blacklisted, skipping")
            print(f"{first_name} {last_name} {parsed_num} is blacklisted, skipping")
            continue
        else:
            try:
                account_sid = twilio_credentals['account_sid']
                auth_token = twilio_credentals['auth_token'] 
                client = Client(account_sid, auth_token)

                
                img_link = [""]

                message = client.messages.create(
                                            body=fmt_msg,
                                            messaging_service_sid=twilio_credentals['messaging_service_sid'],
                                            # media_url=img_link,
                                            to=number
                                        )

                twilio_sid = message.sid
                log_outgoing(twilio_sid,parsed_num,first_name,last_name,campain_id,fmt_msg)

            except Exception as e: 

                log_failed(parsed_num,first_name,last_name,campain_id, e)

        time.sleep(1)

def get_send_list(fpath):
    send_list = []
    with open(fpath, "r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            line = line.split(",")
            send_list.append((line[0], line[1], line[2]))
    return send_list 

def update_campains(msg_body):
    con = sqlite3.connect('rushbot.db')
    cur = con.cursor()
    cur.execute("SELECT rowid FROM campains WHERE msg_body = ?", (msg_body,))
    res = cur.fetchall()
    if len(res) == 0:
        print("New campain created")
        cur.execute("INSERT INTO campains VALUES(?)", (msg_body,))
        con.commit()
        cur.execute("SELECT rowid FROM campains WHERE msg_body = ?", (msg_body,))
        campain_id = cur.fetchone()
        con.close()
        return campain_id[0]
    else:
        campain_id = res[0][0]
        return campain_id 

def log_outgoing(twilio_sid,phone_number,first_name,last_name,campain_id,msg_body):
    ts = datetime.datetime.now()
    logging.info(f"Message Sent,{twilio_sid},{first_name},{last_name}, {phone_number}, {msg_body}")
    print(f"Message Sent: {twilio_sid},{first_name},{last_name}, {phone_number}, {msg_body}")

    con = sqlite3.connect('rushbot.db')
    cur = con.cursor()
    cur.execute("INSERT INTO sent_msg VALUES(?,?,?,?,?,?)", (twilio_sid,phone_number,first_name,last_name,campain_id,ts))
    con.commit()
    con.close()    

def log_failed(phone_number,first_name,last_name,campain_id,e):
    ts = datetime.datetime.now()
    logging.error(f"Message Failed {first_name},{last_name},{phone_number}, {e}")
    print(f"Message Failed, {first_name},{phone_number},{e}")
    print(type(e))
    con = sqlite3.connect('rushbot.db')
    cur = con.cursor()
    cur.execute("INSERT INTO sent_msg VALUES(?,?,?,?,?,?)", ("FAILED",phone_number,first_name,last_name,campain_id, ts))
    con.commit()
    con.close()    

def check_double_text(curent_campain,phone_number): 
    con = sqlite3.connect('rushbot.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM sent_msg WHERE phone_number = ?", (phone_number,) )
    res = cur.fetchall()
    if len(res) == 0:
        con.close()    
        return False
    
    campain_ids = []
    for msg in res:
        campain_id = msg[4]
        campain_ids.append(campain_id)

    if curent_campain in campain_ids:
        return True
    else:
        return False

def get_blacklist():
    blacklist = []
    with open("blacklist.csv","r") as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',') 
        for row in spamreader:
            blacklist.append(row[0])
    return blacklist



if __name__ == '__main__':
    now = datetime.datetime.now().strftime("%m_%d_%-I:%M:%S%p")
    logging.basicConfig(filename=f'logs/{now}.log', encoding='utf-8', level=logging.DEBUG, format='%(levelname)s:%(message)s')
    main()