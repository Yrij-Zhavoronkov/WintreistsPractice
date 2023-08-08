import os
import pandas as pd
import xml.etree.ElementTree as ET
from argparse import ArgumentParser

# Аргументы
parser = ArgumentParser()
parser.add_argument('--work-dir')
parser.add_argument('--result-dir',nargs="?", default='result.xlsx')
namespace = parser.parse_args()
#
data = []
for i in os.listdir(namespace.work_dir):
    # Условие для обработки .xgtf
    if (i.find(".xgtf") == -1):
        continue
    # Подготовка
    data.append([])
    tree = ET.parse(namespace.work_dir+"\\"+i)
    root_data_sourcefile = tree.getroot().find('./{http://lamp.cfar.umd.edu/viper#}data/{http://lamp.cfar.umd.edu/viper#}sourcefile')
    # Имя
    data[-1].append(root_data_sourcefile.attrib['filename'])
    # Количество объектов
    count_of_objects = len(root_data_sourcefile.findall('./{http://lamp.cfar.umd.edu/viper#}object'))
    data[-1].append(count_of_objects)
    # Длинна видео (секунд)
    root_data_sourcefile_file = root_data_sourcefile.find('./{http://lamp.cfar.umd.edu/viper#}file')
    numframes = int(root_data_sourcefile_file.find('./{http://lamp.cfar.umd.edu/viper#}attribute[@name="NUMFRAMES"]/').attrib['value']) # NUMFRAMES
    framerate = float(root_data_sourcefile_file.find('.//{http://lamp.cfar.umd.edu/viper#}attribute[@name="FRAMERATE"]/').attrib['value']) # FRAMERATE
    # Расчет времени
    time = numframes / framerate
    hours = int(time // 3600)
    time -= 3600*hours
    minutes = int(time//60)
    time -= 60*minutes
    seconds = int(time)
    # ~~~~~~~~~~
    data[-1].append(f"{hours}:{minutes}:{seconds}")
    # Длинна видео (кадры)
    data[-1].append(numframes)
    # Среднее кол-во объектов на кадре
    data[-1].append(count_of_objects / numframes)
    # Классы
    classes = []
    for i in root_data_sourcefile.findall('./{http://lamp.cfar.umd.edu/viper#}object/{http://lamp.cfar.umd.edu/viper#}attribute[@name="Class"]/{http://lamp.cfar.umd.edu/viperdata#}svalue'):
        classes.append(i.attrib['value'])
    data[-1].append(','.join(set(classes)))
df = pd.DataFrame(data, columns=['Имя', 'Количество объектов', 'Длинна видео (секунд)', 'Длинна видео (кадры)', 'Среднее кол-во объектов на кадре', 'Классы'])
df.to_excel(namespace.result_dir)