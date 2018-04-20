# script.tvheadend.apiutils

A kodi addon to expose extra functionality from the Tvheadend backend, which isn't currently used by the pvr.hts addon.

Currently supports deleting all watched recordings, scheduling series links, and triggering an OTA EPG refresh.

After installing the addon, you must configure the Tvheadend server details in the addon settings.

You can then map the following actions to your kodi remote buttons (keyboard.xml / remote.xml), or include these in your skin:

* `RunScript(script.tvheadend.apiutils,delete-watched-recordings)`
   => This will only work from the TVRecordings window (WindowID: 10701) so must be placed in your <TVRecordings> section of the keymap.

* `RunScript(script.tvheadend.apiutils,toggle-series-link)`
   => This will only work from the TVGuide window (WindowID: 10702) so must be placed in your <TVGuide> section of the keymap.

* `RunScript(script.tvheadend.apiutils,refresh-epg)`
   => This will trigger an OTA EPG refresh in the Tvheadend backend. Note: this currently only supports the OTA grabbers.


## Installation

Launch Kodi >> Add-ons >> Get More >> .. >> Install from zip file

Enjoy!
