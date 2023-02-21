import gspread, csv

import csv, datetime
import os.path
from os import path

from config import diff_prod_url 

def main():

    # order is importent here
    now = str(datetime.datetime.now())
    latest_csv = get_csv(diff_prod_url, now)
    last_csv = get_last_csv()

    if check_diff(last_csv, latest_csv): 
        diff_list = find_diff(last_csv,latest_csv)
        print(diff_list)
        make_sendlist(diff_list, now) 
    else:
        print("Files Are The Same")


def get_csv(csv_url, now): 
    gc = gspread.service_account(filename='rushdiffcheck.json')

    sh = gc.open_by_url(csv_url)
    worksheet = sh.get_worksheet(0)

    list_of_lists = worksheet.get_values()

    with open("csvs/" + now + ".csv", 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter='|', quoting=csv.QUOTE_MINIMAL)
        for row in list_of_lists:
            spamwriter.writerow(row)

    if not path.exists("csvs/lastcheck.txt"):
        with open("csvs/lastcheck.txt","w") as f: 
            pass

    with open("csvs/lastcheck.txt", "a") as f:
        f.write(f"{str(now)}\n")
    return "csvs/" + str(now).strip() + ".csv"

def get_last_csv():
    with open("csvs/lastcheck.txt", "r") as f:
        lines = f.readlines()
        last_check = lines[len(lines) - 2].strip()
        return "csvs/" + last_check + ".csv"

def check_diff(last_csv, latest_csv):
    with open(last_csv,"r") as f:
        last = f.readlines()

    with open(latest_csv,"r") as f:
        latest = f.readlines()
    
    if len(latest) > len(last):
        return True 
    else:
        return False

def find_diff(last_csv, latest_csv):

    with open(last_csv,"r") as csvfile:
        spamreader = csv.reader(csvfile, delimiter='|')
        last = []
        for row in spamreader:
            last.append(row)

    with open(latest_csv,"r") as csvfile:
        spamreader = csv.reader(csvfile, delimiter='|',)
        latest = []
        for row in spamreader:
            latest.append(row)

    diff = []
    for row in latest:
        if row not in last:
            diff.append(row)
    return diff

def make_sendlist(diff_list, now):
    filename = "diff_list" + now + ".csv"
    with open(filename, "w") as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        for row in diff_list:
            full_name = row[1].strip()
            number = row[2]

            name_list = full_name.split(" ")
            first_name = name_list[0]

            if len(name_list) == 2: 
                last_name = name_list[1]
            elif len(name_list) > 2:
                last_name = name_list[-1]

            numeric_filter = filter(str.isdigit, number)
            parsed_number = "".join(numeric_filter)

            spamwriter.writerow([first_name,last_name,parsed_number])
    print(f"diff written to {filename}")



if __name__ == '__main__':
    main()