import os
import pandas as pd
import xml.etree.ElementTree as ET
from argparse import ArgumentParser
import cv2
from dataclasses import dataclass, field
from typing import Optional, Tuple, Callable
from math import isnan
from numpy import sum as npsum
from alive_progress import alive_it


# Константы
VIPER = "{http://lamp.cfar.umd.edu/viper#}"
VIPERDATA = "{http://lamp.cfar.umd.edu/viperdata#}"
#

def get_fps_and_numframes_from_video(work_dir:str, file_name:str) -> Tuple[float, float]:
    extensions = ["mkv", "mp4", "mpeg", "mov", "avi"]
    file_name = file_name.removesuffix(".xgtf")
    video_path = None
    for video_name in [f"{file_name}.{extension}" for extension in extensions]:
        if os.path.isfile(os.path.join(work_dir, video_name)):
            video_path = os.path.join(work_dir, video_name)
            break
    if video_path is not None:
        video = cv2.VideoCapture(video_path)
        return video.get(cv2.CAP_PROP_FRAME_COUNT), video.get(cv2.CAP_PROP_FPS)
    else:
        return 0.0, 0.0

def calculate_time(time:float) -> str:
    hours = int(time // 3600)
    time -= 3600*hours
    minutes = int(time//60)
    time -= 60*minutes
    seconds = int(time)
    return f"{hours}:{minutes}:{seconds}"

def get_default_value_for_class(tree:ET.ElementTree) -> str:
    default_value = "None"
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
        elif element == "0:0:0":
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
    objectsCount:int=0
    objectsFramesCount:int=0
    videoDuration:float=0.0
    framesCount:float=0.0
    classes:Optional[set[Optional[str]]]=field(default_factory=set)

    def to_excel(self) -> list:
        return [self.fileName,
                self.objectsCount, 
                calculate_time(self.videoDuration),
                self.framesCount, 
                self.objectsFramesCount/self.framesCount if self.framesCount != 0 else 0.0,
                ",".join(self.classes)]
    pass

@dataclass
class AllXgtfData:
    _xgtfData:list[XgtfData] = field(default_factory=list)

    def to_excel(self) -> list:
        statistics = XgtfData("Итого")
        statistics.objectsCount, statistics.videoDuration, statistics.framesCount, statistics.objectsFramesCount = npsum([[xgtf.objectsFramesCount, xgtf.videoDuration, xgtf.framesCount, xgtf.objectsFramesCount] for xgtf in self._xgtfData], axis=0)
        statistics.classes = set.union(*[xgtf.classes for xgtf in self._xgtfData])
        return [xgtf.to_excel() for xgtf in self._xgtfData] + [statistics.to_excel()]
    def append(self, element:XgtfData):
        self._xgtfData.append(element)
        pass
    pass

def xgtf_to_excel_work(work_dir, result_dir = os.path.join(os.getcwd(), 'result.xlsx'), callback:Optional[Callable[[int], None]]=None):
    allData = AllXgtfData()
    bar = alive_it(os.listdir(work_dir)) if callback is None else os.listdir(work_dir)
    for file_name in bar:
        if callback is not None:
            callback(int((bar.index(file_name)+1) * 100 / len(bar)))
        # Условие для обработки .xgtf
        if file_name.find(".xgtf") == -1:
            continue
        # Подготовка
        # Имя
        data = XgtfData(file_name)

        try:
            tree = ET.parse(os.path.join(work_dir, file_name))
        except ET.ParseError:
            allData.append(data)
            continue
        print(os.path.join(work_dir, file_name))
        root_data_sourcefile = tree.getroot().find(f'./{VIPER}data/{VIPER}sourcefile')
        
        # Количество рамок объектов
        for v_object in root_data_sourcefile.findall(f'./{VIPER}object'):
            data.objectsCount += 1
            for bbox in v_object.findall(f'./{VIPER}attribute[@name="Position"]/{VIPERDATA}bbox'):
                data.objectsFramesCount += sum([right-left+1 for splited_bbox in bbox.attrib["framespan"].split(" ") for left, right in [map(int, splited_bbox.split(":"))]])
                
            # Классы
            try:
                data.classes.add(v_object.find(f'./{VIPER}attribute[@name="Class"]/{VIPERDATA}svalue').attrib['value'])
            except AttributeError:
                data.classes.add(get_default_value_for_class(tree))
        
        root_data_sourcefile_file = root_data_sourcefile.find(f'./{VIPER}file')
        try:
            # Длинна видео (кадры)
            data.framesCount = float(root_data_sourcefile_file.find(f'./{VIPER}attribute[@name="NUMFRAMES"]/').attrib['value']) # NUMFRAMES
            framerate = float(root_data_sourcefile_file.find(f'.//{VIPER}attribute[@name="FRAMERATE"]/').attrib['value'])  # FRAMERATE
            if data.framesCount == 0 or framerate == 0:
                raise AttributeError
        except AttributeError:
            data.framesCount,framerate = get_fps_and_numframes_from_video(work_dir, file_name)

        if framerate != 0:
            # Расчет времени
            data.videoDuration = data.framesCount / framerate
        
        
        # Сохраняем в общий массив
        allData.append(data)

    # Вывод в файл
    df = pd.DataFrame(allData.to_excel(), columns=['Имя', 'Количество объектов', 'Длинна видео (секунд)', 'Длинна видео (кадры)', 'Среднее кол-во рамок объектов на кадре', 'Классы'])
    writer = pd.ExcelWriter(result_dir, engine='xlsxwriter') 
    df.style.applymap(painting_errors).to_excel(writer, sheet_name='Sheet1', index=False, na_rep='NaN')

    for column in df:
        column_length = max(df[column].astype(str).map(len).max(), len(column)) + 1
        col_idx = df.columns.get_loc(column)
        writer.sheets['Sheet1'].set_column(col_idx, col_idx, column_length)

    writer.close()
    

if __name__ == "__main__":
    # Аргументы
    parser = ArgumentParser()
    parser.add_argument('--work-dir', required=True)
    parser.add_argument('--result-dir',nargs="?", default='result.xlsx')
    namespace = parser.parse_args()
    #
    xgtf_to_excel_work(namespace.work_dir, namespace.result_dir)
    
