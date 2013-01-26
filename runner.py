import cgi
import json

from constants import directions
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
    

class display_game(webapp.RequestHandler):
    path = template_path('game.html')

    def get(self):
        authorize(self)
        game = get_game('bar')
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

urls = [
  ('/', display_game)
  ]

app = webapp.WSGIApplication(urls, debug=True)

def main():
    run_wsgi_app(app)

if __name__ == '__main__':
    main()
