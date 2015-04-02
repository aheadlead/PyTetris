__author__ = 'weiyulan'

import keydown
import keyvalue
import Queue

l = Queue.Queue()
monitor = keydown.Keydown(l.put)
monitor.start()

while 1:
    kv = l.get()
    if kv == keyvalue.ARROW_UP:
        print "ARROW_UP"
    elif kv == keyvalue.ARROW_DOWN:
        print "ARROW_DOWN"
    elif kv == keyvalue.ARROW_LEFT:
        print "ARROW_LEFT"
    elif kv == keyvalue.ARROW_RIGHT:
        print "ARROW_RIGHT"
    elif kv == keyvalue.Q_SHIFT:
        print "QUIT"
        break

