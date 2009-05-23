#!/usr/bin/python2.5

import logging

from mercurial import commands


class Downy(object):
  def __init__(self, repo):
    self.repo = repo

  def on_blip_created(self, event, context):
    logging.info('blip created')
    logging.info(event.GetProperties())
    logging.info(context)

  def on_participants_changed(self, event, context):
    added = event.GetProperties()['participantsAdded']
    if self._in_participant_list(added):
      self.announce(context)

  def command(self, cmd):
    cmd_fn = getattr(commands)
    cmd_fn(self.repo.ui, self.repo)

  def announce(self, context):
    wavelet = context.GetRootWavelet()
    blip = context.GetBlipById(wavelet.GetRootBlipId())
    if blip:
      inline_blip = blip.GetDocument().AppendInlineBlip()
      doc.SetText(
        'Hello! I\'m Downy. You can give me instructions '
        'by replying to this blip.')
      doc.AnnotateDocument('downy-comm', '1')

  def _in_participant_list(self, names):
    return any([name.startswith('Downy') for name in names])
