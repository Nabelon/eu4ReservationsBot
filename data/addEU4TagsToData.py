# Work with Python 3.6
# -*- coding: iso-8859-1 -*-
import discord
import json
from PIL import Image
from discord.ext import commands
import os
import time

directory = 'countries'
 
 
with open('data.json') as json_file:
    tagToNations = json.load(json_file)
    
with open ("00_countries.txt", "r") as myfile:
    data=myfile.readlines()
    for i in range(0,len(data)):
        if "=" in data[i] and data[i].split()[0].lower() not in tagToNations.keys():
            tagToNations[data[i].split()[0].lower()] = [[data[i].split("countries/")[1].split(".txt")[0].lower()],0,0];
            print(tagToNations[data[i].split()[0].lower()]) 
with open('dataNew.json', 'w') as f:
    json.dump(tagToNations, f)    
     