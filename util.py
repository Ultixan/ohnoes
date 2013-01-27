import json
import os

from constants import template_dir
from constants import max_beats
from constants import elements
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
            'abilities':[ 0, 0, 0, 0 ]
        }
        monsters = {}
        for monster in elements.keys():
            monsters[monster] = {
                'x': -1,
                'y': -1
            }
        powerups = []
        active_monsters = []
        game.player = json.dumps(player)
        game.monsters = json.dumps(monsters)
        game.active_monsters = json.dumps(active_monsters)
        game.powerups = json.dumps(powerups)
        game.game_id = game_id
        game.turn_count = 0
        game.is_dead = 0
        game.put()
    else:
        game = game[0]
    return game

def calc_move(move_code, coords):  
    if move_code == 0:
        coords['y'] = (coords['y']-1)%10
    elif move_code == 1:
        coords['x'] = (coords['x']+1)%10
    elif move_code == 2:
        coords['y'] = (coords['y']+1)%10
    elif move_code == 3:
        coords['x'] = (coords['x']-1)%10

    return coords;
    
def gen_rand_coords():
    # gen random coords
    x = randint(0, 9)
    y = randint(0, 9)
    return {'x': x, 'y': y}

