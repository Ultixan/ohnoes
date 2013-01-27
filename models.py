from google.appengine.ext import db

class Game(db.Model):
    game_id = db.StringProperty()
    tiles = db.StringProperty(indexed=False)
    monsters = db.StringProperty(indexed=False)
    active_monsters = db.StringProperty(indexed=False)
    powerups = db.StringProperty(indexed=False)
    drop_chance = db.FloatProperty(indexed=False)
    player = db.StringProperty(indexed=False)
    turn_count = db.IntegerProperty(indexed=False)
    is_dead = db.IntegerProperty(indexed=False)
    candy_eaten = db.IntegerProperty(indexed=False)

class Account(db.Model):
    user = db.UserProperty()
    game_id = db.StringProperty()
