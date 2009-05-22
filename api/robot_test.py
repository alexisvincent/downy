#!/usr/bin/python2.4
#
# Copyright 2009 Google Inc. All Rights Reserved.

"""Unit tests for the robot module."""


__author__ = 'davidbyttow@google.com (David Byttow)'


import unittest

import robot


# TODO(davidbyttow): Add more unit tests. Currently this is not so easy because
# robot module depends on app-engine specific packages and this unit test
# is platform agnostic.


class TestRobotCapabilitiesHeader(unittest.TestCase):
  def setUp(self):
    self.robot = robot.Robot()

  def testCapabilitiesXml(self):
    noop_robot = robot.Robot()
    caps_handler = robot.RobotCapabilitiesHandler(noop_robot)
    xml = caps_handler._CapabilitiesXml()
    self.assertEqual('', xml)
