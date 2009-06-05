#!/usr/bin/python2.5

import logging
import mercurial
import webob
import webob.exc

from api import robot_abstract
from api import events
import downy

import optparse


def NonInteractiveUI():
  ui = mercurial.ui.ui()
  ui.setconfig('ui', 'interactive', 'off')
  return ui


class RobotMiddleware(object):
  """WSGI middleware that routes /_wave/ requests to a robot wsgi app."""
  def __init__(self, robot_app, main_app):
    self._robot_app = robot_app
    self._main_app = main_app

  def __call__(self, environ, start_response):
    path = environ['PATH_INFO']
    if path.startswith('/_wave/'):
      return self._robot_app(environ, start_response)
    return self._main_app(environ, start_response)


class SimpleRobotApp(object):

  def __init__(self, robot):
    self._robot = robot

  def capabilities(self):
    xml = self._robot.GetCapabilitiesXml()
    response = webob.Response(content_type='text/xml', body=xml)
    response.cache_control = 'Private'  # XXX
    return response

  def profile(self):
    xml = self._robot.GetProfileJson()
    response = webob.Response(content_type='text/xml', body=xml)
    response.cache_control = 'Private'  # XXX
    return response

  def jsonrpc(self, req):
    json_body = req.body
    if not json_body:
      return
    logging.info('Incoming: %s', json_body)

    context, events = robot_abstract.ParseJSONBody(json_body)
    for event in events:
      self._robot.HandleEvent(event, context)

    json_response = robot_abstract.SerializeContext(context)
    logging.info('Outgoing: %s', json_response)
    return webob.Response(content_type='application/json',
                          body=json_response)

  def __call__(self, environ, start_response):
    req = webob.Request(environ)
    if req.path_info == '/_wave/capabilities.xml' and req.method == 'GET':
      response = self.capabilities()
    elif req.path_info == '/_wave/robot/profile' and req.method == 'GET':
      response = self.profile()
    elif req.path_info == '/_wave/robot/jsonrpc' and req.method == 'POST':
      response = self.jsonrpc(req)
    else:
      response = webob.exc.HTTPNotFound()
    return response(environ, start_response)


def downy_app(repo_path):
  hgui = NonInteractiveUI()
  repo = mercurial.hg.repository(hgui, path=repo_path)

  model = downy.Downy(repo)
  bot = robot_abstract.Robot(
      'Downy',
      image_url='http://downybot.appspot.com/public/downy.png',
      profile_url='http://downybot.appspot.com/public/profile.xml')
  bot.RegisterHandler(events.WAVELET_BLIP_CREATED,
                      model.on_blip_created)
  bot.RegisterHandler(events.WAVELET_PARTICIPANTS_CHANGED,
                      model.on_participants_changed)
  bot.RegisterHandler(events.BLIP_SUBMITTED,
                      model.on_blip_submitted)
  bot.RegisterHandler(events.FORM_BUTTON_CLICKED,
                      model.on_button_clicked)

  robot_app = SimpleRobotApp(bot)
  hg_app = mercurial.hgweb.hgweb(repo)
  return RobotMiddleware(robot_app, hg_app)


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
