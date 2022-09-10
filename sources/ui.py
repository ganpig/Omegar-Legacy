import sys
import time
import tkinter
import tkinter.colorchooser
from configparser import ConfigParser

import easygui
import pygame

from common import *


class Window:
    blit_list: list = []  # 延迟绘制列表
    logo: pygame.Surface = pygame.image.load(get_res('icons', 'logo.png'))
    mouse_pos: tuple = (0, 0)  # 光标位置
    msg_time: float = 0  # 消息更新时间
    msg: str = ''  # 消息
    on_exit = None  # 退出程序时执行

    def __init__(self, cp: ConfigParser) -> None:
        self.cp = cp
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_icon(self.logo)
        pygame.key.set_repeat(300, 50)

        # 设置窗口背景
        self.background = self.get_or_set('window', 'background', '#c2e3eb')
        if self.background.startswith('#'):
            self.apply_bg_mode('color')
        else:
            self.apply_bg_mode('image')

        # 设置主题颜色
        try:
            self.main_color_hex = self.get_or_set(
                'window', 'main_color', '#dd10fa')
            self.main_color = self.color2rgb(self.main_color_hex)
        except:
            self.main_color = (255, 255, 255)
            self.set_and_save('window', 'main_color', '#dd10fa')

        # 设置提示颜色
        try:
            self.tip_color_hex = self.get_or_set(
                'window', 'tip_color', '#0000ff')
            self.tip_color = self.color2rgb(self.tip_color_hex)
        except:
            self.tip_color = (0, 0, 255)
            self.set_and_save('window', 'main_color', '#0000ff')

    """
    配置文件相关部分
    """

    def get_or_set(self, section: str, option: str, default: str = '') -> str:
        """
        若设置项存在，获取该项的值，否则将该项设置为默认值并返回该值。
        """
        if self.cp.has_option(section, option):
            return self.cp.get(section, option)
        else:
            self.set_and_save(section, option, default)
            return default

    def set_and_save(self, section: str, option: str, value: str) -> None:
        """
        修改设置并保存。
        """
        if not self.cp.has_section(section):
            self.cp.add_section(section)
        self.cp.set(section, option, value)
        self.cp.write(open(CONFIG_FILE, 'w', encoding='utf-8'))

    def get_options(self, section: str) -> list:
        """
        获取设置列表。
        """
        if not self.cp.has_section(section):
            return []
        return self.cp.options(section)

    """
    颜色相关部分
    """

    def ask_color(self, default: str = '#ffffff', title: str = '') -> str:
        """
        颜色选择对话框。
        """
        tk = tkinter.Tk()
        tk.withdraw()
        color = tkinter.colorchooser.askcolor(default, title=title)[1]
        tk.destroy()
        return color

    def color2rgb(self, hex_color: str) -> tuple:
        """
        将 #xxxxxx 格式的十六进制颜色转换为 RGB 颜色。
        """
        return tuple(int(hex_color[i:i+2], 16) for i in range(1, 7, 2))

    """
    外观设置部分
    """

    def apply_bg_mode(self, mode: str) -> None:
        """
        应用背景模式。
        """
        if mode == 'color':
            self.bg_mode = 'color'
            try:
                self.bg_color = self.color2rgb(self.background)
            except:
                self.background = '#c2e3eb'
                self.bg_color = (0, 0, 0)
                self.set_and_save('window', 'background', '#c2e3eb')
        elif mode == 'image':
            try:
                self.bg_image = pygame.transform.scale(
                    pygame.image.load(self.background), WINDOW_SIZE)
                self.bg_image_with_mask = self.bg_image.copy()
                self.bg_color = (0, 0, 0)
                self.bg_mode = 'image'
                try:
                    self.mask_alpha = int(self.get_or_set(
                        'window', 'mask_alpha', '200'))
                    assert (0 <= self.mask_alpha <= 255)
                except:
                    self.mask_alpha = 200
                    self.set_and_save('window', 'mask_alpha', '200')
                mask = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
                mask.fill((0, 0, 0, self.mask_alpha))
                self.bg_image_with_mask.blit(mask, (0, 0))
            except:
                self.bg_mode = 'color'
                self.background = '#c2e3eb'
                self.bg_color = (0, 0, 0)
                self.set_and_save('window', 'background', '#c2e3eb')

    def bg_config(self) -> None:
        """
        设置背景。
        """
        eval('self.set_bg_'+self.bg_mode)()

    def change_bg_mode(self) -> None:
        """
        切换背景模式。
        """
        eval('self.set_bg_'+{'image': 'color',
             'color': 'image'}[self.bg_mode])()

    def set_bg_color(self) -> None:
        """
        设置背景颜色。
        """
        color = self.ask_color(self.bg_color, '选择背景颜色')
        if color:
            self.background = color
            self.apply_bg_mode('color')
            self.set_and_save('window', 'background', color)

    def set_bg_image(self) -> None:
        """
        设置背景图片。
        """
        image = easygui.fileopenbox('选择背景图片', WINDOW_TITLE)
        if image:
            try:
                pygame.image.load(image)
                self.background = image
                self.apply_bg_mode('image')
                self.set_and_save('window', 'background', image)
            except:
                easygui.exceptionbox('无法加载所选的背景图片，请重新选择。', '设置背景图片')
                self.set_bg_image()

    def set_main_color(self) -> None:
        """
        设置主题颜色。
        """
        color = self.ask_color(self.main_color_hex, '选择主题颜色')
        if color:
            self.main_color_hex = color
            self.main_color = self.color2rgb(color)
            self.set_and_save('window', 'main_color', color)

    def set_tip_color(self) -> None:
        """
        设置提示颜色。
        """
        color = self.ask_color(self.tip_color_hex, '选择提示颜色')
        if color:
            self.tip_color_hex = color
            self.tip_color = self.color2rgb(color)
            self.set_and_save('window', 'tip_color', color)

    def set_mask_alpha(self, value: float) -> None:
        """
        设置蒙版不透明度（参数为小数）。
        """
        self.mask_alpha = int(value * 255)
        self.set_and_save('window', 'mask_alpha', str(self.mask_alpha))
        self.bg_image_with_mask = self.bg_image.copy()
        mask = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        mask.fill((0, 0, 0, self.mask_alpha))
        self.bg_image_with_mask.blit(mask, (0, 0))

    """
    窗口绘制部分
    """

    def draw_frame(self) -> None:
        """
        绘制窗口框架。
        """
        if self.bg_mode == 'color':
            self.screen.fill(self.bg_color)
        elif self.bg_mode == 'image':
            self.screen.blit(self.bg_image_with_mask, (0, 0))
        pygame.draw.line(self.screen, self.main_color,
                         (SPLIT_LINE, 0), (SPLIT_LINE, 600), 3)

    def draw_text(self, text: str, pos: tuple, align: str = 'topleft', size: int = 1, font: int = 0, color: tuple = None) -> pygame.Rect:
        """
        绘制文字。
        """
        render = FONTS[font][size].render(
            text, True, color if color else self.main_color)
        rect = render.get_rect()
        exec(f'rect.{align}=pos')
        return self.screen.blit(render, rect)

    def draw_msg(self) -> None:
        """
        绘制消息。
        """
        if time.time() <= self.msg_time+MSG_SHOW_TIME:
            msg_appear_time = time.time()-self.msg_time
            if msg_appear_time <= MSG_ANIMATION_TIME:
                msg_top = (MSG_HEIGHT+10)*msg_appear_time / \
                    MSG_ANIMATION_TIME-MSG_HEIGHT
            elif msg_appear_time >= MSG_SHOW_TIME-MSG_ANIMATION_TIME:
                msg_top = (MSG_HEIGHT+10)*(MSG_SHOW_TIME -
                                           msg_appear_time)/MSG_ANIMATION_TIME-MSG_HEIGHT
            else:
                msg_top = 10
            msg_rect = pygame.Rect(10, msg_top, WINDOW_SIZE[0]-20, MSG_HEIGHT)
            pygame.draw.rect(self.screen, self.main_color,
                             msg_rect, border_radius=MSG_HEIGHT//2)
            self.draw_text(self.msg, msg_rect.center,
                           'center', color=self.tip_color)

    def later_blit(self, surface: pygame.Surface, pos: tuple) -> None:
        """
        绘制在窗口最上层
        """
        self.blit_list.append((surface, pos))

    """
    程序流程部分
    """

    def set_subtitle(self, title: str = '') -> None:
        """
        修改窗口子标题。
        """
        pygame.display.set_caption(title+bool(title)*' - '+WINDOW_TITLE)

    def set_msg(self, msg: str) -> None:
        """
        设置消息。
        """
        self.msg = msg
        self.msg_time = time.time()

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
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.KEYDOWN, pygame.USEREVENT):
                ret.append(event)
            elif event.type == pygame.QUIT:
                if easygui.ynbox('真的要退出程序吗？', '不要离开我啊 QwQ', ('退出', '手滑了')):
                    self.exit()
        return ret

    def update(self) -> None:
        """
        刷新窗口。
        """
        while self.blit_list:
            self.screen.blit(*self.blit_list.pop())
        pygame.display.flip()

    def error(self, msg: str, serious: bool = False) -> None:
        """
        错误弹窗。
        """
        if serious:
            easygui.msgbox(msg, '出错了', '退出')
            self.exit()
        else:
            easygui.msgbox(msg, '提示', '知道了')

    def exit(self) -> None:
        """
        退出程序。
        """
        self.on_exit()
        pygame.quit()
        sys.exit()


class Button:
    touch_time: float = 0  # 正值代表光标触碰按钮的时间，负值代表光标离开按钮的时间

    def __init__(self, window: Window, icon: pygame.Surface, pos: tuple, align: str = 'topleft', todo=easygui.msgbox, background: str = '', text: str = '', text_align: str = 'midright', button_align: str = 'midleft', todo_right=None) -> None:
        self.window = window
        self.icon = icon
        self.align = align
        self.size = icon.get_size()
        self.todo = todo
        self.background = background
        self.text = text
        self.text_align = text_align
        self.button_align = button_align
        self.todo_right = todo_right
        self.rect = self.icon.get_rect()
        exec(f'self.rect.{align}=pos')

    def show(self) -> pygame.Rect:
        """
        显示按钮。
        """
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
            tip = FONTS[0][0].render(
                self.text, True, self.window.tip_color, self.window.main_color)
            tip.set_alpha(alpha)
            rect = tip.get_rect()
            exec(f'rect.{self.text_align}=self.rect.{self.button_align}')
            self.window.later_blit(tip, rect)
        return self.window.screen.blit(self.icon, self.rect)

    def move(self, pos: tuple) -> None:
        """
        移动按钮位置。
        """
        self.rect = self.icon.get_rect()
        exec(f'self.rect.{self.align}=pos')

    def change_icon(self, icon: pygame.Surface) -> None:
        """
        更换按钮图标。
        """
        self.icon = icon
        self.size = icon.get_size()

    def process_click_event(self, mouse_pos: tuple, button: int) -> None:
        """
        处理点击事件。
        """
        if self.rect.collidepoint(*mouse_pos):
            if button == pygame.BUTTON_LEFT:
                self.todo()
            elif button == pygame.BUTTON_RIGHT and self.todo_right:
                self.todo_right()


class Slider:
    click_pos: tuple = (0, 0)  # 点击滑块时的光标位置
    setting: bool = False  # 是否处于“滑动即设置”状态
    touch_time: float = 0  # 见 Button 类说明

    def __init__(self, window: Window, pos: tuple, length: int, width: int = 10, align: str = 'topleft', get_value=None, set_value=None, set_directly=None, get_text=None, text_align: str = 'midright', button_align: str = 'midleft') -> None:
        self.window = window
        self.color = self.window.main_color
        self.pos = pos
        self.length = length
        self.width = width
        self.align = align
        self.get_value = get_value
        self.set_value = set_value
        self.set_directly = set_directly
        self.get_text = get_text
        self.text_align = text_align
        self.button_align = button_align
        self.icon_rect = ICONS['crystal'].get_rect()
        self.bar = pygame.Surface((length, width), pygame.SRCALPHA)
        self.bar_rect = self.bar.get_rect()
        self.redraw_bar()
        exec(f'self.bar_rect.{self.align}=pos')

    def redraw_bar(self) -> None:
        """
        重绘滑动条。
        """
        pygame.draw.rect(self.bar, self.color, pygame.Rect(
            (0, 0), (self.length, self.width)), 0, self.width//2)

    def show(self) -> pygame.Rect:
        """
        显示滑动条。
        """
        if self.color != self.window.main_color:
            self.color = self.window.main_color
            self.redraw_bar()
        self.window.screen.blit(self.bar, self.bar_rect)
        if self.touch_time <= 0 and self.icon_rect.collidepoint(*self.window.mouse_pos):
            self.touch_time = time.time()
        elif self.touch_time > 0 and not self.icon_rect.collidepoint(*self.window.mouse_pos) and not self.setting:
            self.touch_time = -time.time()-min(0.5, abs(time.time()-self.touch_time))
        if self.setting:
            if not 0 <= self.get_value() <= 1:
                self.set_value(max(0, min(1, self.get_value())))
            elif self.window.mouse_pos != self.click_pos:
                self.set_value(max(0, min(1,
                                          (self.window.mouse_pos[0]-self.bar_rect.left-SLIDER_BUTTON_SIZE/2)/(self.length-SLIDER_BUTTON_SIZE))))
        alpha = int((min(0.5, time.time()-self.touch_time) if self.touch_time
                    > 0 else max(0, -time.time()-self.touch_time))*510)
        alpha_surface = pygame.Surface(
            (SLIDER_BUTTON_SIZE, SLIDER_BUTTON_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(alpha_surface, (*self.window.main_color,
                           alpha), (SLIDER_BUTTON_SIZE//2, SLIDER_BUTTON_SIZE//2), SLIDER_BUTTON_SIZE//2)
        self.icon_rect.midbottom = (
            self.bar_rect.left+SLIDER_BUTTON_SIZE/2+(self.length-SLIDER_BUTTON_SIZE)*max(0, min(1, self.get_value())), self.bar_rect.centery)
        self.window.screen.blit(alpha_surface, self.icon_rect)
        self.window.screen.blit(
            ICONS['crystal' if 0 <= self.get_value() <= 1 else 'warning'], self.icon_rect)
        if self.get_text:
            tip = FONTS[0][0].render(
                self.get_text(), True, self.window.tip_color, self.window.main_color)
            tip.set_alpha(alpha)
            rect = tip.get_rect()
            exec(f'rect.{self.text_align}=self.icon_rect.{self.button_align}')
            self.window.later_blit(tip, rect)
        return self.bar_rect

    def move(self, pos: tuple) -> None:
        """
        移动滑动条位置。
        """
        self.bar_rect = self.bar.get_rect()
        exec(f'self.bar_rect.{self.align}=pos')

    def process_click_event(self, mouse_pos: tuple) -> None:
        """
        处理点击事件。
        """
        if self.icon_rect.collidepoint(*mouse_pos):
            self.setting = True
            self.click_pos = mouse_pos
        elif self.bar_rect.collidepoint(*mouse_pos):
            self.setting = True

    def process_release_event(self, mouse_pos: tuple) -> None:
        """
        处理鼠标释放事件。
        """
        if self.setting:
            self.setting = False
            if mouse_pos == self.click_pos and self.set_directly:
                self.set_directly()
