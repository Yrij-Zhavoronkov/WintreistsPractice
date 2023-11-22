from threading import Thread
from os import PathLike
from typing import List, Callable, Optional

from .classes import ObjectData
from ..eject_objects_from_xgtf_and_video import eject_objects

class ThreadForEjectingObjects(Thread):
    def __init__(
            self, 
            xgtf_files: List[PathLike],
            callback: Callable[[ObjectData], None],
            on_finish_callback: Optional[Callable[[], None]] = None,
        ):
        super().__init__()
        self.xgtf_files = xgtf_files
        self.callback = callback
        self.on_finish_callback = on_finish_callback
        self.stop_work = False
        pass

    def run(self):
        for xgtf_file in self.xgtf_files:
            for data in eject_objects(xgtf_file):
                if self.stop_work: 
                    return # Выход из thread
                self.callback(data)
        if self.on_finish_callback:
            self.on_finish_callback()
            
    def interinput(self):
        self.stop_work = True
  