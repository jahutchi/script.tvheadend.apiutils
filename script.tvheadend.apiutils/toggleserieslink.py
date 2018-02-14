# -*- coding: utf-8 -*-

"""
toggleserieslink.py
~~~~~~~~~~~~~~~~~~~

This module is used to toggle a series link timer from within the TV guide

By James Hutchinson 2017
"""

def main():

  from common import log, logNotice, logError, epochFromUTCTimestamp, epochFromLocalTimestamp, epochNow, getString
  from common import getKodiInfoLabel, getKodiCondVisibility, getCurrentWindowId, xbmcExecuteBuiltin
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
      log('The Tvheadend lookup found ' + len(tvhRecording) + ' upcoming recordings for the current event, but we expected 1')
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
      log('The Tvheadend lookup found ' + len(tvhEpgEvent) + ' events, but we expected 1')
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

  def createTvhTimer(tvhEpgEvent):
    tvhShowTitle = tvhEpgEvent["title"]
    tvhEventId = tvhEpgEvent["eventId"]
    tvhChannelUuid = tvhEpgEvent["channelUuid"]
    if tvhEventHasSeriesLinkInfo(tvhEpgEvent):
      logNotice('Creating series link via the Tvheadend API for: ' + tvhShowTitle)
      try:
        seriesLinkResponse = tvhapi.addTvhSeriesLink(tvhEventId)
        tvhTimerUuid = seriesLinkResponse["uuid"][0]
        tvhTimerComment = getString(32308) + ' URI: ' + tvhEpgEvent["serieslinkUri"]
        logNotice('Series link successfully scheduled via the Tvheadend API')
      except:
        logError('Invalid series link response from Tvheadend')
        raise RuntimeError(getString(32204))
    else:
      logNotice('Creating timer rule via the Tvheadend API for: ' + tvhShowTitle)
      try:
        timerRuleResponse = tvhapi.addTvhAutoRecRule(tvhShowTitle, tvhChannelUuid)
        tvhTimerUuid = timerRuleResponse["uuid"]
        tvhTimerComment = getString(32309)
        logNotice('Timer tule successfully scheduled via the Tvheadend API')
      except:
        logError('Invalid timer rule creation response from Tvheadend')
        raise RuntimeError(getString(32205))
    renameTvhTimer(tvhTimerUuid, tvhShowTitle, tvhTimerComment)

  def deleteTvhTimer(tvhEpgEvent):
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
        deleteTvhTimer(tvhEpgEvent)
      else:
        createTvhTimer(tvhEpgEvent)
    else:
      logNotice('Event is in the past so prompting the user')
      xbmcExecuteBuiltin('Action(ShowTimerRule)')

  #End of function declarations

  checkWindowId()
  checkEpgEventStatus()
  toggleSeriesLink()

