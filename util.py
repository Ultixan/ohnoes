import json
import os

from constants import template_dir
from constants import max_beats
from google.appengine.ext import db
from models import Account
from models import Game
from random import randint

def template_path(template):
    path = os.path.join(
        os.path.dirname(__file__) + template_dir, 
        template
    )
    return path

def get_account(user):
    existing = db.GqlQuery('SELECT * from Account ' +
        'WHERE user = :1',
        user)
    if existing.count() == 0:
        account = Account()
        account.user = user
        import uuid
        account.game_id=uuid.uuid4().hex
        account.put()
        return account
    else:
        return existing[0]

def get_game(game_id):
    game = db.GqlQuery('SELECT * from Game ' +
        'WHERE game_id = :1',
        game_id)
    if game.count() < 1:
        game = Game()
        import uuid
        grid = []
        for i in range(0, 10):
            row = []
            for j in range(0, 10):
                row.append(randint(0,3))
            grid.append(row)
        game.tiles = json.dumps(grid)
        player = {
            'heartrate': 50,
            'heartbeats': max_beats,
            'x': 5,
            'y': 5,
            'objects': []
        }
        monsters = []
        powerups = []
        game.player = json.dumps(player)
        game.monsters = json.dumps(monsters)
        game.powerups = json.dumps(powerups)
        game.game_id = game_id
        game.put()
    else:
        game = game[0]
    return game
