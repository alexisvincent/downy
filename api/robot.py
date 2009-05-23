#!/usr/bin/python2.4
#
# Copyright 2009 Google Inc. All Rights Reserved.

"""Defines the robot class and handlers associated.

This is currently App Engine specific with respect to web handlers.

TODO(davidbyttow): Split App Engine specific code into separate module.
"""

__author__ = 'davidbyttow@google.com (David Byttow)'


import logging
import sys
import traceback

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import robot_abstract


DEBUG_DATA = None
#DEBUG_DATA = '{"blips":{"map":{"wdykLROk*13":{"lastModifiedTime":1242079608457,"contributors":{"javaClass":"java.util.ArrayList","list":["davidbyttow@google.com"]},"waveletId":"conv+root","waveId":"wdykLROk*11","parentBlipId":null,"version":3,"creator":"davidbyttow@google.com","content":"\n","blipId":"wdykLROk*13","javaClass":"com.google.walkabout.api.impl.BlipData","annotations":{"javaClass":"java.util.ArrayList","list":[{"range":{"start":0,"javaClass":"com.google.walkabout.api.Range","end":1},"name":"user/e/davidbyttow@google.com","value":"David","javaClass":"com.google.walkabout.api.Annotation"}]},"elements":{"map":{},"javaClass":"java.util.HashMap"},"childBlipIds":{"javaClass":"java.util.ArrayList","list":[]}}},"javaClass":"java.util.HashMap"},"events":{"javaClass":"java.util.ArrayList","list":[{"timestamp":1242079611003,"modifiedBy":"davidbyttow@google.com","javaClass":"com.google.walkabout.api.impl.EventData","properties":{"map":{"participantsRemoved":{"javaClass":"java.util.ArrayList","list":[]},"participantsAdded":{"javaClass":"java.util.ArrayList","list":["monty@appspot.com"]}},"javaClass":"java.util.HashMap"},"type":"WAVELET_PARTICIPANTS_CHANGED"}]},"wavelet":{"lastModifiedTime":1242079611003,"title":"","waveletId":"conv+root","rootBlipId":"wdykLROk*13","javaClass":"com.google.walkabout.api.impl.WaveletData","dataDocuments":null,"creationTime":1242079608457,"waveId":"wdykLROk*11","participants":{"javaClass":"java.util.ArrayList","list":["davidbyttow@google.com","monty@appspot.com"]},"creator":"davidbyttow@google.com","version":5}}'


class RobotCapabilitiesHandler(webapp.RequestHandler):
  """Handler for serving capabilities.xml given a robot."""

  def __init__(self, robot):
    """Initializes this handler with a specific robot."""
    self._robot = robot

  def get(self):
    """Handles HTTP GET request."""
    xml = robot_abstract.CapabilitiesXml(self._robot)
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

    context, events = robot_abstract.ParseJSONBody(json_body)
    for event in events:
      try:
        self._robot._HandleEvent(event, context)
      except Exception:
        logging.error(traceback.format_exc())

    json_response = robot_abstract.SerializeContext(context)
    # Build the response.
    logging.info('Outgoing: ' + json_response)
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json_response)


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


class Robot(robot_abstract.Robot):
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
