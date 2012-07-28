import os
import sys
sys.path.insert(0, "/Library/Frameworks/GStreamer.framework/Versions/0.10/x86_64/lib/python2.7/site-packages/gst-0.10")
sys.path.insert(0, "/Library/Frameworks/GStreamer.framework/Versions/0.10/x86_64/lib/python2.7/site-packages")
import glib, gobject
import gst

RMS_THRESHOLD = -10
MP3_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'res', 'feira_da_fruta.mp3')

def player_on_eos(bus, message):
    print 'feira acabou de tocar. reiniciando detector.'
    player.set_state(gst.STATE_NULL)
    pipeline.set_state(gst.STATE_PLAYING)

def play():
    global player, player_bus
    player = gst.parse_launch("playbin2 uri=file://%s" % MP3_FILE)
    player_bus = player.get_bus()
    player_bus.add_signal_watch()
    player_bus.connect("message::eos", player_on_eos)
    player.set_state(gst.STATE_PLAYING)

def on_feira_detected():
    print 'feira'
    pipeline.set_state(gst.STATE_NULL)
    play()

def callback(bus, message):
    if message.type == gst.MESSAGE_ELEMENT:
        if message.structure.get_name() == "level":
            rms = message.structure["rms"][0]
            if rms > RMS_THRESHOLD:
                on_feira_detected()
    elif message.type == gst.MESSAGE_ERROR:
        err, debug = message.parse_error()
        print "Error: %s" % err, debug
        loop.quit()

def start_detector():
    global pipeline, bus
    pipeline = gst.parse_launch("autoaudiosrc ! level ! fakesink")
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", callback)
    pipeline.set_state(gst.STATE_PLAYING)


def main():
    start_detector()
    gobject.threads_init()
    loop = glib.MainLoop()
    loop.run()

if __name__ == '__main__':
    main()
