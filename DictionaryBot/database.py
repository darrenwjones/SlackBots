# LikeBot
# Author: Zachary Gillis
#
# DATABASE ACCESS LAYER

import mysql.connector
from config import db_config


class DictionaryBotDatabase:
    con = None

    def db_connect(self):
        self.con = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            passwd=db_config['password'],
            database=db_config['database']
        )

    def __init__(self):
        print("Connecting to database..")
        self.con = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            passwd=db_config['password'],
            database=db_config['database']
        )
        print("Connected to database.")
        self.con.close()

    def getName(self, uid):
        self.db_connect()
        thing = None
        cursor = self.con.cursor()
        sql = "SELECT * FROM things WHERE UID = %s"
        cursor.execute(sql, (uid,))
        rs_thing = cursor.fetchone()
        if rs_thing is not None:
            thing = Thing(rs_thing[0], rs_thing[1], rs_thing[2], rs_thing[3], rs_thing[4], rs_thing[5], rs_thing[6])
        cursor.close()
        self.con.close()
        if thing is None:
            print("pls register first, my guy")
            return None
        return thing.name
    
class Thing:
    thing_id = None
    UID = None
    name = None
    pwr_lvl = None
    like_bal = None
    wager_uid = None
    wager_likes = None

    def __init__(self, thing_id, uid, name, pwr_lvl, like_bal, wager_uid, wager_likes):
        self.thing_id = thing_id
        self.UID = uid
        self.name = name
        self.pwr_lvl = pwr_lvl
        self.like_bal = like_bal
        self.wager_uid = wager_uid
        self.wager_likes = wager_likes
