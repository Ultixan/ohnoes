from google.appengine.ext import db

class Game(db.Model):
    game_id = db.StringProperty()
    tiles = db.StringProperty(indexed=False)

class Account(db.Model):
    user = db.UserProperty()
    game_id = db.StringProperty()
