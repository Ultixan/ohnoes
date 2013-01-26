import cgi
import json
import logging

from constants import directions
from constants import column_range
from constants import max_beats
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from util import template_path
from util import get_game
from util import get_account
from random import randint

def authorize(scope):
    user = users.get_current_user() 
    return user

class display_game(webapp.RequestHandler):
    path = template_path('game.html')

    def get(self):
        user = authorize(self)
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return
        account = get_account(user)
        game = get_game(account.game_id)
        tiles = []
        for row in json.loads(game.tiles):
            newRow = []
            for cell in row:
                newRow.append(directions[cell])
            tiles.append(newRow)
        self.response.out.write(
            template.render(self.path, {
                'tiles': tiles,
                'columns': column_range,
                'player': json.loads(game.player),
                'max_beats': max_beats
            })
        )

def move_pos(move_code, coords):  
    if move_code == 0:
        coords['y'] = (coords['y']-1)%10
    elif move_code == 1:
        coords['x'] = (coords['x']+1)%10
    elif move_code == 2:
        coords['y'] = (coords['y']+1)%10
    elif move_code == 3:
        coords['x'] = (coords['x']-1)%10
    return coords;
    
def rotate(world, mosters, player, params, tick):
    x = params['x']
    y = params['y']
    direction = (world[y][x] + tick) % 4
    
    return {
        'world': [{
            'x': x,
            'y': y,
            'direction': direction
        }]
        }
def rotate_left(world, monsters, player, params):
    return rotate(world, monsters, player, params, -1)
def rotate_right(world, monsters, player, params):
    return rotate(world, monsters, player, params, 1)

def move_player(world, player):
    # check direction of tile
    move_code = world[player['y']][player['x']]
    # move player
    new_pos = move_pos(move_code, {'x':player['x'], 'y':player['y']})
    player['x'] = new_pos['x']
    player['y'] = new_pos['y']
    
    return player   
    
def move_monsters(world, monsters, player, m_grid):
    prox_count = {'near':0, 'superclose':0, 'gruesome_death' : 0}
    
    for m in monsters:
        # check direction of tile
        move_code = world[m['y']][m['x']]
        # move monster
        new_pos = move_pos(move_code, {'x':m['x'], 'y':m['y']})
        # check if it can move there
        if m_grid[new_pos['y']][new_pos['x']] == None:
            # moving allowed! (i.e. nothing in the way)
            m_grid[m['y']][m['x']] = None   # off of old spot
            m_grid[new_pos['y']][new_pos['x']] = m  # onto new spot
            # save new position
            m['x'] = new_pos['x']
            m['y'] = new_pos['y']
        # if moving blocked, nothing happens
        
        # calculate proximity
        if abs(m['x']-player['x'])<=2 and abs(m['y']-player['y'])<=2:
            if m['x'] == player['x'] and m['y'] == player['y']:
                # on the same square
                prox_count['gruesome_death'] += 1
            elif abs(m['x']-player['x'])<=1 and abs(m['y']-player['y'])<=1:
                # superclose
                prox_count['superclose'] += 1
            else:
                # nearby
                prox_count['near'] += 1

    return {'prox_count' : prox_count, 'monsters' : monsters, 'm_grid':m_grid}

def calc_damage(player, prox_count):
    new_rate = player['heartrate'] + prox_count['near']*2 + prox_count['superclose']*5
    if prox_count['near'] == 0 and prox_count['superclose'] == 0:
        new_rate -= 10
        player['heartrate'] = new_rate if new_rate > 50 else 50
    player['heartbeats'] -= player['heartrate']
    return player

def shift_tiles(world, monsters, player, params):
    #Get the direction. If it's left or right, x++ for all x in world[params[y]]
    #If it's top or bottom, y++ for all y in world[params[x]]
    direction=params['direction']
    changes=[]

    if direction == "left":
        for i in range(10):
            changes.append({'change_type':'world','change':{'x':i,'y':params['y'],'direction':world[params['y']][params[(i-1)%10]]}})
    elif direction == "right":
        for i in range(10):
            changes.append({'change_type':'world','change':{'x':i,'y':params['y'],'direction':world[params['y']][params[(i+1)%10]]}})
    elif direction == "up":
        for i in range(10):
            changes.append({'change_type':'world','change':{'x':params['x'],'y':i,'direction':world[params[(i-1)%10]][params['x']]}})
    elif direction == "down": 
        for i in range(10):
            changes.append({'change_type':'world','change':{'x':params['x'],'y':i,'direction':world[params[(i+1)%10]][params['x']]}})
    
    return changes

def swap_tiles(world, monsters, player, params):
    direction=params['direction']

    # We have two tiles changing: Which two depends on the direction. Set both of them to x and y in the meantime 
    changes=[]
    changes.append({'change_type':'world','change':{'x':params['x'],'y':params['y'],'direction':world[params['y']][params['x']]}})
    changes.append({'change_type':'world','change':{'x':params['x'],'y':params['y'],'direction':world[params['y']][params['x']]}})

    if direction == 'left':
        changes[0]['change']['direction']=world[params['y']][(params['x']-1)%10]
        changes[1]['change']['x']-=1
        changes[1]['change']['x']%=10
    elif direction == 'right':
        changes[0]['change']['direction']=world[params['y']][(params['x']+1)%10]
        changes[1]['change']['x']+=1
        changes[1]['change']['x']%=10
    elif direction == 'top':
        changes[0]['change']['direction']=world[(params['y']-1)%10][params['x']]
        changes[1]['change']['y']-=1
        changes[1]['change']['y']%=10
    elif direction == 'bottom':
        changes[0]['change']['direction']=world[(params['y']+1)%10][params['x']]
        changes[1]['change']['y']+=1
        changes[1]['change']['y']%=10
    
    return changes

def gen_rand_coords():
	# gen random coords
	x = randint(0, 99)
	y = randint(0, 99)
	return {'x':x, 'y':y}

def spawn_monster(monsters, active_monsters, player, m_grid):
	# get free monsters
	free_monsters = []
	for key in monsters.keys():
		if key not in active_monsters:
			free_monsters.append(key)
			
	while (true):
		coords = gen_rand_coords()
		x = coords['x']
		y = coords['y']
		# check if space is free
		if m_grid[y][x] is None and not (player['x'] == x and player['y'] == y):
			# if so, spawn random free monster there and break
			new_monst = free_monsters[randint(0, len(free_monsters))]
			monsters[new_monst]['x'] = x
			monsters[new_monst]['y'] = y
			active_monsters.append(new_monst)
			break
		# else loop again
		
	# when monster has spawned, return updated lists
	return {'monsters':monsters, 'active_monsters':active_monsters}

actions = {
    'rotate_right': rotate_right,
    'rotate_left': rotate_left,
    'shift_tiles': shift_tiles,
    'swap_tiles': swap_tiles
}

class action(webapp.RequestHandler):
    def post(self):

        # authenticate user
        user = authorize(self)
        
        # get world state (from user)
        game = get_game(get_account(user).game_id)
        world = json.loads(game.tiles)

        monsters = json.loads(game.monsters)
        active_monsters = json.loads(game.active_monsters)
        powerups = json.loads(game.powerups)

        player = json.loads(game.player)
        
        # FIRST update allowed actions (i.e. a turn has passed for them)
        #for a in player['abilities']:
        #    if a > 0:
        #        a -= 1
        #@TODO update countdown on powerups on board
        
        # THEN perform new action && make it invalid
        # get action params from POST
        params = json.loads(self.request.body)
        # get action key
        action_key = params['action']
        
        # calculate action on the world
        changes = actions[action_key](world, monsters, player, params)
        
        # loop through changes and apply
        for change in changes.keys():
            if change == 'world':
                for tile in changes[change]:
                    world[tile['y']][tile['x']] = tile['direction']
                    tile['direction'] = directions[tile['direction']]
            elif change == 'monsters':
                continue #@TODO
            elif change == 'player':
                continue #@TODO
        
        # move player & pick up any powerups
        player = move_player(world, player)
        new_powerups = []
        for p in powerups:
            if (p['x'] == player['x'] and p['y'] == player['y']): # if there is a powerup on the square
                player['abilities'][p['name']] = 0  # pick it up
            else:
                new_powerups.append(p)
        powerups = new_powerups
                
        # establish monster positions
        m_grid = []
        for m in monsters:
            m_grid[m['y']][m['x']] = m  
        # move monsters 
        monster_changes = move_monsters(world, monsters, player, m_grid)
        monsters = monster_changes['monsters']
        m_grid = monster_changes['m_grid']
        #calculate damage
        player = calc_damage(player, monster_changes['prox_count'])
                
        # board updates!
        # tile randomising (non-vital)
        # monster spawning
        if game.turn_count % 5 == 0:
			spawn_results = spawn_monster(monsters, active_monsters, player, m_grid)
			monsters = spawn_results['monsters']
			active_monsters = spawn_results['active_monsters']
        
        # powerup drops
        
        # save the changed world
        game.tiles = json.dumps(world)
        # save the new monster positions
        #game.monsters = json.dumps(monsters)
        # save the new powerup positions
        #game.powerups = json.dumps(powerups)
        # save the updated health
        game.player = json.dumps(player)
        
        game.turn_count+=1
        
        game.put()

        changes['player'] = player
        
        # response: send changes!
        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(json.dumps(changes))

urls = [
    ('/', display_game),
    ('/action', action)
  ]

app = webapp.WSGIApplication(urls, debug=True)

def main():
    run_wsgi_app(app)

if __name__ == '__main__':
    main()
