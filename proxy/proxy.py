from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util


REMOTE_ROBOT = 'http://artdent-chi.homelinux.net/'


def proxy(environ, start_response):
  robot_response = urlfetch.fetch(
      REMOTE_ROBOT + environ['PATH_INFO'], method=environ['REQUEST_METHOD'])
  resp.set_status(robot_response.status_code)
  resp.out.write(robot_response.content)
  resp.wsgi_write(start_response)


def main():
  webapp.util.run_wsgi_app(proxy)


if __name__=='__main__':
  main()
