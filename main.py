import sys
sys.path.insert(0, "/Library/Frameworks/GStreamer.framework/Versions/0.10/x86_64/lib/python2.7/site-packages/gst-0.10")
sys.path.insert(0, "/Library/Frameworks/GStreamer.framework/Versions/0.10/x86_64/lib/python2.7/site-packages")
import glib, gobject
import gst

RMS_THRESHOLD = -10
MP3_FILE = "file:///Users/juarez.bochi/dev/personal/feiradetector/res/feira_da_fruta.mp3"

def play():
    player = gst.parse_launch("playbin2 uri=%s" % MP3_FILE)
    player.set_state(gst.STATE_PLAYING)
    pipeline.set_state(gst.STATE_NULL)

def on_feira_detected():
    print 'feira'
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

pipeline = gst.parse_launch("autoaudiosrc ! level ! fakesink")
bus = pipeline.get_bus()
bus.add_signal_watch()
bus.connect("message", callback)
pipeline.set_state(gst.STATE_PLAYING)

gobject.threads_init()
loop = glib.MainLoop()
loop.run()

pipeline.set_state(gst.STATE_NULL)
