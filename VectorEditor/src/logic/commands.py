from PySide6.QtGui import QUndoCommand

class AddShapeCommand(QUndoCommand):
    def __init__(self, scene, item):
        super().__init__()
        self.scene = scene
        self.item = item
        self.setText(f"Add {item.type_name}")

    def redo(self):
        if self.item.scene() != self.scene:
            self.scene.addItem(self.item)

    def undo(self):
        self.scene.removeItem(self.item)

class DeleteCommand(QUndoCommand):
    def __init__(self, scene, item):
        super().__init__()
        self.scene = scene
        self.item = item
        self.setText(f"Delete {item.type_name}")

    def redo(self):
        self.scene.removeItem(self.item)

    def undo(self):
        self.scene.addItem(self.item)

class MoveCommand(QUndoCommand):
    def __init__(self, item, old_pos, new_pos):
        super().__init__()
        self.item = item
        self.old_pos = old_pos
        self.new_pos = new_pos
        self.setText("Move")

    def undo(self):
        self.item.setPos(self.old_pos)

    def redo(self):
        self.item.setPos(self.new_pos)

class ChangeColorCommand(QUndoCommand):
    def __init__(self, item, new_color):
        super().__init__()
        self.item = item
        self.new_color = new_color
        self.old_color = item.current_color
        self.setText("Change Color")

    def redo(self):
        self.item.set_active_color(self.new_color)

    def undo(self):
        self.item.set_active_color(self.old_color)

class ChangeWidthCommand(QUndoCommand):
    def __init__(self, item, new_width):
        super().__init__()
        self.item = item
        self.new_width = new_width
        self.old_width = item.current_width
        self.setText("Change Thickness")

    def redo(self):
        self.item.set_stroke_width(self.new_width)

    def undo(self):
        self.item.set_stroke_width(self.old_width)

class ChangeGeometryCommand(QUndoCommand):
    def __init__(self, item, new_pos):
        super().__init__()
        self.item = item
        self.new_pos = new_pos
        self.old_pos = item.pos()
        self.setText("Change Pos")

    def redo(self):
        self.item.setPos(self.new_pos)

    def undo(self):
        self.item.setPos(self.old_pos)
