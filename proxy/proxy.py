import logging

from google.appengine.api import urlfetch
from google.appengine.ext import webapp
import google.appengine.ext.webapp.util

REMOTE_ROBOT = 'http://downy.artdent.homelinux.net'
ATTEMPTS = 3


class Proxy(webapp.RequestHandler):

  def _forward(self, method):
    path = REMOTE_ROBOT + self.request.path
    logging.info('path: <%s>', path)
    robot_response = None
    for i in range(ATTEMPTS):
      try:
        robot_response = urlfetch.fetch(path, method=method, deadline=10,
                                        payload=self.request.body)
        logging.info('remote response: %d', robot_response.status_code)
      except urlfetch.DownloadError, e:
        logging.error('Download error: %s', e)
    if not robot_response:
      raise RuntimeError(
        'Did not receive response from %s after %s tries. '
        'Either the host is down or urlfetch is still broken.'
        % (path, ATTEMPTS))
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
