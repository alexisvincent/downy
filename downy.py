#!/usr/bin/python2.4

from api import robot
from api import events


class Downy(object):
  def on_blip_created(self, properties, context):
    print 'blip created'
    print properties
    print context

  def on_participants_changed(self, properties, context):
    print 'somebody was added'
    print properties['participantsAdded']
    #if self._in_participant_list(properties['participantsAdded']):
    #


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
