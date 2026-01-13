from src.logic.shapes import Rectangle, Ellipse, Line, Group, Shape
from src.constants import *

class ShapeFactory:
    @staticmethod
    def create_shape(shape_type, start, end, color=DEFAULT_COLOR, width=DEFAULT_STROKE_WIDTH):
        x = min(start.x(), end.x())
        y = min(start.y(), end.y())
        w = abs(end.x() - start.x())
        h = abs(end.y() - start.y())

        if shape_type == TOOL_RECT:
            return Rectangle(x, y, w, h, color, width)
        elif shape_type == TOOL_ELLIPSE:
            return Ellipse(x, y, w, h, color, width)
        elif shape_type == TOOL_LINE:
            return Line(start.x(), start.y(), end.x(), end.y(), color, width)
        else:
            raise ValueError(f"Unknown shape type: {shape_type}")

    @staticmethod
    def from_dict(data: dict):
        shape_type = data.get("type")

        if shape_type == "group":
            group = Group()
            pos = data.get("pos", [0, 0])
            group.setPos(pos[0], pos[1])

            for child_data in data.get("children", []):
                child = ShapeFactory.from_dict(child_data)
                if child:
                    group.addToGroup(child)
                    if "pos" in child_data:
                        c_pos = child_data["pos"]
                        child.setPos(c_pos[0], c_pos[1])
            return group

        props = data.get("props", {})
        pos = data.get("pos", [0, 0])
        color = props.get("color", DEFAULT_COLOR)
        width = props.get("width", DEFAULT_STROKE_WIDTH)

        obj = None
        if shape_type == TOOL_RECT:
            obj = Rectangle(props['x'], props['y'], props['w'], props['h'], color, width)
        elif shape_type == TOOL_ELLIPSE:
            obj = Ellipse(props['x'], props['y'], props['w'], props['h'], color, width)
        elif shape_type == TOOL_LINE:
            obj = Line(props['x1'], props['y1'], props['x2'], props['y2'], color, width)

        if obj:
            obj.setPos(pos[0], pos[1])

        return obj
