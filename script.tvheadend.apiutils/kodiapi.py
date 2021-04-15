# -*- coding: utf-8 -*-

"""
kodiapi.py
~~~~~~~~~~~~~~~

This module is used to make various calls to the Kodi API

By James Hutchinson 2017
"""

import xbmc
import json
from common import log

def kodiJSONRPC(method, params):
  try:
    response = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "' + method + '", "params": { ' + params + ' } }')
  except:
    raise RuntimeError(getString(32400) + ' ' + getString(32401))
  unicodeStr = response.encode('utf-8')
  log('Kodi JSON API ' + method + ' result:')
  log(unicodeStr)
  return json.loads(unicodeStr, strict=False)

def getRecordings():
  return kodiJSONRPC('PVR.GetRecordings', '"properties": [ "title", "channel", "playcount", "starttime", "endtime", "plot" ]')
