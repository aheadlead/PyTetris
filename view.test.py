# coding=utf-8
__author__ = 'weiyulan'

import view
from Queue import Queue
from time import sleep


def terminal_test():
    q = Queue()
    current_view = view.PyTerisViewTerminal()
    current_view.event_callback = q.put

    current_view.start()

    test_map = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
                [0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
                [0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
                [0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
                [0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
                [0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
                [0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
                [0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
                [0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
                [0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
                [0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
                [0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
                [0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
                [0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
                [0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
                [0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
                [0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
                [0, 1, 0, 0, 0, 0, 0, 1, 0, 1]]

    test_next_block = [[0, 0, 1],
                       [1, 1, 1]]

    test_active_block = [[0, 1, 0],
                         [1, 1, 1]]
    test_active_block_position = (3, 8)

    for i in range(len(test_active_block)):
        for j in range(len(test_active_block[i])):
            if test_active_block[i][j] == 1:
                test_active_block[i][j] = (255, 0, 0)
            else:
                test_active_block[i][j] = None

    for i in range(len(test_next_block)):
        for j in range(len(test_next_block[i])):
            if test_next_block[i][j] == 1:
                test_next_block[i][j] = (127, 127, 127)
            else:
                test_next_block[i][j] = None

    for i in range(len(test_map)):
        for j in range(len(test_map[i])):
            if test_map[i][j] == 1:
                test_map[i][j] = (255, 255, 255)
            else:
                test_map[i][j] = None


    test_score = 233

    current_view.map = test_map
    current_view.score = test_score
    current_view.next_block = test_next_block
    current_view.active_block = test_active_block
    current_view.active_block_position = test_active_block_position

    while 1:
        while q.empty() is False:
            print q.get()

        current_view.update()
        sleep(0.05)

terminal_test()