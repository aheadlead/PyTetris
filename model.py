#!/usr/bin/env python
# coding=utf-8

__author__ = 'weiyulan'

from exception import *
from timer import Timer
from random import choice, randint
from threading import Thread, Lock
from sys import stderr
from copy import deepcopy

# 难度常量
#
# 难度与方块下落的间隔时间有关系，也与分数计算有关系。
DIFFICULTY = {'so easy': {'interval': 3, 'score_factor': 0.5},
              'easy':    {'interval': 2, 'score_factor': 1},
              'normal':  {'interval': 1, 'score_factor': 1.5},
              'hard':    {'interval': .5, 'score_factor': 2},
              'crazy':   {'interval': .25, 'score_factor': 2.5}}


class Block(object):
    def __init__(self, content):
        self._content = content

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        # TODO for debug
        if len(self._content) > 5:
            stderr.write("model: Block: member content has been changed\n")
        self._content = value

    def rotate(self):
        """顺时针旋转当前方块。

            旋转前
           [[0, 1, 1],
            [1, 1, 0]]
            旋转后
           [[1, 0],
            [1, 1],
            [0, 1]]"""
        new_content = [[] for i in range(len(self.content[0]))]
        for a in self.content:
            for index, b in enumerate(a):
                new_content[index].append(b)
        for new_row in new_content:
            new_row.reverse()
        self.content = new_content

    def is_conflicting(self, map_, position):
        """给定一个棋盘 map_ ，判断方块放在 position 所描述的位置上是否会引起冲突。
           引起冲突则不能放在这个位置。
        :param map_: 给定的棋盘。
        :param position: 描述方块位于棋盘的位置。
        :type position: 二维元组
        :returns: 是否能放在 position 所描述的位置上。
        :rtype: Bool
        """

        map_size = (len(map_[0]), len(map_))  # map_ 的宽和高
        self_size = (len(self.content[0]), len(self.content))
        # 判断是否超出棋盘
        if position[0] < 0 or position[1] < 0:
            return True
        if position[0] > map_size[0]-self_size[0] or \
           position[1] > map_size[1]-self_size[1]:
            return True
        # 判断是否覆盖棋盘上已有的格子
        for row_index, row in enumerate(self.content):
            for cell_index, cell in enumerate(row):
                if cell is not None and \
                   map_[position[1]+row_index][position[0]+cell_index] is not None:
                    return True

        return False

    def __len__(self):
        return len(self.content)

    def __getitem__(self, item):
        return self.content[item]


class PyTetrisModel(object):

    blockList = {"I": Block([[1, 1, 1, 1]]),

                 "J": Block([[1, 0, 0],
                             [1, 1, 1]]),

                 "L": Block([[0, 0, 1],
                             [1, 1, 1]]),

                 "O": Block([[1, 1],
                             [1, 1]]),

                 "S": Block([[0, 1, 1],
                             [1, 1, 0]]),

                 "T": Block([[0, 1, 0],
                             [1, 1, 1]]),

                 "Z": Block([[1, 1, 0],
                             [0, 1, 1]])}

    blockColorList = [(0, 0, 0),
                      (194, 54, 33),
                      (37, 188, 36),
                      (173, 173, 39),
                      (73, 46, 255),
                      (211, 56, 211),
                      (51, 187, 200),
                      (203, 204, 205)]

    def __init__(self):
        self._state = "initialized"

        self._difficulty = 'crazy'

        # map 以左上角为原点，从左往右是 x 正方向，从上往下是 y 正方向。
        #
        #   (0, 0)  (1, 0)  (2, 0)  ...     (9, 0)
        #   (0, 1)  (1, 1)  (2, 1)  ...     (9, 1)
        #   ...     ...     ...     ...     ...
        #   (0, 19) (1, 19) (2, 19) ...     (9, 19)
        #
        self.map = Block([[None]*10 for i in range(20)])

        self.timer = None

        self.next_block = Block([[]])
        self.active_block = Block([[]])
        self.active_block_position = (0, 0)

        self.gameover_callback = None

        # 在按左右方向键时，可能会和正在对自身进行访问的 tick 函数造成的冲突。
        # 所以这儿准备一个 Lock 。
        self.lock = Lock()

        self.score = 0

    @property
    def difficulty(self):
        return self._difficulty

    @difficulty.setter
    def difficulty(self, value):
        if self.state == "initialized":
            if value in DIFFICULTY.keys():
                self.difficulty = value
            else:
                raise NoSuchDifficulty
        else:
            raise WrongState

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        stderr.write("model: set state to " + str(value) + "\n")
        self._state = value

    def start(self):
        if self.state == "initialized":
            self.state = "start"
            self.timer = Timer(target=self.tick,
                               interval=DIFFICULTY[self.difficulty]['interval'])
            self.timer.run()
        else:
            stderr.write("model: the state is not initialized, can not start the game")

    def pause(self):
        self.timer.pause()

    def resume(self):
        self.timer.resume()

    def press_arrow_key(self, direction):
        if self.state == "falling":
            with self.lock:
                class Apple(BaseException):
                    def __init__(self):
                        pass
                try:
                    self.active_block_position[0] -= 1 if direction == "left" else -1  # 移一格
                    if self.active_block.is_conflicting(map_=self.map,
                                                        position=self.active_block_position) is True:
                        raise Apple()
                except Apple:
                    # 不能移动
                    self.active_block_position[0] += 1 if direction == "left" else -1  # 回滚更改
                    return

    def press_rotate_key(self):
        if self.state == "falling":
            with self.lock:
                self.active_block.rotate()
                if self.active_block.is_conflicting(self.map, self.active_block_position) is True:
                    self.active_block.rotate()
                    self.active_block.rotate()
                    self.active_block.rotate()

    def press_hard_drop(self):
        if self.state == "falling":
            with self.lock:
                while 1:
                    self.active_block_position[1] += 1
                    if self.active_block.is_conflicting(self.map, self.active_block_position) is True:
                        self.active_block_position[1] -= 1
                        break

    def tick(self):
        # TODO for debug
        stderr.write("model: ticking!!! state: " + self.state + "\n")

        def start():  # 开始状态
            self.map = Block([[None]*10 for i in xrange(20)])  # 清空地图
            self.next_block = self.choice_a_block()  # 下一个方块
            self.state = "new_block"
            return

        def new_block():  # 出现新方块
            self.active_block_position = [3, 0]  # 方块首次出现在地图的(3, 0)点
            # 每个方块的锚点都在于左上角，如同 map 的原点一样。

            self.active_block = self.next_block
            self.next_block = self.choice_a_block()

            # 判断是否和 map 上的碰撞，若有碰撞则游戏结束
            if self.active_block.is_conflicting(map_=self.map,
                                                position=self.active_block_position) is True:
                self.state = "gameover"
                return

            # 判断最高的一行有没有方块覆盖，有则游戏结束。
            for cell in self.map[0]:
                if cell is not None:
                    self.state = "gameover"
                    return

            self.state = "falling"

        def falling():  # 下落
            class Apple(BaseException):
                def __init__(self):
                    pass
            try:
                stderr.write("model: try to fall block (" + str(self.active_block_position) + ")\n")
                self.active_block_position[1] += 1  # 下落一格
                if self.active_block.is_conflicting(map_=self.map,
                                                    position=self.active_block_position) is True:
                    raise Apple()
            except Apple:
                # 不能再下落了
                stderr.write("model: falling: stop falling\n")
                self.active_block_position[1] -= 1  # 回滚更改

                # 将 active_block 写入 map
                for y in range(len(self.active_block)):
                    for x in range(len(self.active_block[0])):
                        if self.active_block[y][x] is not None:
                            self.map[y+self.active_block_position[1]][x+self.active_block_position[0]] = self.active_block[y][x]

                self.state = "line_clear"
            else:
                self.state = "falling"

        def line_clear():  # 行消除
            def tmp_check(row):  # 检查行 row 是不是存在空白的格子
                try:
                    row.index(None)
                    return True  # 存在空白的格子
                except ValueError:
                    return False  # 不存在空白的格子，可以消除

            self.map.content = filter(tmp_check, self.map.content)  # 清除掉可以清除的行

            clear_row_n = 20 - len(self.map.content)  # 如果有行消除要统计消除的行数量
            self.map.content = [[None]*10 for i in range(clear_row_n)] + self.map.content  # 消除了多少行就在顶部补上多少空行
            # 下面这一行的float那儿是为了应付PEP8的检查（莫名其妙的错误也是醉了）
            score_delta = float(DIFFICULTY[self.difficulty]['score_factor']) * \
                int(2**(clear_row_n-1)) * 10  # 分数计算（int那儿是为了应对没有行消除的情况）

            self.score += score_delta

            stderr.write("model: line_clear: score_delta = " + str(score_delta) + "\n")

            self.state = "new_block"

        def gameover():  # 游戏结束状态
            self.timer.stop()

            if hasattr(self.gameover_callback, '__call__') is True:
                gameover_thread = Thread(target=self.gameover_callback)
                gameover_thread.setDaemon(True)
                gameover_thread.run()

            self.state = "stopped"

        with self.lock:
            fsm = {"start": start,
                   "new_block": new_block,
                   "falling": falling,
                   "line_clear": line_clear,
                   "gameover": gameover}
            if self.state in fsm.keys():
                fsm[self.state]()
            else:
                raise WrongState("状态 " + str(self.state) + " 不应该出现在 tick 过程中。")

    @staticmethod
    def choice_a_block():
        """choice_a_block() -> String

        :rtype : String
        随机返回一个方块。"""
        block = deepcopy(choice(PyTetrisModel.blockList.values()))  # 随机选取方块

        # TODO for debug
        stderr.write("model: choice_a_block: step 1: " + str(block.content) + "\n")

        for i in range(randint(0, 3)):  # 随机旋转方块
            block.rotate()

        color = choice(PyTetrisModel.blockColorList)  # 随机选择颜色
        for index, row in enumerate(block.content):
            block.content[index] = [color if item == 1 else None for item in row]

        # TODO for debug
        stderr.write("model: choice_a_block: step 2: " + str(block.content) + "\n")

        return block
