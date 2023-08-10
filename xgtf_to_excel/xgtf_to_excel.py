import os
import pandas as pd
import xml.etree.ElementTree as ET
from argparse import ArgumentParser
import cv2
from dataclasses import dataclass
from typing import Optional, Tuple
from math import isnan


# Константы
VIPER = "{http://lamp.cfar.umd.edu/viper#}"
VIPERDATA = "{http://lamp.cfar.umd.edu/viperdata#}"
#

def get_fps_and_numframes_from_video(work_dir:str, file_name:str) -> Tuple[float, float]:
    extensions = ["mkv", "mp4", "mpeg", "mov", "avi"]
    video_dir = None
    for video_name in [f"{file_name.split('.')[0]}.{extension}" for extension in extensions]:
        if os.path.isfile(os.path.join(work_dir, video_name)):
            video_dir = os.path.join(work_dir, video_name)
            break
    if video_dir is not None:
        video = cv2.VideoCapture(video_dir)
        return video.get(cv2.CAP_PROP_FRAME_COUNT), video.get(cv2.CAP_PROP_FPS)
    else:
        return 0.0, 0.0

def calculate_time(time:int) -> str:
    hours = int(time // 3600)
    time -= 3600*hours
    minutes = int(time//60)
    time -= 60*minutes
    seconds = int(time)
    return f"{hours}:{minutes}:{seconds}"

def get_default_value_for_class(tree:ET.ElementTree) -> str:
    default_value = 'None'
    for attribute in tree.getroot().findall(f'./{VIPER}config/{VIPER}descriptor/{VIPER}attribute[@name="Class"]/{VIPER}default/{VIPERDATA}svalue'):
        default_value = attribute.attrib['value']
    return default_value

def painting_errors(element):
    if isinstance(element, int):
        if element == 0:
            return 'background-color: #ff4c5b;'
    elif isinstance(element, str):
        if "None" in element or element == "":
            return 'background-color: #ff4c5b;'
    elif isinstance(element, float):
        if element == 0.0:
            return 'background-color: #ff4c5b;'
        elif isnan(element):
            return 'background-color: #ff4c5b;'
    elif element is None:
        return 'background-color: #ff4c5b;'
    return None


@dataclass
class XgtfData:
    
    fileName:str
    objectsCount:Optional[int]=None
    videoDuration:Optional[str]=None
    framesCount:Optional[float]=None
    averageObjectsInFrame:Optional[float]=None
    classes:Optional[str]=None

    def __iter__(self):
        return iter([self.fileName, self.objectsCount, self.videoDuration, 
                self.framesCount, self.averageObjectsInFrame, self.classes])
    


# Аргументы
parser = ArgumentParser()
parser.add_argument('--work-dir')
parser.add_argument('--result-dir',nargs="?", default='result.xlsx')
namespace = parser.parse_args()
#
allData = []
for file_name in os.listdir(namespace.work_dir):
    # Условие для обработки .xgtf
    if file_name.find(".xgtf") == -1:
        continue
    # Подготовка
    # Имя
    data = XgtfData(file_name)

    try:
        tree = ET.parse(os.path.join(namespace.work_dir, file_name))
    except ET.ParseError:
        allData.append(data)
        continue
    print(os.path.join(namespace.work_dir, file_name))
    root_data_sourcefile = tree.getroot().find(f'./{VIPER}data/{VIPER}sourcefile')
    
    # Количество объектов
    classes = []
    count_of_objects = 0
    for objects in root_data_sourcefile.findall(f'./{VIPER}object/{VIPER}attribute[@name="Class"]'):
        count_of_objects += 1
        try:
            classes.append(objects.find(f'./{VIPERDATA}svalue').attrib['value'])
        except AttributeError:
            classes.append(get_default_value_for_class(tree))
    data.objectsCount = count_of_objects
    # Классы
    data.classes = ','.join(set(classes))
    # Длинна видео (секунд)
    root_data_sourcefile_file = root_data_sourcefile.find(f'./{VIPER}file')
    try:
        numframes = float(root_data_sourcefile_file.find(f'./{VIPER}attribute[@name="NUMFRAMES"]/').attrib['value']) # NUMFRAMES
        framerate = float(root_data_sourcefile_file.find(f'.//{VIPER}attribute[@name="FRAMERATE"]/').attrib['value'])  # FRAMERATE
        if numframes == 0 or framerate == 0:
            raise AttributeError
    except AttributeError:
        numframes,framerate = get_fps_and_numframes_from_video(namespace.work_dir, file_name)

    try:
        # Расчет времени
        data.videoDuration = calculate_time(numframes / framerate)
        # Среднее кол-во объектов на кадре
        data.averageObjectsInFrame = count_of_objects / numframes
        # Длинна видео (кадры)
        data.framesCount = numframes
    except ZeroDivisionError:
        pass
    
    # Сохраняем в общий массив
    allData.append(list(data))
df = pd.DataFrame(allData, columns=['Имя', 'Количество объектов', 'Длинна видео (секунд)', 'Длинна видео (кадры)', 'Среднее кол-во объектов на кадре', 'Классы'])
df.style.applymap(painting_errors).to_excel(namespace.result_dir)
