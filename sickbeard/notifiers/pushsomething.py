# Author: Chris Marshall <chrismar035@gmail.com>
# URL: http://code.google.com/p/sickbeard/
#
# This file is part of Sick Beard.
#
# Sick Beard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sick Beard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sick Beard.  If not, see <http://www.gnu.org/licenses/>.

import urllib, urllib2
import time
import json

import sickbeard

from sickbeard import logger
from sickbeard.common import notifyStrings, NOTIFY_SNATCH, NOTIFY_DOWNLOAD
from sickbeard.exceptions import ex

API_URL = "https://pushsomething.com/api/v1/notifications"

class PushSomethingNotifier:

    def _sendNotification(self, title, body, api_token=None):
        """
        Sends a notification to your PushSomething devices

        title - title string of the notification
        body - body of the notification
        """
        if not sickbeard.USE_PUSHSOMETHING:
          logger.log("PushSomething notifications are disabled; skipping", logger.DEBUG)
          return False

        logger.log("PushSomething: Sending notification for " + body, logger.DEBUG)
        return self._notify(title, body, api_token)

    def _notify(self, title, body, api_token):
        if not api_token:
            api_token = sickbeard.PUSHSOMETHING_SERVICE_TOKEN

        payload = self._assemble_payload(title, body, api_token)

        try:
            req = urllib2.Request(API_URL)
            req.add_header('Content-Type', 'application/json')
            handle = urllib2.urlopen(req, payload)
            handle.close

        except urllib2.URLError, e:
            # make sure we can get an error code
            if not hasattr(e, 'code'):
                logger.log("PushSomething notification failed" + ex(e), logger.ERROR)
                return False
            else:
                logger.log("PushSomething notification failed:" + str(e.code), logger.WARNING)

            if e.code == 401:
                logger.log("Not authorized to access PushSomething. Get your services' API tokens at http://pushsomething.com/services", logger.ERROR)
                return False

        logger.log("PushSomething notification sent", logger.DEBUG)
        return True

    def _assemble_payload(self, title, body, api_token):
        return json.dumps({
                'token': api_token,
                'notification': {
                    'title': title,
                    'body': body
                }
            })

##############################################################################
# Public functions
##############################################################################

    def notify_snatch(self, ep_name, title=notifyStrings[NOTIFY_SNATCH]):
        if sickbeard.PUSHSOMETHING_NOTIFY_ONSNATCH:
            self._sendNotification(title, ep_name)

    def notify_download(self, ep_name, title=notifyStrings[NOTIFY_DOWNLOAD]):
        if sickbeard.PUSHSOMETHING_NOTIFY_ONDOWNLOAD:
          self._sendNotification(title, ep_name)

    def test_notify(self, api_token=None):
        return self._notify("Testing from Sickbeard!", "This is a test notification from SickBeard. Everything looks good!", api_token)

    def update_library(self, ep_obj=None):
        pass

notifier = PushSomethingNotifier
