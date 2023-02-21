import csv, sys

def main():
    fix()

def fix():
    with open(sys.argv[1]) as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')
            for row in spamreader:
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

                print(f"{first_name},{last_name},{parsed_number}")

def remove_dupes():

    with open("full_name_number.csv") as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')
            numbers = []
            for row in spamreader:
                number = row[2]
                numbers.append(number)

            temp = []
            for i in numbers:
                if i in temp:
                    print(i)
                else:
                    temp.append(i)

if __name__ == '__main__':
    main()