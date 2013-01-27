from constants import directions
from util import calc_move
from util import gen_rand_coords
from random import randint

def move_monsters(world, monsters, player, m_grid, active_monsters):
    changes = {
        'world': [],
        'monsters': [],
        'is_dead': False
    }
    
    px = player['x']
    py = player['y']

    heartrate = player['heartrate']

    for a in active_monsters:
        m = monsters[a]
        mx = m['x']
        my = m['y']
        mcode = world[my][mx]
        new_pos = calc_move(mcode, {'x': mx, 'y': my})
        nx = new_pos['x']
        ny = new_pos['y']
        ncode = world[ny][nx]
        #Check if new location points back here
        if abs(ncode - mcode) == 2:
            ncode = (ncode + [-1,1][randint(0,1)]) % 4
            world[ny][nx] = ncode
            changes['world'].append({
                'x': nx,
                'y': ny,
                'direction': directions[ncode]
            })
        # check if it can move there
        if m_grid[ny][nx] == None:
            # moving allowed! (i.e. nothing in the way)
            m_grid[my][mx] = None   # off of old spot
            m_grid[ny][nx] = m  # onto new spot
            # save new position
            m['x'] = nx
            m['y'] = ny
        else:
            mcode = (mcode + [-1,1][randint(0,1)]) % 4
            world[my][mx] = mcode
            changes['world'].append({
                'x': mx,
                'y': my,
                'direction': directions[mcode]
            })
       
        mx = m['x']
        my = m['y']
        # calculate proximity
        if abs(mx - px) <= 2 and abs(my - py) <= 2:
            if mx == px and my == py:
                # on the same square
                heartrate += 1
                changes['is_dead'] = True
            elif abs(mx - px) <= 1 and abs(my - py) <= 1:
                # superclose
                heartrate += 5
            else:
                # nearby
                heartrate += 2

    if heartrate == player['heartrate']:
        heartrate -= 10
    player['heartrate'] = heartrate if heartrate > 50 else 50
    player['heartbeats'] -= player['heartrate']
    changes['player'] = player

    return {
        'm_grid': m_grid,
        'changes': changes,
        'world': world,
        'monsters': monsters
    }

def spawn_monster(monsters, active_monsters, player, m_grid):
    # get free monsters
    free_monsters = []
    for key in monsters.keys():
        if key not in active_monsters:
            free_monsters.append(key)

    if len(free_monsters) > 0:
        while (True):
            coords = gen_rand_coords()
            x = coords['x']
            y = coords['y']
            # check if space is free
            if (y not in m_grid or x not in m_grid[y]) and not (player['x'] == x and player['y'] == y):
                # if so, spawn random free monster there and break
                new_monst = free_monsters[randint(
                    0, 
                    len(free_monsters) - 1)]
                monsters[new_monst]['x'] = x
                monsters[new_monst]['y'] = y
                active_monsters.append(new_monst)
                break
            # else loop again
        
    # when monster has spawned, return updated lists
    return {
        'monsters': monsters,
        'active_monsters': active_monsters
    }

def move_player(world, player, m_grid):
    px = player['x']
    py = player['y']
    # move player
    new_pos = calc_move(world[py][px], {'x': px, 'y': py})
    player['x'] = new_pos['x']
    player['y'] = new_pos['y']
    
    died = False
    # see if player lands on monster
    if m_grid[player['y']] is not None and m_grid[player['y']][player['x']] is not None:
        died = True
    
    return {'player':player, 'died':died}
