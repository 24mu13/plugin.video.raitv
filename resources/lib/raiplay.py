﻿# -*- coding: utf-8 -*-
import json, urlparse, urllib, urllib2
from simplecache import SimpleCache, use_cache
import xbmc, xbmcgui, xbmcplugin

from relinker import Relinker
from utils import log

BASE_URL      = 'http://www.rai.it'
#TODO get all following URLs from http://www.raiplay.it/mobile/prod/config/RaiPlay_Config.json
GUIDE_URL     = BASE_URL + '/dl/palinsesti/Page-e120a813-1b92-4057-a214-15943d95aa68-json.html?canale={channel}&giorno={day}' # mm-dd-yyyy
CHANNELS_URL  = BASE_URL + '/dl/RaiPlay/2016/PublishingBlock-9a2ff311-fcf0-4539-8f8f-c4fee2a71d58.html?json'
NO_LOGO_URL   = BASE_URL + '/cropgd/256x144/dl/components/img/imgPlaceholder.png'

CONTENT_TYPE  = 'episodes'
MAIN_MENU     = [('Dirette',            '' , 1),
                 ('Guida TV / Replay',  '' , 2),
                 ('Programmi (TODO)',   '' , 3)]

class RaiPlay(object):   
    def __init__(self, sysARG):
        log('__init__')
        self.sysARG  = sysARG
        self.cache   = SimpleCache()
        self.channels   = self.getChannels()

    @use_cache(1)
    def getChannels(self):
        response = json.load(urllib2.urlopen(CHANNELS_URL))
        return response["dirette"]
        
    def getParams(self):
        return dict(urlparse.parse_qsl(self.sysARG[2][1:]))

    def addDir(self, name, u, mode, infoList=False, infoArt=False):
        name = name.encode("utf-8")
        log('addDir, name = ' + name)
        liz=xbmcgui.ListItem(name)
        liz.setProperty('IsPlayable', 'false')
        if infoList == False: liz.setInfo(type="Video", infoLabels={"mediatype":"video","label":name,"title":name})
        else: liz.setInfo(type="Video", infoLabels=infoList)
        #if infoArt == False: liz.setArt({'thumb':ICON,'fanart':FANART})
        #else: liz.setArt(infoArt)
        u=self.sysARG[0]+"?url="+urllib.quote_plus(u)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        xbmcplugin.addDirectoryItem(handle=int(self.sysARG[1]),url=u,listitem=liz,isFolder=True)

    def addLink(self, name, u, mode, infoList=False, infoArt=False, total=0, contextMenu=None):
        name = name.encode("utf-8")
        log('addLink, name = ' + name)
        liz=xbmcgui.ListItem(name)
        if mode == 21: liz.setProperty("IsPlayable","false")
        else: liz.setProperty('IsPlayable', 'true')
        if infoList == False: liz.setInfo(type="Video", infoLabels={"mediatype":"video","label":name,"title":name})
        else: liz.setInfo(type="Video", infoLabels=infoList)
        if infoArt == False: liz.setArt({'thumb':ICON,'fanart':FANART})
        else: liz.setArt(infoArt)
        if contextMenu is not None: liz.addContextMenuItems(contextMenu)
        u=self.sysARG[0]+"?url="+urllib.quote_plus(u)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        xbmcplugin.addDirectoryItem(handle=int(self.sysARG[1]),url=u,listitem=liz,totalItems=total)

    def buildMenu(self, items):
        for item in items:
            self.addDir(*item)

    def buildLive(self):
        for channel in self.channels:
            chname = channel["channel"]
            chlogo = NO_LOGO_URL
            if channel["transparent-icon"]:
                chlogo = channel["transparent-icon"].replace("[RESOLUTION]", "256x-")
            thumb  = chlogo
            genre  = 'Live'
            link   = channel["video"]["contentUrl"]
            infoLabels = {"mediatype":"episode","label":chname,"title":chname,"genre":genre}
            infoArt    = {"thumb":thumb,"poster":thumb,"fanart":FANART,"icon":chlogo,"clearlogo":chlogo}
            self.addLink(label, link, 9, infoLabels, infoArt, len(self.channels))
        xbmcplugin.addSortMethod(int(self.sysARG[1]) , xbmcplugin.SORT_METHOD_NONE)
 
    def playVideo(self, name, url, liz=None):
        log('playVideo')
        #if pathId != "":
        #    log("PathID: " + pathId)
        #    raiplay = RaiPlay()
        #    url = raiplay.getVideoUrl(pathId)

        # Handle RAI relinker
        if url[:53] == "http://mediapolis.rai.it/relinker/relinkerServlet.htm" or \
            url[:56] == "http://mediapolisvod.rai.it/relinker/relinkerServlet.htm" or \
            url[:58] == "http://mediapolisevent.rai.it/relinker/relinkerServlet.htm":
            log("Relinker URL: " + url)
            relinker = Relinker()
            url = relinker.getURL(url)
            
        # Add the server to the URL if missing
        if url !="" and url.find("://") == -1:
            url = raiplay.getBaseURL() + url
        log("Media URL: " + url)

        # It seems that all .ram files I found are not working
        # because upstream file is no longer present
        if url[-4:].lower() == ".ram":
            dialog = xbmcgui.Dialog()
            dialog.ok("Errore", "I file RealAudio (.ram) non sono supportati.")
            return
        
        # Play the item
        item=xbmcgui.ListItem(path=url + '|User-Agent=' + urllib.quote_plus(Relinker.UserAgent))
        xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=item)

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
        elif mode == 2: self.buildLineup(name, url)
        elif mode == 9: self.playVideo(name, url)

        xbmcplugin.setContent(int(self.sysARG[1])    , CONTENT_TYPE)
        xbmcplugin.addSortMethod(int(self.sysARG[1]) , xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(int(self.sysARG[1]) , xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.addSortMethod(int(self.sysARG[1]) , xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.addSortMethod(int(self.sysARG[1]) , xbmcplugin.SORT_METHOD_TITLE)
        xbmcplugin.endOfDirectory(int(self.sysARG[1]), cacheToDisc=True)