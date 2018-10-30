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
    msg = str(" ".join(text.lower().split(" ")[1:]))
    response = None
    attachments = None

    print(text)

    commands = msg.split(" ")
    main_commands = {'like':1,'dislike':-1,'love':2,'hate': -2}

    if commands[0] in main_commands:
        name = " ".join(commands[1:])
        if db.getName(sender_id) == name:
            message(channel, "you cannot " + commands[0] + " yourself, silly willy")
        else:
            name = " ".join(commands[1:]).lower()
            thing = db.getThing(name)
            if thing:
                db.addLikes(thing.thing_id, main_commands[commands[0]])
                likes = str(thing.like_bal + main_commands[commands[0]])
                message(channel, db.getName(sender_id) + " " + commands[0] + "d '" + name + "' and added " + str(main_commands[commands[0]])
                        + " like(s). '" + name + "' now has " + likes + " like(s)!")
            else:
                db.createThing(name);
                thing = db.getThing(name)
                if thing:
                    db.addLikes(thing.thing_id, main_commands[commands[0]])
                    likes = str(thing.like_bal + main_commands[commands[0]])
                    message(channel, db.getName(sender_id) + " " + commands[0] + "d '" + name + "' and added " + str(main_commands[commands[0]])
                            + " like(s). '" + name + "' now has " + likes + " like(s)!")
    elif msg == 'scoreboard' or msg == 'anti-scoreboard':
        display = 'DESC' if msg == 'scoreboard' else 'ASC'
        thing_list = db.scoreboard(display);
        scoreboard = []
        for thing in thing_list:
            scoreboard.append(thing.name + ": " + str(thing.like_bal))
        message(channel, "  \n".join(scoreboard))
    elif commands[0] == 'score':
        name = " ".join(commands[1:])
        thing = db.getThing(name)
        if thing:
            message(channel, "they haz " + str(thing.like_bal) + " likes")
        else:
            message(channel, "idk who that is")
    elif commands[0] == 'fight':
        fighter = db.getThing(db.getName(sender_id))
        fightee = db.getThing(" ".join(commands[1:]))

        if fighter and fightee:
            if db.getName(sender_id) == fightee.name:
                message(channel, "you cannot fight yourself, silly willy")
                return

            if random.random() >= .5:
                db.addLikes(fighter.thing_id, 2)
                db.addLikes(fightee.thing_id, -2)
                message(channel, fighter.name + " has won the fight and has stole 2 likes from " + fightee.name)
            else:
                db.addLikes(fighter.thing_id, -2)
                db.addLikes(fightee.thing_id, 2)
                message(channel, fightee.name + " has won the fight and has stole 2 likes from " + fighter.name)
        else:
            message(channel, "idk who u is trying to fight")
    elif commands[0] == 'wager':
        message(channel, "feature coming soon!")
    else:
        message(channel, response)

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
