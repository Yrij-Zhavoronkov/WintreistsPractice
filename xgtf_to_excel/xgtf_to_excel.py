import os
import pandas as pd
import xml.etree.ElementTree as ET
from argparse import ArgumentParser
import cv2


def get_fps_and_numframes_from_video(work_dir:str, file_name:str):
    video = cv2.VideoCapture(os.path.join(work_dir, file_name))
    return video.get(cv2.CAP_PROP_FRAME_COUNT), video.get(cv2.CAP_PROP_FPS)

def calculate_time(time:int):
    hours = int(time // 3600)
    time -= 3600*hours
    minutes = int(time//60)
    time -= 60*minutes
    seconds = int(time)
    return str(hours), str(minutes), str(seconds)

# Аргументы
parser = ArgumentParser()
parser.add_argument('--work-dir')
parser.add_argument('--result-dir',nargs="?", default='result.xlsx')
namespace = parser.parse_args()
#
data = []
for i in os.listdir(namespace.work_dir):
    # Условие для обработки .xgtf
    if i.find(".xgtf") == -1:
        continue
    # Подготовка
    try:
        tree = ET.parse(namespace.work_dir+"\\"+i)
    except ET.ParseError:
        data.append([i, 0, 0, 0, 0, None])
        continue
    print(namespace.work_dir+"\\"+i)
    root_data_sourcefile = tree.getroot().find('./{http://lamp.cfar.umd.edu/viper#}data/{http://lamp.cfar.umd.edu/viper#}sourcefile')
    data.append([])
    # Имя
    data[-1].append(i)
    # Количество объектов
    classes = []
    count_of_objects = 0
    for objects in root_data_sourcefile.findall('./{http://lamp.cfar.umd.edu/viper#}object/{http://lamp.cfar.umd.edu/viper#}attribute[@name="Class"]/{http://lamp.cfar.umd.edu/viperdata#}svalue'):
        count_of_objects += 1
        classes.append(objects.attrib['value'])
    data[-1].append(count_of_objects)
    # Длинна видео (секунд)
    root_data_sourcefile_file = root_data_sourcefile.find('./{http://lamp.cfar.umd.edu/viper#}file')
    try:
        numframes = int(root_data_sourcefile_file.find('./{http://lamp.cfar.umd.edu/viper#}attribute[@name="NUMFRAMES"]/').attrib['value']) # NUMFRAMES
        framerate = float(root_data_sourcefile_file.find('.//{http://lamp.cfar.umd.edu/viper#}attribute[@name="FRAMERATE"]/').attrib['value'])  # FRAMERATE
        if numframes == 0 or framerate == 0:
            raise AttributeError
    except AttributeError:
        numframes,framerate = get_fps_and_numframes_from_video(namespace.work_dir, root_data_sourcefile.attrib['filename'].split("\\")[-1])
    # Расчет времени
    data[-1].append(":".join(calculate_time(numframes / framerate)))
    # Длинна видео (кадры)
    data[-1].append(numframes)
    # Среднее кол-во объектов на кадре
    data[-1].append(count_of_objects / numframes)
    # Классы
    data[-1].append(','.join(set(classes)))
df = pd.DataFrame(data, columns=['Имя', 'Количество объектов', 'Длинна видео (секунд)', 'Длинна видео (кадры)', 'Среднее кол-во объектов на кадре', 'Классы'])
df.to_excel(namespace.result_dir)
