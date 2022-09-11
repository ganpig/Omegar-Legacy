import os
import sys

import pygame

pygame.init()

"""
程序 UI
"""
# 窗口标题
WINDOW_TITLE = 'Omegar v0.1'

# 窗口大小
WINDOW_SIZE = (1000, 600)

# 分割线位置
SPLIT_LINE = 600

# 滑块大小
SLIDER_BUTTON_SIZE = 20

# 消息显示时间
MSG_SHOW_TIME = 3

# 消息动画时间
MSG_ANIMATION_TIME = 0.5

# 消息栏高度
MSG_HEIGHT = 50

# 配置文件名称
CONFIG_FILE = 'Omegar.ini'

# 最近项目文件名称
RECENT_FILE = 'Recent.pkl'

# 资源文件路径
try:
    RES_DIR = sys._MEIPASS
except:
    RES_DIR = '.'


def validate_filename(filename: str) -> str:
    """
    文件名合法化。
    """
    for i in '\\/:*?"<>|= ':
        filename = filename.replace(i, '_')
    return filename


def get_res(name: str) -> str:
    """
    获取资源文件路径。
    """
    return os.path.join(RES_DIR, 'res', name)


# 字体列表
FONTS = [pygame.font.Font(get_res('FZFWQingYinTiJWL.ttf'), size)
         for size in range(18, 42, 6)]

# 图标名称和大小
ICON_INFO: dict = {
    'add':          (40, 40),
    'change':       (65, 30),
    'crystal':      (SLIDER_BUTTON_SIZE,)*2,
    'go':           (40, 40),
    'green_beat':   (30, 30),
    'help':         (20, 20),
    'orange_beat':  (30, 30),
    'pause':        (40, 40),
    'play':         (40, 40),
    'return':       (50, 50),
    'set':          (65, 30),
    'settings':     (50, 50),
    'warning':      (SLIDER_BUTTON_SIZE,)*2
}

ICONS = {}
for name in ICON_INFO:
    ICONS[name] = pygame.transform.scale(pygame.image.load(
        get_res(name+'.png')), ICON_INFO[name])

# 页面名称
PAGE_NAME = {
    'home':         '欢迎使用 Omegar',
    'pick_beats':   '采拍',
    'edit':         '谱面编辑',
    'settings':     '设置'
}


"""
快捷键
"""
CTRL = 0x01
ALT = 0x02


"""
采拍
"""
# 采拍时拍子图标每秒钟行走的像素数
PICK_BEAT_SPEED = 100

# 自动修正时同组拍子所允许的最大方差
AUTO_CORRECT_MAX_VARIANCE = 0.01

# 默认判定线初始位置
DEFAULT_LINE_INITIAL_POSITION = 800


"""
播放音乐
"""
# 检验 pygame.mixer.music 是否处于播放状态前的等待秒数
MUSIC_CHECK_DELAY = 0.02

# 二分求时长的精确秒数
MUSIC_CHECK_ACCURACY = 0.1


"""
导出工程
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
