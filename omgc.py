import json
import struct


# 游戏可见区域中判定线上方像素数
ABOVE_PIXEL = 500

# event 编号
SHOW_NOTE = 0x01
CHANGE_SPEED = 0x02


def frac_to_float(frac: list) -> float:
    """
    将分数（[分子,分母]形式）转换为浮点型。
    """
    return frac[0]/frac[1]


def convert(json_path: str, omgc_path: str) -> None:
    """
    将 json 工程文件转换为 omgc 谱面文件。
    """
    notes = []
    events = []
    data = []
    sections = json.load(open(json_path, 'r'))  # 将 json 文件加载为 Section 列表

    for section in sections:
        # Section 0拍对应的时间 (ms)
        section_start_time = section['start']
        # 该 Section 每拍长度 (ms)
        beat_time = 60000/section['bpm']
        for note in section['notes']:
            # note 所在的轨道 (0~3)
            note_track = note['track']
            # note 点击拍数
            note_start_beat = frac_to_float(note['beat'])
            # note 点击时间 (ms)
            note_start_time = int(
                section_start_time+note_start_beat*beat_time)
            # note 持续拍数
            note_length_beat = frac_to_float(note['length'])
            # note 结束时间 (ms)
            note_end_time = int(section_start_time +
                                (note_start_beat+note_length_beat)*beat_time)
            # note 初始速度 (pixel/s)
            note_initial_speed = note['initialSpeed']
            # note 出现时间 (ms)
            note_appear_time = int(
                note_start_time-ABOVE_PIXEL/note_initial_speed*1000)

            # note 编号
            note_id = len(notes)
            # 添加 note
            notes.append(
                (note_track, note_start_time, note_end_time, note_initial_speed))
            # 添加 note 显示事件
            events.append((note_appear_time, SHOW_NOTE, note_id))
            for change_beat_frac, change_speed in note['changeSpeed']:
                # 变速拍数
                change_beat = frac_to_float(change_beat_frac)
                # 变速时间 (ms)
                change_time = int(section_start_time+change_beat*beat_time)
                events.append(
                    (change_time, CHANGE_SPEED, note_id, change_speed))

    data.append(len(notes))  # note 总数
    for note in notes:
        data.extend(note)
    data.append(len(events))  # event 总数
    for event in sorted(events):  # 按时间排序
        data.extend(event)

    with open(omgc_path, 'wb') as f:
        for i in data:
            f.write(struct.pack('>I', i))  # 作为 4 字节大端整型写入到文件