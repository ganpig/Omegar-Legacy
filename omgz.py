import hashlib
import os
import pickle
import tempfile
import zipfile

import easygui

import omgc


def convert_charts(charts_info: list) -> tuple:
    """
    批量转换谱面格式。
    参数：一个 list，每个元素均为 dict，含有 4 个 key：difficulty，diff_number，writer，json_path。
    返回值：表示转换后的谱面目录。
    备注：该函数会在 charts_info 的每个元素中添加 key：md5。
    """
    charts_dir = tempfile.mkdtemp(prefix='Omega-Charts-')
    for chart_info in charts_info:
        omgc_path = os.path.join(
            charts_dir, chart_info['difficulty']+'.omgc')
        omgc.convert(chart_info['json_path'], omgc_path)
        chart_info['md5'] = hashlib.md5(
            open(omgc_path, 'rb').read()).hexdigest()
    return charts_dir, charts_info


def make_info(name: str, composer: str, illustrator: str, charts_info: list) -> str:
    """
    生成 info 文件。
    参数：前三个为歌曲信息，第四个为 convert_charts() 返回值的第二项。
    返回值：生成的 info 文件 path。
    """
    with open(tempfile.mkstemp('.omgs')[1], 'w', encoding='utf-8') as f:
        print(name, composer, illustrator, len(charts_info), sep='\n', file=f)
        for chart_info in charts_info:
            print(chart_info['difficulty'], chart_info['diff_number'],
                  chart_info['writer'], chart_info['md5'], sep='\n', file=f)
        return f.name


def build(info_path: str, music_path: str, illustration_path: str, charts_dir: str, omgz_path: str) -> None:
    """
    打包成 omgz 文件。
    参数：前三个为 info.omgs/music.ogg/illustration.png 文件的 path，
    第四个为 convert_charts() 返回值的第一项，第五个为生成的 omgz 文件 path。
    """
    with zipfile.ZipFile(omgz_path, 'w') as f:
        f.write(info_path, 'info.omgs')
        f.write(music_path, 'music.ogg')
        f.write(illustration_path, 'illustration.png')
        for chart_name in os.listdir(charts_dir):
            f.write(os.path.join(charts_dir, chart_name), 'charts/'+chart_name)


def wizard() -> None:
    """
    omgz 文件生成向导。
    """
    if easygui.ynbox('欢迎使用 omgz 文件生成向导!', '生成 omgz 文件', ('使用已有的生成设置', '创建新的生成设置')):
        pickle_path = easygui.fileopenbox('请选择生成设置文件', default='*.pickle')
        if pickle_path:
            name, composer, illustrator, music_path, illustration_path, chart_projects = pickle.load(
                open(pickle_path, 'rb'))
        else:
            return
    else:
        name = easygui.enterbox('请输入曲名', '生成 omgz 文件')
        if not name:
            return

        composer = easygui.enterbox('请输入曲师', '生成 omgz 文件')
        if not composer:
            return

        illustrator = easygui.enterbox('请输入画师', '生成 omgz 文件')
        if not illustrator:
            return

        music_path = easygui.fileopenbox(
            '请选择歌曲音频', default='*.ogg')
        if not music_path:
            return

        illustration_path = easygui.fileopenbox(
            '请选择曲绘', default='*.png')
        if not illustration_path:
            return

        chart_projects = []
        while True:
            if chart_projects:
                if not easygui.ynbox('\n'.join((f'已添加 {len(chart_projects)} 张谱面:', *[i['difficulty']+' By '+i['writer'] for i in chart_projects])), '生成 omgz 文件', ('继续', '完成')):
                    break

            difficulty = easygui.enterbox(
                '请输入谱面难度', f'添加第 {len(chart_projects)+1} 张谱面')
            if not difficulty:
                continue

            diff_number = easygui.enterbox(
                '请输入谱面定数', f'添加第 {len(chart_projects)+1} 张谱面')
            if not diff_number:
                continue

            writer = easygui.enterbox(
                '请输入谱师', f'添加第 {len(chart_projects)+1} 张谱面')
            if not writer:
                continue

            json_path = easygui.fileopenbox(
                '请选择谱面工程文件', default='*.json')
            if not json_path:
                continue

            chart_projects.append(
                {'difficulty': difficulty, 'diff_number': diff_number, 'writer': writer, 'json_path': json_path})

    charts_dir, charts_info = convert_charts(chart_projects)
    info_path = make_info(name, composer, illustrator, charts_info)
    omgz_path = easygui.filesavebox('保存 omgz 文件', default=name+'.omgz')
    build(info_path, music_path, illustration_path, charts_dir, omgz_path)
    if easygui.ynbox('成功保存为 '+omgz_path, '生成 omgz 文件', ('保存生成设置', '完成')):
        pickle_path = easygui.filesavebox('保存生成设置', default=name+'.pickle')
        if pickle_path:
            pickle.dump((name, composer, illustrator, music_path,
                        illustration_path, chart_projects), open(pickle_path, 'wb'))
            easygui.msgbox('生成设置保存成功!', '生成 omgz 文件')


if __name__ == '__main__':
    wizard()
