﻿# -*- coding: utf-8 -*-
import urllib2
import json

BASE_URL      = 'http://www.rai.it'
#TODO get all following URLs from http://www.raiplay.it/mobile/prod/config/RaiPlay_Config.json
GUIDE_URL     = BASE_URL + '/dl/palinsesti/Page-e120a813-1b92-4057-a214-15943d95aa68-json.html?canale={channel}&giorno={day}' # mm-dd-yyyy
CHANNELS_URL  = BASE_URL + '/dl/RaiPlay/2016/PublishingBlock-9a2ff311-fcf0-4539-8f8f-c4fee2a71d58.html?json'

class RaiPlay(object):
    localizeUrl = "http://mediapolisgs.rai.it/relinker/relinkerServlet.htm?cont=201342"
    menuUrl = "http://www.rai.it/dl/RaiPlay/2016/menu/PublishingBlock-20b274b1-23ae-414f-b3bf-4bdc13b86af2.html?homejson"
    AzTvShowPath = "/dl/RaiTV/RaiPlayMobile/Prod/Config/programmiAZ-elenco.json"
    noThumbUrl = "http://www.rai.it/cropgd/256x144/dl/components/img/imgPlaceholder.png"
    
    def getBaseURL(self):
        return BASE_URL

    def getCountry(self):
        response = urllib2.urlopen(self.localizeUrl).read()
        return response
        
    def getChannels(self):
        response = json.load(urllib2.urlopen(CHANNELS_URL))
        return response["dirette"]
        
    def getProgrammes(self, channelName, epgDate):
        channelTag = channelName.replace(" ", "")
        #url = url.replace("[nomeCanale]", channelTag)
        #url = url.replace("[dd-mm-yyyy]", epgDate)
        url = GUIDE_URL.format(channel=channelTag, day=epgDate)
        response = json.load(urllib2.urlopen(url))
        return response[channelName][0]["palinsesto"][0]["programmi"]
        
    def getMainMenu(self):
        response = json.load(urllib2.urlopen(self.menuUrl))
        return response["menu"]

    # RaiPlay Genere Page
    # RaiPlay Tipologia Page
    def getCategory(self, pathId):
        url = self.getUrl(pathId)
        response = json.load(urllib2.urlopen(url))
        return response["blocchi"]
  
    # Raiplay Tipologia Item
    def getProgrammeList(self, pathId):
        url = self.getUrl(pathId)
        response = json.load(urllib2.urlopen(url))
        return response
    
    #  PLR programma Page
    def getProgramme(self, pathId):
        url = self.getUrl(pathId)
        response = json.load(urllib2.urlopen(url))
        return response["Blocks"]
    
    def getContentSet(self, url):
        url = self.getUrl(url)
        response = json.load(urllib2.urlopen(url))
        return response["items"]
    
    def getVideoUrl(self, pathId):
        url = self.getUrl(pathId)
        response = json.load(urllib2.urlopen(url))
        url = response["video"]["contentUrl"]
        return url

    def getUrl(self, pathId):
        pathId = pathId.replace(" ", "%20")
        if pathId[0:2] == "//":
            url = "http:" + pathId
        elif pathId[0] == "/":
            url = BASE_URL + pathId
        else:
            url = pathId
        return url
        
    def getThumbnailUrl(self, pathId):
        if pathId == "":
            url = self.noThumbUrl
        else:
            url = self.getUrl(pathId)
            url = url.replace("[RESOLUTION]", "256x-")
        return url
