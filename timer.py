# coding=utf-8
__author__ = 'weiyulan'

import threading
import time


class Timer(object):
    """这是一个可以不断的重复执行一个函数的定时器。"""
    def __init__(self, interval, target, args=(), kwargs={}, repeat_times=-1, start_flag=False):
        """构造函数。

        Keyword arguments:
        interval -- 运行函数的周期。（大于零）
        target -- 要运行的函数。
        args -- 参数（列表）。
        kwargs -- 参数（字典）。
        repeat_times -- 循环次数。（－1为无限循环）
        start_flag -- 初始化的同时是否开始定时器。
        """
        self._interval = 0
        self.interval = interval
        self.interval_lock = threading.Lock()

        if hasattr(target, '__call__') is False:
            raise Exception("function应当为一个函数。")
        self.target = target

        self.repeat_times = repeat_times
        self.repeat_times_lock = threading.Lock()

        self.pause_lock = threading.Lock()

        self.args = args
        self.kwargs = kwargs

        self.thread_handle = threading.Thread(target=self.worker)
        self.thread_handle.setDaemon(True)

        if start_flag is True:
            self.run()

    def run(self):
        """运行计时器。"""
        self.thread_handle.start()

    def worker(self):
        """计时器的工作线程。"""
        while True:
            self.pause_lock.acquire()           # 处理暂停
            self.pause_lock.release()

            with self.repeat_times_lock:
                self.repeat_times -= 1
                if self.repeat_times == -1:
                    return

            self.target(*self.args,           # 执行操作
                        **self.kwargs)

            with self.interval_lock:
                time.sleep(self.interval)

    def pause(self):
        """暂停计时器。"""
        self.pause_lock.acquire()

    def resume(self):
        """恢复计时器。用于暂停后的计时器。"""
        self.pause_lock.release()

    def stop(self):
        """停止计时器。"""
        with self.repeat_times_lock:
            self.repeat_times = 0

    def __del__(self):
        self.stop()

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, value):
        if value > 0.:
            self._interval = value
        else:
            raise ValueError("时间间隔不能小于等于零。")
