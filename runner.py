import cgi
import json

from constants import directions
from constants import column_range
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from util import template_path
from util import get_game

def authorize(scope):
    user = users.get_current_user()
    if not user:
        return scope.redirect(
            users.create_login_url(scope.request.uri)
        )
    return user

class display_game(webapp.RequestHandler):
    path = template_path('game.html')

    def get(self):
        user = authorize(self)
        game = get_game('bar')
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
	def rotate_left(self, world_json, params_json):
		world = json.loads(world_json)
		params = json.loads(params_json)
		
		# tiles[row][column] -- world[y][x]
		world[params[y]][params[x]] -= 1
		world[params[y]][params[x]] %= 4 # to wrap direction around to 0
		
		return [{"x":params[x], "y":params[y], "direction":world[params[y]][params[x]]}]
	
	# takes world json and tile coords, transforms, returns new version
	def rotate_right(self, world_json, params_json):
		world = json.loads(world_json)
		params = json.loads(params_json)
		
		# tiles[row][column] -- world[y][x]
		world[params[y]][params[x]] += 1
		world[params[y]][params[x]] %= 4 # to wrap direction around to 0
		
		return world.dumps(json)

	actions = {
		'rotate_right': rotate_right,
		'rotate_left': rotate_left
	}
	
	def post(self):
		# authenticate user
		user = authorize(self)
		# get world state (from user)
		world_json = get_game(get_account(user).game_id).tiles
		
		#get action params from POST
		params_json = self.request.body;
		# get action key
		action_key = json.loads(params_json)["action"]
		# perform action on the world
		changed_tiles = actions[action_key](world_json, params_json)
		self.response.out.write(json.dumps({"tiles":changed_tiles}))
	

urls = [
    ('/', display_game),
    ('/action', action)
  ]

app = webapp.WSGIApplication(urls, debug=True)

def main():
    run_wsgi_app(app)

if __name__ == '__main__':
    main()
