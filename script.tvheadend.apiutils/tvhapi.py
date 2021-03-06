# -*- coding: utf-8 -*-

"""
tvhapi.py
~~~~~~~~~~~~~~~

This module is used to make various calls to the Tvheadend API.

By James Hutchinson 2017
"""

from common import log, logError, getString, tvhServername, tvhPort, tvhUsername, tvhPass
import urllib
import urllib.error
import urllib.parse
import urllib.request
import json

def raiseHTTPError(errMsg):
  logError(errMsg)
  onScreenErrMsg = getString(32300) + ' (' + 'http://' + tvhServername + ':' + tvhPort + ')'
  raise RuntimeError(onScreenErrMsg)

def httpAuth(url, authType='digest'):
  passwordMgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
  passwordMgr.add_password(None, url, tvhUsername, tvhPass)

  if authType == 'digest':
    log('Attempting Tvheadend Digest Authentication')
    authHandler = urllib.request.HTTPDigestAuthHandler(passwordMgr)
  else:
    log('Attempting Tvheadend Basic Authentication')
    authHandler = urllib.request.HTTPBasicAuthHandler(passwordMgr)
  return urllib.request.build_opener(authHandler)

def httpPost(url, encodedParams, authType='digest'):
  try:
    request = httpAuth(url, authType)
    response = request.open(url, data=encodedParams)
  except urllib.error.HTTPError as e:
    if e.code == 401:
      if authType == 'digest': #attempt to fallback to basic http auth
        log('Digest Authentication Failed')
        return httpPost(url, encodedParams, 'basic')
      else:
        logError(getString(32301))
    raiseHTTPError('HTTP error %s: %s' % (e.code, e.reason))
  except urllib.error.URLError as e:
    raiseHTTPError('URL error: %s: %s' % (e.code, e.reason))
  except Exception as e:
    raiseHTTPError('HTTP general exception: %s' % e)
  else:
    log('Tvheadend API Request Successful:')
    log('  URL: ' + url)
    log('  Parameters: ' + str(encodedParams))
    log('Content Type: '+ response.headers['content-type'])
    encoding = response.headers['content-type'].split('charset=')[-1]
    log('Encoding: ' + encoding)
    rawResponse = response.read().decode(encoding).encode('utf-8')
    log('Response: ' + str(rawResponse))
    return rawResponse

def tvhApiResponse(urlPath, urlParams):
  url = 'http://' + tvhServername + ':' + tvhPort + urlPath
  encodedParams = urllib.parse.urlencode(urlParams).encode('utf-8')
  response = httpPost(url, encodedParams)
  log('Converting JSON response')
  jsonResponse = json.loads(response, strict=False)
  log('JSON Conversion Complete')
  return jsonResponse

def getTvhUpcomingRecording(uuid, fields):
  return tvhApiResponse('/api/idnode/load', {'uuid':uuid,'list':fields})

def getTvhFinishedRecordings():
  return tvhApiResponse('/api/dvr/entry/grid_finished', {'limit':'999999999'})

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

def triggerOtaEpgGrabber():
  return tvhApiResponse('/api/epggrab/ota/trigger', {'trigger':'1'})
