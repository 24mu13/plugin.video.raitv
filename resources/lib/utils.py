import datetime
import xbmc, xbmcaddon

ADDON_ID      = 'plugin.video.raitv'
REAL_SETTINGS = xbmcaddon.Addon(id=ADDON_ID)
ADDON_VERSION = REAL_SETTINGS.getAddonInfo('version')
DEBUG         = True #REAL_SETTINGS.getSetting('Enable_Debugging') == 'true'

def sortedDictKeys(adict):
    keys = adict.keys()
    keys.sort()
    return keys

def daterange(start_date, end_date):
    for n in range((end_date - start_date).days + 1):
        yield end_date - datetime.timedelta(n)

def log(msg, level=xbmc.LOGDEBUG):
    if DEBUG == False and level != xbmc.LOGERROR: return
    if level == xbmc.LOGERROR: msg += ' ,' + traceback.format_exc()
    if level == xbmc.LOGDEBUG and DEBUG == True: level = xbmc.LOGNOTICE
    xbmc.log('{}-{} - {}'.format(ADDON_ID, ADDON_VERSION, msg), level)
 