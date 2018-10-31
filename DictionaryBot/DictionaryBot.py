# THE MOST INTERESTING MAN IN THE WORLD
# SLACK CHATBOT IN PYTHON
#
# Author: Zachary Gillis
#--------------------------------------

import os
import time
import re
import random
import urllib
from slackclient import SlackClient
from config import SLACK_BOT_TOKEN

# Instantiate Slack Client
slack_client = SlackClient(SLACK_BOT_TOKEN)
starterbot_id = None

# Database access
db = None

# Constants
RTM_READ_DELAY = 1 # 1-second delay RTM read
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
HELP_TEXT = """

  
"""


def parse_bot_commands(slack_events):
    for event in slack_events:
        if event['type'] == "message" and not "subtype" in event:
            user_id, message, text = parse_direct_mention(event['text'])
            if user_id == starterbot_id:
                sender_id = event['user']
                return message, sender_id, event['channel'], text
    return None, None, None, None


def parse_direct_mention(message_text):
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip(), message_text) if matches else (None, None, None)


def handle_command(command, channel, sender_id, text):

    # Finds and executes given command, filling in response
    command = command.lower()
    response = None
    attachments = None

    print(text)

    # COMMAND HANDLING
    webster(channel, text.lower())
    oxford(channel, text.lower())

def database(channel, sender_id, text):

def webster(channel, text):
    app_key = '0143d4cb-e83b-4c32-88c5-fb7665e9bee7'
    word = urllib.quote(text.encode('utf-8'))
    url = 'https://dictionaryapi.com/api/v3/references/collegiate/json/'  + word + '?key='  + app_key
    r = requests.get(url)
    print("json \n" + json.dumps(r.json()))

def oxford(channel, text):
    app_id = '8749e6b9'
    app_key = '69a7a0ae687d283ad4e125382036b61d'
    language = 'en'
    word = urllib.quote(text.encode('utf-8'))
    url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/'  + language + '/'  + word
    r = requests.get(url, headers = {'app_id' : app_id, 'app_key' : app_key})
    print("json \n" + json.dumps(r.json()))    
    
def message(channel, response):
    
    # Sends response back to channel.
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        as_user=True,
        text=response or "no u",
        attachments=None
    )


if __name__ == "__main__":
    logging.basicConfig(filename="botlog.log", level=logging.INFO, format='%(asctime)s %(message)s')
    logging.info("Logging started")
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter bot connected and running!")

        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]

        #db = TMIMDatabase()

        while True:
            command, user_id, channel, text = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel, user_id, text)
            time.sleep(RTM_READ_DELAY)

    else:
        print("Connection failed.")



