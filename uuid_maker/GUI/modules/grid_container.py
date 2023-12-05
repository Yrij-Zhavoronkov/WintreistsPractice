from typing import List, Union
from math import ceil

from PyQt6.QtWidgets import QGridLayout, QWidget, QApplication, QLabel
from PyQt6.QtCore import Qt, QTimer


class GridContainer(QGridLayout):

    def __init__(self, parent:QWidget, objects_in_row:int=0, alignment=Qt.AlignmentFlag.AlignCenter):
        super().__init__(parent)
        parent.setLayout(self)
        self.objects_in_row = objects_in_row
        self.default_alignment = alignment
        self.objects:List[QWidget] = []

    def setColumns(self, columns:int):
        self.objects_in_row = columns
        self.updateMe()

    @property
    def getColumns(self):
        return self.objects_in_row

    def addObject(self, object_instance:Union[List[QWidget], QWidget]):
        if isinstance(object_instance, list):
            self.objects.extend(object_instance)
        elif isinstance(object_instance, QWidget):
            self.objects.append(object_instance)
        self.updateMe()

    def removeObject(self, object_index:int) -> QWidget:
        widget = self.objects.pop(object_index)
        self.updateMe()
        return widget

    def updateMe(self, from_index:int = 0):
        if self.objects_in_row == 0:
            # QTimer.singleShot(0, self._updateMeFlex)
            self._updateMeFlex()
            return
        
        for _ in range(from_index, self.count()):
            widget = self.takeAt(from_index).widget()
        for index, widget in enumerate(self.objects[from_index:]):
            final_index = index + from_index
            self.addWidget(
                widget,
                final_index//self.objects_in_row,
                final_index%self.objects_in_row,
                alignment=self.default_alignment
            )
            if hasattr(widget, "updateInGrid"):
                widget.updateInGrid(
                    position=(
                        final_index//self.objects_in_row,
                        final_index%self.objects_in_row
                    )
                )
        pass

    def _updateMeFlex(self):
        while self.count():
            widget = self.takeAt(0).widget()
        self.parent().update()
        QApplication.processEvents()
        objects_per_row = ceil(self.parent().width() / (self._getMaxObjectsWidth() + self.horizontalSpacing()*2))
        for index, widget in enumerate(self.objects):
            self.addWidget(
                widget,
                index//objects_per_row,
                index % objects_per_row,
                alignment=self.default_alignment
            )
            if hasattr(widget, "updateInGrid"):
                widget.updateInGrid(position=(index//objects_per_row, index % objects_per_row))
        pass
    
    def _getMaxObjectsWidth(self):
        max_width = 0
        for widget in self.objects:
            widget_width = self._getWidgetWidth(widget)
            if widget_width > max_width:
                max_width = widget_width
        return max_width
    
    def _getWidgetWidth(self, widget:Union[QWidget, QLabel]):
        if isinstance(widget, QLabel):
            return widget.pixmap().width()
        elif isinstance(widget, QWidget):
            return widget.width()