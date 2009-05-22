#!/usr/bin/python2.4
#
# Copyright 2009 Google Inc. All Rights Reserved.

"""Defines the robot class and handlers associated.

This is currently App Engine specific with respect to web handlers.

TODO(davidbyttow): Split App Engine specific code into separate module.
"""

__author__ = 'davidbyttow@google.com (David Byttow)'


import logging
from django.utils import simplejson

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import ops
import util


DEBUG_DATA = None
#DEBUG_DATA = '{"blips":{"map":{"wdykLROk*13":{"lastModifiedTime":1242079608457,"contributors":{"javaClass":"java.util.ArrayList","list":["davidbyttow@google.com"]},"waveletId":"conv+root","waveId":"wdykLROk*11","parentBlipId":null,"version":3,"creator":"davidbyttow@google.com","content":"\n","blipId":"wdykLROk*13","javaClass":"com.google.walkabout.api.impl.BlipData","annotations":{"javaClass":"java.util.ArrayList","list":[{"range":{"start":0,"javaClass":"com.google.walkabout.api.Range","end":1},"name":"user/e/davidbyttow@google.com","value":"David","javaClass":"com.google.walkabout.api.Annotation"}]},"elements":{"map":{},"javaClass":"java.util.HashMap"},"childBlipIds":{"javaClass":"java.util.ArrayList","list":[]}}},"javaClass":"java.util.HashMap"},"events":{"javaClass":"java.util.ArrayList","list":[{"timestamp":1242079611003,"modifiedBy":"davidbyttow@google.com","javaClass":"com.google.walkabout.api.impl.EventData","properties":{"map":{"participantsRemoved":{"javaClass":"java.util.ArrayList","list":[]},"participantsAdded":{"javaClass":"java.util.ArrayList","list":["monty@appspot.com"]}},"javaClass":"java.util.HashMap"},"type":"WAVELET_PARTICIPANTS_CHANGED"}]},"wavelet":{"lastModifiedTime":1242079611003,"title":"","waveletId":"conv+root","rootBlipId":"wdykLROk*13","javaClass":"com.google.walkabout.api.impl.WaveletData","dataDocuments":null,"creationTime":1242079608457,"waveId":"wdykLROk*11","participants":{"javaClass":"java.util.ArrayList","list":["davidbyttow@google.com","monty@appspot.com"]},"creator":"davidbyttow@google.com","version":5}}'


class RobotCapabilitiesHandler(webapp.RequestHandler):
  """Handler for serving capabilities.xml given a robot."""

  def __init__(self, robot):
    """Initializes this handler with a specific robot."""
    self._robot = robot

  def _CapabilitiesXml(self):
    lines = ['<w:capabilities>']
    for capability in self._robot.GetCapabilities():
      lines.append('  <w:capability name="%s"/>' % capability)
    lines.append('</w:capabilities>')

    if self._robot.cron_jobs:
      lines.append('<w:crons>')
      for job in self._robot.cron_jobs:
        lines.append('  <w:cron path="%s" timerinseconds="%s"/>' % job)
      lines.append('</w:crons>')

    robot = self._robot
    robot_attrs = ' name="%s"' % robot.name
    if robot.image_url:
      robot_attrs += ' imageurl="%s"' % robot.image_url
    if robot.image_url:
      robot_attrs += ' profileurl="%s"' % robot.profile_url
    lines.append('<w:profile%s/>' % robot_attrs)
    return ('<?xml version="1.0"?>\n'
            '<w:robot xmlns:w="http://www.google.com/fake/ns/whee">\n'
            '%s\n</w:robot>\n') % ('\n'.join(lines))

  def get(self):
    """Handles HTTP GET request."""
    xml = self._CapabilitiesXml()
    self.response.headers['Content-Type'] = 'text/xml'
    self.response.out.write(xml)


class RobotEventHandler(webapp.RequestHandler):
  """Handler for the dispatching of events to various handlers to a robot.

  This handler only responds to post events with a JSON post body. Its primary
  task is to separate out the context data from the events in the post body
  and dispatch all events in order. Once all events have been dispatched
  it serializes the context data and its associated operations as a response.
  """

  def __init__(self, robot):
    """Initializes self with a specific robot."""
    self._robot = robot

  def get(self):
    """Handles HTTP GET requests."""
    if DEBUG_DATA:
      self.request.body = DEBUG_DATA
      self.post()
      self.response.headers['Content-Type'] = 'text/html'

  def post(self):
    """Handles HTTP POST requests."""
    json_body = self.request.body
    if not json_body:
      # TODO(davidbyttow): Log error?
      return

    json = simplejson.loads(json_body)
    logging.info('Incoming: ' + str(json))

    # TODO(davidbyttow): Remove this once no longer needed.
    data = util.CollapseJavaCollections(json)
    context = ops.CreateContext(data)

    event_list = data['events']
    # For each event, construct an event object and allow the robot to
    # handle it.
    for event_data in event_list:
      event_type = event_data['type']
      properties = event_data['properties'] or {}
      if event_type:
        self._DispatchEvent(event_type, properties, context)

    # Build the response.
    response = util.Serialize(context)
    self.response.headers['Content-Type'] = 'application/json'
    json_response = simplejson.dumps(response)
    logging.info('Outgoing: ' + json_response)
    self.response.out.write(json_response)

  def _DispatchEvent(self, event_type, properties, context):
    """Dispatches this event to the robot."""
    self._robot._HandleEvent(event_type, properties, context)


def RobotHandlerFactory(cls, robot):
  """Creates a handler class that need a robot when instantiated.

  This exists because the webapp framework allows mapping of url patterns to
  classes, which it constructs with no arguments. This allows specification
  of a robot with the request handler that is constructed.

  Args:
    cls: The webapp handler class.
    robot: The robot to use with the handler when constructed.

  Returns:
    Method to construct the desired class with the specific robot.
  """

  def CreateRobotHandler():
    return cls(robot)
  return CreateRobotHandler


class RobotListener(object):
  """Listener interface for robot events.

  The RobotListener is a high-level construct that hides away the details
  of events. Instead, a client will derive from this class and register
  it with the robot. All event handlers are automatically registered. When
  a relevant event comes in, logic is applied based on the incoming data and
  the appropriate function is invoked.

  For example:
    If the user implements the "OnRobotAdded" method, the OnParticipantChanged
    method of their subclass, this will automatically register the
    events.WAVELET_PARTICIPANTS_CHANGED handler and respond to any events
    that add the robot.

    class MyRobotListener(robot.RobotListener):

      def OnRobotAdded(self):
        wavelet = self.context.GetRootWavelet()
        blip = wavelet.CreateBlip()
        blip.GetDocument.SetText("Thanks for adding me!")

    robot = robots.Robot()
    robot.RegisterListener(MyRobotListener)
    robot.Run()

  TODO(davidbyttow): Implement this functionality.
  """

  def __init__(self):
    pass

  def OnRobotAdded(self):
    # TODO(davidbyttow): Implement.
    pass

  def OnRobotRemoved(self):
    # TODO(davidbyttow): Implement.
    pass


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
    self.__handlers = {}
    self.name = name
    self.image_url = image_url
    self.profile_url = profile_url
    self.cron_jobs = []

  def RegisterHandler(self, event_type, handler):
    """Registers a handler on a specific event type.

    Multiple handlers may be registered on a single event type and are
    guaranteed to be called order.

    The handler takes two arguments, the event properties and the Context of
    this session. For example:

    def OnParticipantsChanged(properties, context):
      pass

    Args:
      event_type: An event type to listen for.
      handler: A function handler which takes two arguments, event properties
          and the Context of this session.
    """
    self.__handlers.setdefault(event_type, []).append(handler)


  def RegisterCronJob(self, path, seconds):
    """Registers a cron job to surface in capabilities.xml."""
    self.cron_jobs.append((path, seconds))

  def _HandleEvent(self, event_type, event_properties, context):
    """Calls all of the handlers associated with an event."""
    for handler in self.__handlers.get(event_type, []):
      handler(event_properties, context)

  def GetCapabilities(self):
    """Returns a list of the event types that we are interested in."""
    return self.__handlers.keys()

  def Run(self, debug=False):
    """Sets up the webapp handlers for this robot and starts listening.

    Args:
      debug: Optional variable that defaults to False and is passed through
          to the webapp application to determine if it should show debug info.
    """
    app = webapp.WSGIApplication([
        ('/_wave/capabilities.xml',
         RobotHandlerFactory(RobotCapabilitiesHandler, self)),
        ('/_wave/robot/jsonrpc',
         RobotHandlerFactory(RobotEventHandler, self)),
    ], debug=debug)
    run_wsgi_app(app)
