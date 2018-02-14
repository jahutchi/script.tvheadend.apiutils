# script.tvheadend.apiutils

A kodi addon to expose extra functionality from the Tvheadend backend, which isn't currently used by the pvr.hts addon.

Currently supports deleting all watched recordings, and scheduling series links.

After installing the addon, you must configure the Tvheadend server details in the addon settings.

You can then map the following actions to your kodi remote buttons (keyboard.xml / remote.xml), or include these in your skin:

* `RunScript(script.tvheadend.apiutils,delete-watched-recordings)`
   => This will only work from the TVRecordings window (WindowID: 10701) so must be placed in your <TVRecordings> section of the keymap.

* `RunScript(script.tvheadend.apiutils,toggle-series-link)`
   => This will only work from the TVGuide window (WindowID: 10702) so must be placed in your <TVGuide> section of the keymap.


## Installation

Launch Kodi >> Add-ons >> Get More >> .. >> Install from zip file

Enjoy!
