# Bitcoin Price Logger
# Author: Zach Gillis

import requests
import mysql.connector
import time
import datetime

def getBTCPrice():
    # API URL for Bitcoin price
    URL = "https://api.coindesk.com/v1/bpi/currentprice/BTC.json"
    price = None

    try:
        print("Requesting BTC/USD price...")
        r = requests.get(URL)
        data = r.json()

        price = data['bpi']['USD']['rate']
        price = float(price.replace(',', ''))

    except:
        print("Failed to retrieve BTC price.")

    return price


def getKohlsPrice():
    # API URL for Kohls Stock Price
    URL = "https://api.iextrading.com/1.0/tops/?symbols=KSS"
    price = None

    try:
        print("Getting Kohl's stock price...")
        r = requests.get(URL)
        data = r.json()

        price = data[0]['lastSalePrice']
        price = float(price)
    except:
        print("Failed to retrieve stock price.")

    return price


def getStockPrice(ticker):
    # API URL for Kohls Stock Price
    URL = "https://api.iextrading.com/1.0/tops/?symbols=%s" % ticker
    price = None

    try:
        print("Getting stock price for %s..." % ticker)
        r = requests.get(URL)
        data = r.json()
        if len(data) > 0:
            price = data[0]['lastSalePrice']
            price = float(price)
    except:
        print("Failed to retrieve stock price.")

    return price


def getRandomDog():
    # API URL for random dog image
    URL = "https://dog.ceo/api/breeds/image/random"
    image = None

    try:
        print("Getting random dog image...")
        r = requests.get(URL)
        data = r.json()
        image = data['message']
    except:
        print("Failed to retrieve random dog image.")

    return image


def getTrumpQuote():
    # API URL for random Trump quote
    URL = "https://api.whatdoestrumpthink.com/api/v1/quotes/random"
    quote = None

    try:
        print("Getting Trump quote...")
        r = requests.get(URL)
        data = r.json()
        quote = data['message']
    except:
        pass

    return quote


