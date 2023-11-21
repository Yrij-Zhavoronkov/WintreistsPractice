from threading import Thread, Lock
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
        self.lock = Lock()
        pass

    def run(self):
        for xgtf_file in self.xgtf_files:
            print(f"{self} req lock")
            self.lock.acquire()
            print(f"{self} work with {xgtf_file.name}")
            if self.stop_work: 
                return
            for data in eject_objects(xgtf_file):
                if self.stop_work: 
                    return # Выход из thread
                self.callback(data)
            if self.on_finish_callback:
                self.on_finish_callback()
            if not self.lock.locked():
                self.lock.acquire()
            
    def interinput(self):
        self.stop_work = True
        self.notify()

    def notify(self):
        if self.lock.locked():
            self.lock.release()
  