#!/usr/bin/python2.4
#
# Copyright 2009 Google Inc. All Rights Reserved.

"""Defines event types that are sent from the wave server.

This module defines all of the event types currently supported by the wave
server.
"""

__author__ = 'davidbyttow@google.com (David Byttow)'


# Event Types
WAVELET_BLIP_CREATED = 'WAVELET_BLIP_CREATED'
WAVELET_BLIP_REMOVED = 'WAVELET_BLIP_REMOVED'
WAVELET_PARTICIPANTS_CHANGED = 'WAVELET_PARTICIPANTS_CHANGED'
WAVELET_TIMESTAMP_CHANGED = 'WAVELET_TIMESTAMP_CHANGED'
WAVELET_TITLE_CHANGED = 'WAVELET_TITLE_CHANGED'
WAVELET_VERSION_CHANGED = 'WAVELET_VERSION_CHANGED'
BLIP_CONTRIBUTORS_CHANGED = 'BLIP_CONTRIBUTORS_CHANGED'
BLIP_DELETED = 'BLIP_DELETED'
BLIP_SUBMITTED = 'BLIP_SUBMITTED'
BLIP_TIMESTAMP_CHANGED = 'BLIP_TIMESTAMP_CHANGED'
BLIP_VERSION_CHANGED = 'BLIP_VERSION_CHANGED'
DOCUMENT_CHANGED = 'DOCUMENT_CHANGED'


class Event(object):
  def __init__(self, event_data):
    self.type = event_data['type']
    self.properties = event_data['properties'] or {}
