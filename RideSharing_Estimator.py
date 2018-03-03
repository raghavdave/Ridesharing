# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 19:25:58 2017

@author: rpankajdave
"""
#%%

import os
import datetime
import time
import pandas as pd
from uber_rides.session import Session
from uber_rides.client import UberRidesClient
import googlemaps
import smtplib
import requests

os.chdir('C:\\Users\\rpankajdave\\Desktop\\Firm Initiative\\Uber')
#%%

def initialization(from_addr,to_addr):
    
    global gmaps,lat_start,long_start,lat_end,long_end
    GOOGLEMAPS_API_KEY = 'AIzaSyAIG7S5FpC-C4kvp0-7ee0Q__R04QLFk00'
    gmaps = googlemaps.Client(key=GOOGLEMAPS_API_KEY)
    
    start_loc = gmaps.geocode(from_addr)
    print start_loc[0]['formatted_address']
    lat_start = start_loc[0]["geometry"]["location"]["lat"]
    long_start = start_loc[0]["geometry"]["location"]["lng"]
    
    end_loc = gmaps.geocode(to_addr)
    print end_loc[0]['formatted_address']
    lat_end = end_loc[0]["geometry"]["location"]["lat"]
    long_end = end_loc[0]["geometry"]["location"]["lng"]

def initialization_uber():

    global uber_client
    session = Session(server_token='Mj357yha2eIXfYPOg1OctVUElS8J7gCfOlke87V5')
    uber_client = UberRidesClient(session)
    
def initialization_ola():
    
    global headers
    headers = {'X-APP-TOKEN' : "d5b49ae8ae744a78b7534353ec1b59ab"}

#%%
def fare_estimator_uber(lat_start, long_start, lat_end, long_end):

    response = uber_client.get_price_estimates(
    start_latitude=lat_start,
    start_longitude=long_start,
    end_latitude=lat_end,
    end_longitude=long_end,
    seat_count=1
    )

    estimate_uber = response.json.get('prices')
    
    return estimate_uber

def run_estimator_uber():
    
    initialization_uber()
    global time_now
    
    time_now = datetime.datetime.now()
    
    estimate_uber = fare_estimator_uber(lat_start, long_start, lat_end, long_end)

    global text
    text = pd.DataFrame()
    
    for obj in range(len(estimate_uber)):
        a = estimate_uber[obj]
        type_car = a.items()[2][1]
        high = a.items()[4][1]
        low = a.items()[5][1]
        avg = (high + low)/2
        text.loc[obj,'type_car'] =  type_car 
        text.loc[obj,'high'] =  high 
        text.loc[obj,'low'] =  low 
        text.loc[obj,'avg'] =  avg  
    
    print text

def fare_estimator_ola(lat_start, long_start, lat_end, long_end):
    
    global payload
    payload= {'pickup_lat': lat_start, 'pickup_lng': long_start, 'drop_lat': lat_end, 'drop_lng': long_end}
    response = requests.get('http://sandbox-t.olacabs.com/v1/products', params=payload, headers=headers)

    a = response.json()
    estimate_ola = a['ride_estimate']

    return estimate_ola

def run_estimator_ola():
    
    initialization_ola()
    global time_now
    
    time_now = datetime.datetime.now()
    
    estimate_ola = fare_estimator_ola(lat_start, long_start, lat_end, long_end)

    global text
    text = pd.DataFrame()
    
    for obj in range(len(estimate_ola)-1):
        b = estimate_ola[obj]
        high = b['amount_max']
        low = b['amount_min']
        type_car = b['category']
        avg = (high + low)/2
        text.loc[obj,'type_car'] =  type_car 
        text.loc[obj,'high'] =  high 
        text.loc[obj,'low'] =  low 
        text.loc[obj,'avg'] =  avg  
    
    print text

#%%
def mail():
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    
    gmail_user = "raghavfoolcool@gmail.com"
    gmail_pwd = "indiarock"
    TO = 'rpankajdave@deloitte.com'
    SUBJECT = "Uber Prices at " + str(time_now)
    TEXT = text.word.str.cat(sep='\n')
    
    BODY = '\r\n'.join(['To: %s' % TO,
    'From: %s' % gmail_user,
    'Subject: %s' % SUBJECT,
    '', TEXT])    
    
    server.login(gmail_user, gmail_pwd)
    server.sendmail(gmail_user, [TO], BODY)
    print ('email sent')

def document():
    
    master_table = pd.read_csv('master_table - Copy.csv')
    text.loc[:,'Datetime'] = time_now
    text.loc[:,'From'] = from_addr
    text.loc[:,'To'] = to_addr
    master_table = master_table.append(text,ignore_index=True)
    master_table.to_csv('master_table - Copy.csv',index= False)
    
    
#%%

global from_addr,to_addr

from_addr = 'Deloitte L Block, Hyderabad'
to_addr = 'Rainbow Vistas Rock Garden'

initialization(from_addr,to_addr)
run_estimator_uber()
run_estimator_ola()
#document()

counter = 0
while counter<20:
    run_estimator_uber()
    document()
    print counter
#    run_estimator_ola()
#    document()
    time.sleep(120)
    counter = counter + 1
