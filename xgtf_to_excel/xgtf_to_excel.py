import os
import pandas as pd
import xml.etree.ElementTree as ET
from xml.etree.cElementTree import ElementTree
from argparse import ArgumentParser
import cv2
from dataclasses import dataclass 


def get_fps_and_numframes_from_video(work_dir:str, file_name:str):
    video = cv2.VideoCapture(os.path.join(work_dir, file_name))
    return video.get(cv2.CAP_PROP_FRAME_COUNT), video.get(cv2.CAP_PROP_FPS)

def calculate_time(time:int):
    hours = int(time // 3600)
    time -= 3600*hours
    minutes = int(time//60)
    time -= 60*minutes
    seconds = int(time)
    return f"{hours}:{minutes}:{seconds}"

def get_default_value(what:str, tree:ElementTree):
    default_value = 'None'
    for i in tree.getroot().findall('./{http://lamp.cfar.umd.edu/viper#}config/{http://lamp.cfar.umd.edu/viper#}descriptor/{http://lamp.cfar.umd.edu/viper#}attribute'+f'[{what}]'+'/{http://lamp.cfar.umd.edu/viper#}default/{http://lamp.cfar.umd.edu/viperdata#}bvalue'):
        default_value = i.attrib['value']
    return default_value


@dataclass
class DataClass:
    
    fileName:str=None
    objectsCount:int=None
    videoDuration:str=None
    framesCount:int=None
    averageObjectsInFrame:float=None
    classes:str=None

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
for i in os.listdir(namespace.work_dir):
    # Условие для обработки .xgtf
    if i.find(".xgtf") == -1:
        continue
    # Подготовка
    # Имя
    data = DataClass(i)

    try:
        tree = ET.parse(os.path.join(namespace.work_dir, i))
    except ET.ParseError:
        allData.append(data)
        continue
    print(os.path.join(namespace.work_dir, i))
    root_data_sourcefile = tree.getroot().find('./{http://lamp.cfar.umd.edu/viper#}data/{http://lamp.cfar.umd.edu/viper#}sourcefile')
    
    # Количество объектов
    classes = []
    count_of_objects = 0
    for objects in root_data_sourcefile.findall('./{http://lamp.cfar.umd.edu/viper#}object/{http://lamp.cfar.umd.edu/viper#}attribute[@name="Class"]'):
        count_of_objects += 1
        try:
            classes.append(objects.find('./{http://lamp.cfar.umd.edu/viperdata#}svalue').attrib['value'])
        except AttributeError:
            classes.append(get_default_value('@name="Class"', tree))
    data.objectsCount = count_of_objects
    # Классы
    data.classes = ','.join(set(classes))
    # Длинна видео (секунд)
    root_data_sourcefile_file = root_data_sourcefile.find('./{http://lamp.cfar.umd.edu/viper#}file')
    try:
        numframes = int(root_data_sourcefile_file.find('./{http://lamp.cfar.umd.edu/viper#}attribute[@name="NUMFRAMES"]/').attrib['value']) # NUMFRAMES
        framerate = float(root_data_sourcefile_file.find('.//{http://lamp.cfar.umd.edu/viper#}attribute[@name="FRAMERATE"]/').attrib['value'])  # FRAMERATE
        if numframes == 0 or framerate == 0:
            raise AttributeError
    except AttributeError:
        numframes,framerate = get_fps_and_numframes_from_video(namespace.work_dir, root_data_sourcefile.attrib['filename'].split("\\")[-1]) # поправить для других ОС
    # Расчет времени
    data.videoDuration = calculate_time(numframes / framerate)
    # Длинна видео (кадры)
    data.framesCount = numframes
    # Среднее кол-во объектов на кадре
    data.averageObjectsInFrame = count_of_objects / numframes
    # Сохраняем в общий массив
    allData.append(list(data))
df = pd.DataFrame(allData, columns=['Имя', 'Количество объектов', 'Длинна видео (секунд)', 'Длинна видео (кадры)', 'Среднее кол-во объектов на кадре', 'Классы'])
df.to_excel(namespace.result_dir)
