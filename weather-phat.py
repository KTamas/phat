#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import time
import os
import argparse
import json
from inky import InkyPHAT
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
load_dotenv()

try:
    import requests
except ImportError:
    exit("This script requires the requests module\nInstall with: sudo pip install requests")

try:
    import geocoder
except ImportError:
    exit("This script requires the geocoder module\nInstall with: sudo pip install geocoder")

try:
    from bs4 import BeautifulSoup
except ImportError:
    exit("This script requires the bs4 module\nInstall with: sudo pip install beautifulsoup4")


print("Inky pHAT: Weather")

# Command line arguments to set display colour

parser = argparse.ArgumentParser()
parser.add_argument('--color', '-c', type=str, required=False, choices=["red", "black", "yellow"], help="ePaper display color", nargs="?", default="black")
args = parser.parse_args()

# Set up the display

color = args.color
inky_display = InkyPHAT(color)
inky_display.set_border(inky_display.BLACK)

# Details to customise your weather display

CITY = "London"
COUNTRYCODE = "UK"
WARNING_TEMP = 23.0

# Convert a city name and country code to latitude and longitude
def get_coords(address):
    g = geocoder.arcgis(address)
    coords = g.latlng
    return coords

# Query Dark Sky (https://darksky.net/) to scrape current weather data
def get_weather(address):
    coords = get_coords(address)
    weather = {}
    apikey = os.getenv("PW_API_KEY")
    res = requests.get("https://api.pirateweather.net/forecast/{apikey}/{latlon}?units=si".format(apikey=apikey,latlon=",".join([str(c) for c in coords])))
    if res.status_code == 200:
        w = json.loads(res.content)
        weather["summary"]=w["currently"]["summary"]
        weather["temperature"] = int(w["currently"]["temperature"])
        weather["pressure"] = int(w["currently"]["pressure"])
        return weather
    else:
        return weather

def create_mask(source, mask=(inky_display.WHITE, inky_display.BLACK, inky_display.RED)):
    """Create a transparency mask.

    Takes a paletized source image and converts it into a mask
    permitting all the colours supported by Inky pHAT (0, 1, 2)
    or an optional list of allowed colours.

    :param mask: Optional list of Inky pHAT colours to allow.

    """
    mask_image = Image.new("1", source.size)
    w, h = source.size
    for x in range(w):
        for y in range(h):
            p = source.getpixel((x, y))
            if p in mask:
                mask_image.putpixel((x, y), 255)

    return mask_image

# Dictionaries to store our icons and icon masks in
icons = {}
masks = {}

# Get the weather data for the given location
location_string = "{city}, {countrycode}".format(city=CITY, countrycode=COUNTRYCODE)
weather = get_weather(location_string)

# This maps the weather summary from Dark Sky
# to the appropriate weather icons
icon_map = {
    "snow": ["snow", "sleet"],
    "rain": ["rain"],
    "cloud": ["fog", "cloudy", "partly-cloudy-day", "partly-cloudy-night"],
    "sun": ["clear-day", "clear-night"],
    "storm": [],
    "wind": ["wind"]
}

# Placeholder variables
pressure = 0
temperature = 0
weather_icon = None

if weather:
    temperature = weather["temperature"]
    pressure = weather["pressure"]
    summary = weather["summary"]

    for icon in icon_map:
        if summary in icon_map[icon]:
            weather_icon = icon
            break

else:
    print("Warning, no weather information found!")

# Create a new canvas to draw on
img = Image.open("resources/backdrop.png")
draw = ImageDraw.Draw(img)

# Load our icon files and generate masks
for icon in glob.glob("resources/icon-*.png"):
    icon_name = icon.split("icon-")[1].replace(".png", "")
    icon_image = Image.open(icon)
    icons[icon_name] = icon_image
    masks[icon_name] = create_mask(icon_image)

font = ImageFont.load("fonts/slkr24.pil")

# Draw lines to frame the weather data
draw.line((69, 36, 69, 81))       # Vertical line
draw.line((31, 35, 210, 35))      # Horizontal top line
draw.line((69, 58, 174, 58))      # Horizontal middle line
draw.line((169, 58, 169, 58), 2)  # Red seaweed pixel :D

# Write text with weather values to the canvas
os.environ['TZ'] = 'Europe/London'
time.tzset()
datetime = time.strftime("%m/%d %H:%M")

font2 = ImageFont.load("fonts/slk8.pil")
draw.text((40, 2), "London", inky_display.WHITE, font=font2) 
draw.text((34, 8), datetime, inky_display.WHITE, font=font)

draw.text((72, 31), "T", inky_display.WHITE, font=font)
draw.text((90, 31), u"{}°".format(temperature), inky_display.WHITE if temperature < WARNING_TEMP else inky_display.RED, font=font)

draw.text((72, 54), "P", inky_display.WHITE, font=font)
draw.text((90, 54), "{}".format(pressure), inky_display.WHITE, font=font)

# Draw the current weather icon over the backdrop
if weather_icon is not None:
    img.paste(icons[weather_icon], (28, 36), masks[weather_icon])

else:
    draw.text((28, 36), "?", inky_display.RED, font=font)

# Display the weather data on Inky pHAT
inky_display.set_image(img)
inky_display.show()
