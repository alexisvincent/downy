#!/usr/bin/python2.5

"""Main entry point for Downy."""

import logging
import os
import mercurial

from api import robot_abstract
import app
import downy

import optparse


def _non_interactive_ui():
  ui = mercurial.ui.ui()
  ui.setconfig('ui', 'interactive', 'off')
  return ui


def downy_app(repo_path):
  """Builds a WSGI application to serve both an Hg repository and Downy."""
  hgui = _non_interactive_ui()
  repo = mercurial.hg.repository(hgui, path=repo_path)

  model = downy.Downy(repo)
  bot = robot_abstract.Robot(
      'Downy', version=1,
      image_url='http://downybot.appspot.com/public/downy.png',
      profile_url='http://downybot.appspot.com/public/profile.xml')
  bot.RegisterListener(model)
  logging.info('Registered %d handlers', len(bot._handlers))

  robot_app = app.SimpleRobotApp(bot)
  hg_app = mercurial.hgweb.hgweb(repo)
  return app.RobotMiddleware(robot_app, hg_app)


def main():
  from wsgiref import simple_server, validate

  logging.basicConfig(level=logging.INFO)

  parser = optparse.OptionParser()
  parser.add_option('-p', '--port', dest='port', type='int', default=8000,
                    help='Port to listen on')
  options, args = parser.parse_args()
  if len(args) == 0:
    repo_path = '.'
  elif len(args) == 1:
    repo_path = args[0]
  else:
    print 'Usage: main.py [options] [path to repository]'
    return
  app = validate.validator(downy_app(repo_path))
  httpd = simple_server.make_server('', options.port, app)
  logging.info('Serving on port %d', options.port)
  httpd.serve_forever()


if __name__=='__main__':
  main()
else:
  # Mod_wsgi application object
  application = downy_app(os.path.dirname(__file__))
