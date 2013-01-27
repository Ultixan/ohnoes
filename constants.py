template_dir = '/templates/'

directions = [
    'up',
    'right',
    'down',
    'left'
]

elements = {
	'ghost' : 'dark',
	'orb'	: 'dark',
	'boogey': 'dark',
    'bat' : 'dark',
	'stove'	: 'fire',
	'lighter' : 'fire',
	'flame' : 'fire',
    'firefly' : 'firefly',
	'jelly' : 'water',
	'shark' : 'water',
	'octo'	: 'water',
    'toilet' : 'water',
	'spider': 'crawlies',
	'rat'	: 'crawlies',
	'snake' : 'crawlies',
    'mantis' : 'crawlies'
}

ability_codes = {
		'rotate_right':0,
        'rotate_left':1,
        'swap_tiles':2,
        'shift_tiles':3
}

powerup_list = {
	'normal':['blanket','candy']
}

start_drop_rate = 0.02

column_range = range(0, 12)

max_beats = 2500

monster_spawn_rate = 3
