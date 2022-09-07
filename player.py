"""
该文件修改自 https://github.com/PyPigStudio/PyPigPlayer。
"""

import time

import mutagen.mp3
import pygame


class Player:
    """
    音乐播放器。
    """

    delay: float = 0.02
    fadeout: float = 0.5
    file: str = ''
    length: float = 0
    offset: float = 0
    opening: bool = False
    playing: bool = False
    precision: float = 0.1
    rate: float = 1
    ready: bool = False

    def __init__(self) -> None:
        pygame.mixer.init()

    def close(self) -> None:
        """
        关闭正在播放的文件。
        """
        pygame.mixer.music.unload()
        self.file = ''
        self.playing = False
        self.ready = False
        self.length = 0

    def get_pos(self) -> float:
        """
        获取当前播放位置 (单位:秒)。
        """
        return pygame.mixer.music.get_pos() / 1000 + self.offset if self.ready else 0

    def get_prog(self) -> float:
        """
        获取当前播放进度。
        """
        return self.get_pos() / self.length if self.length else 0

    def get_text(self) -> str:
        """
        获取进度条文字。
        """
        return '/'.join(map((lambda s: '{:0>2d}:{:0>2d}'.format(
            *divmod(int(s), 60))), (self.get_pos(), self.length)))

    def open(self, file: str) -> None:
        """
        打开文件。
        """
        if not self.opening:
            self.opening = True
            pygame.mixer.music.load(file)
            self.file = file
            self.offset = 0

            # 获取 Pygame 音乐时长以计算比率
            def check(length):
                pygame.mixer.music.play()
                pygame.mixer.music.set_pos(length)
                time.sleep(self.delay)
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                    return True
                else:
                    return False

            # 设置音量与结束事件
            vol_bak = pygame.mixer.music.get_volume()
            pygame.mixer.music.set_volume(0)
            pygame.mixer.music.set_endevent(0)

            l = 0
            r = 1.0
            # 倍增求上界
            while check(r):
                l = r
                r *= 2
            # 二分求时长
            while l + self.precision < r:
                mid = (l + r) / 2
                if check(mid):
                    l = mid
                else:
                    r = mid

            self.length = mutagen.mp3.MP3(self.file).info.length
            self.rate = l / self.length

            # 还原音量与结束事件
            pygame.mixer.music.set_volume(vol_bak)
            pygame.mixer.music.set_endevent(pygame.USEREVENT)
            pygame.mixer.music.play()
            pygame.mixer.music.pause()
            self.playing = False
            self.ready = True
            self.opening = False

    def pause(self) -> None:
        """
        暂停。
        """
        if self.ready:
            self.playing = False
            pos_bak = self.get_pos()
            pygame.mixer.music.fadeout(int(self.fadeout*1000))
            time.sleep(self.fadeout)
            pygame.mixer.music.play()
            pygame.mixer.music.pause()
            self.set_pos(pos_bak+self.fadeout)

    def play(self) -> None:
        """
        播放。
        """
        if self.ready:
            pygame.mixer.music.unpause()
            self.playing = True

    def replay(self) -> None:
        """
        从头播放。
        """
        pygame.mixer.music.stop()
        self.offset = 0
        pygame.mixer.music.play()
        self.playing = True

    def set_pos(self, pos: float) -> None:
        """
        设置当前播放位置 (单位:秒)。
        """
        if self.ready:
            pos = min(max(pos, 0), self.length)
            pygame.mixer.music.set_pos(pos * self.rate)
            self.offset = pos - pygame.mixer.music.get_pos() / 1000

    def set_prog(self, prog: float) -> float:
        """
        设置当前播放进度。
        """
        self.set_pos(self.length * prog)
