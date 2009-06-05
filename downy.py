#!/usr/bin/python2.5

import logging

from mercurial import commands
from api import document

STATS = document.StringEnum(
    'modified', 'added', 'removed', 'deleted', 'unknown')


class LocalFile(object):
  def __init__(self, name):
    self.name = name


class Downy(object):
  def __init__(self, repo):
    self.repo = repo
    self.tracked_files = []

  def on_blip_created(self, props, context):
    logging.info('blip created')
    logging.info(props)
    logging.info(context)

  def on_participants_changed(self, props, context):
    added = props['participantsAdded']
    if self._in_participant_list(added):
      self.announce(context)

  def load_file(self, context, file_name):
    wavelet = context.GetRootWavelet()
    new_blip = wavelet.CreateBlip()
    doc = new_blip.GetDocument()
    doc.AppendElement(FormElement(
        document.ElementType.BUTTON,
        name=file_name + '_commit', label='Commit'))
    file_text = self.repo.wread(file_name)
    doc.AppendText(file_text)

  def root_blip(self, context):
    wavelet = context.GetRootWavelet()
    return context.GetBlipById(wavelet.GetRootBlipId())

  def command(self, cmd):
    cmd_fn = getattr(commands)
    cmd_fn(self.repo.ui, self.repo)

  def announce(self, context):
    blip = self.root_blip(context)
    if not blip:
      logging.info('Um, no root blip?')
      return
    inline_blip = blip.GetDocument().AppendInlineBlip()
    doc = inline_blip.GetDocument()
    doc.AnnotateDocument('downy-comm', '1')
    doc.SetText(
      'Hello! I\'m Downy. You can give me instructions '
      'by replying to this blip.')
    doc.AppendText('\n')
    doc.AppendText('I know about the following files:\n')
    self.status(doc)

  def status(self, doc):
    (modified, added, removed, deleted, _, _, clean) = self.repo.status(
      clean=True)
    logging.info('%d modified, %d clean',
                 len(modified), len(clean))
    for file_name in clean:
      doc.AppendElement(document.FormElement(
          document.ELEMENT_TYPE.CHECK, name=file_name))
      doc.AppendText(file_name + ' ')
      doc.AppendElement(document.FormElement(
          document.ELEMENT_TYPE.BUTTON, name=file_name, label='Load',
          value='Load'))
      doc.AppendText('\n')
    doc.AppendElement(document.FormElement(
        document.ELEMENT_TYPE.BUTTON, name='_loadselected',
        value='Load Selected'))

  def _in_participant_list(self, names):
    return any([name.startswith('tdurden.chi') for name in names])
