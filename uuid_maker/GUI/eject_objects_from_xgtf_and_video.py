from pathlib import Path
import io
import os
import typing
from dataclasses import dataclass, field

import cv2
from lxml import etree as ET
import numpy as np

from .modules.classes import Position, ObjectData, EjectedObjectFrameInfo



# Константы
VIPER = "{http://lamp.cfar.umd.edu/viper#}"
VIPERDATA = "{http://lamp.cfar.umd.edu/viperdata#}"
#


def ejectObjects(path_to_xgtf_file: os.PathLike) -> typing.Generator[ObjectData, None, None]:
    path_to_xgtf_file = Path(path_to_xgtf_file)
    xgtf = ET.parse(path_to_xgtf_file)
    sourcefile = xgtf.getroot().find(f"./{VIPER}data/{VIPER}sourcefile")
    file_name = Path(sourcefile.attrib['filename']).name
    path_to_video_file = path_to_xgtf_file.parent.joinpath(file_name)
    video = cv2.VideoCapture(str(path_to_video_file))

    for xgtf_object in sourcefile.findall(f"./{VIPER}object[@name='Object']"):
        objects_frame_position: typing.Dict[int, EjectedObjectFrameInfo] = {}
        object_id = int(xgtf_object.attrib['id'])
        uuid = xgtf_object.find(f'./{VIPER}attribute[@name="UniqueId"]/').attrib['value'] if xgtf_object.find(f'./{VIPER}attribute[@name="UniqueId"]/') is not None else "0"

        max_width, max_height = 0, 0

        for bbox in xgtf_object.findall(f'./{VIPER}attribute[@name="Position"]/'):
            framespan_borders = list(
                map(int, bbox.attrib['framespan'].split(":")))
            x = int(bbox.attrib['x'])
            y = int(bbox.attrib['y'])
            height = int(bbox.attrib['height'])
            width = int(bbox.attrib['width'])

            for frame in range(framespan_borders[0], framespan_borders[1]+1):
                object_frame_info = EjectedObjectFrameInfo(
                    False,
                    False,
                    Position(x, y, height, width),
                )
                objects_frame_position[frame] = object_frame_info
        for truncated_info in xgtf_object.findall(f'./{VIPER}attribute[@name="Truncated"]/'):
            framespan_borders = list(
                map(int, truncated_info.attrib['framespan'].split(":")))
            for frame in range(framespan_borders[0], framespan_borders[1]+1):
                if truncated_info.attrib['value'] == 'true':
                    if frame in objects_frame_position:
                        objects_frame_position[frame].truncated = True
        for difficult_info in xgtf_object.findall(f'./{VIPER}attribute[@name="Difficult"]/'):
            if difficult_info.attrib['value'] == 'true':
                framespan_borders = list(
                    map(int, difficult_info.attrib['framespan'].split(":")))
                for frame in range(framespan_borders[0], framespan_borders[1]+1):
                    if frame in objects_frame_position:
                        objects_frame_position[frame].difficult = True
        num_of_clear_data_frames = sum([not (objects_frame_position[key].truncated or objects_frame_position[key].difficult) for key in objects_frame_position])
        temp_objects_frame_position = {}
        if num_of_clear_data_frames < 15:
            keys = list(objects_frame_position.keys())
            if num_of_clear_data_frames > 0:
                for index in range(len(objects_frame_position.keys())):
                    key = keys[index]
                    if not (objects_frame_position[key].truncated or objects_frame_position[key].difficult):
                        temp_objects_frame_position[key] = objects_frame_position[key]
                        del objects_frame_position[key]
            for item in [objects_frame_position[list(objects_frame_position.keys())[index]] for index in range(0, len(objects_frame_position), len(objects_frame_position)//(15-num_of_clear_data_frames))]:
                temp_objects_frame_position[list(objects_frame_position.keys())[
                    list(objects_frame_position.values()).index(item)]] = item

            from collections import OrderedDict
            temp_objects_frame_position = dict(OrderedDict(
                sorted(temp_objects_frame_position.items())))
        else:
            for i in [objects_frame_position[list(objects_frame_position.keys())[i]] for i in range(0, len(objects_frame_position), len(objects_frame_position)//15)]:
                temp_objects_frame_position[list(objects_frame_position.keys())[
                    list(objects_frame_position.values()).index(i)]] = i
        objects_frame_position = temp_objects_frame_position

        for frame in objects_frame_position:
            max_width = max(
                max_width, objects_frame_position[frame].position.width)
            max_height = max(
                max_height, objects_frame_position[frame].position.height)

        object_data = ObjectData(
            file_name,
            object_id,
            uuid,
            [],
        )

        for frame in objects_frame_position:
            video.set(cv2.CAP_PROP_POS_FRAMES, frame)
            ret, video_frame = video.read()
            if ret:
                object_frame_info = objects_frame_position[frame]
                position: Position = object_frame_info.position
                x, y, width, height = position.x, position.y, position.width, position.height
                true_x = x
                true_y = y
                if height > width:
                    x -= (height - width) // 2
                    x = max(x, 0)
                    width = height
                elif width > height:
                    y -= (width - height) // 2
                    y = max(y, 0)
                    height = width
                object_border = video_frame[position.y:position.y+position.height, position.x:position.x+position.width]
                # Создаем маску для затемнения
                square_object = video_frame[y:y+height, x:x+width]
                mask = np.zeros_like(square_object)
                transparency = 0.7
                square_object_with_mask = cv2.addWeighted(square_object, 1 - transparency, mask, transparency, 0)
                square_object_with_mask[position.y-y:position.y-y+position.height, position.x-x:position.x-x+position.width] = object_border
                # Кодирование изображения в формат .jpg для сохранения в буфере
                _, buffer = cv2.imencode('.jpg', square_object_with_mask)
                io_buffer = io.BytesIO(buffer)
                object_data.images.append(io_buffer)
        yield object_data
    video.release()


def makeChangeUUID(path_to_xgtf_file: os.PathLike, data: typing.List[typing.Dict]):
    path_to_xgtf_file = Path(path_to_xgtf_file)
    xgtf = ET.parse(path_to_xgtf_file)
    sourcefile = xgtf.getroot().find(f"./{VIPER}data/{VIPER}sourcefile")
    for object_data in data:
        xgtf_object = sourcefile.find(
            f"./{VIPER}object[@id='{object_data['object_id']}']")
        if xgtf_object.find(f"./{VIPER}attribute[@name='UniqueId']/") is not None:
            xgtf_object.find(f"./{VIPER}attribute[@name='UniqueId']/").attrib['value'] = object_data['uuid']
        else:
            pos_attr = xgtf_object.find(f"./{VIPER}attribute[@name='Position']")
            diff_attr = xgtf_object.find(f"./{VIPER}attribute[@name='Difficult']")
            uuid = ET.Element(f"{VIPER}attribute")
            uuid.set("name", "UniqueId")
            uuid.tail, uuid.text = pos_attr.tail, pos_attr.text
            pos_attr.tail, pos_attr.text = diff_attr.tail, diff_attr.text
            xgtf_object.append(uuid)
            value = ET.Element(f"{VIPERDATA}svalue")
            value.tail = uuid.text.replace("    ", "", 1)
            value.set("value", object_data['uuid'])
            uuid.append(value)

    
    ET.register_namespace("ns", VIPER.strip("{}"))
    ET.register_namespace("data", VIPERDATA.strip("{}"))
    xgtf.write(str(path_to_xgtf_file), encoding="UTF-8", xml_declaration=True, method='xml')


