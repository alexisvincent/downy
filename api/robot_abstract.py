#!/usr/bin/python2.4
#
# Copyright 2009 Google Inc. All Rights Reserved.

"""Defines the robot class and handlers associated.

This is currently App Engine specific with respect to web handlers.

TODO(davidbyttow): Split App Engine specific code into separate module.
"""

__author__ = 'davidbyttow@google.com (David Byttow)'


import logging
import simplejson

import ops
import util


def CapabilitiesXml(robot):
  lines = ['<w:capabilities>']
  for capability in robot.GetCapabilities():
    lines.append('  <w:capability name="%s"/>' % capability)
  lines.append('</w:capabilities>')

  if robot.cron_jobs:
    lines.append('<w:crons>')
    for job in robot.cron_jobs:
      lines.append('  <w:cron path="%s" timerinseconds="%s"/>' % job)
    lines.append('</w:crons>')

  robot_attrs = ' name="%s"' % robot.name
  if robot.image_url:
    robot_attrs += ' imageurl="%s"' % robot.image_url
  if robot.image_url:
    robot_attrs += ' profileurl="%s"' % robot.profile_url
  lines.append('<w:profile%s/>' % robot_attrs)
  return ('<?xml version="1.0"?>\n'
          '<w:robot xmlns:w="http://www.google.com/fake/ns/whee">\n'
          '%s\n</w:robot>\n') % ('\n'.join(lines))


def ParseJSONBody(self, json_body):
  """Parse a JSON string and return a context and an event list."""
  json = simplejson.loads(json_body)
  logging.info('Incoming: ' + str(json))

  # TODO(davidbyttow): Remove this once no longer needed.
  data = util.CollapseJavaCollections(json)

  context = ops.CreateContext(data)
  events = []
  for event_data in data['events']:
    event = events.Event(event_data)
    if event.type:
      events.append(event)

  return context, events


def SerializeContext(self, context):
  """Return a JSON string representing the given context."""
  context_dict = util.Serialize(context)
  return simplejson.dumps(context_dict)


class Robot(object):
  """Robot class used to setup this application.

  A robot is typically setup in the following steps:
    1. Instantiate and define robot.
    2. Register various handlers that it is interested in.
    3. Call Run, which will setup the handlers for the app.

  For example:
    robot = Robot('Terminator',
                  image_url='http://www.sky.net/models/t800.png',
                  profile_url='http://www.sky.net/models/t800.html')
    robot.RegisterHandler(WAVELET_PARTICIPANTS_CHANGED, KillParticipant)
    robot.Run()
  """

  def __init__(self, name, image_url=None, profile_url=None):
    """Initializes self with robot information."""
    self._handlers = {}
    self.name = name
    self.image_url = image_url
    self.profile_url = profile_url
    self.cron_jobs = []

  def RegisterHandler(self, event_type, handler):
    """Registers a handler on a specific event type.

    Multiple handlers may be registered on a single event type and are
    guaranteed to be called in order.

    The handler takes two arguments, the event properties and the Context of
    this session. For example:

    def OnParticipantsChanged(properties, context):
      pass

    Args:
      event_type: An event type to listen for.
      handler: A function handler which takes two arguments, event properties
          and the Context of this session.
    """
    self._handlers.setdefault(event_type, []).append(handler)


  def RegisterCronJob(self, path, seconds):
    """Registers a cron job to surface in capabilities.xml."""
    self.cron_jobs.append((path, seconds))

  def _HandleEvent(self, event, context):
    """Calls all of the handlers associated with an event."""
    for handler in self._handlers.get(event.type, []):
      handler(event.properties, context)

  def GetCapabilities(self):
    """Returns a list of the event types that we are interested in."""
    return self._handlers.keys()
