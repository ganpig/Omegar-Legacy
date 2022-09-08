import os
import sys

import pygame

pygame.init()

"""
主程序相关
"""

# 窗口标题
WINDOW_TITLE = 'Omegar v0.1'

# 窗口大小
WINDOW_SIZE = (1000, 600)

# 分割线位置
SPLIT_LINE = 600

# 配置文件名称
CONFIG_FILE = 'config.ini'

# 资源文件路径
try:
    RESOURCES = sys._MEIPASS
except:
    RESOURCES = '.'


def get_res(*args):
    """
    获取资源文件路径。
    """
    return os.path.join(RESOURCES, *args)


# 字体大小
FONT_SIZE = [20, 25, 30, 35]

# 字体列表
FONT_LIST = [
    'FZFWQingYinTiJWL.ttf',
    'CascadiaCode.ttf'
]

FONTS = []
for font in FONT_LIST:
    FONTS.append([pygame.font.Font(get_res('fonts', font), size)
                 for size in FONT_SIZE])

# 图标名称和大小
ICON_INFO: dict = {
    'add':      (40, 40),
    'change':   (65, 30),
    'crystal':  (20, 20),
    'go':       (40, 40),
    'help':     (20, 20),
    'pause':    (40, 40),
    'play':     (40, 40),
    'return':   (50, 50),
    'set':      (65, 30),
    'settings': (50, 50),
    'warning':  (20, 20)
}

ICONS = {}
for name in ICON_INFO:
    ICONS[name] = pygame.transform.scale(pygame.image.load(
        get_res('icons', name+'.png')), ICON_INFO[name])

# 页面名称
PAGE_NAME = {
    'home':         '欢迎来到 Omegar',
    'pick_beats':   '采拍',
    'edit':         '谱面编辑',
    'settings':     '设置'
}


"""
工程相关
"""

# 默认判定线初始位置
DEFAULT_LINE_INITIAL_POSITION = 800


"""
音乐播放相关
"""

# 检验 pygame.mixer.music 是否处于播放状态前的等待秒数
MUSIC_CHECK_DELAY = 0.02

# 二分求时长的精确秒数
MUSIC_CHECK_ACCURACY = 0.1

# 暂停时的淡出时长
MUSIC_FADEOUT_TIME = 0.5


"""
OMGC 相关
"""

# 可见区域边界
TOP_EDGE = 0
BOTTOM_EDGE = 1000

# 提前激活 note 的秒数
PREACTIVATING_TIME = 1.0

# 指令列表
ADD_NOTE = 0x01
CHANGE_NOTE_POS = 0x02
CHANGE_NOTE_TRACK = 0x03
ACTIVATE_NOTE = 0x04
CHANGE_LINE_POS = 0x10

# 用 2 的整数次幂表示 note 属性以便通过加法运算合并属性
NOTE_PROPERTIES = [
    ('property_1', 1 << 0),
    ('property_2', 1 << 1),
    ('property_3', 1 << 2),
    ('property_4', 1 << 3)
]

# 缓动类型
LINEAR_SLOW_MOVING = 0x01
SIN_SLOW_MOVING = 0x02

# 写入格式
WRITING_FORMATS = {int: '>i', float: '>f'}
