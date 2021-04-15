# -*- coding: utf-8 -*-

"""
deletewatched.py
~~~~~~~~~~~~~~~

This module is used to delete all recordings from tvheadend that are marked watched in kodi

By James Hutchinson 2017
"""

def main():

  from common import log, logInfo, logError, epochFromUTCTimestamp, getString, notificationPopup, getCurrentWindowId, okDialog, yesNoDialog, kodiMajorVersion
  import kodiapi
  import tvhapi

  def filterWatchedKodiRecordings(kodiRecordings):
    return [x for x in kodiRecordings["result"]["recordings"] if x["playcount"] > 0]

  def deletionConfirmMsg(numRecordings):
    if numRecordings == 1:
      return getString(32103) + '\n' + getString(32106)
    else:
      return getString(32104) + ' ' + str(numRecordings) + ' ' + getString(32105) + '\n' + getString(32106)

  def getTvhRecordingUuid(kodiWatchedRecording, tvhRecordings):
    kodiEpochStartTime = epochFromUTCTimestamp(kodiWatchedRecording["starttime"])
    logInfo('Found Watched Recording:')
    logInfo('  Channel: ' + kodiWatchedRecording["channel"])
    logInfo('  Title: ' + kodiWatchedRecording["title"])
    logInfo('  Start Date/Time: ' + kodiWatchedRecording["starttime"])
    logInfo('  Epoch Start Time: ' + str(kodiEpochStartTime))
    logInfo('  End Date/Time: ' + kodiWatchedRecording["endtime"])
    logInfo('  Plot: ' + kodiWatchedRecording["plot"])

    tvhRecording = [x for x in tvhRecordings["entries"] \
                        if     kodiWatchedRecording["channel"] == x["channelname"] \
                       and     kodiWatchedRecording["title"]   == x["disp_title"] \
                       and     kodiEpochStartTime >= x["start_real"] \
                       and     kodiEpochStartTime < x["stop_real"] \
                       and (   kodiWatchedRecording["plot"] == x["disp_description"] \
                            or kodiWatchedRecording["plot"] == x["disp_subtitle"] ) ]
    if len(tvhRecording) == 1: #Make sure that one and only one recording was found
      tvhRecordingUuid = str(tvhRecording[0]["uuid"])
      logInfo('  Tvheadend Recording UUID: ' + tvhRecordingUuid)
      return tvhRecordingUuid
    else:
      logError('The Tvheadend lookup found ' + str(len(tvhRecording)) + ' recordings, but we expected 1')
      return 0

  def deleteWatchedRecording(kodiWatchedRecording, tvhRecordings):
    success = False

    tvhRecordingUuid = getTvhRecordingUuid(kodiWatchedRecording, tvhRecordings)
    if tvhRecordingUuid:
      if len(tvhRecordingUuid) == 32:
        logInfo('Deleting Watched Recording UUID: ' + tvhRecordingUuid)
        deletionResponse = tvhapi.deleteTvhFinishedRecording(tvhRecordingUuid)
        if not deletionResponse: #Successful deletion yields a blank {} response
          logInfo('Recording Successfully Deleted')
          success = True
        else:
          logError('Deletion failed, invalid response from the Tvheadend API')
      else:
        logError('Skipping deletion since the Tvheadend lookup returned an invalid UUID')
    else:
      logError('Skipping deletion, since the Tvheadend lookup failed to identify a unique entry')
    logInfo('--------------------------------------------------------------------------------')
    return success

  def checkWindowId():
    log('WindowID: ' + str(getCurrentWindowId()) )
    if getCurrentWindowId() != 10701:
      raise RuntimeError(getString(32100))

  def deleteAllWatchedRecordings():
    logInfo('Attempting to delete all watched recordings')
    logInfo('Gathering list of recordings from Kodi')
    kodiRecordings = kodiapi.getRecordings()
    logInfo('Filtering out watched Kodi recordings')
    kodiWatchedRecordings = filterWatchedKodiRecordings(kodiRecordings)

    if len(kodiWatchedRecordings) == 0:
      logInfo('No watched recordings were found')
      okDialog(getString(32102), getString(32101))
    else:
      logInfo(str(len(kodiWatchedRecordings)) + ' watched recordings were found')
      logInfo('Prompting for confirmation before proceeding')
      confirmMsg = deletionConfirmMsg(len(kodiWatchedRecordings))
      if yesNoDialog(confirmMsg, getString(32101)):
        logInfo('User answered yes to the confirmation prompt, so continuing')
        logInfo('Gathering list of recordings from Tvheadend')
        tvhRecordings = tvhapi.getTvhFinishedRecordings()

        numFilesDeleted = 0
        logInfo('----------------------------------------------------------------------')
        for kodiWatchedRecording in kodiWatchedRecordings:
          if deleteWatchedRecording(kodiWatchedRecording, tvhRecordings): numFilesDeleted += 1

        notificationPopup(str(numFilesDeleted) + ' ' + getString(32107))
        logInfo(str(numFilesDeleted) + ' watched recording(s) were deleted')
      else:
        logInfo('The user answered no to the confirmation prompt, so skipping deletion')

  #End of function declarations
  checkWindowId()
  deleteAllWatchedRecordings()
