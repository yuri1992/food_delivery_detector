import logging
import os
import time
from slackclient import SlackClient
from settings import settings

log = logging.getLogger(__name__)

class SlackClientThrottled(SlackClient):
    def api_call(self, *args, **kwargs):
        response = super(SlackClientThrottled, self).api_call(*args, **kwargs)

        if response["ok"]:
            return response
        elif response["ok"] is False and response["headers"]["Retry-After"]:
            # The `Retry-After` header will tell you how long to wait before retrying
            delay = int(response["headers"]["Retry-After"])
            log.info("Rate limited. Retrying in " + str(delay) + " seconds")
            time.sleep(delay)
            return super(SlackClientThrottled, self).api_call(*args, **kwargs)


class SlackManager(object):
    def __init__(self):
        self.client = SlackClientThrottled(os.getenv('CRM_SERVICE_SLACK_API_TOKEN'))


    def send_message(self, channel, *args, **kwargs):
        self.client.api_call("chat.postMessage", channel=channel, *args, **kwargs)


Slack = SlackManager()