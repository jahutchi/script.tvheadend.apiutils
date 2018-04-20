# -*- coding: utf-8 -*-

"""
otaepggrab.py
~~~~~~~~~~~~~~~~~~~

This module is used to manually trigger the OTA EPG grabber via the Tvheadend API

By James Hutchinson 2018
"""

def main():

  from common import logNotice, logError, notificationPopup, getString

  import tvhapi

  def triggerTvhOtaEpgGrabber():
    logNotice('Triggering the OTA EPG grabber via the Tvheadend API')
    if tvhapi.triggerOtaEpgGrabber(): #A success yields a blank {} response
      logError('Encountered an invalid response when attempting to trigger the OTA EPG grabber via the Tvheadend API')
      raise RuntimeError(getString(32500))
    else:
      logNotice('Successfully triggered the OTA EPG grabber via the Tvheadend API')
      notificationPopup(getString(32501))

  #End of function declarations

  triggerTvhOtaEpgGrabber()
