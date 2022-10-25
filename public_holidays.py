# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 18:08:01 2020

@author: LR
"""

# installing packages
#pip install requests_html
#pip install selenium

from os import chdir
chdir ("C:/Users/LR/Desktop/ME/Programación/Python") # this must change

from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
from selenium import webdriver

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import locale
locale.setlocale(locale.LC_TIME, "es_ES")
'es_ES'

url = "https://www.timeanddate.com/holidays/"
page = requests.get(url, 'html.parser')

soup = BeautifulSoup(page.text)

ul=BeautifulSoup(str(soup.find_all("ul", class_='category-list__list')))
  
# we can store them in a loop
# COUNTRIES=[]
# for i in ul.find_all("li"):
#     print(i.find("a").get_text())
#     COUNTRIES.append(i.find("a").get_text())
# COUNTRIES = COUNTRIES[0:len(COUNTRIES)-3] 

# generating the list of urls to scrape information
URLS=[]
for i in ul.find_all("li"):
    for year in range(2000, 2020):
        # print(i.find("a").get_text())
        URLS.append(i.find("a").get("href")+ str(year) + '?hol=9')
URLS = URLS[0:len(URLS)-60] # delete country groups

# ---------------------------------------------------------------------------
# Example: Chile 2000
URL="https://www.timeanddate.com%s"%URLS[780]
browser = webdriver.Chrome()

browser.get(URL)
time.sleep(3)
html = browser.page_source
soup = BeautifulSoup(html, "lxml")

browser.quit()

table=soup.find("table", class_="table table--left table--inner-borders-rows table--full-width table--sticky table--holidaycountry").tbody

date = [] # date of the holiday day, month
dow  = [] # day of the week
name = [] # name of the holiday
det  = [] # type (e.g. national holiday)
for i in range(0,100):
    try:
        date_ = table.find_all("tr", class_="showrow")[i].find("th", class_="nw")
        date.append(date_.text)
        
        dow_ = table.find_all("tr", class_="showrow")[i].find("td", class_="nw").text
        dow_ = time.strptime(dow_, '%A').tm_wday        
        dow.append(dow_)
        
        # holiday name
        name_ = table.find_all("tr", class_="showrow")[i].find_all("td")[1]
        name.append(name_.text)
        
        det_ = table.find_all("tr", class_="showrow")[i].find_all("td")[2]
        det.append(det_.text)
    except IndexError:
        break
    
df = pd.DataFrame({'date':date,'dow':dow,'name':name,'type':det})
df.to_csv(path_or_buf='data.csv',na_rep='.',sep=',',index=False)
print(df)

# ---------------------------------------------------------------------------

# final_data 
date = [] # date of the holiday day, month
dow  = [] # day of the week (Monday 0 - Sunday 6)
name = [] # name of the holiday
det  = [] # type (e.g. national holiday)
year = [] 
country = [] 
# Now for all countries in every year
for i in URLS:
    URL="https://www.timeanddate.com%s"%i
    print(URL)
    browser = webdriver.Chrome()
    browser.get(URL)
    time.sleep(10)
    html = browser.page_source
    soup = BeautifulSoup(html, "lxml")
    browser.quit()
    try:
        table=soup.find("table", class_="table table--left table--inner-borders-rows table--full-width table--sticky table--holidaycountry").tbody
        for j in range(0,365):
            try:
                date_ = table.find_all("tr", class_="showrow")[j].find("th", class_="nw")
                date.append(date_.text)
         
                dow_ = table.find_all("tr", class_="showrow")[j].find("td", class_="nw").text
                dow_ = time.strptime(dow_, '%A').tm_wday        
                dow.append(dow_)
        
                name_ = table.find_all("tr", class_="showrow")[j].find_all("td")[1]
                name.append(name_.text)
        
                det_ = table.find_all("tr", class_="showrow")[j].find_all("td")[2]
                det.append(det_.text)
                
                year.append(URL[-10:-6]) # URL always ends with '/year?hol=9'
                
                start = URL.find("s/") # path always of the form '/holidays/country/'
                end   = URL.find("/2")
                country.append(URL[start+2:end])
            except IndexError:
                break
        
    except: 
        print(soup.find("section", class_="table-data__table").find("p").text)
        pass      

df = pd.DataFrame({
    'country':country,
    'year':year,
    'date':date,
    'dow':dow,
    'name':name,
    'type':det
})
    
df.to_csv(path_or_buf='public_holidays.csv',na_rep='.',sep=',',index=False)


# ---------------------------------------------------------------------------


#send data to email address

subject = 'New Data!'
FILENAME = 'public_holidays.csv'
sender = 'lrosso@fen.uchile.cl'
password = 'password'
smtp_server = "smtp.gmail.com"
port = 587

recipients  = ['lrosso@fen.uchile.cl', 'rodrigo.a.wagner@gmail.com'] 

msg = MIMEMultipart()
msg['From'] = sender
msg['To'] = ", ".join(recipients ) #COMMASPACE.join([receivers])
msg['Subject'] = subject  

body = 'Code to scrape holidays data ended successfully! (sent from python)'
msg.attach(MIMEText(body,'plain'))  

part = MIMEBase('application', "octet-stream")
part.set_payload(open(FILENAME, "rb").read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', 'attachment', filename=FILENAME)
msg.attach(part)

smtpObj = smtplib.SMTP(smtp_server, port)
smtpObj.ehlo()
smtpObj.starttls()
smtpObj.login(sender, password)
smtpObj.sendmail(sender, recipients, msg.as_string())
smtpObj.quit()

