"""
该文件修改自 https://github.com/ganpig/pwxysq。
"""

import os
import sys
import time
import tkinter
import tkinter.colorchooser
from configparser import ConfigParser

import easygui
import pygame

WINDOW_SIZE = (1000, 600)
WINDOW_TITLE = 'Omegar v0.1'
SIDEBAR_LEFT = WINDOW_SIZE[0]-400
SIDEBAR_MID = (SIDEBAR_LEFT+WINDOW_SIZE[0])//2
try:
    RESOURCES = sys._MEIPASS
except:
    RESOURCES = '.'


def askcolor(default, title):
    tk = tkinter.Tk()
    tk.withdraw()
    color = tkinter.colorchooser.askcolor(default, title=title)[1]
    tk.destroy()
    return color


class Window:
    def __init__(self, cp: ConfigParser) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption(WINDOW_TITLE)
        self.fonts = [[pygame.font.Font(os.path.join(
            RESOURCES, 'fonts', m), 18+i*8) for i in range(4)] for m in ('FZFWQingYinTiJWL.ttf', 'CascadiaCode.ttf')]
        self.mouse_pos = (0, 0)
        self.cp = cp

        if not self.cp.has_section('window'):
            self.cp.add_section('window')

        # 设置窗口背景
        self.background = self.get_or_set('background', '#000000')
        if self.background.startswith('#'):
            self.apply_bg_mode('color')
        else:
            self.apply_bg_mode('image')

        # 设置主题颜色
        try:
            self.main_color_hex = self.get_or_set('main_color', '#ffffff')
            self.main_color = [int(self.main_color_hex[i:i+2], 16)
                               for i in range(1, 7, 2)]
        except:
            self.main_color = (255, 255, 255)
            self.cp.set('window', 'main_color', '#ffffff')

        self.cp.write(open('config.ini', 'w', encoding='utf-8'))

    def get_or_set(self, key: str, default: str) -> str:
        if self.cp.has_option('window', key):
            return self.cp.get('window', key)
        else:
            self.cp.set('window', key, default)
            return default

    def apply_bg_mode(self, mode: str) -> None:
        """
        应用背景模式。
        """
        if mode == 'color':
            self.bg_mode = 'color'
            try:
                self.bg_color = tuple(int(self.background[i:i+2], 16)
                                      for i in range(1, 7, 2))
            except:
                self.background = '#000000'
                self.bg_color = (0, 0, 0)
                self.cp.set('window', 'background', '#000000')
        elif mode == 'image':
            try:
                self.bg_image = pygame.transform.scale(
                    pygame.image.load(self.background), WINDOW_SIZE)
                self.bg_image_with_mask = self.bg_image.copy()
                self.bg_color = (0, 0, 0)
                self.bg_mode = 'image'
                try:
                    self.mask_alpha = int(self.get_or_set('mask_alpha', '200'))
                    assert (0 <= self.mask_alpha <= 255)
                except:
                    self.mask_alpha = 200
                    self.cp.set('window', 'mask_alpha', '200')
                mask = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
                mask.fill((0, 0, 0, self.mask_alpha))
                self.bg_image_with_mask.blit(mask, (0, 0))
            except:
                self.bg_mode = 'color'
                self.background = '#000000'
                self.bg_color = (0, 0, 0)
                self.cp.set('window', 'background', '#000000')

    def change_bg_mode(self) -> None:
        """
        切换背景模式。
        """
        exec(f'self.set_bg_{"image" if self.bg_mode=="color" else "color"}()')

    def set_bg(self) -> None:
        """
        修改背景。
        """
        exec(f'self.set_bg_{self.bg_mode}()')

    def set_bg_color(self) -> None:
        """
        设置背景颜色。
        """
        color = askcolor(self.bg_color, '选择背景颜色')
        if color:
            self.background = color
            self.apply_bg_mode('color')
            self.cp.set('window', 'background', color)
            self.cp.write(open('config.ini', 'w', encoding='utf-8'))

    def set_bg_image(self) -> None:
        """
        设置背景图片。
        """
        image = easygui.fileopenbox('选择背景图片')
        if image:
            try:
                pygame.image.load(image)
                self.background = image
                self.apply_bg_mode('image')
                self.cp.set('window', 'background', image)
                self.cp.write(open('config.ini', 'w', encoding='utf-8'))
            except:
                self.error('无法加载所选的背景图片，请重新选择。')
                self.set_bg_image()

    def set_main_color(self) -> None:
        """
        设置主题颜色。
        """
        color = askcolor(self.main_color_hex, '选择主题颜色')
        if color:
            self.main_color_hex = color
            self.main_color = [int(color[i:i+2], 16)
                               for i in range(1, 7, 2)]
            self.cp.set('window', 'main_color', color)
            self.cp.write(open('config.ini', 'w', encoding='utf-8'))

    def set_mask_alpha(self, value: float) -> None:
        """
        设置蒙版不透明度（参数为小数）。
        """
        self.mask_alpha = int(value * 255)
        self.cp.set('window', 'mask_alpha', str(self.mask_alpha))
        self.cp.write(open('config.ini', 'w', encoding='utf-8'))
        self.bg_image_with_mask = self.bg_image.copy()
        mask = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        mask.fill((0, 0, 0, self.mask_alpha))
        self.bg_image_with_mask.blit(mask, (0, 0))

    def draw_frame(self) -> None:
        """
        绘制窗口框架。
        """
        if self.bg_mode == 'color':
            self.screen.fill(self.bg_color)
        elif self.bg_mode == 'image':
            self.screen.blit(self.bg_image_with_mask, (0, 0))
        pygame.draw.line(self.screen, self.main_color,
                         (SIDEBAR_LEFT, 0), (SIDEBAR_LEFT, 600), 3)

    def draw_text(self, text: str, pos: tuple, align: str = 'topleft', size: int = 1, font: int = 0, color: tuple = None) -> pygame.Rect:
        """
        绘制文字。
        """
        render = self.fonts[font][size].render(
            text, True, color if color else self.main_color)
        rect = render.get_rect()
        exec(f'rect.{align}=pos')
        return self.screen.blit(render, rect)

    def error(self, msg: str, serious: bool = False) -> None:
        """
        错误弹窗。
        """
        if serious:
            easygui.msgbox(msg, title='出错了', ok_button='退出程序')
            pygame.quit()
            sys.exit()
        else:
            easygui.msgbox(msg, title='提示', ok_button='我知道了')

    def process_events(self) -> list:
        """
        处理事件。
        """
        ret = []
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
                ret.append(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                ret.append(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                ret.append(event)
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        return ret

    def update(self) -> None:
        """
        刷新窗口。
        """
        pygame.display.flip()


class Button:
    def __init__(self, window: Window, icon: pygame.Surface, pos: tuple, align: str = 'topleft', todo=lambda: print('Ding dong~'), background: str = '', text: str = '') -> None:
        self.window = window
        self.icon = icon
        self.align = align
        self.size = icon.get_size()
        self.todo = todo
        self.background = background
        self.text = text
        self.rect = self.icon.get_rect()
        exec(f'self.rect.{align}=pos')
        self.touch_time = 0

    def draw(self) -> pygame.Rect:
        if self.touch_time <= 0 and self.rect.collidepoint(*self.window.mouse_pos):
            self.touch_time = time.time()
        elif self.touch_time > 0 and not self.rect.collidepoint(*self.window.mouse_pos):
            self.touch_time = -time.time()-min(0.5, abs(time.time()-self.touch_time))
        alpha = int((min(0.5, time.time()-self.touch_time) if self.touch_time
                     > 0 else max(0, -time.time()-self.touch_time))*510)
        if self.background:
            alpha_surface = pygame.Surface(
                self.icon.get_size(), pygame.SRCALPHA)
            if self.background == 'circle':
                pygame.draw.circle(alpha_surface, (*self.window.main_color, alpha),
                                   (self.size[0]//2, self.size[1]//2), self.size[0]//2)
                self.window.screen.blit(alpha_surface, self.rect)
            elif self.background == 'rect':
                pygame.draw.rect(alpha_surface, (*self.window.main_color, alpha),
                                 pygame.Rect((0, 0), self.size), 0, 5)
            self.window.screen.blit(alpha_surface, self.rect)
        if self.text:
            tip = self.window.fonts[0][0].render(
                self.text, True, (0, 0, 255), self.window.main_color)
            tip.set_alpha(alpha)
            rect = tip.get_rect()
            rect.midright = self.rect.midleft
            self.window.screen.blit(tip, rect)
        return self.window.screen.blit(self.icon, self.rect)

    def move(self, pos: tuple) -> None:
        self.rect = self.icon.get_rect()
        exec(f'self.rect.{self.align}=pos')

    def process_click_event(self, mouse_pos: tuple) -> None:
        if self.rect.collidepoint(*mouse_pos):
            self.todo()


class Slider:
    def __init__(self, window: Window, pos: tuple, length: int, width: int, align: str = 'topleft', size: int = 30, getvalue=None, setvalue=None, setdirectly=None, sdtext='') -> None:
        self.window = window
        self.pos = pos
        self.length = length
        self.width = width
        self.align = align
        self.size = size
        self.getvalue = getvalue
        self.setvalue = setvalue
        self.setdirectly = setdirectly
        self.sdtext = sdtext
        self.setting = False
        self.click_pos = (0, 0)
        self.color = self.window.main_color
        self.icon = pygame.transform.scale(pygame.image.load(
            os.path.join(RESOURCES, 'icons', 'crystal.png')), (size, size))
        self.warning = pygame.transform.scale(pygame.image.load(
            os.path.join(RESOURCES, 'icons', 'warning.png')), (size, size))
        self.icon_rect = self.icon.get_rect()
        self.bar = pygame.Surface((length, width), pygame.SRCALPHA)
        pygame.draw.rect(self.bar, self.color,
                         pygame.Rect((0, 0), (length, width)), 0, width//2)
        self.bar_rect = self.bar.get_rect()
        exec(f'self.bar_rect.{self.align}=pos')
        self.touch_time = 0

    def draw(self) -> pygame.Rect:
        if self.color != self.window.main_color:
            self.color = self.window.main_color
            self.bar = pygame.Surface(
                (self.length, self.width), pygame.SRCALPHA)
            pygame.draw.rect(self.bar, self.color,
                             pygame.Rect((0, 0), (self.length, self.width)), 0, self.width//2)
            self.bar_rect = self.bar.get_rect()
            exec(f'self.bar_rect.{self.align}=self.pos')
        self.window.screen.blit(self.bar, self.bar_rect)
        if self.touch_time <= 0 and self.icon_rect.collidepoint(*self.window.mouse_pos):
            self.touch_time = time.time()
        elif self.touch_time > 0 and not self.icon_rect.collidepoint(*self.window.mouse_pos) and not self.setting:
            self.touch_time = -time.time()-min(0.5, abs(time.time()-self.touch_time))
        if self.setting:
            if not 0 <= self.getvalue() <= 1:
                self.setvalue(max(0, min(1, self.getvalue())))
            elif self.window.mouse_pos != self.click_pos:
                self.setvalue(max(0, min(1,
                                         (self.window.mouse_pos[0]-self.bar_rect.left-self.size/2)/(self.length-self.size))))
        alpha = int((min(0.5, time.time()-self.touch_time) if self.touch_time
                    > 0 else max(0, -time.time()-self.touch_time))*510)
        alpha_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(alpha_surface, (*self.window.main_color,
                           alpha), (self.size//2, self.size//2), self.size//2)
        self.icon_rect.midbottom = (
            self.bar_rect.left+self.size/2+(self.length-self.size)*max(0, min(1, self.getvalue())), self.bar_rect.centery)
        self.window.screen.blit(alpha_surface, self.icon_rect)
        self.window.screen.blit(
            self.icon if 0 <= self.getvalue() <= 1 else self.warning, self.icon_rect)
        if self.touch_time > 0 and self.setdirectly and (not pygame.mouse.get_pressed()[0] or self.window.mouse_pos == self.click_pos):
            tip = self.window.fonts[0][0].render(
                '点击以精确设置'+self.sdtext, True, (0, 0, 255), self.window.main_color)
            tip.set_alpha(alpha)
            rect = tip.get_rect()
            rect.midright = self.icon_rect.midleft
            self.window.screen.blit(tip, rect)
        return self.bar_rect

    def move(self, pos: tuple) -> None:
        self.bar_rect = self.bar.get_rect()
        exec(f'self.bar_rect.{self.align}=pos')

    def process_click_event(self, mouse_pos: tuple) -> None:
        if self.icon_rect.collidepoint(*mouse_pos):
            self.setting = True
            self.click_pos = mouse_pos

    def process_release_event(self, mouse_pos: tuple) -> None:
        if self.setting:
            self.setting = False
            if mouse_pos == self.click_pos and self.setdirectly:
                self.setdirectly()
