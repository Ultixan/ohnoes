import actions
import cgi
import json
import logging
import zoo

from constants import directions
from constants import column_range
from constants import max_beats
from constants import monster_spawn_rate
from constants import ability_codes
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from util import template_path
from util import get_game
from util import get_account
from util import drop_powerup
from random import choice
from random import randint

def authorize(scope):
    user = users.get_current_user() 
    if not user:
        scope.redirect(users.create_login_url(scope.request.uri))
        return None
    return user

class results(webapp.RequestHandler):
    path = template_path('results.html')

    def get(self):
        user = authorize(self)
        account = get_account(user)
        game = get_game(account.game_id)

        if game.is_dead != 1:
            self.redirect('/')
            return

        player = json.loads(game.player)
        turns_lasted = game.turn_count
        last_heartrate = player['heartrate']
        last_heartbeats = player['heartbeats']
        monsters = json.loads(game.monsters)
        active_monsters = json.loads(game.active_monsters)
        px = player['x']
        py = player['y']
        killer = None
        for a in active_monsters:
            m = monsters[a]
            if m['x'] == px and m['y'] == py:
                killer = a
                break

        clean_up_game(game)

        self.response.out.write(
                template.render(self.path, {
                    'heartrate': last_heartrate,
                    'heartbeat': last_heartbeats if last_heartbeats > 0 else 0,
                    'killer': killer,
                    'turns': turns_lasted
                })
            )
        

def clean_up_game(game):
    # get stuff
    active_monsters = json.loads(game.active_monsters)
    powerups = json.loads(game.powerups)
    player = json.loads(game.player)
    
    player['heartrate'] = 50    # reset heartrate
    player['heartbeats'] = max_beats # reset heartbeats
    active_monsters = []        # reset active monsters
    powerups = []               # clear all powerups
    for a in player['abilities']:           # reset timedown on abilities
        a = 0
    
    game.active_monsters = json.dumps(active_monsters)
    game.powerups = json.dumps(powerups)
    game.player = json.dumps(player)
    game.is_dead = 0
    game.turn_count = 0
    
    # save stuff
    game.put()
    logging.info('Saved!')

class display_game(webapp.RequestHandler):
    path = template_path('game.html')

    def get(self):
        user = authorize(self)
        account = get_account(user)
        game = get_game(account.game_id)
        
        # check for death condition
        if game.is_dead == 1:
            self.redirect('/results')
        
        tiles = []
        for row in json.loads(game.tiles):
            newRow = []
            for cell in row:
                newRow.append(directions[cell])
            tiles.append(newRow)
        monsters = json.loads(game.monsters)
        monster_details = []
        for monster in json.loads(game.active_monsters):
            m = monsters[monster]
            monster_details.append({
                'name': monster,
                'x': m['x'],
                'y': m['y']
            })

        p = json.loads(game.player)

        self.response.out.write(
            template.render(self.path, {
                'tiles': tiles,
                'columns': column_range,
                'player': p,
                'abilities': p['abilities'],
                'max_beats': max_beats,
                'monsters': monster_details
            })
        )

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
        
        # establish monster positions
        m_grid = []
        for i in range(10):
            row = []
            for j in range(10):
                row.append(None)
            m_grid.append(row)
        for a in active_monsters:
            m = monsters[a]
            m_grid[m['y']][m['x']] = m  
        
        # establish powerup positions and update countdown on powerups        
        p_grid = []
        for i in range(10):
            row = []
            for j in range(10):
                row.append(None)
            p_grid.append(row)
        new_powerups = []
        for a in powerups:
            a['t'] -= 1
            if a['t']>=0:   # if the powerup is still active, add to grid
                new_powerups.append(a)
                p_grid[a['y']][a['x']] = a['type']
        powerups = new_powerups
        
        
        # FIRST update allowed actions (i.e. a turn has passed for them)
        for i in range(len(player['abilities'])):
            if player['abilities'][i] > 0:
                player['abilities'][i] -= 1
        
        # THEN perform new action && make it invalid

        # get action params from POST
        params = json.loads(self.request.body)

        # FIRST update allowed actions (i.e. a turn has passed for them) if they used an actual ability
        # get action key
        action_key = params['action']
        action_code = ability_codes[action_key] if action_key in ability_codes else None
        if action_code is not None:
            for i in range(len(player['abilities'])):
                if player['abilities'][i] > 0:
                    player['abilities'][i] -= 1
            player['abilities'][action_code] = 2
        # update countdown on powerups
        
        # THEN perform new action && make it invalid
        
        # calculate action on the world
        changes = actions.perform[action_key](world, params)
        
        # loop through changes and apply
        for change in changes.keys():
            if change == 'world':
                for tile in changes[change]:
                    world[tile['y']][tile['x']] = tile['direction']
                    tile['direction'] = directions[
                        tile['direction']
                    ]
            elif change == 'monsters':
                continue #Futureproofing
            elif change == 'player':
                continue #Futureproofing
        
        # move player & pick up any powerups
        player_changes = zoo.move_player(world, player, m_grid)
        player = player_changes['player']
        if player_changes['died']:
            game.is_dead = 1
            changes['is_dead'] = True
            player['stupid'] = True
        
        # powerups effect
        new_powerups = []
        for pu in powerups:
            if (pu['x'] == player['x'] and pu['y'] == player['y']): # if there is a powerup on the square
                p_grid[pu['y']][pu['x']] = None # pick it up
                
                # blanket
                if pu['type'] == 'blanket':
                    # loop through active monsts and remove close ones
                    safe_monsters = []
                    for m in active_monsters:
                        if abs(monsters[m]['x'] - pu['x']) > 2 and abs(monsters[m]['y'] - pu['y']) > 2:
                            safe_monsters.append[m]
                    active_monsters = safe_monsters
                
                # candy
                elif pu['type'] == 'candy':
                    # move player again
                    player_changes = zoo.move_player(world, player, m_grid)
                    player = player_changes['player']
                    if player_changes['died']:
                        game.is_dead = 1
                        changes['is_dead'] = True
                        player['stupid'] = True
            else:
                new_powerups.append(pu)
        powerups = new_powerups
                
        # move monsters
        monster_changes = zoo.move_monsters(
            world, 
            monsters, 
            player, 
            m_grid, 
            active_monsters,
            p_grid,
            powerups)
        monsters = monster_changes['monsters']
        m_grid = monster_changes['m_grid']
        world = monster_changes['world']
        m_change = monster_changes['changes']
        p_grid = monster_changes['p_grid']
        powerups = monster_changes['powerups']

        # add tile changes caused by monsters
        changes['world'].extend(m_change['world'])
        changes['is_dead'] = m_change['is_dead']
        player = m_change['player']
        
        # board updates!
        # tile randomising (non-vital)
        # monster spawning
        
        if game.turn_count % monster_spawn_rate == 0:
            spawn_results = zoo.spawn_monster(
                monsters, 
                active_monsters, 
                player,
                m_grid,
                powerups,
                p_grid)
            monsters = spawn_results['monsters']
            active_monsters = spawn_results['active_monsters']
            p_grid = monster_changes['p_grid']
            powerups = monster_changes['powerups']
        
        # powerup drop
        powerup_changes = drop_powerup(game.drop_chance, powerups, m_grid, player, p_grid)
        powerups = powerup_changes['powerups']
        game.drop_chance = powerup_changes['drop_chance']
        # not updating p_grid because not used again
        
        # check death conditions
        # no more heartbeats
        if player['heartbeats'] < 1 or player['heartrate'] > 199 or changes['is_dead']: 
            game.is_dead = 1
            changes['is_dead'] = True
        
        # save the changed world
        game.tiles = json.dumps(world)
        # save the new monster positions
        game.monsters = json.dumps(monsters)
        game.active_monsters = json.dumps(active_monsters)
        # save the new powerup positions
        game.powerups = json.dumps(powerups)
        # save the updated health
        game.player = json.dumps(player)
        
        game.turn_count+=1
        
        game.put()

        monster_details = {}
        for monster in active_monsters:
            monster_details[monster] = monsters[monster]
        changes['monsters'] = monster_details
        changes['player'] = player
        changes['powerups'] = powerups
        
        # response: send changes!
        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(json.dumps(changes))

urls = [
    ('/', display_game),
    ('/action', action),
    ('/results', results)
  ]

app = webapp.WSGIApplication(urls, debug=True)

def main():
    run_wsgi_app(app)

if __name__ == '__main__':
    main()
