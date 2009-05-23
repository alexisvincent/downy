#!/usr/bin/python2.5

import logging


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
      self.announce(context)

  def announce(self, context):
    pass

  def _in_participant_list(self, l):
    pass


