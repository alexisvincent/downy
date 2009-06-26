#!/usr/bin/python2.5
#
# Copyright 2009 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
      'Downy', version='1',
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
