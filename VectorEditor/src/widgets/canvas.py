from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtCore import Qt
from PySide6.QtGui import QUndoStack
from src.constants import *
from src.logic.tools import SelectionTool, CreationTool
from src.logic.shapes import Group
from src.logic.commands import DeleteCommand

class EditorCanvas(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.scene.setSceneRect(0, 0, SCENE_WIDTH, SCENE_HEIGHT)

        self.setRenderHint(self.renderHints() | Qt.RenderHint.Antialiasing)
        self.setMouseTracking(True)

        self.undo_stack = QUndoStack(self)

        self.tools = {
            TOOL_SELECT: SelectionTool(self, self.undo_stack),
            TOOL_RECT: CreationTool(self, TOOL_RECT, self.undo_stack),
            TOOL_ELLIPSE: CreationTool(self, TOOL_ELLIPSE, self.undo_stack),
            TOOL_LINE: CreationTool(self, TOOL_LINE, self.undo_stack),
        }
        self.current_tool = self.tools[TOOL_SELECT]

    def set_tool(self, tool_name):
        if tool_name in self.tools:
            self.current_tool = self.tools[tool_name]
            if tool_name == TOOL_SELECT:
                self.setCursor(Qt.ArrowCursor)
            else:
                self.setCursor(Qt.CrossCursor)

    def mousePressEvent(self, event):
        self.current_tool.mouse_press(event)

    def mouseMoveEvent(self, event):
        self.current_tool.mouse_move(event)

    def mouseReleaseEvent(self, event):
        self.current_tool.mouse_release(event)

    def group_selection(self):
        sel = self.scene.selectedItems()
        if len(sel) < 1: return

        group = Group()
        self.scene.addItem(group)
        for item in sel:
            item.setSelected(False)
            group.addToGroup(item)
        group.setSelected(True)

    def ungroup_selection(self):
        for item in self.scene.selectedItems():
            if isinstance(item, Group):
                self.scene.destroyGroup(item)

    def delete_selected(self):
        sel = self.scene.selectedItems()
        if not sel: return

        self.undo_stack.beginMacro("Delete")
        for item in sel:
            self.undo_stack.push(DeleteCommand(self.scene, item))
        self.undo_stack.endMacro()
