import cgi
import json
import logging

from constants import directions
from constants import column_range
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from util import template_path
from util import get_game
from util import get_account

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
        logging.info(user)
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
                'columns': column_range
            })
        )

class action(webapp.RequestHandler):
    # takes world json and tile coords, transforms, returns new version
    def rotate_left(self, world, monsters, player, params_json):
        params = json.loads(params_json)
        
        # tiles[row][column] -- world[y][x]
        world[params[y]][params[x]] -= 1
        world[params[y]][params[x]] %= 4 # to wrap direction around to 0
        
        player['abilities']['rotate_left'] = 2
        
        return {'change_type':'world', change:{'x':params[x], 'y':params[y], 'direction':world[params[y]][params[x]]}}
    
    # takes world json and tile coords, transforms, returns new version
    def rotate_right(self, world, monsters, player, params_json):
        params = json.loads(params_json)
        
        # tiles[row][column] -- world[y][x]
        world[params[y]][params[x]] += 1
        world[params[y]][params[x]] %= 4 # to wrap direction around to 0
        
        player['abilities']['rotate_left'] = 2
        
        return [{'change_type':'world', 'change':{'x':params[x], 'y':params[y], 'direction':world[params[y]][params[x]]}}]

    actions = {
        'rotate_right': rotate_right,
        'rotate_left': rotate_left
    }

	def move_pos(self, move_code, coords):	
		if move_code == 0:
			coords['y'] = (coords['y']-1)%10
		elif move_code == 1:
			coords['x'] = (coords['x']+1)%10
		elif move_code == 2:
			coords['y'] = (coords['y']+1)%10
		elif move_code == 3:
			coords['x'] = (coords['x']-1)%10
		return coords;
        
    def move_player(self, world, player):
		# check direction of tile
		move_code = world[player['y']][player['x']]
		# move player
		new_pos = move_pos(move_code, {'x':player['x'], 'y':player['y']})
		player['x'] = new_pos['x']
		player['y'] = new_pos['y']
		
		return player	
		
	def move_monsters(self, world, monsters, player, m_grid):
		prox_count = {'near':0, 'superclose':0, 'gruesome_death' : 0}
		
		for m in monsters:
			# check direction of tile
			move_code = world[m['y']][m['x']]
			# move monster
			new_pos = move_pos(move_code, {'x':m['x'], 'y':m['y']})
			# check if it can move there
			if m_grid[new_pos['y']][new_pos['x']] == None:
				# moving allowed! (i.e. nothing in the way)
				m_grid[m['y']][m['x']] = None	# off of old spot
				m_grid[new_pos['y']][new_pos['x']] = m	# onto new spot
				# save new position
				m['x'] = new_pos['x']
				m['y'] = new_pos['y']
			# if moving blocked, nothing happens
			
			# calculate proximity
			if abs(m['x']-player['x'])<=2 && abs(m['y']-player['y'])<=2:
				if m['x'] == player['x'] && m['y'] == player['y']:
					# on the same square
					prox_count['gruesome_death'] += 1
				elif abs(m['x']-player['x'])<=1 && abs(m['y']-player['y'])<=1:
					# superclose
					prox_count['superclose'] += 1
				else
					# nearby
					prox_count['near'] += 1

		return {'prox_count' : prox_count, 'monsters' : monsters, 'm_grid':m_grid}
	
	def calc_damage(self, player, prox_count):
		player['heartrate'] += prox_count['near']*2 + prox_count['superclose']*5
		if prox_count['near'] == 0 && prox_count['superclose'] == 0:
			new_rate -= 10
			player['heartrate'] = new_rate > 50 ? new_rate : 50
		player['heartbeats'] -= player['heartrate']
		return player
	
	def post(self):
        # authenticate user
        user = authorize(self)
        
        # get world state (from user)
        game = get_game(get_account(user).game_id)
        world = json.loads(game.tiles)
        monsters = json.loads(game.monsters)
        powerups = json.loads(game.powerups)
        player = json.loads(game.player)
        
        # FIRST update allowed actions (i.e. a turn has passed for them)
        for a in player['abilities']:
			if a > 0:
				a -= 1
		#@TODO update countdown on powerups on board
		
        # THEN perform new action && make it invalid
        # get action params from POST
        params_json = self.request.body;
        # get action key
        action_key = json.loads(params_json)['action']
        
        # calculate action on the world
        changes = actions[action_key](world, monsters, player, params_json)
        
        # loop through changes and apply
        for c in changes:
			if c['change_type'] == 'world':
				x = c['change']['x']
				y = c['change']['y']
				direction = c['change']['direction']
				world[y][x] = direction
			elif c['change_type'] == 'monsters':
				continue #@TODO
			elif c['change_type'] == 'player':
				continue #@TODO
		
		# move player
		player = move_player(world, player)
		# check for powerups
		new_powerups = []
		for p in powerups:
			if (p['x'] == player['x'] && p['y'] == player['y']): # if there is a powerup on the square
				player['abilities'][p['name']] = 0	# pick it up
			else
				new_powerups.append(p)
		powerups = new_powerups
				
		# establish monster positions
		m_grid = []
		for m in monsters:
			m_grid[m['y']][m['x']] = m	
		# move monsters	
		monster_changes = move_monsters(world, monsters, player)
		monsters = monster_changes['monsters']
		m_grid = monster_changes['m_grid']
		#calculate damage
		player = calc_damage(player, monster_changes['prox_count'])
		
		# board updates!
		# tile randomising (non-vital)
		# monster spawning
		# powerup drops        
        
        # save the changed world
        game.tiles = json.dumps(world)
        # save the new monster positions
        game.monsters = json.dumps(monsters)
        # save the new powerup positions
        game.powerups = json.dumps(powerups)
        # save the updated health
        game.player = json.dumps(player)
        
        game.put()
        
        # response: send changes!
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
