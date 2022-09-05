import bisect
import hashlib
import json
import math
import os
import pickle
import shutil
import struct
import tempfile
import zipfile

import popup

# 事件列表
ADD_NOTE = 0x01
CHANGE_NOTE_POS = 0x02
CHANGE_NOTE_TRACK = 0x03
ACTIVATE_NOTE = 0x04
CHANGE_LINE_POS = 0x10

# 用 2 的整数次幂表示 note 属性以便通过加法运算合并属性
PROPERTIES = [
    ('property_1', 1 << 0),
    ('property_2', 1 << 1),
    ('property_3', 1 << 2),
    ('property_4', 1 << 3)
]


def convert_chart(json_path: str, omgc_path: str) -> None:
    """
    将 json 工程文件转换为 omgc 谱面文件。
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

    for note in project_data['notes']:
        start_time = beat2sec(note['start'])  # 判定秒数
        end_time = beat2sec(note['end'])  # 结束秒数
        key_points = list((beat2sec(i), j) for i, j
                          in note['speed_key_points'])  # 转换关键点列表
        key_points.append((float('inf'), key_points[-1][1]))
        cur_point_pos = 0  # 当前关键点的 note 位置
        key_points_abc = []  # 位置函数列表

        for i in range(len(key_points)-1):  # 通过关键点计算二次函数
            k = (key_points[i+1][1]-key_points[i][1]) / \
                (key_points[i+1][0]-key_points[i][0])  # 速度函数斜率
            a = k/2  # 对速度函数做不定积分
            b = key_points[i][1]-k*key_points[i][0]  # 将当前关键点代入速度函数求解 b
            def first_two(x): return a*x**2+b*x  # 计算二次函数前两项之和
            c = cur_point_pos-first_two(key_points[i][0])  # 将当前关键点代入二次函数求解 c
            key_points_abc.append([key_points[i][0], a, b, c])
            if key_points[i][0] <= start_time < key_points[i+1][0]:  # 开始时间处于当前区间
                start_pos = first_two(start_time)+c  # 计算 note 开始时的位置以便后续计算显示长度
            if key_points[i][0] <= end_time < key_points[i+1][0]:  # 结束时间处于当前区间
                end_pos = first_two(end_time)+c  # 计算 note 结束时的位置以便后续计算显示长度
            cur_point_pos = first_two(key_points[i+1][0])+c  # 将下一个关键点代入二次函数
        for i in range(len(key_points_abc)):
            key_points_abc[i][-1] -= start_pos  # 使 note 判定时的位置为 0，即与判定线重合

        add_instr = [0]*10  # 初始化长度为 10 的数组
        add_instr[0] = note['id']  # note 的 ID
        add_instr[1] = sum(j for i, j in PROPERTIES if note[i])  # note 的属性
        add_instr[2:5] = key_points_abc.pop(0)[1:]  # 初始位置函数
        add_instr[5] = note['initial_showing_track']  # 初始显示轨道
        add_instr[6] = note['judging_track']  # 实际判定轨道
        add_instr[7] = start_time  # 开始时间
        add_instr[8] = end_time  # 结束时间
        add_instr[9] = end_pos-start_pos  # 显示长度
        instructions.append((-1, ADD_NOTE, *add_instr))  # 添加指令


def convert_charts(charts_info: list) -> None:
    """
    批量转换谱面格式。
    参数：一个 list，每个元素均为 dict，含有 4 个 key：difficulty，diff_number，writer，json_path。
    功能：在该 list 的每个元素中添加 2 个 key：omgc_path，md5。
    """
    for chart_info in charts_info:
        chart_info['omgc_path'] = tempfile.mkstemp()[1]  # 获取临时 omgc 文件名
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
    os.makedirs(os.path.join(folder_path, 'charts'))  # 建立文件夹及子文件夹 charts
    shutil.copy(info_path, os.path.join(folder_path, 'info.omgs'))
    shutil.copy(music_path, os.path.join(folder_path, 'music.ogg'))
    shutil.copy(illustration_path, os.path.join(
        folder_path, 'illustration.png'))
    for chart_info in charts_info:
        shutil.copy(chart_info['omgc_path'],
                    os.path.join(folder_path, 'charts', charts_info['difficulty']+'.omgc'))


def export_wizard() -> None:
    """
    导出向导。
    """
    if popup.yesno('是否使用已有的生成设置?', '导出'):
        pickle_path = popup.open('请选择生成设置文件', '生成设置文件', 'pickle')
        if pickle_path:
            name, composer, illustrator, music_path, illustration_path, charts_info = pickle.load(
                open(pickle_path, 'rb'))  # 从 pickle 文件读取生成设置
        else:
            return
    else:
        name = popup.input('请输入曲名', '导出')
        if not name:
            return

        composer = popup.input('请输入曲师', '导出')
        if not composer:
            return

        illustrator = popup.input('请输入画师', '导出')
        if not illustrator:
            return

        music_path = popup.open('请选择歌曲音频', '歌曲音频', 'ogg')
        if not music_path:
            return

        illustration_path = popup.open('请选择曲绘', '曲绘', 'png')
        if not illustration_path:
            return

        charts_info = []
        while True:
            if charts_info:  # 一张谱面都没添加时无法继续
                if not popup.yesno(f'已添加 {len(charts_info)} 张谱面，是否继续？', '导出'):
                    break

            difficulty = popup.input(
                '请输入谱面难度', f'添加第 {len(charts_info)+1} 张谱面')
            if not difficulty:
                continue

            diff_number = popup.input(
                '请输入谱面定数', f'添加第 {len(charts_info)+1} 张谱面')
            if not diff_number:
                continue

            writer = popup.input(
                '请输入谱师', f'添加第 {len(charts_info)+1} 张谱面')
            if not writer:
                continue

            json_path = popup.open('请选择谱面工程文件', '谱面工程文件', 'json')
            if not json_path:
                continue

            charts_info.append(
                {'difficulty': difficulty, 'diff_number': diff_number, 'writer': writer, 'json_path': json_path})

    convert_charts(charts_info)
    info_path = make_info(name, composer, illustrator, charts_info)

    if popup.yesno('是否打包成 omgz 文件？', '导出'):
        ok = omgz_path = popup.save(
            '保存 omgz 文件', name+'.omgz', 'Omega 曲谱文件', 'omgz')
        if ok:
            build_omgz(info_path, music_path,
                       illustration_path, charts_info, omgz_path)
    else:
        popup.print('建议新建文件夹，否则选择的文件夹将被清空！', '导出')
        ok = folder_path = popup.folder('选择导出文件夹')
        if ok:
            build_folder(info_path, music_path, illustration_path,
                         charts_info, folder_path)

    if popup.yesno('是否保存生成设置？', '文件已导出' if ok else '文件未导出'):
        pickle_path = popup.save(
            '保存生成设置', name+'.pickle', '生成设置文件', 'pickle')  # 将生成设置保存到 pickle 文件
        if pickle_path:
            pickle.dump((name, composer, illustrator, music_path,
                        illustration_path, charts_info), open(pickle_path, 'wb'))
            popup.print('生成设置保存成功!', '导出')


if __name__ == '__main__':
    export_wizard()
