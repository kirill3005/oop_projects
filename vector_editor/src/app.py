import json
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QToolBar, QFileDialog, QMessageBox, QVBoxLayout
from PySide6.QtGui import QAction, QKeySequence
from src.widgets.canvas import EditorCanvas
from src.widgets.properties import PropertiesPanel
from src.constants import *
from src.logic.strategies import JsonSaveStrategy, ImageSaveStrategy
from src.logic.factory import ShapeFactory

class VectorEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vector Editor v1.0")
        self.resize(1000, 700)

        self.canvas = EditorCanvas()
        self.props = PropertiesPanel(self.canvas.scene, self.canvas.undo_stack)

        self._init_ui()
        self._create_actions()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0,0,0,0)

        canvas_container = QWidget()
        canvas_container.setStyleSheet("background-color: #555;")
        v_layout = QVBoxLayout(canvas_container)
        v_layout.addWidget(self.canvas)

        main_layout.addWidget(canvas_container, stretch=1)
        main_layout.addWidget(self.props)

        self.statusBar().showMessage("Ready")

    def _create_actions(self):
        toolbar = self.addToolBar("Tools")

        self._add_tool_action(toolbar, "Select", TOOL_SELECT)
        self._add_tool_action(toolbar, "Rect", TOOL_RECT)
        self._add_tool_action(toolbar, "Ellipse", TOOL_ELLIPSE)
        self._add_tool_action(toolbar, "Line", TOOL_LINE)

        toolbar.addSeparator()

        undo_act = self.canvas.undo_stack.createUndoAction(self, "Undo")
        undo_act.setShortcut(QKeySequence.Undo)
        toolbar.addAction(undo_act)

        redo_act = self.canvas.undo_stack.createRedoAction(self, "Redo")
        redo_act.setShortcut(QKeySequence.Redo)
        toolbar.addAction(redo_act)

        del_act = QAction("Delete", self)
        del_act.setShortcut("Delete")
        del_act.triggered.connect(self.canvas.delete_selected)
        self.addAction(del_act)

        toolbar.addSeparator()

        grp_act = QAction("Group", self)
        grp_act.setShortcut("Ctrl+G")
        grp_act.triggered.connect(self.canvas.group_selection)
        toolbar.addAction(grp_act)

        ungrp_act = QAction("Ungroup", self)
        ungrp_act.setShortcut("Ctrl+U")
        ungrp_act.triggered.connect(self.canvas.ungroup_selection)
        toolbar.addAction(ungrp_act)

        menu = self.menuBar().addMenu("File")

        save_act = QAction("Save...", self)
        save_act.setShortcut("Ctrl+S")
        save_act.triggered.connect(self.on_save)
        menu.addAction(save_act)

        open_act = QAction("Open...", self)
        open_act.setShortcut("Ctrl+O")
        open_act.triggered.connect(self.on_open)
        menu.addAction(open_act)

    def _add_tool_action(self, toolbar, name, tool_id):
        act = QAction(name, self)
        act.setCheckable(True)
        act.triggered.connect(lambda: self._set_tool(tool_id, act))
        toolbar.addAction(act)
        if not hasattr(self, "tool_actions"): self.tool_actions = []
        self.tool_actions.append(act)

    def _set_tool(self, tool_id, action):
        for act in self.tool_actions:
            act.setChecked(False)
        action.setChecked(True)
        self.canvas.set_tool(tool_id)
        self.statusBar().showMessage(f"Tool: {tool_id}")

    def on_save(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Save", "", "JSON (*.json);;PNG (*.png)")
        if not fname: return

        if fname.endswith(".png"):
            strategy = ImageSaveStrategy("PNG", "white")
        else:
            strategy = JsonSaveStrategy()

        try:
            strategy.save(fname, self.canvas.scene)
            self.statusBar().showMessage(f"Saved: {fname}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def on_open(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open", "", "JSON (*.json)")
        if not fname: return

        try:
            with open(fname, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.canvas.scene.clear()
            self.canvas.undo_stack.clear()

            for s_data in data.get("shapes", []):
                item = ShapeFactory.from_dict(s_data)
                if item:
                    self.canvas.scene.addItem(item)

            self.statusBar().showMessage(f"Loaded: {fname}")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
