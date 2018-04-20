# -*- coding: utf-8 -*-

"""
addon.py
~~~~~~~~~~~~~~~

This script takes an argument for which action to take and calls the relevant module.

By James Hutchinson 2017
"""

from datetime import datetime
start = datetime.now()
from common import handleException, displayError, log, logNotice, getString, setAddonExecutingStatus, logExecutionTime

log('Script Started')
try:
  setAddonExecutingStatus(True)
except RuntimeError as e:
  logNotice(e.message)
except:
  handleException(getString(32009))
else:
  from sys import argv
  if len(argv) > 1:
    if argv[1] == 'delete-watched-recordings':
      try:
        import deletewatched
        deletewatched.main()
      except RuntimeError as e:
        displayError(e.message)
      except:
        handleException(getString(32004) + '\n' + getString(32006))
    elif argv[1] == 'toggle-series-link':
      try:
        import toggleserieslink
        toggleserieslink.main()
        logExecutionTime(start)
      except RuntimeError as e:
        displayError(e.message)
      except:
        handleException(getString(32005) + '\n' + getString(32006))
    elif argv[1] == 'refresh-epg':
      try:
        import otaepggrab
        otaepggrab.main()
      except RuntimeError as e:
        displayError(e.message)
      except:
        handleException(getString(32010) + '\n' + getString(32006))
    else:
      displayError(getString(32001) + ": " + argv[1] + "\n" + getString(32003) )
  else:
    displayError(getString(32002) + "\n" + getString(32003) )

setAddonExecutingStatus(False)
