import configparser
import json
import math
import os
import pickle
import time

import easygui
import pygame

from common import *
from exporter import *
from player import Player
from ui import *


class App:
    bars: int = 8  # 要添加的小节数
    bpb: int = 4  # 每小节拍子数
    bpm: int = 120  # 每分钟拍子数
    buttons: dict = {}  # 按钮
    earliest_beat: float = 0
    later_buttons: dict = {}  # 延迟添加的按钮
    later_del_buttons: list = []  # 延迟删除的按钮
    project_data: dict = {}  # 项目数据
    project_path: str = ''  # 项目文件路径
    shortcuts: list = [{}, {}, {}, {}]  # 快捷键列表
    sliders: dict = {}  # 滑动条
    tmp_beats: dict = {}
    recent_projects: dict = {}  # 最近项目

    def __init__(self) -> None:
        cp = configparser.ConfigParser()
        if os.path.isfile(CONFIG_FILE):
            try:
                cp.read(CONFIG_FILE, encoding='utf-8')
            except:
                pass
        if os.path.isfile(RECENT_FILE):
            with open(RECENT_FILE, 'rb') as f:
                self.recent_projects = pickle.load(f)
        self.window = Window(cp)
        self.window.on_exit = self.close_project
        self.player = Player()
        self.open('home')

    """
    基本操作
    """

    def main(self) -> None:
        """
        程序主体循环。
        """
        while True:
            self.draw()
            self.process_events()

    def open(self, page) -> None:
        """
        打开页面。
        """
        self.page = page
        self.page_open_time = time.time()
        self.buttons = {}
        self.sliders = {}
        self.shortcuts = [{}, {}, {}, {}]
        eval('self._open_'+page)()

    def record_project(self, path: str) -> None:
        """
        记录最近项目。
        """
        if path:
            self.recent_projects[path] = time.time()
            with open(RECENT_FILE, 'wb') as f:
                pickle.dump(self.recent_projects, f)

    def draw(self) -> None:
        """
        绘制当前页面。
        """
        self.window.draw_frame()
        start = self.window.draw_text(PAGE_NAME[self.page], ((SPLIT_LINE+WINDOW_SIZE[0])//2, 10-max(
            0, 1-(time.time()-self.page_open_time)/0.3)**2*100), 'midtop', 3).bottom
        eval('self._draw_'+self.page)(start)
        self.window.draw_msg()
        self.window.update()

    def exit(self) -> None:
        """
        从当前页面返回。
        """
        eval('self._exit_'+self.page)()

    def return_home(self) -> None:
        """
        关闭项目并返回首页。
        """
        self.open('home')
        self.player.close()

    def process_events(self) -> None:
        """
        处理事件。
        """
        for event in self.window.process_events():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.buttons.values():
                    button.process_click_event(event.pos, event.button)
                for slider in self.sliders.values():
                    slider.process_click_event(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                for slider in self.sliders.values():
                    slider.process_release_event(event.pos)
            elif event.type == pygame.KEYDOWN:
                pressed = pygame.key.get_pressed()
                ctrl_alt = CTRL*(pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]) +\
                    ALT*(pressed[pygame.K_LALT] or pressed[pygame.K_RALT])
                if event.key in self.shortcuts[ctrl_alt]:
                    self.shortcuts[ctrl_alt][event.key]()
            elif event.type == pygame.USEREVENT:
                self.player.replay()
        self.buttons.update(self.later_buttons)
        self.later_buttons.clear()
        for i in self.later_del_buttons:
            del self.buttons[i]
        self.later_del_buttons.clear()

    """
    UI 操作
    """

    def show_button(self, name: str, icon: pygame.Surface, pos: tuple, align: str = 'topleft', todo=easygui.msgbox, background: str = '', text: str = '', text_align: str = 'midright', button_align: str = 'midleft', todo_right=None) -> None:
        """
        添加或更新并显示按钮。
        """
        if name not in self.buttons:
            self.buttons[name] = Button(
                self.window, icon, pos, align, todo, background, text, text_align, button_align, todo_right)
        elif icon != self.buttons[name].icon:
            self.buttons[name].change_icon(icon)
        elif text != self.buttons[name].text:
            self.buttons[name].text = text
        else:
            self.buttons[name].move(pos)
        return self.buttons[name].show()

    def show_slider(self, name: str, pos: tuple, length: int, width: int = 10, align: str = 'topleft', get_value=None, set_value=None, set_directly=None, get_text=None, text_align: str = 'midright', button_align: str = 'midleft') -> None:
        """
        添加或更新并显示滑动条。
        """
        if name not in self.sliders:
            self.sliders[name] = Slider(
                self.window, pos, length, width, align, get_value, set_value, set_directly, get_text, text_align, button_align)
        else:
            self.sliders[name].move(pos)
        return self.sliders[name].show()

    def later_add_button(self, name: str, icon: pygame.Surface, pos: tuple, align: str = 'topleft', todo=easygui.msgbox, background: str = '', text: str = '', text_align: str = 'midright', button_align: str = 'midleft', todo_right=None) -> None:
        """
        延迟添加按钮。
        """
        if name in self.later_del_buttons:
            self.later_del_buttons.remove(name)
        self.later_buttons[name] = Button(self.window, icon, pos, align, todo,
                                          background, text, text_align, button_align, todo_right)

    def later_del_button(self, name: str) -> None:
        """
        延迟删除按钮。
        """
        self.later_del_buttons.append(name)

    """
    项目操作
    """

    def create_project(self) -> None:
        """
        创建项目。
        """
        try:
            project_name = easygui.enterbox('请输入项目名称', '创建项目')
            if not project_name:
                return
            music_path = easygui.fileopenbox(
                '请选择歌曲音频', WINDOW_TITLE, '*.mp3', ['*.mp3'])
            if not music_path:
                return
            project_path = easygui.filesavebox(
                '请先保存项目文件', WINDOW_TITLE, validate_filename(project_name+'.json'), ['*.json'])
            if not project_path:
                return
            self.project_path = project_path
            self.project_data = {
                'project_name': project_name,
                'music_path': music_path,
                'beats': [],
                'page': 'pick_beats',
                'notes': [],
                'line': {
                    'initial_position': DEFAULT_LINE_INITIAL_POSITION,
                    'motions': []
                }
            }
            self.open('pick_beats')
            self.record_project(project_path)
        except:
            easygui.exceptionbox('创建项目失败！', WINDOW_TITLE)
            self.return_home()

    def open_project(self, path: str = None) -> None:
        """
        打开项目。
        """
        try:
            if not path:
                path = easygui.fileopenbox(
                    '打开项目', WINDOW_TITLE, '*.json', ['*.json'])
                if not path:
                    return
            if not os.path.isfile(path):
                easygui.msgbox(f'文件 {path} 不存在！')
                return
            self.project_path = path
            self.project_data = json.load(open(path))
            while not os.path.isfile(self.project_data['music_path']):
                self.project_data['music_path'] = easygui.fileopenbox(
                    '歌曲音频文件无效，请重新选择', WINDOW_TITLE, '*.mp3', ['*.mp3'])
            self.record_project(path)
            self.open(self.project_data['page'])

        except:
            easygui.exceptionbox('打开项目失败！', WINDOW_TITLE)
            self.return_home()

    def save_project(self, path=None) -> None:
        """
        保存项目。
        """
        self.project_data['page'] = self.page
        json.dump(self.project_data, open(
            path if path else self.project_path, 'w'), indent=4)
        if not path:
            self.window.set_msg('保存成功！')

    def close_project(self) -> None:
        """
        保存并关闭项目。
        """
        if self.project_path:
            if not os.path.isdir('Autosave'):
                os.makedirs('Autosave')

            self.save_project(os.path.join(
                'Autosave', validate_filename(f'{self.project_data["project_name"]}_{int(time.time())}.json')))
            if easygui.ynbox(f'是否保存项目文件为 {self.project_path}？', '关闭项目', ('保存', '不保存')):
                self.save_project()
            self.project_path = ''
            self.project_data.clear()

    def view_recent_projects(self) -> None:
        """
        查看最近的项目。
        """
        recent_projects = sorted(
            self.recent_projects, key=lambda x: self.recent_projects[x], reverse=True)
        if not recent_projects:
            self.window.set_msg('无最近项目！')
        else:
            path = easygui.choicebox(
                '请选择要打开的项目', '最近项目', recent_projects+['清除项目打开记录'])
            if not path:
                return
            elif path == '清除项目打开记录':
                self.recent_projects.clear()
                os.remove(RECENT_FILE)
            else:
                self.open_project(path)

    def export_project(self) -> None:
        """
        导出项目。
        """
        try:
            ch = easygui.buttonbox(
                '是否使用已有的生成设置？（首次使用请选择后者）', '导出项目', ('使用已有生成设置', '创建新的生成设置'))
            if ch == '使用已有生成设置':
                using_pickle = True
                pickle_path = easygui.fileopenbox(
                    '请选择生成设置文件', '导出项目', '*.pkl', ['*.pkl'])
                if pickle_path:
                    name, composer, illustrator, music_path, illustration_path, charts_info = pickle.load(
                        open(pickle_path, 'rb'))  # 从 pickle 文件读取生成设置
                else:
                    return
            elif ch == '创建新的生成设置':
                using_pickle = False
                data = ['']*3
                while True:
                    data = easygui.multenterbox(
                        '请输入歌曲信息：', '导出项目', ['曲名', '曲师', '画师'], data)
                    if not data:
                        return
                    if not all(data):
                        easygui.msgbox('请将歌曲信息填写完整！', '导出项目', '哦~')
                    else:
                        name, composer, illustrator = data
                        break

                music_path = easygui.fileopenbox(
                    '请选择歌曲音频', '导出项目', '*.ogg', ['*.ogg'])
                if not music_path:
                    return

                illustration_path = easygui.fileopenbox(
                    '请选择曲绘图片', '导出项目', '*.png', ['*.png'])
                if not illustration_path:
                    return

                charts_info = []
                while True:
                    if charts_info:  # 一张谱面都没添加时无法继续
                        if not easygui.ynbox(f'已添加 {len(charts_info)} 张谱面：\n'+'\n'.join(
                                f'{i["difficulty"]} {i["diff_number"]} By {i["writer"]} ({i["json_path"]})'
                                for i in charts_info), '导出项目', ('继续', '完成')):
                            break

                    data = ['']*3
                    while True:
                        data = easygui.multenterbox(
                            f'请输入第 {len(charts_info)+1} 张谱面信息：', '导出项目', ['难度', '定数', '谱师'], data)
                        if not data:
                            return
                        if not all(data):
                            easygui.msgbox('请将谱面信息填写完整！', '导出项目', '哦~')
                        else:
                            difficulty, diff_number, writer = data
                            break

                    json_path = easygui.fileopenbox(
                        '请选择谱面项目文件', '导出项目', '*.json', ['*.json'])
                    if not json_path:
                        if charts_info:
                            continue
                        else:
                            break

                    charts_info.append(
                        {'difficulty': difficulty, 'diff_number': diff_number, 'writer': writer, 'json_path': json_path})
            else:
                return

            convert_charts(charts_info)
            info_path = make_info(name, composer, illustrator, charts_info)

            if easygui.ynbox('请选择导出方式', '导出项目', ('打包为 OMGZ 文件', '导出到文件夹')):
                ok = omgz_path = easygui.filesavebox(
                    '保存 omgz 文件', '导出项目', name+'.omgz',  ['*.omgz'])
                if ok:
                    build_omgz(info_path, music_path,
                               illustration_path, charts_info, omgz_path)
            else:
                easygui.msgbox('建议新建文件夹，否则选择的文件夹将被清空！', '导出项目', '哦~')
                ok = folder_path = easygui.diropenbox('选择导出文件夹', '导出项目')
                if ok:
                    build_folder(info_path, music_path, illustration_path,
                                 charts_info, folder_path)
        except:
            easygui.exceptionbox('导出失败了……www', '导出项目')
            return

        easygui.msgbox('谱面导出成功！', '导出项目', '好耶')

        if not using_pickle:
            if easygui.ynbox('是否保存生成设置以便以后导出同一项目使用？', '文件已导出' if ok else '文件未导出', ('保存', '不保存')):
                pickle_path = easygui.filesavebox(
                    '保存生成设置', '导出项目', name+'.pkl', ['*.pkl'])  # 将生成设置保存到 pickle 文件
                if pickle_path:
                    pickle.dump((name, composer, illustrator, music_path,
                                illustration_path, charts_info), open(pickle_path, 'wb'))
                    easygui.msgbox('生成设置保存成功!', '导出项目', '好耶')

    """
    首页
    """

    def _open_home(self) -> None:
        self.window.set_subtitle()

        self.shortcuts[CTRL][pygame.K_n] = self.create_project
        self.shortcuts[CTRL][pygame.K_o] = self.open_project
        self.shortcuts[CTRL][pygame.K_h] = self.view_recent_projects
        self.shortcuts[CTRL][pygame.K_e] = self.export_project

    def _draw_home(self, start) -> None:
        self.show_button('settings', ICONS['settings'], (WINDOW_SIZE[0]-10, WINDOW_SIZE[1]-10),
                         'bottomright', lambda: self.open('settings'), 'circle', '设置')

        rect = self.window.logo.get_rect()
        rect.center = (SPLIT_LINE/2, WINDOW_SIZE[1]/2)
        self.window.screen.blit(self.window.logo, rect)

        t = self.window.draw_text(
            '创建项目 (Ctrl+N)', (SPLIT_LINE+10, start+20), 'topleft')
        self.show_button('new', ICONS['go'], (WINDOW_SIZE[0]-10,
                                              t.centery), 'midright', self.create_project, 'circle')

        t = self.window.draw_text(
            '打开项目 (Ctrl+O)', (SPLIT_LINE+10, t.bottom+10), 'topleft')
        self.show_button('open', ICONS['go'], (WINDOW_SIZE[0]-10,
                                               t.centery), 'midright', self.open_project, 'circle')

        t = self.window.draw_text(
            '最近项目 (Ctrl+H)', (SPLIT_LINE+10, t.bottom+10), 'topleft')
        self.show_button('recent', ICONS['go'], (WINDOW_SIZE[0]-10,
                                                 t.centery), 'midright', self.view_recent_projects, 'circle')

        t = self.window.draw_text(
            '导出项目 (Ctrl+E)', (SPLIT_LINE+10, t.bottom+10), 'topleft')
        self.show_button('export', ICONS['go'], (WINDOW_SIZE[0]-10,
                                                 t.centery), 'midright', self.export_project, 'circle')

    """
    采拍页面
    """

    def _open_pick_beats(self) -> None:
        self.player.open(self.project_data['music_path'])
        self.window.set_subtitle(self.project_data['project_name'])
        self.earliest_beat = math.inf
        self.tmp_beats.clear()  # key 为时间，value 为 True 表示强拍，False 表示弱拍
        for bar in self.project_data['beats']:
            for i, time in enumerate(bar):
                self._add_beat(time, not i, False)

        self.shortcuts[0][pygame.K_ESCAPE] = self.exit
        self.shortcuts[0][pygame.K_SPACE] = self._play_or_pause
        self.shortcuts[0][pygame.K_LEFT] = lambda: self.player.set_pos(
            self.player.get_pos()-1)
        self.shortcuts[0][pygame.K_RIGHT] = lambda: self.player.set_pos(
            self.player.get_pos()+1)
        self.shortcuts[0][pygame.K_DOWN] = lambda: self._add_beat(
            self.player.get_pos(), False)
        self.shortcuts[0][pygame.K_UP] = lambda: self._add_beat(
            self.player.get_pos(), True)
        self.shortcuts[CTRL][pygame.K_s] = self.save_project

    def _draw_pick_beats(self, start) -> None:
        self.show_button('return', ICONS['return'], (SPLIT_LINE+10, 10), 'topleft',
                         self.exit, 'circle', '返回', 'midleft', 'midright')

        t1 = self.show_button(
            'play_or_pause', ICONS['pause' if self.player.get_playing() else 'play'], (10, 10), 'topleft', self._play_or_pause, 'rect', '播放/暂停', 'midleft', 'midright', True)

        t2 = self.show_button('add_beat', ICONS['add'], (SPLIT_LINE-10, 10), 'topright', lambda: self._add_beat(self.player.get_pos(
        ), False), 'rect', '左击或按↓添加弱拍，右击或按↑添加强拍' if self.player.get_pos() > self.earliest_beat else '单击或按↑添加强拍', todo_right=lambda: self._add_beat(self.player.get_pos(), True))

        t = self.show_slider('music_pos', (t1.right+10, t1.centery), t2.left-t1.right-20, align='midleft', get_value=self.player.get_prog,
                             set_value=self.player.set_prog, set_directly=self._set_player_pos, get_text=self.player.get_text, text_align='midtop', button_align='midbottom')

        pygame.draw.line(self.window.screen, self.window.main_color, (SPLIT_LINE/2,
                         WINDOW_SIZE[1]/2-50), (SPLIT_LINE/2, WINDOW_SIZE[1]/2+50), 5)

        for sec in self.buttons:
            if type(sec) == float:
                pos = SPLIT_LINE/2+PICK_BEAT_SPEED*(sec-self.player.get_pos())
                self.buttons[sec].move((pos, WINDOW_SIZE[1]/2))
                if 0 < self.buttons[sec].rect.right < SPLIT_LINE:
                    self.buttons[sec].show()

        t = self.window.draw_text(
            'Tip: 可点击进度条滑块精确定位时间', (SPLIT_LINE+10, start+20), size=0)
        t = self.window.draw_text('全部清除', (SPLIT_LINE+10, t.bottom+20))
        self.show_button('clear_all', ICONS['go'], (
            WINDOW_SIZE[0]-10, t.centery), 'midright', self._clear_all_beats, 'circle')
        t = self.window.draw_text('自动修正', (SPLIT_LINE+10, t.bottom+10))
        self.show_button('auto_correct', ICONS['go'], (
            WINDOW_SIZE[0]-10, t.centery), 'midright', self._auto_correct_beats, 'circle')

        t = self.window.draw_text('批量添加拍子', (SPLIT_LINE+10, t.bottom+20))
        self.show_button('batch_add', ICONS['go'], (
            WINDOW_SIZE[0]-10, t.centery), 'midright', self._batch_add_beats, 'circle')
        t = self.window.draw_text(
            f'添加的小节数：{self.bars}', (SPLIT_LINE+20, t.bottom+10), size=0)
        self.show_button('enter_bars', ICONS['set'], (
            WINDOW_SIZE[0]-10, t.centery), 'midright', self._enter_bars, 'rect')
        t = self.window.draw_text(
            f'每小节拍子数：{self.bpb}', (SPLIT_LINE+20, t.bottom+10), size=0)
        self.show_button('change_btb', ICONS['change'], (
            WINDOW_SIZE[0]-10, t.centery), 'midright', self._change_bpb, 'rect')
        t = self.window.draw_text(
            f'BPM：{self.bpm}', (SPLIT_LINE+20, t.bottom+10), size=0)
        self.show_slider('change_bpm', (SPLIT_LINE+150, t.centery),
                         WINDOW_SIZE[0]-SPLIT_LINE-160, 10, 'midleft', self._get_bpm, self._set_bpm, self._enter_bpm)

    def _play_or_pause(self) -> None:
        if self.player.get_playing():
            self.player.pause()
            self.buttons['play_or_pause'].change_icon(ICONS['play'])
        else:
            self.player.play()
            self.buttons['play_or_pause'].change_icon(ICONS['pause'])

    def _set_player_pos(self) -> None:
        pos = easygui.enterbox('请输入定位秒数', '控制播放进度', str(self.player.get_pos()))
        if pos:
            try:
                self.player.set_pos(float(pos))
            except:
                easygui.msgbox('请输入一个整数或小数！', '控制播放进度')

    def _add_beat(self, sec: float, strong: bool, process: bool = True) -> None:
        if sec <= self.player.length:
            if sec < self.earliest_beat:
                self.earliest_beat = sec
                strong = True
            self.tmp_beats[sec] = strong
            self.later_add_button(sec, ICONS['orange_beat' if strong else 'green_beat'], (0, 0), 'center', lambda: self.player.set_pos(
                sec), 'circle', '左击定位到此，右击删除拍子', 'midtop', 'midbottom', lambda: self._delete_beat(sec))
            if process:
                self._process_beats()

    def _delete_beat(self, sec: float, process: bool = True) -> None:
        del self.tmp_beats[sec]
        self.later_del_button(sec)
        if process:
            self._process_beats()

    def _process_beats(self) -> None:
        if self.tmp_beats:
            tmp = []
            sorted_beats = sorted(self.tmp_beats)
            self.earliest_beat = sorted_beats[0]
            self.tmp_beats[self.earliest_beat] = True
            if self.earliest_beat in self.buttons:
                self.buttons[self.earliest_beat].change_icon(
                    ICONS['orange_beat'])
            for i in sorted_beats:
                if self.tmp_beats[i]:
                    tmp.append([i])
                else:
                    tmp[-1].append(i)
            self.project_data['beats'] = tmp
        else:
            self.earliest_beat = math.inf
            self.project_data['beats'] = []

    def _clear_all_beats(self, ask=True) -> None:
        if not ask or easygui.ynbox('确认清除全部节拍？', '清除全部'):
            for time in list(self.tmp_beats.keys()):
                self._delete_beat(time, False)
            self._process_beats()

    def _auto_correct_beats(self) -> None:
        bak_beats = dict(self.tmp_beats)
        time_points = sorted(bak_beats)
        time_points_arr = (ctypes.c_double*len(time_points))(*time_points)
        dll = load_dll('autoCorrect')
        dll.autoCorrect.argtypes = (
            ctypes.c_int, ctypes.Array, ctypes.c_double)
        dll.autoCorrect(len(time_points),
                        time_points_arr, AUTO_CORRECT_MAX_VARIANCE)
        self._clear_all_beats(False)
        for i, time in enumerate(list(time_points_arr)):
            self._add_beat(time, bak_beats[time_points[i]], False)
        self._process_beats()
        self.window.set_msg('自动修正完成！')

    def _change_bpb(self) -> None:
        self.bpb = {1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 1}[self.bpb]

    def _set_bpm(self, f: float) -> None:
        self.bpm = int(60*(1-f)+320*f)

    def _get_bpm(self) -> float:
        return (self.bpm-60)/260

    def _enter_bpm(self) -> None:
        bpm = easygui.enterbox('请输入每分钟拍子数', '设置 BPM')
        try:
            self.bpm = round(float(bpm), 2)
            if self.bpm == int(self.bpm):
                self.bpm = int(self.bpm)
        except:
            self.window.set_msg('输入的 BPM 无效！')

    def _enter_bars(self) -> None:
        bars = easygui.enterbox('请输入要添加的小节数', '批量采拍')
        try:
            self.bars = int(bars)
        except:
            self.window.set_msg('输入的小节数无效！')

    def _batch_add_beats(self) -> None:
        now = self.player.get_pos()
        spb = 60/self.bpm
        for i in range(self.bars):
            for j in range(self.bpb):
                self._add_beat(now+(i*self.bpb+j)*spb, not j, False)
        self._process_beats()

    def _exit_pick_beats(self) -> None:
        self.player.close()
        self.close_project()
        self.open('home')

    """
    谱面编辑页面
    """

    def _open_edit(self) -> None:
        self.window.set_subtitle(self.project_path)
        self.shortcuts[0][pygame.K_ESCAPE] = self.exit

    def _draw_edit(self, start) -> None:
        self.show_button('return', ICONS['return'], (SPLIT_LINE+10, 10), 'topleft',
                         self.exit, 'circle', '返回', 'midleft', 'midright')
        self.window.set_subtitle(self.project_path)

    def _exit_edit(self) -> None:
        self.player.close()
        self.close_project()
        self.open('home')

    """
    设置页面
    """

    def _open_settings(self) -> None:
        self.shortcuts[0][pygame.K_ESCAPE] = self.exit

    def _draw_settings(self, start) -> None:
        self.show_button('return', ICONS['return'], (SPLIT_LINE+10, 10), 'topleft',
                         self.exit, 'circle', '返回', 'midleft', 'midright')

        t = self.window.draw_text('背景模式:'+('纯色' if self.window.bg_mode ==
                                           'color' else '图片'), (SPLIT_LINE+10, start+20), 'topleft')
        t = self.show_button('change_bg_mode', ICONS['change'], (
            WINDOW_SIZE[0]-10, t.centery), 'midright', self.window.change_bg_mode, 'rect')
        t = self.show_button('set_bg', ICONS['set'], (
            self.buttons['change_bg_mode'].rect.left-10, t.centery), 'midright', self.window.bg_config, 'rect')
        if self.window.bg_mode == 'image':
            t = self.window.draw_text(
                '蒙版不透明度:'+str(self.window.mask_alpha), (SPLIT_LINE+10, t.bottom+10), 'topleft')
            t = self.show_slider('change_mask_alpha', (SPLIT_LINE+10, t.bottom+15),
                                 WINDOW_SIZE[0]-SPLIT_LINE-20,  get_value=lambda: self.window.mask_alpha/255, set_value=self.window.set_mask_alpha)

        def draw_color(color: tuple, pos: tuple) -> None:
            """
            绘制颜色小方块。
            """
            pygame.draw.rect(self.window.screen, color, pos, 0, 3)
            pygame.draw.rect(self.window.screen, (255, 255, 255), pos, 1, 3)

        t = self.window.draw_text(
            '主题颜色:', (SPLIT_LINE+10, t.bottom+10), 'topleft')
        draw_color(self.window.main_color, (t.right+5, t.centery-10, 20, 20))
        self.show_button('set_main_color', ICONS['set'], (
            WINDOW_SIZE[0]-10, t.centery), 'midright', self.window.set_main_color, 'rect')

        t = self.window.draw_text(
            '提示颜色:', (SPLIT_LINE+10, t.bottom+10), 'topleft')
        draw_color(self.window.tip_color, (t.right+5, t.centery-10, 20, 20))
        self.show_button('set_tip_color', ICONS['set'], (
            WINDOW_SIZE[0]-10, t.centery), 'midright', self.window.set_tip_color, 'rect')

    def _exit_settings(self) -> None:
        self.open('home')


if __name__ == '__main__':
    App().main()
