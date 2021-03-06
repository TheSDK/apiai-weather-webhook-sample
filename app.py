#!/usr/bin/env python

import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") is None:
        print("Wrong action!")
        return {}
    #baseurl = "https://query.yahooapis.com/v1/public/yql?"
    baseurl = "http://api.openweathermap.org/data/2.5/weather?"
    owm_query = makeYqlQuery(req)
    if owm_query is None:
        print("owm_query in none!")
        return {}
    print("owm_query: " + owm_query)
    #yql_url = baseurl + urllib.urlencode({'q': yql_query}) + "&format=json"
    #owm_url = baseurl + urllib.urlencode({'q': owm_query})
    #owm_url = "http://api.openweathermap.org/data/2.5/weather?q=" + owm_query + "&appid=" + req.get("result").get("action") + "&units=metric"
    owm_url = baseurl + urllib.urlencode({'q': owm_query}) + "&appid=" + req.get("result").get("action") + "&units=metric"
    print("owm_url: " + owm_url)
    result = urllib.urlopen(owm_url).read()
    data = json.loads(result)
    res = makeWebhookResultOWM(data, owm_query)
    return res


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    #return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"
    return city

def makeWebhookResultOWM(data, location):
    print("OWM result:")
    print(json.dumps(data, indent=4))
    
    wheater_list = data.get('weather')
    if wheater_list is None:
        print("Invalid return: wheater")
        return {}
    
    description = ""
    for wheater in wheater_list:
        descr = wheater.get('description')
        print("wheater.get('description'): " + descr)
        if descr is None:
            print("Invalid return: description")
            return {}
        
        description = description + ", " + descr
        print("description: " + description)
        
    description = description[2:]
    print("description: " + description)
        
    print("before main")
    main_info = data.get('main')
    if main_info is None:
        print("Invalid return: main_info")
        return {}
    temperature = main_info.get('temp')
    if temperature is None:
        print("Invalid return: temperature")
        return {}
    city_name = data.get('name')
    if city_name is None:
        print("Invalid return: city_name")
        return {}
    print("after name")
    
    speech = "Today in " + location + " you find " + description + ", the current temperature is " + str(temperature) + " degree celsius"
        
    print("Response:")
    print(speech)
    
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "owm"
    }


def makeWebhookResult(data):
    print("OWM result:")
    print(json.dumps(data, indent=4))
    
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
             ", the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')
