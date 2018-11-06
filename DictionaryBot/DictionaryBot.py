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
import requests
import json
import sqlite3
from slackclient import SlackClient
from config import SLACK_BOT_TOKEN
from database import DictionaryBotDatabase
from urllib.parse import quote

# Instantiate Slack Client
slack_client = SlackClient(SLACK_BOT_TOKEN)
starterbot_id = None

# Database access
nameDB = None

# Constants
found = False
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

    # Finds and executes given command, filling in response
    command = command.lower()
    response = None
    global found
    attachments = None
    split = text.split(" ")[1:]
    msg = str(" ".join(text.lower().split(" ")[1:]))
    print(text)

    if msg == 'help':
        message(channel, "Send me a word, bish... orrrrrrrr  \n•  Create a new definition using ' *DEFINE* _{word/phrase}_ *AS* _{definition}_ '" + 
                "  \n•  Change a definition using ' *CHANGE* _{word/phrase}_ *TO* _{definition}_ '")
    elif split[0] == 'DEFINE' and 'AS' in split:
        define(channel, sender_id, " ".join(split[1:(split.index('AS'))]).lower(), " ".join(split[(split.index('AS')+1):]).lower())
    elif split[0] == 'CHANGE' and 'TO' in split:
        change(channel, sender_id, " ".join(split[1:(split.index('TO'))]).lower(), " ".join(split[(split.index('TO')+1):]).lower())
    else:
        # COMMAND HANDLING
        display(channel, msg)
        webster(channel, msg)
        oxford(channel, msg)
        if not found:
            message(channel, 'huh?')
            found = False

def define(channel, sender_id, phrase, definition):
    db = sqlite3.connect('/home/darren/SlackBots/DictionaryBot/DictionaryBot.db')
    sql = ''' INSERT OR IGNORE INTO definitions(phrase, definition, name) VALUES(?,?,?) '''
    cur = db.cursor()
    cur.execute(sql, (phrase, definition, sender_id))
    db.commit()
    db.close()
    message(channel, "The definition has been set")

def change(channel, sender_id, phrase, definition):
    db = sqlite3.connect('/home/darren/SlackBots/DictionaryBot/DictionaryBot.db')
    sql = ''' UPDATE definitions SET definition=? WHERE phrase=? AND name=?'''
    cur = db.cursor()
    cur.execute(sql, (definition, phrase, sender_id))
    db.commit()
    db.close()
    message(channel, "The definition has been changed")

def display(channel, text):
    global found
    db = sqlite3.connect('/home/darren/SlackBots/DictionaryBot/DictionaryBot.db')
    sql = ''' SELECT * FROM definitions WHERE phrase=? '''
    cur = db.cursor()
    cur.execute(sql, (text,))
    for row in cur:
        message(channel, "According to *" + nameDB.getName(row[2]) + "*, _" + row[0] + "_ is defined as:  \n•  " + row[1])
        found = True
    db.close()

def webster(channel, text):

    global found
    spelling = True
    try:
        msg = None
        app_key = '0143d4cb-e83b-4c32-88c5-fb7665e9bee7'
        word = urllib.parse.quote(text.encode('utf-8'))
        url = 'https://dictionaryapi.com/api/v3/references/collegiate/json/'  + word + '?key='  + app_key
        r = requests.get(url)
        msg = r.json()
        definitions = []
    except:
        return
    
    try:
        if msg is not None:
            for result in msg:
                for defs in result['shortdef']:
                    found = True
                    spelling = False
                    definitions.append(defs)

            length = len(definitions)
            if length > 5:
                length = 5
            if not spelling:
                message(channel, "According to the *Webster* dictionary, _" + text + "_ is defined as:  \n•  " + "  \n•  ".join(definitions[0:length]))        
                spelling = True
    except:
        return

def oxford(channel, text):

    global found
    try:
        msg = None
        app_id = '8749e6b9'
        app_key = '69a7a0ae687d283ad4e125382036b61d'
        language = 'en'
        word = urllib.parse.quote(text.encode('utf-8'))
        url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/'  + language + '/'  + word
        r = requests.get(url, headers = {'app_id' : app_id, 'app_key' : app_key})
        msg = r.json()
        definitions = []
    except:
        return

    try:
        if msg is not None:
            for results in msg['results']:
                for lexical in results['lexicalEntries']:
                    for entry in lexical['entries']:
                        for senses in entry['senses']:
                            for defs in senses['definitions']:
                                found = True
                                definitions.append(defs)

            length = len(definitions)
            if length > 5:
                length = 5
            message(channel, "  \n  \nAccording to the *Oxford* dictionary, _" + text + "_ is defined as:  \n•  " + "  \n•  ".join(definitions[0:length]))
    except:
        return

def message(channel, response):
    
    # Sends response back to channel.
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        as_user=True,
        text=response,
        attachments=None
    )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter bot connected and running!")

        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        
        try:
            nameDB = DictionaryBotDatabase()
        except Exception as e:
            print(e)

        while True:
            try:
                command, user_id, channel, text = parse_bot_commands(slack_client.rtm_read())
                if command:
                    handle_command(command, channel, user_id, text)
                time.sleep(RTM_READ_DELAY)
            except Exception as e:
                print(e)
                print("\nRESTARTING BOT LOGIC")
                if slack_client.rtm_connect(with_team_state=False):
                    starterbot_id = slack_client.api_call("auth.test")["user_id"]
                    continue
                else:
                    exit(5)
        else:
            print("Connection failed.")
