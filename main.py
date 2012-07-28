import sys
sys.path.insert(0, "/Library/Frameworks/GStreamer.framework/Versions/0.10/x86_64/lib/python2.7/site-packages/gst-0.10")
sys.path.insert(0, "/Library/Frameworks/GStreamer.framework/Versions/0.10/x86_64/lib/python2.7/site-packages")

import os
import random

import glib
import gobject
import gst

RMS_THRESHOLD = -15
RESOURCES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'res')

def get_alert_file():
    chosen = random.choice(os.listdir(RESOURCES_PATH))
    return os.path.join(RESOURCES_PATH, chosen)


class Detector(object):
    def player_on_eos(self, bus, message):
        print 'feira acabou de tocar. reiniciando detector.'
        self.player.set_state(gst.STATE_NULL)
        self.pipeline.set_state(gst.STATE_PLAYING)

    def play(self):
        self.player = gst.parse_launch("playbin2 uri=file://%s" % get_alert_file())
        self.player_bus = self.player.get_bus()
        self.player_bus.add_signal_watch()
        self.player_bus.connect("message::eos", self.player_on_eos)
        self.player.set_state(gst.STATE_PLAYING)

    def on_feira_detected(self):
        print 'feira detectada'
        self.pipeline.set_state(gst.STATE_NULL)
        self.play()

    def callback(self, bus, message):
        if message.type == gst.MESSAGE_ELEMENT:
            if message.structure.get_name() == "level":
                rms = message.structure["rms"][0]
                if rms > RMS_THRESHOLD:
                    self.on_feira_detected()
        elif message.type == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            loop.quit()

    def start_detector(self):
        self.pipeline = gst.parse_launch("autoaudiosrc ! level ! fakesink")
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self.callback)
        self.pipeline.set_state(gst.STATE_PLAYING)


def main():
    d = Detector()
    d.start_detector()

    gobject.threads_init()
    loop = glib.MainLoop()
    loop.run()

if __name__ == '__main__':
    main()
