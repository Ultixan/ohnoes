def rotate(world, params, tick):
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

def rotate_left(world, params):
    return rotate(world, params, -1)

def rotate_right(world, params):
    return rotate(world, params, 1)

def shift_tiles(world, params):
    x = params['x']
    y = params['y']
    direction = params['direction']
    changes = {'world': []}
    tick = 1;
    if (direction == 'right' or direction == 'down'):
        tick = -1;

    if direction == 'left' or direction == 'right':
        for i in range(10):
            changes['world'].append({
                'x': i,
                'y': y,
                'direction': world[y][(i+tick)%10]
            })
    else:
        for i in range(10):
            changes['world'].append({
                'x': x,
                'y':i,
                'direction': world[(i+tick)%10][x]
            })
    
    return changes

def swap_tiles(world, params):
    x1 = params['x']
    y1 = params['y']
    x2 = x1
    y2 = y1
    direction = params['direction']
    if direction == 'left':
        x2 = (x1 - 1) % 10
    elif direction == 'right':
        x2 = (x1 + 1) % 10
    elif direction == 'up':
        y2 = (y1 - 1) % 10
    else:
        y2 = (y1 + 1) % 10

    return {
        'world': [{
            'x': x1,
            'y': y1,
            'direction': world[y2][x2]
        }, {
            'x': x2,
            'y': y2,
            'direction': world[y1][x1]
        }]
    }

def null_action(world, params):
    return {
        'world': []
    }

perform = {
    'rotate_right': rotate_right,
    'rotate_left': rotate_left,
    'shift_tiles': shift_tiles,
    'swap_tiles': swap_tiles,
    'timeout': null_action
}
