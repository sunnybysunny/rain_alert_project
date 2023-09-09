import requests
import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()


def get_coordinates():
    """this function retrieves the latitude and longitude of the requested location in the United States using the
    Location IQ API"""

    location_iq_key = os.environ.get("LOCATION_IQ_KEY")
    location_iq_endpoint = "https://us1.locationiq.com/v1/search"
    location = input("Please enter a city and state in the United States: ")
    params = {
        'key': location_iq_key,
        'q': location,
        'format': 'json'
    }
    response = requests.get(location_iq_endpoint, params)
    response.raise_for_status()
    data = response.json()[0]
    latitude = data['lat']
    longitude = data['lon']

    return latitude, longitude, location


def get_weather():
    """this function will retrieve the weather from a specified location in the United States and check if it is
    forecasted to rain between 6 am to 9pm using the Open Weather API. Afterward this function will send an SMS
    message to a user if it is going to rain in their city using the TWILIO API"""

    lat_lon = get_coordinates()
    lat = lat_lon[0]
    lon = lat_lon[1]
    location = lat_lon[2]

    weather_key = os.environ.get("WEATHER_KEY")

    weather_params = {
        "lat": lat,
        "lon": lon,
        "appid": weather_key
    }
    weather_endpoint = "https://api.openweathermap.org/data/2.5/forecast"
    response = requests.get(weather_endpoint, weather_params)

    # will raise an exception if the response status code is not 200
    response.raise_for_status()
    data = response.json()
    hours_of_day = data['list']

    rain_times = {}

    # i=2 represets 6am and increments 3 hours until dictionary i=7 which represents 9pm
    for i in range(2, 8):
        time = int(hours_of_day[i]['dt_txt'].split(" ")[1].split(":")[0])
        description = hours_of_day[i]['weather'][0]['main']

        if description == "Rain":
            if time > 12:
                time -= 12
                rain_times[f"{time} pm"] = description
            else:
                rain_times[f"{time} am"] = description

    # TWILIO API requirements
    account_sid = os.environ.get("TWILIO_SID")
    auth_token = os.environ.get("TWILIO_TOKEN")
    from_num = os.environ.get("TWILIO_NUMBER")
    to_num = os.environ.get("USER_NUMBER")

    # if there is no Rain in forecast, the dictionary will remain empty.
    if rain_times:
        alert = f"Ello mate! Bring an umbrella tomorrow, it's going to rain in {location}"
        client = Client(account_sid, auth_token)
        message = client.messages \
            .create(
                from_=from_num,
                body=alert,
                to=to_num
            )
        print(alert, message.status)
    else:
        no_rain_alert = f"Ello mate! No rain tomorrow in {location} :)"
        client = Client(account_sid, auth_token)
        message = client.messages \
            .create(
                from_=from_num,
                body=no_rain_alert,
                to=to_num
            )
        print(no_rain_alert, message.status)


get_weather()