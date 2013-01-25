import cgi
import json

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from util import template_path

class game_list(webapp.RequestHandler):
    path = template_path('index.html')

    def get(self):
        grid = []
        row = []
        for j in range(0, 10):
            row.append('')
        for i in range(0, 10):
            grid.append(row)
        self.response.out.write(
            template.render(self.path, {'grid': grid})
        )

urls = [
  ('/', game_list)
  ]

app = webapp.WSGIApplication(urls, debug=True)

def main():
    run_wsgi_app(app)

if __name__ == '__main__':
    main()
