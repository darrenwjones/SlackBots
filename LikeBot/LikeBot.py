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
import requests
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
    commands = msg.split(" ")
    main_commands = {'like':1,'dislike':-1,'love':2,'hate': -2}
    response = None
    attachments = None

    print(text)

    if commands[0] in main_commands:
        like(channel, sender_id, commands, msg, main_commands)
    elif msg == 'scoreboard' or msg == 'anti-scoreboard':
        scoreboard(channel, msg)
    elif commands[0] == 'score':
        score(channel, sender_id, commands)
    elif commands[0] == 'fight':
        fight(channel, sender_id, commands)    
    elif commands[0] == 'wager':
        wager(channel, sender_id, commands)
    elif msg == 'help':
        helper(channel)
    else:
        message(channel, requests.get("https://api.chew.pro/trbmb"))
    
def like(channel, sender_id, commands, msg, main_commands):

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
            db.createThing(name)
            thing = db.getThing(name)
            if thing:
                db.addLikes(thing.thing_id, main_commands[commands[0]])
                likes = str(thing.like_bal + main_commands[commands[0]])
                message(channel, db.getName(sender_id) + " " + commands[0] + "d '" + name + "' and added " + str(main_commands[commands[0]])
                        + " like(s). '" + name + "' now has " + likes + " like(s)!")
    
def scoreboard(channel, msg):

    display = 'DESC' if msg == 'scoreboard' else 'ASC'
    thing_list = db.scoreboard(display)
    scoreboard = []
    for thing in thing_list:
        scoreboard.append(thing.name + ": " + str(thing.like_bal))
    message(channel, "  \n".join(scoreboard))

def score(channel, sender_id, commands):
    
    name = " ".join(commands[1:])
    thing = db.getThing(name)
    if thing:
        if thing.name == db.getName(sender_id):
            message(channel, "u haz " + str(thing.like_bal) + " likes")
        else:
            message(channel, "they haz " + str(thing.like_bal) + " likes")
    else:
        message(channel, "idk who that is")

def fight(channel, sender_id, commands):            
    
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

def wager(channel, sender_id, commands):            
    
    message(channel, "feature coming soon!")

def helper(channel):

    message(channel, "You want to know how to use me, eh?  \n  \n" +
            "* '[Like, Dislike, Love, Hate] {thing}': This command add or subtracts likes from the designated {thing}.  \n" +
            "* 'Fight {person}': This command initiates a fight between you and the {person}. The winner gains two likes while the loser loses two.  \n" +
            "* 'Wager {person} {amount}': This command is for betting your likes on fights. You will gain/lose likes based on the {amount} chosen and the {person} who wins.  \n" +
            "* 'Score {thing}': This command displays the current like count of the designated {thing}.  \n" +
            "* '[Scoreboard, Anti-scoreboard]': This command displays the top 10 and bottom 10 things respectively in terms of likes.  \n")

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
