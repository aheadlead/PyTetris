#!/usr/bin/env python
# coding=utf-8
from Queue import Queue

__author__ = 'weiyulan'

from view import *
from model import *
from time import time, sleep
from Queue import Queue


class PyTerisController(object):

    framerate_limit = 10

    def __init__(self, view, model):
        """
        :type view: PyTetrisViewBase 的子类
        :param view: 视图
        :type model: PyTetrisModel
        :param model: 模型
        :raise Exception: 异常。
        """
        self.view = view
        self.model = model

        self.previous_timestamp = 0
        self.timestamp = 0

        self.event_from_view = Queue()

    def gameover_callback(self):
        self.view.end()

    def run(self):
        self.timestamp = time()

        self.view.clear_screen()

        while True:
            self.view.map = self.model.map
            self.view.score = self.model.score
            self.view.next_block = self.model.next_block
            self.view.active_block = self.model.active_block
            self.view.active_block_position = self.model.active_block_position

            while self.event_from_view.empty() is False:
                event = self.event_from_view.get()
                stderr.write("controller: get event \"" + event + "\"\n")
                if event == "up":
                    self.model.press_rotate_key()
                elif event == "left":
                    self.model.press_arrow_key("left")
                elif event == "right":
                    self.model.press_arrow_key("right")
                elif event == "down" or event == "space":
                    self.model.press_hard_drop()
                elif event == "s":
                    self.model.start()
                    self.view.begin()
                elif event == "q":
                    exit()

            self.view.update()

            # TODO for debug (disabled)
            # stderr.write("controller: redraw the view\n")

            self.previous_timestamp = self.timestamp
            self.timestamp = time()
            wait_interval = 1.0/self.framerate_limit - (self.timestamp-self.previous_timestamp)
            if wait_interval < 0:
                # 掉帧
                wait_interval = 0
            print wait_interval
            sleep(wait_interval)


if __name__ == "__main__":
    # TODO for debug
    stderr.write('-'*40 + '\n')

    current_model = PyTetrisModel()

    current_view = PyTetrisViewMulticaster()
    current_view.add_view(PyTerisViewTerminal())
    current_view.add_view(PyTetrisViewGUI())

    current_controller = PyTerisController(view=current_view, model=current_model)
    current_view.event_callback = current_controller.event_from_view.put

    current_controller.run()
