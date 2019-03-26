from flask import Flask, render_template, request, jsonify

import json
import requests
import time
from pprint import pprint
from json2html import *
from cassandra.cluster import Cluster


app = Flask(__name__,instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

#Connecting to the Cassandra Cluster
cluster = Cluster(['cassandra'])
#Create a sesstion by connecting to cluster
session = cluster.connect()
#Prepare the session to insert the data into database
insert_data = session.prepare("INSERT INTO weatherdata.currenttemp (time, temperature, dew, humidity, wind) VALUES(?,?,?,?,?)")

#The weather url template
weather_url_template = "https://api.breezometer.com/weather/v1/current-conditions?lat={lat}&lon={lng}&key={API_KEY}"


@app.route('/',methods=['GET'])
def weatherconditions():
    my_latitude = request.args.get('lat','51.52369')
    my_longitude = request.args.get('lng','-0.036587')
    
    weather_url = weather_url_template.format(lat=my_latitude, lng=my_longitude, API_KEY=app.config['MY_API_KEY'])

    resp = requests.get(weather_url)

    if resp.ok:
        resp=requests.get(weather_url)
        print(resp.json())
    else:
        print(resp.reason)


    #Extract the data from the replied json format, ready to be inserted into the database
    json_data = requests.get(weather_url).json()
    Temperature = json_data['data']['temperature']['value']
    Dew = json_data['data']['dew_point']['value']
    Humidity = json_data['data']['relative_humidity']
    Wind = json_data['data']['wind']['speed']['value'] 

    #Finally write to the database
    session.execute(insert_data,[time.time(),Temperature,Dew,Humidity,Wind])


    #Return a readable HTML format
    return json2html.convert(resp.json())


if __name__ =="__main__":
     app.run(host="0.0.0.0", port=8080)
    
