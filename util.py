import json
import os

from constants import template_dir
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
        game = [Game()]
        import uuid
        grid = []
        for i in range(0, 10):
            row = []
            for j in range(0, 10):
                row.append(randint(0,3))
            grid.append(row)
        game[0].tiles = json.dumps(grid)
        #player
        player = {}
        player['heartrate']=60
        player['heartbeats']=1000
        player['x']=5
        player['y']=5
        player['abilities']={
        'rotate_right':0,
        'rotate_left':0,
        'shift_tiles':0,
        'swap_tiles':0
        }
        game[0].player = json.dumps(player)
        game[0].game_id = game_id
        game[0].put()
    return game[0]
