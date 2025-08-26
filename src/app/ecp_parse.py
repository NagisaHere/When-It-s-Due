# get course code
# check if exists
# select offering

import requests
from bs4 import BeautifulSoup
import re
import datetime

# base url
base_url = "https://programs-courses.uq.edu.au/course.html?course_code="

def ecpparser():
    # while True:
    #get course code, check if valid
        ccode = input("\nWhat course code would you like to look at: ")
        response = requests.get(base_url + ccode)
        resoup = BeautifulSoup(response.content, 'html.parser')
        content = resoup.find(id="course-notfound")

        while content is not None:
            ccode = input("Course code does not exist. Try again: ")
            response = requests.get(base_url + ccode)
            resoup = BeautifulSoup(response.content, 'html.parser')
            content = resoup.find(id="course-notfound")

        resoup = BeautifulSoup(response.content, 'html.parser')
        cur_offeringss = resoup.find(id="course-current-offerings")
        
        if cur_offeringss is None:
            print("Course is not offered.")
            return
        
        # finding ecp link
        #let user choose
        print("\nThe following offerings are available:")
        offerings = cur_offeringss.findAll(class_="course-offering-year")

        for counter, c in enumerate(offerings, start=1):
            print(str(counter) + ". " + c.text)

        choice = input("Which option would you like to view: ")
        while (not choice.isnumeric()) or int(choice) < 1 or (int(choice) - 1) > counter:
            choice = int(input("Try again: "))

        all_profiles = cur_offeringss.findAll('a', class_="profile-available", href=True)
        ecp_url = all_profiles[int(choice) - 1]['href']

        # now try accessing the current ecp
        ecp_results = requests.get(ecp_url)
        ecpsoup = BeautifulSoup(ecp_results.content, 'html.parser')
        temp = ecpsoup.find(id="assessment--section").find_all('tr')

        collected_data = []
        for c, t in enumerate(temp):
            content = ""
            if c > 0:
                label = t.find('a').contents[0]
            stuff = t.findAll('p')
            # now regex for due dates and titles
            for s in stuff:
                name_n_datetime = re.search(r"(.*\s)?\d{1,2}\/\d{2}\/\d{4}\s\d{1,2}:\d{1,2}\s[ap]m", s.text)
                if name_n_datetime is not None:
                    separated = re.split(r"(\d{1,2}\/\d{2}\/\d{4}\s\d{1,2}:\d{1,2}\s[ap]m)", name_n_datetime.string.strip())
                    separated = [x.strip() for x in separated if x != ""]
                    if len(separated) == 1:
                        separated.insert(0, label)
                    collected_data.append(separated)
        
        print("\nI was able to parse the following due dates:")
        for x in collected_data:
            print(x[0] + ": " + x[1])
        change_name = input("Do you wish to change the names of any of the above? (Y/N): ")
        if change_name.lower() == "y":
            name_change(collected_data)

        for row in collected_data:
            row.append(re.search(r"\d{1,2}:\d{1,2}\s[ap]m", row[1]).group())
            tempdatetime = datetime.datetime.strptime(row[1].upper(), "%d/%m/%Y %I:%M %p")
            tempdatetime = tempdatetime.replace(tzinfo=datetime.timezone.utc)
            row[1] = tempdatetime
            
        return collected_data
    
def name_change(ori_list):
    for row in ori_list:
        print("\nName: " + row[0])
        print("Due Date: " + row[1])
        new_name = input("Type new name to change, or just press ENTER to skip: ")
        if new_name != "":
            row[0] = new_name

if __name__ == "__main__":
    ecpparser()