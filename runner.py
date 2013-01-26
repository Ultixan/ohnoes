import cgi
import json

from constants import directions
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from util import template_path
from util import get_game
from util import get_account

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
                'tiles': tiles
            })
        )

class action():
	actions = {
		"rotate_right" : rotate_right,
		"rotate_left" : rotate_left
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
		new_world_json = actions[action_key](world_json, params_json)	
	
	# takes world json and tile coords, transforms, returns new version
	def rotate_left(self, world_json, params_json):
		world_state = json.loads(world_json)
		
		
		
		
		

urls = [
  ('/', display_game)
  ]

app = webapp.WSGIApplication(urls, debug=True)

def main():
    run_wsgi_app(app)

if __name__ == '__main__':
    main()
