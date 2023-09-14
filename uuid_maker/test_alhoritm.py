import cv2
from xml.etree import ElementTree as ET
from pathlib import Path
import numpy as np


# Константы
VIPER = "{http://lamp.cfar.umd.edu/viper#}"
VIPERDATA = "{http://lamp.cfar.umd.edu/viperdata#}"
#

# Допп классы


class Position:
    def __init__(self, x, y, height, width):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
#


video = cv2.VideoCapture(
    r"C:\Users\smeta\source\repos\WintreistsPractice\xgtf_video\59.Gl.korpus_vhod_Holl_č.2_Glav.Korp.-_Kam_3_2017-02-10_09-59-09_713__2h10m28s__00s_10m.mkv")
xgtf = ET.parse(Path(r"C:\Users\smeta\source\repos\WintreistsPractice\xgtf_video\59.Gl.korpus_vhod_Holl_č.2_Glav.Korp.-_Kam_3_2017-02-10_09-59-09_713__2h10m28s__00s_10m.xgtf"))


sourcefile = xgtf.getroot().find(f"./{VIPER}data/{VIPER}sourcefile")


file_name = Path(sourcefile.attrib['filename']).name
video_framerate = 1  # video.get(cv2.CAP_PROP_FPS)
xgtf_folder = Path(
    r'C:\Users\smeta\source\repos\WintreistsPractice\xgtf_video')
xgtf_folder.joinpath("result").mkdir(exist_ok=True)


for xgtf_object in sourcefile.findall(f"./{VIPER}object"):
    objects_video = {}
    object_id = int(xgtf_object.attrib['id'])
    # ET.dump(xgtf_object)

    max_width, max_height = 0, 0

    for bbox in xgtf_object.findall(f'./{VIPER}attribute[@name="Position"]/'):
        framespan_borders = list(map(int, bbox.attrib['framespan'].split(":")))
        x = int(bbox.attrib['x'])
        y = int(bbox.attrib['y'])
        height = int(bbox.attrib['height'])
        width = int(bbox.attrib['width'])

        for frame in range(framespan_borders[0], framespan_borders[1]+1):
            object_frame_info = {
                'Truncated': False,
                'Difficult': False,
                'Position': Position(x, y, height, width)
            }
            objects_video[frame] = object_frame_info
    for truncated_info in xgtf_object.findall(f'./{VIPER}attribute[@name="Truncated"]/'):
        framespan_borders = list(
            map(int, truncated_info.attrib['framespan'].split(":")))
        for frame in range(framespan_borders[0], framespan_borders[1]+1):
            if truncated_info.attrib['value'] == 'true':
                try:
                    objects_video[frame]['Truncated'] = True
                except KeyError:
                    pass
    for difficult_info in xgtf_object.findall(f'./{VIPER}attribute[@name="Difficult"]/'):
        if difficult_info.attrib['value'] == 'true':
            framespan_borders = list(
                map(int, difficult_info.attrib['framespan'].split(":")))
            for frame in range(framespan_borders[0], framespan_borders[1]+1):
                try:
                    objects_video[frame]['Difficult'] = True
                except KeyError:
                    pass
    num_of_clear_data_frames = sum(
        [not (objects_video[key]['Truncated'] or objects_video[key]['Difficult']) for key in objects_video])
    temp_objects_video = {}
    if num_of_clear_data_frames < 16:
        keys = list(objects_video.keys())
        for index in range(len(objects_video.keys())):
            key = keys[index]
            if not (objects_video[key]['Truncated'] or objects_video[key]['Difficult']):
                temp_objects_video[key] = objects_video[key]
                del objects_video[key]
        for item in [objects_video[list(objects_video.keys())[index]] for index in range(0, len(objects_video), len(objects_video)//(15-num_of_clear_data_frames))]:
            temp_objects_video[list(objects_video.keys())[
                list(objects_video.values()).index(item)]] = item

        from collections import OrderedDict
        temp_objects_video = dict(OrderedDict(
            sorted(temp_objects_video.items())))
    else:
        for i in [objects_video[list(objects_video.keys())[i]] for i in range(0, len(objects_video), len(objects_video)//15)]:
            temp_objects_video[list(objects_video.keys())[
                list(objects_video.values()).index(i)]] = i
    objects_video = temp_objects_video

    for frame in objects_video:
        max_width = max(max_width, objects_video[frame]['Position'].width)
        max_height = max(max_height, objects_video[frame]['Position'].height)

    video.set(cv2.CAP_PROP_POS_FRAMES, 0)
    video_frame_number = 0

    output_video_path = xgtf_folder.joinpath('result').joinpath(
        file_name+"_!_"+f"{object_id}"+"_object_id"+".mkv")
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out_video = cv2.VideoWriter(
        str(output_video_path), fourcc, video_framerate, (max_width, max_height))

    for frame in objects_video:
        if video_frame_number != frame:
            video.set(cv2.CAP_PROP_POS_FRAMES, frame)
            video_frame_number = frame
        ret, video_frame = video.read()
        video_frame_number += 1
        if ret:
            object_frame_info = objects_video[frame]
            position: Position = object_frame_info['Position']
            object_border = video_frame[position.y:position.y +
                                        position.height, position.x:position.x+position.width]

            background = np.zeros((max_height, max_width, 3), dtype=np.uint8)
            background.fill(128)
            h, w, _ = object_border.shape
            x_offset = (max_width - w) // 2
            y_offset = (max_height - h) // 2
            background[y_offset:y_offset+h,
                       x_offset:x_offset+w] = object_border
            out_video.write(background)

    out_video.release()

video.release()
