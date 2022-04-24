# Work with Python 3.6
# -*- coding: iso-8859-1 -*-
import discord
import json
from PIL import Image
from discord.ext import commands
import os
import time

directory = 'countries'
 
countryData = "{\n"
# iterate over files in
# that directory
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    # checking if it is a file
    if os.path.isfile(f):
        print(filename.split(".")[0])
    with open (f, "r") as myfile:
        data=myfile.readlines()
        for i in range(0,10):
            if data[i].startswith("color"):
                print(filename)
                colors =  data[i].split("{")[1].split("}")[0].split()
                countryData += "\"" + filename.split(".")[0].lower() + "\": [" + str(colors[0])+ ", "+str(colors[1])+ ", "+str(colors[2]) + "],\n"
                break
countryData += "}"
with open('countryDataEU4.json', 'w') as f:
    f.write(countryData)    
        
     