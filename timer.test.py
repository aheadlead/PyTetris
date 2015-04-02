__author__ = 'weiyulan'

import time
from timer import Timer


def fn1():
    print "hello, world"


def fn2(para_a, para_b):
    print "hello, " + str(para_a) + " and " + str(para_b)

t1 = Timer(interval=.5, target=fn1, start_flag=True)

t2 = Timer(interval=2, target=fn2, args=['aru', 'ba'])
t2.run()

time.sleep(5)

print "timer t2 has stopped."
t2.stop()

t2 = Timer(interval=1.2, target=fn2, kwargs={"para_b": "hua", "para_a": "ju"}, start_flag=True)

print "timer t1 paused."
t1.pause()

time.sleep(5)

print "timer t1 resumed."
t1.resume()
