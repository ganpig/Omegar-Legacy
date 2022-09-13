import time

import mutagen.mp3
import pygame

from common import *


class Player:
    file: str = ''
    length: float = 0
    offset: float = 0
    rate: float = 1
    opening: bool = False
    playing: bool = False
    ready: bool = False

    def __init__(self) -> None:
        pygame.mixer.init()
        pygame.mixer.music.set_endevent(USEREVENT)

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
                time.sleep(MUSIC_CHECK_DELAY)
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
            while l + MUSIC_CHECK_ACCURACY < r:
                mid = (l + r) / 2
                if check(mid):
                    l = mid
                else:
                    r = mid

            self.length = mutagen.mp3.MP3(self.file).info.length
            self.rate = l / self.length

            # 还原音量与结束事件
            pygame.mixer.music.set_volume(vol_bak)
            pygame.mixer.music.set_endevent(USEREVENT)
            pygame.mixer.music.play()
            pygame.mixer.music.pause()
            self.playing = False
            self.ready = True
            self.opening = False

    def close(self) -> None:
        """
        关闭正在播放的文件。
        """
        pygame.mixer.music.unload()
        self.file = ''
        self.playing = False
        self.ready = False
        self.length = 0

    def play(self) -> None:
        """
        播放。
        """
        if self.ready:
            pygame.mixer.music.unpause()
            self.playing = True

    def pause(self) -> None:
        """
        暂停。
        """
        if self.ready:
            self.playing = False
            pygame.mixer.music.pause()

    def replay(self) -> None:
        """
        从头播放。
        """
        pygame.mixer.music.stop()
        pygame.mixer.music.play()
        pygame.mixer.music.pause()
        self.offset = 0
        self.playing = False

    def get_playing(self) -> bool:
        """
        获取播放状态。
        """
        self.playing = pygame.mixer.music.get_busy()
        return self.playing

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

    def set_pos(self, pos: float) -> None:
        """
        设置当前播放位置 (单位:秒)。
        """
        if self.ready:
            try:
                pos = min(max(pos, 0), self.length)
                pygame.mixer.music.set_pos(pos * self.rate)
                self.offset = pos - pygame.mixer.music.get_pos() / 1000
            except:
                self.replay()

    def set_prog(self, prog: float) -> float:
        """
        设置当前播放进度。
        """
        self.set_pos(self.length * prog)
