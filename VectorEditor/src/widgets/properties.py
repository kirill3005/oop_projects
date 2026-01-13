from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpinBox, QPushButton, QColorDialog, QDoubleSpinBox
from PySide6.QtCore import Qt
from src.logic.commands import ChangeColorCommand, ChangeWidthCommand, ChangeGeometryCommand

class PropertiesPanel(QWidget):
    def __init__(self, scene, undo_stack):
        super().__init__()
        self.scene = scene
        self.undo_stack = undo_stack
        self._init_ui()
        self.scene.selectionChanged.connect(self.on_selection_changed)

    def _init_ui(self):
        self.setFixedWidth(220)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("<b>Properties</b>"))

        self.lbl_type = QLabel("None")
        layout.addWidget(self.lbl_type)

        layout.addWidget(QLabel("Position (X, Y):"))
        self.spin_x = QDoubleSpinBox()
        self.spin_x.setRange(-10000, 10000)
        self.spin_x.valueChanged.connect(self.on_geo_changed)
        layout.addWidget(self.spin_x)

        self.spin_y = QDoubleSpinBox()
        self.spin_y.setRange(-10000, 10000)
        self.spin_y.valueChanged.connect(self.on_geo_changed)
        layout.addWidget(self.spin_y)

        layout.addWidget(QLabel("Stroke Width:"))
        self.spin_width = QSpinBox()
        self.spin_width.setRange(1, 50)
        self.spin_width.valueChanged.connect(self.on_width_changed)
        layout.addWidget(self.spin_width)

        layout.addWidget(QLabel("Color:"))
        self.btn_color = QPushButton("Pick Color")
        self.btn_color.clicked.connect(self.on_color_clicked)
        layout.addWidget(self.btn_color)

        layout.addStretch()
        self.setEnabled(False)

    def on_selection_changed(self):
        sel = self.scene.selectedItems()
        if not sel:
            self.setEnabled(False)
            self.lbl_type.setText("None")
            return

        self.setEnabled(True)
        item = sel[0]

        self.blockSignals(True)

        t_name = getattr(item, "type_name", "Unknown")
        if len(sel) > 1: t_name += f" (+{len(sel)-1})"
        self.lbl_type.setText(t_name)

        self.spin_x.setValue(item.x())
        self.spin_y.setValue(item.y())

        if hasattr(item, "current_width"):
            self.spin_width.setValue(item.current_width)
        if hasattr(item, "current_color"):
            self.btn_color.setStyleSheet(f"background-color: {item.current_color}")

        self.blockSignals(False)

    def on_width_changed(self, val):
        sel = self.scene.selectedItems()
        if not sel: return
        self.undo_stack.beginMacro("Change Width")
        for item in sel:
            self.undo_stack.push(ChangeWidthCommand(item, val))
        self.undo_stack.endMacro()
        self.scene.update()

    def on_color_clicked(self):
        c = QColorDialog.getColor()
        if c.isValid():
            hex_c = c.name()
            self.btn_color.setStyleSheet(f"background-color: {hex_c}")
            sel = self.scene.selectedItems()
            if sel:
                self.undo_stack.beginMacro("Change Color")
                for item in sel:
                    self.undo_stack.push(ChangeColorCommand(item, hex_c))
                self.undo_stack.endMacro()

    def on_geo_changed(self):
        sel = self.scene.selectedItems()
        if not sel: return
        item = sel[0]
        from PySide6.QtCore import QPointF
        new_pt = QPointF(self.spin_x.value(), self.spin_y.value())
        if new_pt != item.pos():
            self.undo_stack.push(ChangeGeometryCommand(item, new_pt))
