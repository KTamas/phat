#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import time
import os
import json
from inky import InkyPHAT
from PIL import Image, ImageDraw, ImageFont
from font_fredoka_one import FredokaOne

try:
    import requests
except ImportError:
    exit("This script requires the requests module\nInstall with: sudo pip install requests")

inky_display = InkyPHAT("black")
inky_display.set_border(inky_display.BLACK)

url = 'https://services7.arcgis.com/nuPvVz1HGGfa0Eh7/arcgis/rest/services/korona_tapaukset_kumulatiivisesti_kunnittain/FeatureServer/0/query?f=json&objectIds=32&outFields=Vaesto%2Cilmaantuvuus_14vrk%2Cilmaantuvuus_edelliset_14vrk%2Ckunta%2Ctapauksia_14_tieto%2Ctapauksia_14vrk%2Ctapauksia_edelliset_14vrk%2COBJECTID&outSR=102100&returnGeometry=false&spatialRel=esriSpatialRelIntersects&where=1%3D1'
res = requests.get(url)
if res.status_code == 200:
    # {u'kunta': u'Helsinki', u'OBJECTID': 32, u'tapauksia_14vrk': 519, u'tapauksia_edelliset_14vrk': 1033, u'Vaesto': 660164, u'ilmaantuvuus_edelliset_14vrk': 156.476269533025, u'tapauksia_14_tieto': 0, u'ilmaantuvuus_14vrk': 78.6168285456341}
    data = json.loads(res.content)['features'][0]['attributes']
    #print(data)

# Create a new canvas to draw on
img = Image.open("resources/backdrop.png")
draw = ImageDraw.Draw(img)

# Load the FredokaOne font
#font = ImageFont.truetype(FredokaOne, 22)
font = ImageFont.load("/home/pi/slkr24.pil")

draw.line((31, 35, 210, 35))      # Horizontal top line
draw.line((28, 58, 174, 58))      # Horizontal middle line
draw.line((169, 58, 169, 58), 2)  # Red seaweed pixel :D

# Write text with weather values to the canvas
os.environ['TZ'] = 'Europe/Helsinki'
time.tzset()
datetime = time.strftime("%m/%d %H:%M")

font2 = ImageFont.load("/home/pi/slk8.pil")
draw.text((40, 2), data['kunta'], inky_display.WHITE, font=font2) 
#draw.text((34, 8), datetime, inky_display.WHITE, font=font)

#draw.text((32, 31), "I-00", inky_display.WHITE, font=font)
draw.text((34, 8), u"{:.0f}/{:.0f}".format(data['ilmaantuvuus_14vrk'], data['tapauksia_14vrk']), inky_display.WHITE, font=font)

#draw.text((32, 54), "I-14", inky_display.WHITE, font=font)
draw.text((34, 31), u"{:.0f}/{:.0f}".format(data['ilmaantuvuus_edelliset_14vrk'], data['tapauksia_edelliset_14vrk']), inky_display.WHITE, font=font)

draw.text((34, 54), u"{:.0f}".format(data['Vaesto']), inky_display.WHITE, font=font)
# Display the weather data on Inky pHAT
inky_display.set_image(img)
inky_display.show()
