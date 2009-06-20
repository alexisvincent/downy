import logging

from google.appengine.api import urlfetch
from google.appengine.ext import webapp


REMOTE_ROBOT = 'http://artdent-chi.homelinux.net'


class Proxy(webapp.RequestHandler):

  def _forward(self, method):
    path = REMOTE_ROBOT + self.request.path
    logging.info('path: <%s>', path)
    robot_response = urlfetch.fetch(path, method=method, deadline=10)
    logging.info('remote response: %d', robot_response.status_code)
    self.response.set_status(robot_response.status_code)
    self.response.out.write(robot_response.content)

  def get(self):
    self._forward('GET')

  def post(self):
    self._forward('POST')


def main():
  app = webapp.WSGIApplication([('.*', Proxy)], debug=True)
  webapp.util.run_wsgi_app(app)


if __name__=='__main__':
  main()
