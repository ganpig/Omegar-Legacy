import json
import os
from configparser import ConfigParser

import pygame

import player
import popup
from window import *


class Sidebar:
    def __init__(self, window: Window) -> None:
        self.window = window
        self.pages = {'home': '欢迎来到 Omegar', 'edit': '谱面编辑', 'settings': '设置'}
        self.icons = {name: pygame.transform.scale(pygame.image.load(
            os.path.join(RESOURCES, 'icons', name+'.png')), size) for name, size in
            [('settings', (50, 50)), ('return', (50, 50)), ('change', (65, 30)), ('set', (65, 30)), ('help', (20, 20),), ('go', (50, 50))]}
        self.buttons = {}
        self.sliders = {}
        self.points_hash = 0
        self.open('home')

    def draw(self) -> None:
        start = self.window.draw_text(
            self.pages[self.page], (SIDEBAR_MID, 10-max(0, 1-(time.time()-self.page_open_time)/0.3)**2*100), 'midtop', 3).bottom
        if self.page == 'home':
            self.draw_home(start)
        elif self.page == 'settings':
            self.draw_settings(start)

    def add_button(self, name: str, icon: pygame.Surface, pos: tuple, align: str = 'topleft', todo=lambda: print('Ding dong~'), background: str = '', text: str = '') -> None:
        if name not in self.buttons:
            self.buttons[name] = Button(
                self.window, icon, pos, align, todo, background, text)
        else:
            self.buttons[name].move(pos)
        return self.buttons[name].draw()

    def add_slider(self, name: str, pos: tuple, length: int, width: int, align: str = 'topleft', size: int = 30, getvalue=None, setvalue=None, setdirectly=None, sdtext='') -> None:
        if name not in self.sliders:
            self.sliders[name] = Slider(
                self.window, pos, length, width, align, size, getvalue, setvalue, setdirectly, sdtext)
        else:
            self.sliders[name].move(pos)
        return self.sliders[name].draw()

    def draw_home(self, start) -> None:
        self.window.set_title()
        self.buttons['settings'].draw()

        t = self.window.draw_text(
            '新建谱面', (SIDEBAR_LEFT+10, start+20), 'topleft')
        self.add_button('new', self.icons['go'], (WINDOW_SIZE[0]-10,
                        t.centery), 'midright', self.new_chart_wizard, 'circle')

    def new_chart_wizard(self) -> None:
        popup.print('Hello world!', '新建谱面')

    def draw_settings(self, start) -> None:
        self.buttons['return'].draw()

        t = self.window.draw_text('背景模式:'+('纯色' if self.window.bg_mode ==
                                           'color' else '图片'), (SIDEBAR_LEFT+10, start+20), 'topleft')
        t = self.add_button('change_bg_mode', self.icons['change'], (
            WINDOW_SIZE[0]-10, t.centery), 'midright', self.window.change_bg_mode, 'rect')
        t = self.add_button('set_bg', self.icons['set'], (
            self.buttons['change_bg_mode'].rect.left-10, t.centery), 'midright', self.window.set_bg, 'rect')
        t = self.window.draw_text(
            '当前背景:', (SIDEBAR_LEFT+10, t.bottom), 'topleft', 0)
        if self.window.bg_mode == 'color':
            pygame.draw.rect(self.window.screen, self.window.bg_color,
                             (t.right+5, t.centery-10, 20, 20), 0, 3)
            pygame.draw.rect(self.window.screen, (255, 255, 255),
                             (t.right+5, t.centery-10, 20, 20), 1, 3)
        else:
            t = self.window.draw_text(os.path.split(self.window.background)[
                                      1], (t.right, t.centery), 'midleft', 0)
            t = self.window.draw_text(
                '蒙版不透明度:'+str(self.window.mask_alpha), (SIDEBAR_LEFT+10, t.bottom+10), 'topleft')
            t = self.add_slider('change_mask_alpha', (SIDEBAR_LEFT+10, t.bottom+15),
                                WINDOW_SIZE[0]-SIDEBAR_LEFT-20, 10, 'topleft', 20, lambda: self.window.mask_alpha/255, self.window.set_mask_alpha)

        t = self.window.draw_text(
            '主题颜色:', (SIDEBAR_LEFT+10, t.bottom+10), 'topleft')
        pygame.draw.rect(self.window.screen, self.window.main_color,
                         (t.right+5, t.centery-10, 20, 20), 0, 3)
        pygame.draw.rect(self.window.screen, (255, 255, 255),
                         (t.right+5, t.centery-10, 20, 20), 1, 3)
        self.add_button('set_main_color', self.icons['set'], (
            WINDOW_SIZE[0]-10, t.centery), 'midright', self.window.set_main_color, 'rect')

    def open(self, page) -> None:
        self.page = page
        self.page_open_time = time.time()
        if page == 'home':
            self.open_home()
        elif page == 'settings':
            self.open_settings()

    def open_home(self) -> None:
        self.points_hash = 0
        self.buttons = {'settings': Button(self.window, self.icons['settings'],
                                           (WINDOW_SIZE[0]-60, WINDOW_SIZE[1]-60), 'topleft', lambda: self.open('settings'), 'circle', '设置')}
        self.sliders = {}

    def open_settings(self) -> None:
        self.buttons = {'return': Button(self.window, self.icons['return'],
                                         (SIDEBAR_LEFT+10, 10), 'topleft', lambda: self.open('home'), 'circle', '返回')}
        self.sliders = {}


if __name__ == '__main__':
    cp = ConfigParser()
    if os.path.isfile('config.ini'):
        try:
            cp.read('config.ini', encoding='utf-8')
        except:
            pass
    window = Window(cp)
    sidebar = Sidebar(window)

    while True:
        window.draw_frame()
        sidebar.draw()
        window.update()
        for event in window.process_events():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in sidebar.buttons.values():
                    button.process_click_event(event.pos)
                for slider in sidebar.sliders.values():
                    slider.process_click_event(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                for slider in sidebar.sliders.values():
                    slider.process_release_event(event.pos)
