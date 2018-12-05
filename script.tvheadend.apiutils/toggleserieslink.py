# -*- coding: utf-8 -*-

"""
toggleserieslink.py
~~~~~~~~~~~~~~~~~~~

This module is used to toggle a series link timer from within the TV guide

By James Hutchinson 2017
"""

def main():

  from common import log, logNotice, logError, epochFromUTCTimestamp, epochFromLocalTimestamp, epochNow, getString
  from common import getKodiInfoLabel, getKodiCondVisibility, getCurrentWindowId, xbmcExecuteBuiltin, seriesLinkManualRecType
  from common import MANUAL_RECTYPE_KODI_PROMPT, MANUAL_RECTYPE_TVH_AUTOREC, MANUAL_RECTYPE_NO_ACTION

  import tvhapi

  def getCurrentEventEpochStartDateTime():
    startDateTimeStr = getKodiInfoLabel('ListItem.StartDate') + ' ' + getKodiInfoLabel('ListItem.StartTime')
    epochStartDateTime = epochFromLocalTimestamp(startDateTimeStr)
    log('Selected Event Start Date/Time (Epoch): ' + str(epochStartDateTime) )
    return epochStartDateTime

  def getCurrentEventEpochEndDateTime():
    endDateTimeStr = getKodiInfoLabel('ListItem.EndDate') + ' ' + getKodiInfoLabel('ListItem.EndTime')
    epochEndDateTime = epochFromLocalTimestamp(endDateTimeStr)
    log('Selected Event End Date/Time (Epoch): ' + str(epochEndDateTime) )
    return epochEndDateTime

  def getTvhAutorecUuid(tvhDvrUuid):
    tvhRecording = tvhapi.getTvhUpcomingRecording(tvhDvrUuid, 'autorec')["entries"]
    if len(tvhRecording) == 1:
      if tvhRecording[0]["params"][0]["id"] == 'autorec':
        autoRec = tvhRecording[0]["params"][0]["value"]
        if len(autoRec) == 32:
          return autoRec
        else:
          log('The Tvheadend Autorec lookup has returned an Invalid UUID')
          raise RuntimeError(getString(32207))
      else:
        log('Unexpected parameters were returned for the Tvheadend Autorec lookup')
        raise RuntimeError(getString(32207))
    else:
      log('The Tvheadend lookup found ' + str(len(tvhRecording)) + ' upcoming recordings for the current event, but we expected 1')
      raise RuntimeError(getString(32207))

  def getTvhEpgEvent(channelNumber, channelName, epochStartDateTime, epochEndDateTime):
    tvhChannelEpg = tvhapi.getTvhEpgEvent(channelNumber, epochStartDateTime, epochEndDateTime)
    tvhEpgEvent = [x for x in tvhChannelEpg["entries"] if x["channelName"] == channelName] #Check the channel name matches
    if len(tvhEpgEvent) == 1: #Make sure that one and only one event was found
      thisEvent = tvhEpgEvent[0]
      if "dvrUuid" in thisEvent:
        thisEvent.setdefault("autorec", getTvhAutorecUuid(thisEvent["dvrUuid"]))
      else:
        thisEvent.setdefault("autorec", 0)
      return thisEvent
    else:
      log('The Tvheadend lookup found ' + str(len(tvhEpgEvent)) + ' events, but we expected 1')
      raise RuntimeError(getString(32202))

  def tvhEventHasSeriesLinkInfo(tvhEpgEvent):
    if "serieslinkId" in tvhEpgEvent and "serieslinkUri" in tvhEpgEvent:
      logNotice('Series Link information was found for this event')
      logNotice('Series Link URI: ' + str(tvhEpgEvent["serieslinkUri"]))
      return True
    else:
      logNotice('Series Link information was not availble for this event')
      return False

  def renameTvhTimer(tvhTimerUuid, tvhShowTitle, tvhTimerComment):
    log('UUID found in timer rule creation response from Tvheadend: ' + str(tvhTimerUuid))
    if len(tvhTimerUuid) == 32:
      log('Renaming the timer rule in the Tvheadend backend')
      tvhRenameNodeResponse = tvhapi.renameTvhIdNode(tvhTimerUuid, tvhShowTitle, tvhTimerComment) #A success yields a blank {} response
      if tvhRenameNodeResponse:
        log('Encountered an invalid response when attempting to rename the Tvheadend timer rule')
        raise RuntimeError(getString(32206))
    else:
      log('Encountered an invalid UUID when attempting to rename the Tvheadend timer rule')
      raise RuntimeError(getString(32206))

  def createTvhSeriesLink(tvhEpgEvent):
    logNotice('Creating series link via the Tvheadend API for: ' + tvhEpgEvent["title"])
    try:
      seriesLinkResponse = tvhapi.addTvhSeriesLink(tvhEpgEvent["eventId"])
      tvhTimerUuid = seriesLinkResponse["uuid"][0]
      tvhTimerComment = getString(32208) + ' URI: ' + tvhEpgEvent["serieslinkUri"]
      logNotice('Series link successfully scheduled via the Tvheadend API')
      renameTvhTimer(tvhTimerUuid, tvhEpgEvent["title"], tvhTimerComment)
    except:
      logError('Invalid series link response from Tvheadend')
      raise RuntimeError(getString(32204))

  def showKodiTimerRulePrompt():
    logNotice('Displaying the kodi built-in create timer rule window')
    xbmcExecuteBuiltin('Action(ShowTimerRule)')

  def createTvhAutoRec(tvhEpgEvent):
    logNotice('Creating timer rule via the Tvheadend API for: ' + tvhEpgEvent["title"])
    try:
      timerRuleResponse = tvhapi.addTvhAutoRecRule(tvhEpgEvent["title"], tvhEpgEvent["channelUuid"])
      tvhTimerUuid = timerRuleResponse["uuid"]
      tvhTimerComment = getString(32209)
      logNotice('Timer tule successfully scheduled via the Tvheadend API')
      renameTvhTimer(tvhTimerUuid, tvhEpgEvent["title"], tvhTimerComment)
    except:
      logError('Invalid timer rule creation response from Tvheadend')
      raise RuntimeError(getString(32205))

  def createTimer(tvhEpgEvent):
    if tvhEventHasSeriesLinkInfo(tvhEpgEvent):
      createTvhSeriesLink(tvhEpgEvent)
    else:
      if seriesLinkManualRecType == MANUAL_RECTYPE_KODI_PROMPT:
        showKodiTimerRulePrompt()
      elif seriesLinkManualRecType == MANUAL_RECTYPE_TVH_AUTOREC:
        createTvhAutoRec(tvhEpgEvent)
      else:
        raise RuntimeError(getString(32210))

  def deleteTimer(tvhEpgEvent):
    logNotice('Removing timer rule via the Tvheadend API for: ' + tvhEpgEvent["title"])
    autorecUuid = tvhEpgEvent["autorec"]
    log('Autorec UUID: ' + autorecUuid)
    if tvhapi.deleteTvhIdNode(autorecUuid): #A success yields a blank {} response
      logError('Encountered an invalid response when attempting to delete the Tvheadend timer rule')
      raise RuntimeError(getString(32203))

  def checkWindowId():
    log('WindowID: ' + str(getCurrentWindowId()) )
    if getCurrentWindowId() != 10702:
      raise RuntimeError(getString(32200))

  def checkEpgEventStatus():
    if getKodiCondVisibility('ListItem.IsRecording'):
      raise RuntimeError(getString(32201))

  def toggleSeriesLink():
    logNotice('Attempting to toggle series link for: ' + getKodiInfoLabel('ListItem.EPGEventTitle'))

    epochStartDateTime = getCurrentEventEpochStartDateTime()
    epochEndDateTime = getCurrentEventEpochEndDateTime()

    if epochEndDateTime > epochNow():
      tvhEpgEvent = getTvhEpgEvent(getKodiInfoLabel('ListItem.ChannelNumber'), \
                                   getKodiInfoLabel('ListItem.ChannelName'), \
                                   epochStartDateTime, \
                                   epochEndDateTime )
      if tvhEpgEvent["autorec"]: #If a timer rule has already been setup then remove it
        deleteTimer(tvhEpgEvent)
      else:
        createTimer(tvhEpgEvent)
    else:
      logNotice('Event is in the past')
      showKodiTimerRulePrompt()

  #End of function declarations

  checkWindowId()
  checkEpgEventStatus()
  toggleSeriesLink()
