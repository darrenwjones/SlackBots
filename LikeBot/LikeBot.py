# LikeBot
# SLACK CHATBOT IN PYTHON
#
# Author: Zachary Gillis & Darren Jones
#--------------------------------------

import os
import time
import re
import logging
import random
from slackclient import SlackClient
from database import LikeBotDatabase
from config import SLACK_BOT_TOKEN
import api_calls

# Instantiate Slack Client
slack_client = SlackClient(SLACK_BOT_TOKEN)
starterbot_id = None

# Database access
db = None

# Constants
RTM_READ_DELAY = 1 # 1-second delay RTM read
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
HELP_TEXT = """
Basic Commands:
        *help* - find a list of commands
        *hello* - say hi to me
        *about* - learn about this bot
User Commands:
        *register* _*[first_name]*_ _*[last_name]*_ - register your name and establish like count
        *me* - see if you are registered, your name and your like count
        *likes* - see your current like count
        *id* - see your Slack user id
Feature Commands:
        *coinflip/flip* _*[heads/tails]*_ - flip a coin
        *scoreboard* - see the like count of all users
API Commands:
        *bitcoin/btc* - get the current Bitcoin price in USD
        *stock* _*[ticker]*_ - get the current stock price for a given ticker in USD
        *kss* - get the current stock price of Kohl's (KSS)
        *dog* - random dog picture
        *trump* - random quote from Donald Trump
  
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

    logging.info("type=command userid=%s command=%s text=%s" % (sender_id, command.lower(), text))
    # Finds and executes given command, filling in response
    command = command.lower()
    response = None
    attachments = None

    print(text)

    commands = command.split(" ")
    main_commands = {'like':1,'dislike':-1,'love':2,'hate': -2}

    if command[0] in main_commands:
        if db.getName(sender_id) == commands[1:]:
            message(channel, "you cannot " + command[0] + " yourself, silly willy")
        else:
            db.addLikes(getThing(commands[1:]), main_commands[command[0]])
            message(channel, db.getName(sender_id) + " " + commands[0] + "d " + commands[1:] + " and added " + main_commands[command[0]]
                    + " likes. " + commands[1:] + " now has " + db.getLikes(getThing(commands[1:]).thing_id) + " likes!")
    elif command == 'scoreboard' or command == 'anti-scoreboard':
        display = 'DESC' if command == 'scoreboard' else 'ASC'
        thing_list = db.scoreboard(display);
        i = 0
        scoreboard = []
        for thing in thing_list:
            scoreboard[i] = thing.name + ": " + thing.like_bal
            i=i+1
        message(channel, scoreboard.join("  \n")

    # COMMAND HANDLING
    if command.startswith("hi") or command.startswith("hello"):
        response = "Hi there %s. u r weird." % ("<@" + sender_id + ">")


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

        db = LikeBotDatabase()

        while True:
            command, user_id, channel, text = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel, user_id, text)
            time.sleep(RTM_READ_DELAY)

    else:
        print("Connection failed.")
