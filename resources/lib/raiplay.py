# -*- coding: utf-8 -*-
import urllib2
import json
import urlparse
from utils import log
import xbmc, xbmcplugin

BASE_URL      = 'http://www.rai.it'
#TODO get all following URLs from http://www.raiplay.it/mobile/prod/config/RaiPlay_Config.json
GUIDE_URL     = BASE_URL + '/dl/palinsesti/Page-e120a813-1b92-4057-a214-15943d95aa68-json.html?canale={channel}&giorno={day}' # mm-dd-yyyy
CHANNELS_URL  = BASE_URL + '/dl/RaiPlay/2016/PublishingBlock-9a2ff311-fcf0-4539-8f8f-c4fee2a71d58.html?json'

MAIN_MENU     = [('Dirette', '' , 1),
                 ('Guida TV / Replay', '' , 2),
                 ('Programmi', '' , 3)]
#        liStyle = xbmcgui.ListItem("Archivio Telegiornali")
#        addDirectoryItem({"mode": "tg"}, liStyle)
#        liStyle = xbmcgui.ListItem("Videonotizie")
#        addDirectoryItem({"mode": "news"}, liStyle)
#        liStyle = xbmcgui.ListItem("Aree tematiche")
#        addDirectoryItem({"mode": "themes"}, liStyle)

class RaiPlay(object):
    localizeUrl = "http://mediapolisgs.rai.it/relinker/relinkerServlet.htm?cont=201342"
    menuUrl = "http://www.rai.it/dl/RaiPlay/2016/menu/PublishingBlock-20b274b1-23ae-414f-b3bf-4bdc13b86af2.html?homejson"
    AzTvShowPath = "/dl/RaiTV/RaiPlayMobile/Prod/Config/programmiAZ-elenco.json"
    noThumbUrl = "http://www.rai.it/cropgd/256x144/dl/components/img/imgPlaceholder.png"
    
    def __init__(self, sysARG):
        log('__init__')
        self.sysARG  = sysARG
        self.cache   = SimpleCache()
        self.channels   = self.getChannels()
        #self.recordings = self.getRecordings()

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

    def getParams(self):
        return dict(urlparse.parse_qsl(self.sysARG[2][1:]))

    def addDir(self, name, u, mode, infoList=False, infoArt=False):
        name = name.encode("utf-8")
        log('addDir, name = ' + name)
        liz=xbmcgui.ListItem(name)
        liz.setProperty('IsPlayable', 'false')
        if infoList == False: liz.setInfo(type="Video", infoLabels={"mediatype":"video","label":name,"title":name})
        else: liz.setInfo(type="Video", infoLabels=infoList)
        if infoArt == False: liz.setArt({'thumb':ICON,'fanart':FANART})
        else: liz.setArt(infoArt)
        u=self.sysARG[0]+"?url="+urllib.quote_plus(u)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        xbmcplugin.addDirectoryItem(handle=int(self.sysARG[1]),url=u,listitem=liz,isFolder=True)

    def buildMenu(self, items):
        for item in items:
            if len(self.recordings['Schedules']) == 0 and item[0] == LANGUAGE(30013): continue
            self.addDir(*item)
 
    def run(self):  
        params=self.getParams()
        try: url=urllib.unquote_plus(params["url"])
        except: url=None
        try: name=urllib.unquote_plus(params["name"])
        except: name=None
        try: mode=int(params["mode"])
        except: mode=None
        log("Mode: "+str(mode))
        log("URL : "+str(url))
        log("Name: "+str(name))

        if mode==None:  self.buildMenu(MAIN_MENU)
        elif mode == 1: self.buildLive()

        elif mode == 9: self.playVideo(name, url)

        xbmcplugin.setContent(int(self.sysARG[1])    , CONTENT_TYPE)
        xbmcplugin.addSortMethod(int(self.sysARG[1]) , xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(int(self.sysARG[1]) , xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.addSortMethod(int(self.sysARG[1]) , xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.addSortMethod(int(self.sysARG[1]) , xbmcplugin.SORT_METHOD_TITLE)
        xbmcplugin.endOfDirectory(int(self.sysARG[1]), cacheToDisc=True)