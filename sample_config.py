import os
import time

class Config(object):

    # Get a bot token from botfather
    TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")


    # Get from my.telegram.org (or @UseTGXBot)
    API_ID = int(os.environ.get("API_ID", 12345))


    # Get from my.telegram.org (or @UseTGXBot)
    API_HASH = os.environ.get("API_HASH", "9415a61fedcc0f00f33667ca46e577a3")
    
    
    # Database URL from https://cloud.mongodb.com/
    DATABASE_URI = os.environ.get("DATABASE_URI", "")


    # Your database name from mongoDB
    DATABASE_NAME = str(os.environ.get("DATABASE_NAME", "Cluster0"))


    # ID of users that can use the bot commands
    AUTH_USERS = set(str(x) for x in os.environ.get("AUTH_USERS", "").split())


    # To save user details (Usefull for getting userinfo and total user counts)
    # May reduce filter capacity :(
    # Give yes or no
    SAVE_USER = os.environ.get("SAVE_USER", "no").lower()


    # Go to https://dashboard.heroku.com/account, scroll down and press Reveal API
    # To check dyno status
    HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY", "")


    # To record start time of bot
    BOT_START_TIME = time.time()
