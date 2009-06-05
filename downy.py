#!/usr/bin/python2.5

import logging

from mercurial import commands
from api import document


class Downy(object):
  def __init__(self, repo):
    self.repo = repo
    self.tracked_files = []

  def on_wavelet_blip_created(self, props, context):
    logging.info('blip created')
    logging.info(props)
    logging.info(context)

  def on_wavelet_self_added(self, props, context):
    logging.info('Added to wave.')
    self.announce(context)

  def on_form_button_clicked(self, props, context):
    logging.info('button clicked')
    button_name = props['button']
    if button_name.startswith('load_'):
      self.load_file(context, button_name[5:])
    elif button_name == 'loadselected':
      # TODO
      logging.info('load selected')

  def on_blip_submitted(self, props, context):
    blip = context.GetBlipById(props['blipId'])
    if not blip:
      logging.error('Unknown blip ID %s submitted.', props['blipId'])
    self.sync_file(blip)

  def _get_annotations(self, blip):
    return dict((ann.name, ann) for ann in blip._data.annotations)

  def tip(self):
    tip_ctx = self.repo[len(self.repo) - 1]
    return '%s:%s' % (tip_ctx.rev(), tip_ctx.hex()[:10])

  def sync_file(self, blip):
    file_name_ann = self._get_annotations(blip).get('downy-file-name')
    if not file_name_ann:
      logging.info('Ignoring blip %s', blip.GetId())
      return
    file_name = file_name_ann.value
    contents = blip.GetDocument().GetText()
    if contents.startswith(file_name + '\n\n'):
      contents = contents[len(file_name) + 2:]
    self.repo.wwrite(file_name, contents, '')

  def load_file(self, context, file_name):
    # TODO: check if child blip for file already exists
    stat_blip = self.find_status_blip(context)
    if not stat_blip:
      logging.info('Could not find status blip')
      return

    # Find insertion point
    parent_doc = stat_blip.GetDocument()
    file_name_loc = parent_doc.GetText().find(file_name)
    if file_name_loc == -1:
      logging.info('Could not find insertion point for %s', file_name)
      return
    # TODO: also account for buttons next to file name
    insert_point = file_name_loc + len(file_name)

    new_blip = parent_doc.InsertInlineBlip(insert_point)
    doc = new_blip.GetDocument()
    doc.AnnotateDocument('downy-file-name', file_name)
    file_text = self.repo.wread(file_name)
    doc.AppendText(file_name + '\n\n') # TODO: add <hr> here instead
    doc.AppendText(file_text)

  def command(self, cmd):
    cmd_fn = getattr(commands, cmd)
    cmd_fn(self.repo.ui, self.repo)

  def announce(self, context):
    new_blip = context.GetRootWavelet().CreateBlip()
    #new_blip = self.root_blip().GetDocument().AppendInlineBlip()
    doc = new_blip.GetDocument()
    self.status(doc)

  def find_status_blip(self, context):
    for blip in context.GetBlips():
      if 'downy-stat' in self._get_annotations(blip):
        return blip

  def status(self, doc):
    doc.AppendText('Mercurial repository at %s\n' % self.repo.root)
    doc.AppendText('Revision %s\n' % self.tip())
    doc.AnnotateDocument('downy-stat', '1')
    (modified, added, removed, deleted, _, _, clean) = self.repo.status(
      clean=True)
    logging.info('%d modified, %d clean',
                 len(modified), len(clean))
    for file_name in clean:
      doc.AppendElement(document.FormElement(
          document.ELEMENT_TYPE.CHECK, name='sel_' + file_name))
      doc.AppendText(file_name + ' ')
      doc.AppendElement(document.FormElement(
          document.ELEMENT_TYPE.BUTTON, name='load_' + file_name, label='Load',
          value='Load'))
      doc.AppendText('\n')
    doc.AppendElement(document.FormElement(
        document.ELEMENT_TYPE.BUTTON, name='loadselected',
        value='Load Selected'))

  def _in_participant_list(self, names):
    return any([name.startswith('tdurden.chi') for name in names])
