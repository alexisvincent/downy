#!/usr/bin/python2.5

import logging
import mercurial
import webob
import webob.exc

from api import robot_abstract
from api import events
import downy


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
    xml = self._robot.CapabilitiesXml()
    response = webob.Response(content_type='text/xml', body=xml)
    response.cache_control = 'Private'  # XXX
    return response

  def jsonrpc(self, req):
    json_body = req.body
    if not json_body:
      return
    logging.info('Incoming: %s', json_body)

    context = robot_abstract.ParseJSONBody(json_body)
    for event in context.GetEvents():
      self._robot.HandleEvent(event, context)

    json_response = robot_abstract.SerializeContext(context)
    logging.info('Outgoing: %s', json_response)
    return webob.Response(content_type='application/json',
                          body=json_response)

  def __call__(self, environ, start_response):
    req = webob.Request(environ)
    if req.path_info == '/_wave/capabilities.xml' and req.method == 'GET':
      response = self.capabilities()
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

  robot_app = SimpleRobotApp(bot)
  hg_app = mercurial.hgweb.hgweb(repo)
  return RobotMiddleware(robot_app, hg_app)


if __name__=='__main__':
  from wsgiref import simple_server, validate

  logging.basicConfig(level=logging.INFO)

  port = 8000
  repo = '.'
  app = validate.validator(downy_app(repo))
  httpd = simple_server.make_server('', port, app)
  logging.info('Serving on port %d', port)
  httpd.serve_forever()
