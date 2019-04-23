# -*- coding: utf-8 -*-
import sys
import sys, urlparse
import xbmc, xbmcplugin, xbmcaddon
from resources.lib.raiplay import RaiPlay

# plugin constants
__plugin__ = "plugin.video.raitv"
__author__ = "Nightflyer, 24mu13"

Addon = xbmcaddon.Addon(id=__plugin__)

if __name__ == '__main__':

    # gets content_type
    params = urlparse.parse_qs(sys.argv[2][1:])
    content_type = params.get('content_type', None)
    if content_type: content_type = content_type[0]

    # RaiPlay
    if content_type == 'video':
        RaiPlay(sys.argv).run()

    # RaiPlayRadio
    #elif content_type == 'audio':
    #    raiplayradio.RaiPlayRadio(sys.argv).run()
