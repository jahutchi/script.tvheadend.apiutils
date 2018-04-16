# -*- coding: utf-8 -*-

"""
tvhapi.py
~~~~~~~~~~~~~~~

This module is used to make various calls to the Tvheadend API.

By James Hutchinson 2017
"""

from common import log, logError, getString, tvhServername, tvhPort, tvhUsername, tvhPass
import httplib
import urllib
import urllib2
import json

def raiseHTTPError(errMsg):
  logError(errMsg)
  onScreenErrMsg = getString(32300) + ' (' + 'http://' + tvhServername + ':' + tvhPort + ')'
  raise RuntimeError(onScreenErrMsg)

def httpAuth(url, authType='digest'):
  passwordMgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
  passwordMgr.add_password(None, url, tvhUsername, tvhPass)

  if authType == 'digest':
    log('Attempting Tvheadend Digest Authentication')
    authHandler = urllib2.HTTPDigestAuthHandler(passwordMgr)
  else:
    log('Attempting Tvheadend Basic Authentication')
    authHandler = urllib2.HTTPBasicAuthHandler(passwordMgr)
  return urllib2.build_opener(authHandler)

def httpPost(url, encodedParams, authType='digest'):
  try:
    request = httpAuth(url, authType)
    response = request.open(url, data=encodedParams)
  except urllib2.HTTPError, e:
    if e.code == 401:
      if authType == 'digest': #attempt to fallback to basic http auth
        log('Digest Authentication Failed')
        return httpPost(url, encodedParams, 'basic')
      else:
        logError(getString(32301))
    raiseHTTPError('HTTP error %s: %s' % (e.code, e.reason))
  except urllib2.URLError, e:
    raiseHTTPError('URL error: %s: %s' % (e.code, e.reason))
  except httplib.HTTPException, e:
    raiseHTTPError('HTTP exception: %s' % e)
  except socket.error, e:
    raiseHTTPError('HTTP socket error: %s' % e)
  except Exception, e:
    raiseHTTPError('HTTP general exception: %s' % e)
  else:
    log('Tvheadend API Request Successful:')
    log('  URL: ' + url)
    log('  Parameters: ' + encodedParams)
    rawResponse = response.read()
    log('Tvheadend API response received:')
    log(rawResponse)
    response.close
    return rawResponse

def tvhApiResponse(urlPath, urlParams):
  url = 'http://' + tvhServername + ':' + tvhPort + urlPath
  encodedParams = urllib.urlencode(urlParams)
  response = httpPost(url, encodedParams)
  log('Converting JSON response')
  jsonResponse = json.loads(response)
  log('JSON Conversion Complete')
  return jsonResponse

def getTvhUpcomingRecording(uuid, fields):
  return tvhApiResponse('/api/idnode/load', {'uuid':uuid,'list':fields})

def getTvhFinishedRecordings(epochStartDateTime=0, epochEndDateTime=0):
  if epochStartDateTime:
    filterParams = '{\"type\":\"numeric\",\"value\":' + str(epochStartDateTime) + ',\"field\":\"start\"}'
  if epochEndDateTime:
    param = '{\"type\":\"numeric\",\"value\":' + str(epochEndDateTime) + ',\"field\":\"stop\"}'
    if filterParams: param = ',' + param
    filterParams = filterParams + param
  if filterParams: filterParams = '[' + filterParams + ']'
  return tvhApiResponse('/api/dvr/entry/grid_finished', {'filter':filterParams,'limit':'999999999'})

def getTvhChannels():
  return tvhApiResponse('/api/channel/list', {'all':'1'})

def getTvhChannelEpg(channelId):
  return tvhApiResponse('/api/epg/events/grid', {'channel':channelId})

def getTvhEpgEvent(channelNumber, epochStartDateTime, epochEndDateTime):
  filterParams = '[{\"type\":\"numeric\",\"comparison\":\"eq\",\"value\":' + channelNumber + ',\"field\":\"channelNumber\"},' + \
                  '{\"type\":\"numeric\",\"value\":' + str(epochStartDateTime) + ',\"field\":\"start\"},' + \
                  '{\"type\":\"numeric\",\"value\":' + str(epochEndDateTime) + ',\"field\":\"stop\"}]'
  return tvhApiResponse('/api/epg/events/grid', {'filter':filterParams})

def deleteTvhFinishedRecording(uuid):
  return tvhApiResponse('/api/dvr/entry/remove', {'uuid':'[\"' + uuid + '\"]'})

def addTvhSeriesLink(eventId):
  return tvhApiResponse('/api/dvr/autorec/create_by_series', {'event_id':eventId,'config_uuid':''})

def addTvhAutoRecRule(tvhShowTitle, tvhChannelUuid, comment=getString(32302)):
  return tvhApiResponse('/api/dvr/autorec/create', {'conf':'{\"enabled\":1,\"comment\":\"' + comment + '\",\"title\":\"' + tvhShowTitle + '\",\"channel\":\"' + tvhChannelUuid + '\"}'})

def renameTvhIdNode(uuid, newName, newComment=getString(32302)):
  return tvhApiResponse('/api/idnode/save', {'node':'[{\"name\":\"' + newName + '\",\"comment\":\"' + newComment + '\",\"uuid\":\"' + uuid + '\"}]'})

def deleteTvhIdNode(uuid):
  return tvhApiResponse('/api/idnode/delete', {'uuid':'[\"' + uuid + '\"]'})
