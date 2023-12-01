from dataclasses import dataclass
import typing
import io


@dataclass
class EjectedObjectDataFileNameAndObjectID:
    file_name: str
    object_id: int

    def __eq__(self, other_object: object) -> bool:
        if isinstance(other_object, EjectedObjectDataFileNameAndObjectID):
            return self.file_name == other_object.file_name and self.object_id == other_object.object_id
        else:
            raise TypeError


@dataclass
class EjectedObjectData(EjectedObjectDataFileNameAndObjectID):
    images: typing.List[io.BytesIO]
    uuid: str
    position: typing.Tuple[int, int] = (0, 0)
    sorted: bool = False
    changed: bool = False

    def __eq__(self, other_object: object) -> bool:
        if isinstance(other_object, EjectedObjectData):
            return self.file_name == other_object.file_name and self.object_id == other_object.object_id
        else:
            raise TypeError

    def __ne__(self, other_object: object) -> bool:
        return not self.__eq__(other_object)

@dataclass
class Position:
    x: int
    y: int
    height: int
    width: int


class ObjectData(typing.NamedTuple):
    file_name: str
    object_id: int
    uuid: str
    images: typing.List[io.BytesIO]


@dataclass
class EjectedObjectFrameInfo:
    truncated: bool
    difficult: bool
    position: Position


# Константы
TypeEjectedObject = typing.List[EjectedObjectData]
UUID_LENGTH = 32
#