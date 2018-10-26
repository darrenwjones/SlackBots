# THE MOST INTERESTING MAN IN THE WORLD
# SLACK CHATBOT IN PYTHON
#
# Author: Zachary Gillis
#--------------------------------------

import os
import time
import re
import logging
import random
from slackclient import SlackClient
from database import TMIMDatabase
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
    default_response = """I don't always understand people, but when I do, they don't speak gibberish like you. 
Shotgun a Dos Equis or five and get back to me. Try *{}* to see what I can do.""".format("help")

    logging.info("type=command userid=%s command=%s text=%s" % (sender_id, command.lower(), text))
    # Finds and executes given command, filling in response
    command = command.lower()
    response = None
    attachments = None

    print(text)

    # COMMAND HANDLING
    if command.startswith("hi") or command.startswith("hello"):
        response = "Hi there %s. Stay thirsty my friend." % ("<@" + sender_id + ">")
    elif command.startswith("help"):
        response = HELP_TEXT
    elif command.startswith("about"):
        response = "I'm a Slack chatbot written in Python. I don't always crash, but when I do, call Zach."
    elif command.startswith("bitcoin") or command.startswith("btc"):
        try:
            btc_price = api_calls.getBTCPrice()
            response = "The current price of Bitcoin is $%.2f USD." % btc_price
        except:
            response = "There was a problem retrieving the Bitcoin price."
    elif command.startswith('id'):
        response = "Your user ID is: %s." % sender_id
    elif command.startswith("me"):
        user = db.get_user(sender_id)
        if user is None:
            response = "I don't have you registered yet. Please register with *register [first_name] [last_name]*."
        else:
            response = "Hi, you're %s %s. You have %s likes. Stay thirsty my friend." % (user.first_name, user.last_name, user.like_bal)
    elif command.startswith("register"):
        strings = text.split(" ")
        valid = False
        if len(strings) == 4:
            first_name = strings[2].capitalize()
            last_name = strings[3].capitalize()
            if first_name.isalpha() and last_name.isalpha():
                valid = True

        if valid:
            user = db.get_user(sender_id)
            if user:
                response = "You are already registered!"
            else:
                db.create_user(sender_id, first_name, last_name)
                response = "You have been registered successfully."
        else:
            response = "Just because I climb mountains in my sleep doesn't mean I can register you without your name.\n"
            response += "Proper usage: *register* _*[first_name]*_ _*[last_name]*_"
    elif command.startswith("likes"):
        user = db.get_user(sender_id)
        if user is None:
            response = "You must register to have a like count.\nTry *register* _*[first_name]*_ _*[last_name]*_"
        else:
            response = "Your like count is *%s*." % user.like_bal
    elif command.startswith("scoreboard"):
        response = "Current scoreboard:\n"
        users = db.get_users()
        for user in users:
            response += "\t%s %s:\t%s\n" % (user.first_name, user.last_name, user.like_bal)
    elif command.startswith("kss"):
        try:
            kss_price = api_calls.getKohlsPrice()
            response = "Kohl's Corporation (NYSE:KSS) current stock price: *$%.2f*" % kss_price
        except:
            response = "There was a problem retrieving the stock price."
    elif command.startswith("stock"):
        try:
            strings = text.split(" ")
            ticker = None
            valid = False
            if len(strings) == 3:
                ticker = strings[2]
                if ticker.isalpha():
                    valid = True
                    ticker = ticker.upper()
            if valid:
                stock_price = api_calls.getStockPrice(ticker)
                if stock_price == None:
                    response = "I was unable to retrieve the stock price for that ticker."
                else:
                    response = "Stock price for %s is $%.2f." % (ticker, stock_price)
            else:
                response = "Just because I climb mountains in my sleep doesn't mean I know what stock you want.\n"
                response += "Proper usage: *stock* _*[ticker]*_"
        except:
            response = "There was a problem retrieving the stock price."
    elif command.startswith("coinflip") or command.startswith("flip"):
        strings = text.split(" ")
        declare = None
        declare_txt = None
        flip = random.randint(0, 1)
        if len(strings) == 3:
            guess = strings[2].lower()
            if guess == "heads" or guess == "head" or guess == "h":
                declare = 0
                declare_txt = "HEADS"
            elif guess == "tails" or guess == "tail" or guess == "t":
                declare = 1
                declare_txt = "TAILS"
        if declare is not None:
            if flip == 0:
                response = "_It's *HEADS*_. You guessed _*%s*_.\n" % declare_txt
            else:
                response = "_It's *TAILS*_. You guessed _*%s*_.\n" % declare_txt
            if declare == flip:
                response += "You guessed correctly!"
            else:
                response += "You guessed incorrectly.."
        else:
            response = "You must guess _*HEADS*_ or _*TAILS*_."
    elif command.startswith("dog"):
        image_url = api_calls.getRandomDog()
        if image_url is not None:
            response = "Here's a random dog."
            attachments = [{"title": "Random Dog", "image_url": image_url}]
        else:
            response = "For some reason I was unable to find a random dog picture :("
    elif command.startswith("trump"):
        quote = api_calls.getTrumpQuote()
        if quote is not None:
            attachments = [{
                "pretext": "Here's a random quote from Donald Trump.",
                "author_name": "Donald J Trump",
                "text": quote,
                "footer": "The Most Interesting Man in The World Bot",
                "footer_icon": "https://i.pinimg.com/originals/7c/c7/a6/7cc7a630624d20f7797cb4c8e93c09c1.png"
            }]
            response = " "
        else:
            response = "Unable to get a Donald Trump quote."

    # Sends response back to channel.
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        as_user=True,
        text=response or default_response,
        attachments=attachments
    )


if __name__ == "__main__":
    logging.basicConfig(filename="botlog.log", level=logging.INFO, format='%(asctime)s %(message)s')
    logging.info("Logging started")
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter bot connected and running!")

        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]

        db = TMIMDatabase()

        while True:
            command, user_id, channel, text = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel, user_id, text)
            time.sleep(RTM_READ_DELAY)

    else:
        print("Connection failed.")



