# -*- coding: utf-8 -*-

"""
common.py
~~~~~~~~~~~~~~~

This module is used to declare various useful common variables and functions.

By James Hutchinson 2017
"""

import traceback
import collections
import xbmc
import xbmcgui
import xbmcaddon
from dateutil.parser import *
from time import time,mktime,strptime,strftime,gmtime
from datetime import datetime

addon = xbmcaddon.Addon()
addonDebug = addon.getSetting('debug')
addonId = addon.getAddonInfo('id')
addonName = addon.getLocalizedString(32000)

tvhServername = addon.getSetting('tvh_servername')
tvhPort = addon.getSetting('tvh_port')
tvhUsername = addon.getSetting('tvh_user')
tvhPass = addon.getSetting('tvh_pass')

seriesLinkManualRecType = addon.getSetting('serieslink_manual_rec_type')
MANUAL_RECTYPE_KODI_PROMPT = '0'  # Display Kodi Timer Rule Prompt
MANUAL_RECTYPE_TVH_AUTOREC = '1'  # Create basic AutoRec entry via the TVHeadend API
MANUAL_RECTYPE_NO_ACTION   = '2'  # Display a Popup and Take No Action

kodiLongdateFormat = xbmc.getRegion('datelong')
kodiTimeFormatNoSeconds = xbmc.getRegion('time').replace(':%S','')
kodiLongDateTimeFormatNoSeconds = kodiLongdateFormat + ' ' + kodiTimeFormatNoSeconds

def setAddonExecutingStatus(newState):
  if newState == True:
    if xbmc.getInfoLabel('Window(10000).Property(script.tvheadend.apiutils.isrunning)') == 'True':
      raise RuntimeError('Another instance of the script is already running')
    else:
      xbmcgui.Window(10000).setProperty('script.tvheadend.apiutils.isrunning', 'True')
  else:
    xbmcgui.Window(10000).setProperty('script.tvheadend.apiutils.isrunning', 'False')

def getString(id):
  return addon.getLocalizedString(id)

def getKodiString(id):
  return xbmc.getLocalizedString(id)

def log(msg, level=xbmc.LOGDEBUG):
  if addonDebug == 'true' and level == xbmc.LOGDEBUG:
    level = xbmc.LOGNOTICE
  try:
    if isinstance(msg, unicode):
      msg = '%s' % (msg.encode('utf-8'))
    xbmc.log('[%s] %s' % (addonId, msg), level)
  except Exception as e:
    try:
      xbmc.log('Logging Failure: %s' % (e), level)
    except:
      pass # just give up

def logNotice(msg):
  log(msg, xbmc.LOGNOTICE)

def logError(errMsg):
  log(errMsg, xbmc.LOGWARNING)

def displayError(errMsg):
  logError(errMsg)
  notificationPopup(errMsg, 'DefaultIconError.png', addonName)

def handleException(onScreenMsg, logMsg='An unexpected error occurred'):
  displayError(onScreenMsg)
  logError(traceback.format_exc())

def notificationPopup(msg, icon='default', title=getKodiString(19166), timeout='5000'):
  args=title+','+msg+','+str(timeout)
  if icon != 'default': args=args+','+icon
  xbmc.executebuiltin('Notification(' + args + ')')

def okDialog(message, title=addonName):
  xbmcgui.Dialog().ok(title, message)

def yesNoDialog(message, title=addonName):
  return xbmcgui.Dialog().yesno(title, message)

def epochFromUTCTimestamp(strTimestamp):
  return int((parse(strTimestamp+'Z') - parse('1970-01-01 00:00:00Z')).total_seconds())

def epochFromLocalTimestamp(strTimestamp, strTimestampFormat=kodiLongDateTimeFormatNoSeconds):
  #return int(mktime(strptime(strTimestamp, strTimestampFormat)))
  localDateTime = datetime.fromtimestamp(mktime(strptime(strTimestamp, strTimestampFormat)))
  utcOffset = datetime.now() - datetime.utcnow()
  utcDateTime = localDateTime - utcOffset
  epoch = datetime.utcfromtimestamp(0)
  return int((utcDateTime - epoch).total_seconds())

def epochNow():
  return int(time())

def convertDictToText(data):
  if isinstance(data, basestring):
    return str(data.encode('utf8'))
  elif isinstance(data, collections.Mapping):
    return dict(map(convertDictToText, data.iteritems()))
  elif isinstance(data, collections.Iterable):
    return type(data)(map(convertDictToText, data))
  else:
    return data

def getKodiInfoLabel(label, errorString=getString(32007)):
  retVal = xbmc.getInfoLabel(label)
  if not retVal:
    errorString = errorString + label
    raise RuntimeError(errorString)
  else:
    log(label + ': ' + retVal)
    return retVal

def getKodiCondVisibility(label, errorString=getString(32008)):
  retVal = xbmc.getCondVisibility(label)
  log(label + ': ' + str(retVal))
  return retVal

def getCurrentWindowId():
  return xbmcgui.getCurrentWindowId()

def xbmcExecuteBuiltin(action):
  xbmc.executebuiltin(action)

def logExecutionTime(start):
  logNotice('Script execution time: ' + str((datetime.now() - start).total_seconds()) + 's')

def kodiMajorVersion():
  return int(xbmc.getInfoLabel('System.BuildVersion')[:2])
