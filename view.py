# coding=utf-8

__author__ = 'weiyulan'

from os import system
from math import sqrt
from copy import deepcopy
from sys import stdout, stderr

from blessings import Terminal
import pygame
from pygame.locals import *

from PyKeydown import keyvalue, keydown


class PyTerisViewBase(object):
    def __init__(self):
        """ 启动并开始运行视图。
        """
        self.event_callback = None
        self.map = None
        self.canvas = None
        self.score = None
        self.next_block = None
        self.active_block = None
        self.active_block_position = None
        pass

    def clear_screen(self):
        pass

    def update(self):
        pass

    def begin(self):
        """ 游戏开始时，由 controller 调用，清除游戏结束信息（如果有）。
        """
        pass

    def end(self):
        """ 游戏结束时，由 controller 调用，显示游戏结束信息和分数。
        """
        pass


class PyTerisViewTerminal(PyTerisViewBase):
    """ 用于终端下的 view 。 """
    def __init__(self):
        self.keyDown = keydown.Keydown(self.keydown_callback)
        self.information_bar = ""

        self.keyDown.start()
        self.clear_screen()

    def keydown_callback(self, key_value):
        keymap = {keyvalue.ARROW_UP: "up",
                  keyvalue.ARROW_DOWN: "down",
                  keyvalue.ARROW_RIGHT: "right",
                  keyvalue.ARROW_LEFT: "left",
                  keyvalue.SPACE: "space",
                  keyvalue.S: "s",
                  keyvalue.Q: "q",
                  }
        try:
            self.event_callback(keymap[key_value])
        except KeyError:
            # TODO for debug
            stderr.write("view: term: pressed key not found\n")

    def __del__(self):
        self.keyDown.stop()
        self.clear_screen()

    def clear_screen(self):
        system("clear")

    def begin(self):
        self.information_bar = "PLAYING"

    def end(self):
        stderr.write("view: end: called")
        self.information_bar = "GAME OVER"

    def update(self):
        def find_match_color(_cell):
            # 寻找和 _cell 描述的颜色最接近的终端颜色

            # color 列表采用了 OS X 的自带终端的配色方案
            # Ref: http://en.wikipedia.org/wiki/ANSI_escape_code#Colors
            colors = {"black": (0, 0, 0),
                      "red": (194, 54, 33),
                      "green": (37, 188, 36),
                      "yellow": (173, 173, 39),
                      "blue": (73, 46, 255),
                      "magenta": (211, 56, 211),
                      "cyan": (51, 187, 200),
                      "white": (203, 204, 205)}

            # 差异度按欧几里德距离计算
            best_color_name = "black"
            best_color_distance = sqrt(255**2 + 255**2 + 255**2)

            for name, color in colors.items():
                distance = sqrt(sum([(_cell[i] - color[i]) ** 2 for i in range(3)]))
                if best_color_distance > distance:
                    best_color_name = name
                    best_color_distance = distance
            return best_color_name
            # 算法完毕

        t = Terminal()

        self.clear_screen()

        # 将 active_block 贴到 canvas 上
        if self.active_block is not None:
            self.canvas = deepcopy(self.map.content)
            for y in range(len(self.active_block)):
                for x in range(len(self.active_block[0])):
                    if self.active_block[y][x] is not None:
                        self.canvas[y+self.active_block_position[1]][x+self.active_block_position[0]] = self.active_block[y][x]

        # 输出游戏地图

        # 打印顶部栏杆
        print t.red("     /-------") + t.yellow("TETRIS") + t.red("-------\\")
        # 打印 canvas
        for index, row in enumerate(self.canvas):
            print t.red("     |"),
            for cell in row:
                if cell is not None:
                    color_name = find_match_color(cell)
                    stdout.write(getattr(t, 'red_on_'+color_name)('  '))  # red_on_ 是随便选的
                else:
                    stdout.write('  ')
            print t.red("|"),

            print "     ",

            # 下一个方块
            if 0 < index:
                try:
                    for cell in self.next_block[index-1]:
                        if cell is not None:
                            color_name = find_match_color(cell)
                            stdout.write(getattr(t, 'red_on_'+color_name)('  '))  # red_on_ 是随便选的
                        else:
                            stdout.write('  ')
                except IndexError:
                    pass
            elif 0 == index:
                print "Next",

            print
        # 打印底部栏杆
        print t.red("     \\--------------------/")
        print
        print t.blue(self.information_bar)
        print
        print t.bold_blue(u"     成绩: " + str(self.score))
        print "     PyTetris 2.33"


class PyTetrisViewGUI(PyTerisViewBase):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480), 0, 32)
        self.information_bar = ""

    def __del__(self):
        pygame.quit()

    def clear_screen(self):
        self.screen.fill((255, 255, 255))

    def update(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.event_callback("q")
            elif event.type == KEYDOWN:
                keymap = {K_UP: "up",
                          K_DOWN: "down",
                          K_RIGHT: "right",
                          K_LEFT: "left",
                          K_SPACE: "space",
                          K_s: "s",
                          K_q: "q"}
                try:
                    self.event_callback(keymap[event.key])
                except KeyError, e:
                    stderr.write("view: gui: pressed key not found")

        self.clear_screen()

        map_position = (100, 100)
        map_border_width = 5
        map_border_color = (0, 0, 0)
        map_size = (100, 200)
        cell_size = (10, 10)
        next_block_map_position = (300, 100)
        next_block_map_size = (50, 50)

        map_surface = pygame.Surface(map_size)
        next_block_map_surface = pygame.Surface(next_block_map_size)

        # 画 map 的边框 （实际上是个比 map 大一圈的矩形，随后让 map 来覆盖它）
        pygame.draw.rect(self.screen,
                         map_border_color,
                         pygame.Rect(tuple([value-map_border_width for value in map_position]),
                                     tuple([value+2*map_border_width for value in map_size])),
                         0)

        # 画 map 到 map_surface 上
        map_surface.fill((255, 255, 255))  # 先刷个白底
        for row_index, row in enumerate(self.map):
            for cell_index, cell in enumerate(row):
                if cell is not None:
                    pygame.draw.rect(map_surface, cell,
                                     pygame.Rect((cell_size[0]*cell_index, cell_size[1]*row_index),
                                                 cell_size),
                                     0)

        # 画 active_block 到 map_surface 上
        if self.active_block is not None:
            for y in range(len(self.active_block)):
                for x in range(len(self.active_block[0])):
                    if self.active_block[y][x] is not None:
                        pygame.draw.rect(map_surface, self.active_block[y][x],
                                         pygame.Rect(((self.active_block_position[0]+x)*cell_size[0],
                                                      (self.active_block_position[1]+y)*cell_size[1]),
                                                     cell_size),
                                         0)

        # 画 next_block_map 到 next_block_map_surface 上
        next_block_map_surface.fill((255, 255, 255))  # 刷个白底
        for row_index, row in enumerate(self.next_block):
            for cell_index, cell in enumerate(row):
                if cell is not None:
                    pygame.draw.rect(next_block_map_surface, cell,
                                     pygame.Rect((cell_size[0]*cell_index, cell_size[1]*row_index),
                                                 cell_size),
                                     0)

        # 把 map_surface 贴到 screen 上
        self.screen.blit(map_surface, map_position)

        # 把 next_block_map 贴到 screen 上
        self.screen.blit(next_block_map_surface, next_block_map_position)

        pygame.display.update()

    def begin(self):
        self.information_bar = "PLAYING"

    def end(self):
        self.information_bar = "GAMEOVER"


class PyTetrisViewMulticaster(object):
    """ 使用此类，可以在一次调用 PyTetrisViewBase 的方法的时候，实际调用多个 View 的效果。 """
    def __init__(self):
        self.views = []
        self._event_callback = None
        self._map = None
        self._score = None
        self._next_block = None
        self._active_block = None
        self._active_block_position = None

    def add_view(self, view):
        self.views.append(view)

    def update(self):
        for view in self.views:
            view.update()

    def clear_screen(self):
        for view in self.views:
            view.clear_screen()

    def begin(self):
        for view in self.views:
            view.begin()

    def end(self):
        for view in self.views:
            view.end()

    @property
    def event_callback(self):
        return self._event_callback

    @event_callback.setter
    def event_callback(self, value):
        self._event_callback = value
        for view in self.views:
            view.event_callback = self._event_callback

    @property
    def map(self):
        return self._map

    @map.setter
    def map(self, value):
        self._map = value
        for view in self.views:
            view.map = self._map

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value
        for view in self.views:
            view.score = self._score

    @property
    def next_block(self):
        return self._next_block

    @next_block.setter
    def next_block(self, value):
        self._next_block = value
        for view in self.views:
            view.next_block = self._next_block

    @property
    def active_block(self):
        return self._active_block

    @active_block.setter
    def active_block(self, value):
        self._active_block = value
        for view in self.views:
            view.active_block = self._active_block

    @property
    def active_block_position(self):
        return self._active_block_position

    @active_block_position.setter
    def active_block_position(self, value):
        self._active_block_position = value
        for view in self.views:
            view.active_block_position = self._active_block_position
