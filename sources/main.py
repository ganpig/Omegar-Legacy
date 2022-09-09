import configparser
import hashlib
import json
import math
import os
import pickle
import shutil
import struct
import tempfile
import time
import zipfile

import easygui
import pygame

from common import *
from player import Player
from ui import *


class App:
    tmp_beats: dict = {}
    buttons: dict = {}  # 按钮
    earliest_beat: float = 0
    later_buttons: dict = {}  # 延迟添加的按钮
    later_del_buttons: list = []  # 延迟删除的按钮
    sliders: dict = {}  # 滑动条
    project_path: str = ''  # 项目文件路径
    project_data: dict = {}  # 项目数据

    def __init__(self) -> None:
        cp = configparser.ConfigParser()
        if os.path.isfile('config.ini'):
            try:
                cp.read('config.ini', encoding='utf-8')
            except:
                pass
        self.window = Window(cp)
        self.window.on_exit = self.close_project
        self.player = Player()
        self.open('home')

    """
    基本操作
    """

    def open(self, page) -> None:
        """
        打开页面。
        """
        self.page = page
        self.page_open_time = time.time()
        self.buttons = {}
        self.sliders = {}
        try:
            eval('self._open_'+page)()
        except:
            pass

    def draw(self) -> None:
        """
        绘制当前页面。
        """
        self.window.draw_frame()
        start = self.window.draw_text(PAGE_NAME[self.page], ((SPLIT_LINE+WINDOW_SIZE[0])//2, 10-max(
            0, 1-(time.time()-self.page_open_time)/0.3)**2*100), 'midtop', 3).bottom
        eval('self._draw_'+self.page)(start)
        self.window.update()

    def exit(self) -> None:
        try:
            eval('self._exit_'+self.page)()
        except:
            pass

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
            elif event.type == pygame.USEREVENT:
                self.player.replay()
        self.buttons.update(self.later_buttons)
        self.later_buttons = {}
        for i in self.later_del_buttons:
            del self.buttons[i]
        self.later_del_buttons = []

    """
    UI 操作
    """

    def show_button(self, name: str, icon: pygame.Surface, pos: tuple, align: str = 'topleft', todo=easygui.msgbox, background: str = '', text: str = '', text_align: str = 'midright', button_align: str = 'midleft', todo_with_arg: bool = False, todo_right=None) -> None:
        """
        添加或更新并显示按钮。
        """
        if name not in self.buttons:
            self.buttons[name] = Button(
                self.window, icon, pos, align, todo, background, text, text_align, button_align, todo_with_arg, todo_right)
        elif icon != self.buttons[name].icon:
            self.buttons[name].change_icon(icon)
        else:
            self.buttons[name].move(pos)
        return self.buttons[name].show()

    def show_slider(self, name: str, pos: tuple, length: int, width: int = 10, align: str = 'topleft', get_value=None, set_value=None, set_directly=None, get_text=None, text_align: str = 'midright', button_align: str = 'midleft',) -> None:
        """
        添加或更新并显示滑动条。
        """
        if name not in self.sliders:
            self.sliders[name] = Slider(
                self.window, pos, length, width, align, get_value, set_value, set_directly, get_text, text_align, button_align)
        else:
            self.sliders[name].move(pos)
        return self.sliders[name].show()

    def later_add_button(self, name: str, icon: pygame.Surface, pos: tuple, align: str = 'topleft', todo=easygui.msgbox, background: str = '', text: str = '', text_align: str = 'midright', button_align: str = 'midleft', todo_with_arg: bool = False, todo_right=None) -> None:
        """
        延迟添加按钮。
        """
        self.later_buttons[name] = Button(self.window, icon, pos, align, todo,
                                          background, text, text_align, button_align, todo_with_arg, todo_right)

    def later_del_button(self, name: str) -> None:
        """
        延迟删除按钮。
        """
        self.later_del_buttons.append(name)

    """
    项目操作
    """

    def create_project_wizard(self) -> None:
        """
        创建项目向导。
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
                '请先保存项目文件', WINDOW_TITLE, project_name+'.json', ['*.json'])
            if not project_path:
                return
            self.project_path = project_path
            self.project_data = {
                "project_name": project_name,
                "music_path": music_path,
                "beats": [],
                "notes": [],
                "line": {
                    "initial_position": DEFAULT_LINE_INITIAL_POSITION,
                    "motions": []
                }
            }
            self.open('pick_beats')
        except:
            easygui.exceptionbox('创建项目失败！', WINDOW_TITLE)
            self.return_home()

    def open_project(self) -> None:
        """
        打开项目。
        """
        try:
            project_path = easygui.fileopenbox(
                '打开项目', WINDOW_TITLE, '*.json', ['*.json'])
            if not project_path:
                return
            self.project_path = project_path
            self.project_data = json.load(open(project_path))
            if self.project_data['beats']:
                self.open('edit')
            else:
                self.open('pick_beats')

        except:
            easygui.exceptionbox('打开项目失败！', WINDOW_TITLE)
            self.return_home()

    def save_project(self, path=None) -> None:
        """
        保存项目。
        """
        json.dump(self.project_data, open(
            path if path else self.project_path, 'w'), indent=4)

    def close_project(self) -> None:
        """
        保存并关闭项目。
        """
        if self.project_path:
            if not os.path.isdir('Autosave'):
                os.makedirs('Autosave')
            self.save_project(os.path.join(
                'Autosave', f'{self.project_data["project_name"]}_{int(time.time())}.json'))
            if easygui.ynbox(f'是否保存项目文件为 {self.project_path}？', '关闭项目', ('保存', '不保存')):
                self.save_project()
            self.project_path = ''
            self.project_data = {}

    def export_project_wizard(self) -> None:
        """
        导出项目向导。
        """

        def convert_chart(json_path: str, omgc_path: str) -> None:
            """
            将 json 项目文件转换为 omgc 谱面文件。
            参数：两个文件的 path。
            """
            project_data = json.load(open(json_path))  # 读取 json 数据
            instructions = []  # 谱面指令列表
            beats = [j for i in project_data['beats'] for j in i]  # 节拍对应的秒数

            def beat2sec(beat: int or float) -> float:
                """
                将拍数转换为秒数。
                """
                beat -= 1
                if int(beat) == beat:
                    beat = int(beat)
                if beat < 0:
                    # 根据开头两拍确定的直线计算
                    return (beats[1]-beats[0])*beat+beats[0]
                elif beat > len(beats)-1:
                    # 根据结尾两拍确定的直线计算
                    return (beats[-1]-beats[-2])*(beat-len(beats)+1)+beats[-1]
                elif type(beat) == int:
                    # 直接作为下标获取
                    return beats[beat]
                else:
                    # 根据前后两拍确定的直线计算
                    last_beat = math.floor(beat)
                    next_beat = math.ceil(beat)
                    return beats[last_beat]*(next_beat-beat)+beats[next_beat]*(beat-last_beat)

            def process_changes(initial_val: int, changes: list) -> dict:
                """
                处理缓动。
                """
                changes_processed = {}
                cur_val = initial_val
                for change in changes:
                    t_0 = beat2sec(change['start'])  # 初时间
                    t_1 = beat2sec(change['end'])  # 末时间
                    val_0 = cur_val  # 初值
                    val_1 = cur_val = change['target']  # 末值
                    moving_type = change['type']
                    if moving_type == LINEAR_SLOW_MOVING:  # 线性缓动
                        k = (val_1-val_0)/(t_1-t_0)
                        b = (t_1*val_0-t_0*val_1)/(t_1-t_0)
                        changes_processed[t_0] = (moving_type, k, b)
                    elif moving_type == SIN_SLOW_MOVING:  # 正弦缓动
                        A = (val_0-val_1)/2
                        o = math.pi/(t_0-t_1)
                        p = o*(t_0+t_1)/2
                        b = (val_0+val_1)/2
                        changes_processed[t_0] = (moving_type, A, o, p, b)
                    changes_processed[t_1] = (LINEAR_SLOW_MOVING, 0, val_1)
                return changes_processed

            for note in project_data['notes']:
                start_time = beat2sec(note['start'])  # 判定秒数
                end_time = beat2sec(note['end'])  # 结束秒数
                key_points = list((beat2sec(i), j) for i, j
                                  in note['speed_key_points'])  # 转换关键点列表
                key_points.append((math.inf, key_points[-1][1]))
                cur_point_pos = 0  # 当前关键点的 note 位置
                key_points_abc = []  # 位置函数列表

                for i in range(len(key_points)-1):  # 通过关键点计算二次函数
                    k = (key_points[i+1][1]-key_points[i][1]) / \
                        (key_points[i+1][0]-key_points[i][0])  # 速度函数斜率
                    a = k/2  # 对速度函数做不定积分
                    b = key_points[i][1]-k*key_points[i][0]  # 将当前关键点代入速度函数求解 b

                    def first_two(x):
                        """
                        计算二次函数前两项之和。
                        """
                        return a*x**2+b*x  #
                    # 将当前关键点代入二次函数求解 c
                    c = cur_point_pos-first_two(key_points[i][0])
                    key_points_abc.append([key_points[i][0], a, b, c])
                    if key_points[i][0] <= start_time < key_points[i+1][0]:  # 开始时间处于当前区间
                        # 计算 note 开始时的位置以便后续计算显示长度
                        start_pos = first_two(start_time)+c
                    if key_points[i][0] <= end_time < key_points[i+1][0]:  # 结束时间处于当前区间
                        # 计算 note 结束时的位置以便后续计算显示长度
                        end_pos = first_two(end_time)+c
                    cur_point_pos = first_two(
                        key_points[i+1][0])+c  # 将下一个关键点代入二次函数
                for i in range(len(key_points_abc)):
                    # 使 note 判定时的位置为 0，即与判定线重合
                    key_points_abc[i][-1] -= start_pos

                if TOP_EDGE <= key_points_abc[0][-1] <= BOTTOM_EDGE:  # note 开始就可见
                    activate_time = -PREACTIVATING_TIME  # 提前激活 note
                else:
                    for i in range(len(key_points_abc)-1):
                        t_0, a, b, c = key_points_abc[i]
                        t_1 = key_points_abc[i+1][0]

                        def solve(pos):
                            """
                            解方程，返回区间内的最小解，若无解则返回 inf。
                            """
                            if b == 0:  # 不是方程
                                return math.inf
                            elif a == 0:  # 一元一次方程
                                x = (pos-c)/b
                                if t_0 <= x <= t_1:
                                    return x
                            else:  # 一元二次方程
                                d = b**2-4*a*(c-pos)  # 求根判别式
                                if d >= 0:  # 在实数范围内有解
                                    x_1 = (-b-math.sqrt(d))/(2*a)  # 较小的根
                                    x_2 = (-b+math.sqrt(d))/(2*a)  # 较大的根
                                    if t_0 <= x_1 <= t_1:
                                        return x_1
                                    elif t_0 <= x_2 <= t_1:
                                        return x_2
                            return math.inf
                        t = min(solve(TOP_EDGE), solve(
                            BOTTOM_EDGE))  # 更早经过哪边就是从哪边出现
                        if t != math.inf:
                            activate_time = t-PREACTIVATING_TIME
                            break

                instr_add = [0]*10  # 初始化长度为 10 的数组
                instr_add[0] = note['id']  # note 的 ID
                instr_add[1] = sum(
                    j for i, j in NOTE_PROPERTIES if note[i])  # note 的属性
                instr_add[2:5] = map(
                    float, key_points_abc.pop(0)[1:])  # 初始位置函数
                instr_add[5] = note['initial_showing_track']  # 初始显示轨道
                instr_add[6] = note['judging_track']  # 实际判定轨道
                instr_add[7] = float(start_time)  # 开始时间
                instr_add[8] = float(end_time)  # 结束时间
                instr_add[9] = float(end_pos-start_pos)  # 显示长度
                instructions.append((-1, ADD_NOTE, *instr_add))  # 添加 note 指令

                instructions.append((activate_time, ACTIVATE_NOTE,
                                    note['id']))  # 激活 note 指令

                for t, a, b, c in key_points_abc:
                    instructions.append((float(t), CHANGE_NOTE_POS, note['id'],
                                        float(a), float(b), float(c)))  # 改变 note 位置函数指令

                showing_track_changes_processed = process_changes(
                    note['initial_showing_track'], note['showing_track_changes'])
                for t in showing_track_changes_processed:
                    instructions.append((t, CHANGE_NOTE_TRACK,
                                        *showing_track_changes_processed[t]))  # 改变 note 轨道函数指令

            line_motions_processed = process_changes(
                project_data['line']['initial_position'], project_data['line']['motions'])
            for t in line_motions_processed:
                instructions.append((t, CHANGE_LINE_POS,
                                    *line_motions_processed[t]))  # 改变判定线位置函数指令

            instructions_processed = [len(instructions)]
            for instruction in sorted(instructions):
                instructions_processed.extend(instruction)
            with open(omgc_path, 'wb') as f:
                for data in instructions_processed:
                    f.write(struct.pack(WRITING_FORMATS[type(data)], data))

        def convert_charts(charts_info: list) -> None:
            """
            批量转换谱面格式。
            参数：一个 list，每个元素均为 dict，含有 4 个 key：difficulty，diff_number，writer，json_path。
            功能：在该 list 的每个元素中添加 2 个 key：omgc_path，md5。
            """
            for chart_info in charts_info:
                chart_info['omgc_path'] = tempfile.mkstemp()[
                    1]  # 获取临时 omgc 文件名
                convert_chart(chart_info['json_path'], chart_info['omgc_path'])
                chart_info['md5'] = hashlib.md5(open(chart_info['omgc_path'], 'rb')
                                                .read()).hexdigest()  # 计算 omgc 文件 MD5

        def make_info(name: str, composer: str, illustrator: str, charts_info: list) -> str:
            """
            生成 info.omgs 文件。
            参数：前三个为歌曲信息，第四个为 convert_charts() 处理后的谱面信息。
            返回值：生成的 info 文件 path。
            """
            with open(tempfile.mkstemp()[1], 'w', encoding='utf-8') as f:
                print(name, composer, illustrator, len(
                    charts_info), sep='\n', file=f)  # 写入歌曲信息
                for chart_info in charts_info:
                    print(chart_info['difficulty'], chart_info['diff_number'],
                          chart_info['writer'], chart_info['md5'], sep='\n', file=f)  # 写入谱面信息
                return f.name

        def build_omgz(info_path: str, music_path: str, illustration_path: str, charts_info: list, omgz_path: str) -> None:
            """
            打包成 omgz 文件。
            参数：前三个为 info.omgs/music.ogg/illustration.png 文件的 path，
            第四个为 convert_charts() 处理后的谱面信息，第五个为生成的 omgz 文件 path。
            """
            with zipfile.ZipFile(omgz_path, 'w') as f:
                f.write(info_path, 'info.omgs')
                f.write(music_path, 'music.ogg')
                f.write(illustration_path, 'illustration.png')
                for chart_info in charts_info:
                    f.write(chart_info['omgc_path'], 'charts/' +
                            chart_info['difficulty']+'.omgc')

        def build_folder(info_path: str, music_path: str, illustration_path: str, charts_info: list, folder_path: str) -> None:
            """
            生成歌曲文件夹。
            参数：前三个为 info.omgs/music.ogg/illustration.png 文件的 path，
            第四个为 convert_charts() 处理后的谱面信息，第五个为生成的文件夹 path。
            """
            if os.path.isdir(folder_path):
                shutil.rmtree(folder_path)  # 删除即清空文件夹
            # 建立文件夹及子文件夹 charts
            os.makedirs(os.path.join(folder_path, 'charts'))
            shutil.copy(info_path, os.path.join(folder_path, 'info.omgs'))
            shutil.copy(music_path, os.path.join(folder_path, 'music.ogg'))
            shutil.copy(illustration_path, os.path.join(
                folder_path, 'illustration.png'))
            for chart_info in charts_info:
                shutil.copy(chart_info['omgc_path'],
                            os.path.join(folder_path, 'charts', chart_info['difficulty']+'.omgc'))

        try:
            ch = easygui.buttonbox(
                '是否使用已有的生成设置？（首次使用请选择后者）', '导出项目', ('使用已有生成设置', '创建新的生成设置'))
            if ch == '使用已有生成设置':
                using_pickle = True
                pickle_path = easygui.fileopenbox(
                    '请选择生成设置文件', '导出项目', '*.pickle', ['*.pickle'])
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
                    '保存生成设置', '导出项目', name+'.pickle', ['*.pickle'])  # 将生成设置保存到 pickle 文件
                if pickle_path:
                    pickle.dump((name, composer, illustrator, music_path,
                                illustration_path, charts_info), open(pickle_path, 'wb'))
                    easygui.msgbox('生成设置保存成功!', '导出项目', '好耶')

    """
    首页
    """

    def _open_home(self) -> None:
        self.window.set_subtitle()

    def _draw_home(self, start) -> None:
        self.show_button('settings', ICONS['settings'], (WINDOW_SIZE[0]-10, WINDOW_SIZE[1]-10),
                         'bottomright', lambda: self.open('settings'), 'circle', '设置')

        t = self.window.draw_text(
            '创建项目', (SPLIT_LINE+10, start+20), 'topleft')
        self.show_button('new', ICONS['go'], (WINDOW_SIZE[0]-10,
                                              t.centery), 'midright', self.create_project_wizard, 'circle', '进入')

        t = self.window.draw_text(
            '打开项目', (SPLIT_LINE+10, t.bottom+10), 'topleft')
        self.show_button('open', ICONS['go'], (WINDOW_SIZE[0]-10,
                                               t.centery), 'midright', self.open_project, 'circle', '进入')

        t = self.window.draw_text(
            '导出项目', (SPLIT_LINE+10, t.bottom+10), 'topleft')
        self.show_button('export', ICONS['go'], (WINDOW_SIZE[0]-10,
                                                 t.centery), 'midright', self.export_project_wizard, 'circle', '进入')

    """
    采拍页面
    """

    def _open_pick_beats(self) -> None:
        self.player.open(self.project_data['music_path'])
        self.window.set_subtitle(self.project_path)
        self.earliest_beat = math.inf
        self.tmp_beats = {}  # key 为时间，value 为 True 表示强拍，False 表示弱拍

    def _draw_pick_beats(self, start) -> None:
        self.show_button('return', ICONS['return'], (SPLIT_LINE+10, 10), 'topleft',
                         self.exit, 'circle', '返回', 'midleft', 'midright')

        def play_or_pause(button: Button) -> None:
            if self.player.get_playing():
                self.player.pause()
                button.change_icon(ICONS['play'])
            else:
                self.player.play()
                button.change_icon(ICONS['pause'])
        t1 = self.show_button(
            'play_or_pause', ICONS['pause' if self.player.get_playing() else 'play'], (10, 0), 'topleft', play_or_pause, 'rect', '播放/暂停', 'midleft', 'midright', True)

        def process_beat() -> None:
            tmp = []
            sorted_beats = sorted(self.tmp_beats)
            self.earliest_beat = sorted_beats[0]
            for i in sorted_beats:
                if self.tmp_beats[i]:
                    tmp.append([i])
                else:
                    tmp[-1].append(i)
            self.project_data['beats'] = tmp

        def delete_beat(sec: float) -> None:
            del self.tmp_beats[sec]
            self.later_del_button(sec)

        def add_beat(sec: float, strong: bool) -> None:
            if sec < self.earliest_beat:
                self.earliest_beat = sec
                strong = True
            self.tmp_beats[sec] = strong
            self.later_add_button(sec, ICONS['orange_beat' if strong else 'green_beat'], (0, 0), 'center', lambda: self.player.set_pos(
                sec), 'circle', '左击定位到此，右击删除拍子', 'midtop', 'midbottom', todo_right=lambda: delete_beat(sec))

        t2 = self.show_button('add_beat', ICONS['add'], (SPLIT_LINE-10, 10), 'topright', lambda: add_beat(self.player.get_pos(
        ), False), 'rect', '左击添加弱拍，右击添加强拍'if self.player.get_pos() > self.earliest_beat else '添加强拍', todo_right=lambda: add_beat(self.player.get_pos(), True))

        def set_player_pos() -> None:
            pos = easygui.enterbox('请输入定位秒数', '控制播放进度')
            if pos:
                try:
                    self.player.set_pos(float(pos))
                except:
                    easygui.msgbox('请输入一个整数或小数！', '控制播放进度')
        t = self.show_slider('music_pos', (t1.right+10, t1.centery), t2.left-t1.right-20, align='midleft', get_value=self.player.get_prog,
                             set_value=self.player.set_prog, set_directly=set_player_pos, get_text=self.player.get_text, text_align='midtop', button_align='midbottom')

        pygame.draw.line(self.window.screen, self.window.main_color, (SPLIT_LINE/2,
                         WINDOW_SIZE[1]/2-50), (SPLIT_LINE/2, WINDOW_SIZE[1]/2+50), 5)

        for sec in self.buttons:
            if type(sec) == float:
                pos = SPLIT_LINE/2+PICK_BEAT_SPEED*(sec-self.player.get_pos())
                self.buttons[sec].move((pos, WINDOW_SIZE[1]/2))
                if 0 < self.buttons[sec].rect.right < SPLIT_LINE:
                    self.buttons[sec].show()

    def _exit_pick_beats(self) -> None:
        self.player.close()
        self.close_project()
        self.open('home')

    """
    谱面编辑页面
    """

    def _open_edit(self) -> None:
        self.window.set_subtitle(self.project_path)

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
        self.save_and_close()
        self.open('home')


if __name__ == '__main__':
    app = App()
    while True:
        app.draw()
        app.process_events()
