#!/usr/bin/env python
import sys
sys.path.insert(0, "/Library/Frameworks/GStreamer.framework/Versions/0.10/x86_64/lib/python2.7/site-packages/gst-0.10")
sys.path.insert(0, "/Library/Frameworks/GStreamer.framework/Versions/0.10/x86_64/lib/python2.7/site-packages")

import os
from optparse import OptionParser
import random

import glib
import gobject

RESOURCES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'res')

def get_alert_file():
    chosen = random.choice(os.listdir(RESOURCES_PATH))
    return os.path.join(RESOURCES_PATH, chosen)


class Detector(object):
    def __init__(self, rms_threshold):
        self.rms_threshold = rms_threshold
        self.pipeline = gst.parse_launch("autoaudiosrc ! level ! fakesink")
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.detector_callback)
        self.start_detector()

    def start_detector(self):
        self.pipeline.set_state(gst.STATE_PLAYING)

    def stop_detector(self):
        self.pipeline.set_state(gst.STATE_NULL)

    def detector_callback(self, bus, message):
        if message.type == gst.MESSAGE_ELEMENT:
            if message.structure.get_name() == "level":
                self.level_measured(message.structure)
        elif message.type == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            loop.quit()

    def level_measured(self, meausure):
        rms = meausure["rms"][0]
        if rms > self.rms_threshold:
            self.feira_detected()

    def feira_detected(self):
        print 'feira detectada'
        self.stop_detector()
        self.play_alert()

    def play_alert(self):
        self.player = gst.parse_launch("playbin2 uri=file://%s" % get_alert_file())
        player_bus = self.player.get_bus()
        player_bus.add_signal_watch()
        player_bus.connect("message::eos", self.alert_ended)
        self.player.set_state(gst.STATE_PLAYING)

    def alert_ended(self, bus, message):
        print 'feira acabou de tocar. reiniciando detector.'
        self.player.set_state(gst.STATE_NULL)
        self.start_detector()

def parse_options():
    parser = OptionParser()
    parser.add_option("-r", "--rms", type="int", dest="rms_threshold",
        default=-15,
        help="set RMS threshold")
    return parser.parse_args()

def start_loop():
    gobject.threads_init()
    loop = glib.MainLoop()
    loop.run()

def main():
    d = Detector(rms_threshold=options.rms_threshold)
    start_loop()

if __name__ == '__main__':
    (options, args) = parse_options()
    import gst # We don't import gst before this point because
               # it messes with optparse
    main()
