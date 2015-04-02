# coding=utf-8
__author__ = 'weiyulan'

from threading import Thread
import termios
import fcntl
import sys
import os
from select import select
from time import sleep

import keyvalue


class Keydown(object):
    def __init__(self, callback):
        self.callback = callback
        self.oldflags = None
        self.oldterm = None
        self.daemon_thread = Thread(target=self.daemon)
        self.daemon_thread.setDaemon(True)
        self.fsm = {}
        self.state = self.fsm
        self.stop_flag = False
        # 从 keyvalue 里面的键值建立自动机
        # 这里使用了 Python 自省的特性
        for key in dir(keyvalue):
            if key[:2] == "__":  # 跳过一些变量，如 __author__ 、 __builtins__ 等。
                return
            last_pointer = None
            pointer = self.fsm
            # print '$' + str(getattr(keyvalue, key))
            value = None
            for value in getattr(keyvalue, key):
                if value not in pointer:
                    pointer[value] = {}
                last_pointer = pointer
                pointer = pointer[value]
                # print '#'+str(self.fsm)
            last_pointer[value] = getattr(keyvalue, key)
            # print '*' + str(self.fsm)

    def start(self):
        self.daemon_thread.start()

    def daemon(self):
        fd = sys.stdin.fileno()

        self.oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        self.oldflags = fcntl.fcntl(fd, fcntl.F_GETFL, 0)
        fcntl.fcntl(fd, fcntl.F_SETFL, self.oldflags | os.O_NONBLOCK)

        while 1:
            if self.stop_flag is True:
                self.stop_flag = False
                break
            try:
                while 1:
                    c = sys.stdin.read(1)
                    print ord(c)
                    if isinstance(self.state, dict):
                        if ord(c) in self.state:
                            # print '-> ', ord(c)
                            self.state = self.state[ord(c)]
                        else:
                            # 不支持此按键
                            # print 'no support'
                            self.state = self.fsm
                    # print self.state
                    if isinstance(self.state, tuple):
                        # print "hehe"
                        if not hasattr(self.callback, '__call__'):
                            raise Exception("回调函数不能被调用。")
                        self.callback(self.state)
                        self.state = self.fsm
                        break
            except IOError:
                pass

    def stop(self):
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
        self.stop_flag = True
