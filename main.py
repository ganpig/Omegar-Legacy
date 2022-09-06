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
        self.pages = {'home': 'Omegar', 'settings': '设置'}
        self.icons = {name: pygame.transform.scale(pygame.image.load(
            os.path.join(RESOURCES, 'icons', name+'.png')), size) for name, size in
            [('settings', (50, 50)), ('return', (50, 50)), ('change', (65, 30)), ('set', (65, 30)), ('help', (20, 20))]}
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

    def draw_home(self, start) -> None:
        self.buttons['settings'].draw()

    def draw_settings(self, start) -> None:
        self.buttons['return'].draw()

        t = self.window.draw_text('背景模式:'+('纯色' if self.window.bg_mode ==
                                           'color' else '图片'), (SIDEBAR_LEFT+10, start+20), 'topleft')
        if 'change_bg_mode' not in self.buttons:
            self.buttons['change_bg_mode'] = Button(
                self.window, self.icons['change'], (WINDOW_SIZE[0]-10, t.centery), 'midright', self.window.change_bg_mode, 'rect')
            self.buttons['set_bg'] = Button(self.window, self.icons['set'], (
                self.buttons['change_bg_mode'].rect.left-10, t.centery), 'midright', self.window.set_bg, 'rect')
        else:
            self.buttons['change_bg_mode'].move((WINDOW_SIZE[0]-10, t.centery))
            self.buttons['set_bg'].move(
                (self.buttons['change_bg_mode'].rect.left-10, t.centery))
        self.buttons['change_bg_mode'].draw()
        self.buttons['set_bg'].draw()
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
            if 'change_mask_alpha' not in self.sliders:
                self.sliders['change_mask_alpha'] = Slider(
                    self.window, (SIDEBAR_LEFT+10, t.bottom+15), WINDOW_SIZE[0]-SIDEBAR_LEFT-20, 10, 'topleft', 20, lambda: self.window.mask_alpha/255, self.window.set_mask_alpha)
            else:
                self.sliders['change_mask_alpha'].move(
                    (SIDEBAR_LEFT+10, t.bottom+15))
            t = self.sliders['change_mask_alpha'].draw()

        t = self.window.draw_text(
            '主题颜色:', (SIDEBAR_LEFT+10, t.bottom+10), 'topleft')
        pygame.draw.rect(self.window.screen, self.window.main_color,
                         (t.right+5, t.centery-10, 20, 20), 0, 3)
        pygame.draw.rect(self.window.screen, (255, 255, 255),
                         (t.right+5, t.centery-10, 20, 20), 1, 3)
        if 'set_main_color' not in self.buttons:
            self.buttons['set_main_color'] = Button(self.window, self.icons['set'], (
                WINDOW_SIZE[0]-10, t.centery), 'midright', self.window.set_main_color, 'rect')
        else:
            self.buttons['set_main_color'].move((WINDOW_SIZE[0]-10, t.centery))
        self.buttons['set_main_color'].draw()

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
