#!/usr/bin/python2.4

import logging

from api import robot
from api import events


class RobotMiddleware(object):
  def __init__(self, robot_app, main_app):
    self._robot = robot_app
    self._main = main_app

  def __call__(self, environ, start_response):
    path = env['PATH_INFO']
    if path.startswith('_wave/'):
      return self._robot(environ, start_response)
    return self._main(environ, start_response)


class Downy(object):
  def __init__(self):
    self._announced = False

  def on_blip_created(self, properties, context):
    logging.info('blip created')
    logging.info(properties)
    logging.info(context)

  def on_participants_changed(self, properties, context):
    if self._announced:
      return
    logging.info(properties['participantsAdded'])
    if self._in_participant_list(properties['participantsAdded']):
      self.announce()

  def announce(self):
    pass

  def _in_participant_list(self, l):
    pass


if __name__=='__main__':
  controller = Downy()
  app = robot.Robot(
      'Downy',
      image_url='http://downybot.appspot.com/public/downy.png',
      profile_url='http://downybot.appspot.com/public/profile.xml')
  app.RegisterHandler(events.WAVELET_BLIP_CREATED,
                      controller.on_blip_created)
  app.RegisterHandler(events.WAVELET_PARTICIPANTS_CHANGED,
                      controller.on_participants_changed)
  app.Run(debug=True)
