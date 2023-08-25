

def defaultOnProgressCallback(completed: int, all: int, curNet: str, curVideo: str):
    if curNet and curVideo:
        print(f"[{completed}/{all}] Work with net {curNet} and video {curVideo}")


def defaultOnErrorCallback(message: str):
    print(f"[E] {message}")


from typing import Tuple, Optional, Callable

def main(
    netsDir: str,
    videosDir: str,
    resDir: str,
    targetClasses: Tuple[str, ...],
    path2Epf: Optional[str] = None,
    useMot: bool = False,
    motIouThr: float = 0.3,
    framerate: int = 13,
    hideStillObjects: bool = False,
    hideStillObjectsSensitivity: float = 0.5,
    minDetectionTriggers: int = 6,
    confThreshold: float = 0.3,
    siameseFile: str = "",
    onProgressCallback: Callable[[int, int, str, str], None] = defaultOnProgressCallback,
    onErrorCallback: Callable[[str], None] = defaultOnErrorCallback
):
    pass
