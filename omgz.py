import tempfile
import zipfile

import easygui

from omgc import convert


def convert_charts(chart_projects: list) -> tuple:
    """
    批量转换谱面格式。
    参数：一个 list，每个元素均为 dict，含有 4 个 key：level，difficulty，by，json_file。
    返回值：第一项为 str，表示转换后的谱面目录；第二项为 list，与上述类似，但 json_file 改为 md5。
    """
    charts_dir = tempfile.mkdtemp(prefix='Omega-Charts-')


def make_info(name: str, composer: str, illustrator: str, charts_info: list) -> str:
    """
    生成 info 文件。
    参数：前三个为歌曲信息，第四个为 convert_charts() 返回值的第二项。
    返回值：生成的 info 文件 path。
    """


def build(info_path: str, music_path: str, illustration_path: str, charts_dir: str, omgz_path: str) -> None:
    """
    打包成 omgz 文件。
    参数：前三个为 info.json/music.ogg/illustration.png 文件的 path，
    第四个为 convert_charts() 返回值的第一项，第五个为生成的 omgz 文件 path。
    """


def wizard() -> None:
    """
    omgz 文件生成向导。
    """
