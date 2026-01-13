from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsItemGroup, QGraphicsItem
from PySide6.QtGui import QPen, QColor, QPainterPath
from src.constants import *

class Shape:
    def __init__(self, color=DEFAULT_COLOR, stroke_width=DEFAULT_STROKE_WIDTH):
        self.current_color = color
        self.current_width = stroke_width

    def init_qt_flags(self):
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

    def _update_pen(self):
        pen = QPen(QColor(self.current_color))
        pen.setWidth(self.current_width)
        self.setPen(pen)

    def set_active_color(self, color: str):
        self.current_color = color
        self._update_pen()

    def set_stroke_width(self, width: int):
        self.current_width = width
        self._update_pen()

    @property
    def type_name(self) -> str:
        raise NotImplementedError

    def set_geometry(self, start, end):
        raise NotImplementedError

    def to_dict(self) -> dict:
        raise NotImplementedError

class Rectangle(QGraphicsPathItem, Shape):
    def __init__(self, x, y, w, h, color=DEFAULT_COLOR, stroke_width=DEFAULT_STROKE_WIDTH):
        QGraphicsPathItem.__init__(self)
        Shape.__init__(self, color, stroke_width)
        self.init_qt_flags()
        self.rect_data = (x, y, w, h)
        self._update_pen()
        self._redraw()

    def _redraw(self):
        path = QPainterPath()
        path.addRect(*self.rect_data)
        self.setPath(path)

    @property
    def type_name(self) -> str:
        return TOOL_RECT

    def set_geometry(self, start, end):
        x = min(start.x(), end.x())
        y = min(start.y(), end.y())
        w = abs(end.x() - start.x())
        h = abs(end.y() - start.y())
        self.rect_data = (x, y, w, h)
        self._redraw()

    def to_dict(self) -> dict:
        x, y, w, h = self.rect_data
        return {
            "type": self.type_name,
            "pos": [self.x(), self.y()],
            "props": {
                "x": x, "y": y, "w": w, "h": h,
                "color": self.current_color,
                "width": self.current_width
            }
        }

class Ellipse(Rectangle):
    @property
    def type_name(self) -> str:
        return TOOL_ELLIPSE

    def _redraw(self):
        path = QPainterPath()
        path.addEllipse(*self.rect_data)
        self.setPath(path)

class Line(QGraphicsPathItem, Shape):
    def __init__(self, x1, y1, x2, y2, color=DEFAULT_COLOR, stroke_width=DEFAULT_STROKE_WIDTH):
        QGraphicsPathItem.__init__(self)
        Shape.__init__(self, color, stroke_width)
        self.init_qt_flags()
        self.line_data = (x1, y1, x2, y2)
        self._update_pen()
        self._redraw()

    @property
    def type_name(self) -> str:
        return TOOL_LINE

    def _redraw(self):
        path = QPainterPath()
        path.moveTo(self.line_data[0], self.line_data[1])
        path.lineTo(self.line_data[2], self.line_data[3])
        self.setPath(path)

    def set_geometry(self, start, end):
        self.line_data = (start.x(), start.y(), end.x(), end.y())
        self._redraw()

    def to_dict(self) -> dict:
        return {
            "type": self.type_name,
            "pos": [self.x(), self.y()],
            "props": {
                "x1": self.line_data[0], "y1": self.line_data[1],
                "x2": self.line_data[2], "y2": self.line_data[3],
                "color": self.current_color,
                "width": self.current_width
            }
        }

class Group(QGraphicsItemGroup, Shape):
    def __init__(self):
        QGraphicsItemGroup.__init__(self)
        Shape.__init__(self)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setHandlesChildEvents(True)

    @property
    def type_name(self) -> str:
        return "group"

    def _update_pen(self):
        pass 

    def set_active_color(self, color: str):
        self.current_color = color
        for child in self.childItems():
            if isinstance(child, Shape):
                child.set_active_color(color)

    def set_stroke_width(self, width: int):
        self.current_width = width
        for child in self.childItems():
            if isinstance(child, Shape):
                child.set_stroke_width(width)

    def set_geometry(self, start, end):
        pass 

    def to_dict(self) -> dict:
        children_data = []
        for child in self.childItems():
            if hasattr(child, "to_dict"):
                children_data.append(child.to_dict())

        return {
            "type": self.type_name,
            "pos": [self.x(), self.y()],
            "children": children_data
        }
