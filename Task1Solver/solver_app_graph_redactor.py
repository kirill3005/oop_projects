import sys
import json
import traceback
import networkx as nx
from typing import Optional, List, Dict, Any

from PySide6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene,
                               QGraphicsItem, QGraphicsEllipseItem,
                               QGraphicsLineItem, QGraphicsTextItem,
                               QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QPushButton, QFileDialog, QMessageBox, QLabel,
                               QTextEdit, QComboBox, QGroupBox, QSplitter)
from PySide6.QtCore import Qt, QRectF, QLineF, QPointF, Signal, QObject
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QPainterPathStroker, QAction

from auto_solver import find_isomorphisms_networkx


class GraphConfig:
    NODE_DIAMETER = 30
    NODE_RADIUS = NODE_DIAMETER / 2
    MIN_DISTANCE = 45

    COLOR_BG = QColor(40, 40, 40)
    COLOR_NODE = QColor(0, 180, 255)
    COLOR_NODE_ACTIVE = QColor(255, 0, 150)
    COLOR_NODE_ISO = QColor(100, 255, 100)
    COLOR_EDGE = QColor(200, 200, 200)
    COLOR_TEXT = QColor(255, 255, 255)


class EdgeItem(QGraphicsLineItem):
    def __init__(self, source, dest):
        super().__init__()
        self.source = source
        self.dest = dest
        self.setPen(QPen(GraphConfig.COLOR_EDGE, 2))
        self.setZValue(0)
        self.update_geometry()

    def update_geometry(self):
        self.setLine(QLineF(self.source.scenePos(), self.dest.scenePos()))

    def shape(self):
        path = super().shape()
        stroker = QPainterPathStroker()
        stroker.setWidth(10)
        return stroker.createStroke(path)


class NodeItem(QGraphicsEllipseItem):
    def __init__(self, name: str, x: float, y: float):
        rect = QRectF(-GraphConfig.NODE_RADIUS, -GraphConfig.NODE_RADIUS,
                      GraphConfig.NODE_DIAMETER, GraphConfig.NODE_DIAMETER)
        super().__init__(rect)
        self.name = name
        self.edges: List[EdgeItem] = []

        self.setBrush(QBrush(GraphConfig.COLOR_NODE))
        self.setPen(QPen(Qt.NoPen))
        self.setPos(x, y)
        self.setZValue(1)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsGeometryChanges)

        self.label = QGraphicsTextItem(name, self)
        self.label.setDefaultTextColor(GraphConfig.COLOR_TEXT)
        center_offset = -8 if len(name) < 2 else -12
        self.label.setPos(center_offset, -8)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for edge in self.edges:
                edge.update_geometry()
        return super().itemChange(change, value)

    def set_color_mode(self, mode: str):
        if mode == 'active':
            self.setBrush(QBrush(GraphConfig.COLOR_NODE_ACTIVE))
        elif mode == 'iso':
            self.setBrush(QBrush(GraphConfig.COLOR_NODE_ISO))
        else:
            self.setBrush(QBrush(GraphConfig.COLOR_NODE))


class GraphManager(QObject):
    graph_changed = Signal()
    node_count_changed = Signal(int)

    def __init__(self, scene: QGraphicsScene):
        super().__init__()
        self.scene = scene
        self.node_counter = 0

    def add_node(self, pos: QPointF, name: str = None) -> NodeItem:
        if not name:
            name = self._generate_name()
        node = NodeItem(name, pos.x(), pos.y())
        self.scene.addItem(node)
        self.graph_changed.emit()
        self.node_count_changed.emit(self.get_node_count())
        return node

    def add_edge(self, u: NodeItem, v: NodeItem):
        if u == v: return
        for e in u.edges:
            if e.dest == v or e.source == v: return

        edge = EdgeItem(u, v)
        self.scene.addItem(edge)
        u.edges.append(edge)
        v.edges.append(edge)
        self.graph_changed.emit()

    def remove_item(self, item):
        if isinstance(item, NodeItem):
            for edge in list(item.edges):
                self.remove_item(edge)
            self.scene.removeItem(item)
            self.node_count_changed.emit(self.get_node_count())
        elif isinstance(item, EdgeItem):
            item.source.edges.remove(item)
            item.dest.edges.remove(item)
            self.scene.removeItem(item)
        self.graph_changed.emit()

    def clear(self):
        self.scene.clear()
        self.node_counter = 0
        self.graph_changed.emit()
        self.node_count_changed.emit(0)

    def get_node_count(self) -> int:
        return len([i for i in self.scene.items() if isinstance(i, NodeItem)])

    def get_adj_dict(self) -> Dict[str, set]:
        adj = {node.name: set() for node in self._get_all_nodes()}
        for edge in self._get_all_edges():
            u, v = edge.source.name, edge.dest.name
            adj[u].add(v)
            adj[v].add(u)
        return adj

    def _get_all_nodes(self) -> List[NodeItem]:
        return [i for i in self.scene.items() if isinstance(i, NodeItem)]

    def _get_all_edges(self) -> List[EdgeItem]:
        return [i for i in self.scene.items() if isinstance(i, EdgeItem)]

    def _generate_name(self) -> str:
        n = self.node_counter
        name = ""
        while n >= 0:
            name = chr(ord('A') + (n % 26)) + name
            n = n // 26 - 1
        self.node_counter += 1
        return name


class MatrixWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        self.itemChanged.connect(self._on_change)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setStyleSheet("background-color: #323232; color: white; gridline-color: #555;")

    def resize_matrix(self, n: int):
        self.blockSignals(True)
        self.setRowCount(n)
        self.setColumnCount(n)
        labels = [f"П{i + 1}" for i in range(n)]
        self.setHorizontalHeaderLabels(labels)
        self.setVerticalHeaderLabels(labels)

        for r in range(n):
            for c in range(n):
                if not self.item(r, c):
                    item = QTableWidgetItem("0")
                    item.setTextAlignment(Qt.AlignCenter)
                    if r == c:
                        item.setFlags(Qt.ItemIsEnabled)
                        item.setBackground(QColor(60, 60, 60))
                    self.setItem(r, c, item)
        self.blockSignals(False)

    def _on_change(self, item):
        r, c = item.row(), item.column()
        if r != c:
            self.blockSignals(True)
            txt = item.text()
            other = self.item(c, r)
            if other: other.setText(txt)
            self.blockSignals(False)

    def get_matrix_data(self) -> List[List[Any]]:
        rows = self.rowCount()
        data = []
        for r in range(rows):
            row_data = []
            for c in range(rows):
                val = self.item(r, c).text().strip()
                if val == '*':
                    row_data.append(1)
                elif val.isdigit():
                    row_data.append(int(val))
                else:
                    row_data.append(0)
            data.append(row_data)
        return data


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graph Isomorphism Studio (PySide6)")
        self.resize(1100, 700)

        self.scene = QGraphicsScene(0, 0, 800, 600)
        self.scene.setBackgroundBrush(GraphConfig.COLOR_BG)
        self.gm = GraphManager(self.scene)
        self.current_mapping = {}

        self._setup_ui()
        self._setup_interactions()

        if not find_isomorphisms_networkx:
            QMessageBox.critical(self, "Ошибка", "Модуль core_solver.py не найден.")

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        left_panel = QWidget()
        l_layout = QVBoxLayout(left_panel)

        self.matrix_table = MatrixWidget()
        self.gm.node_count_changed.connect(self.matrix_table.resize_matrix)

        l_layout.addWidget(QLabel("Матрица смежности:"))
        l_layout.addWidget(self.matrix_table)

        m_btns = QHBoxLayout()
        btn_star = QPushButton("Заполнить '*'")
        btn_star.clicked.connect(lambda: self._fill_selection('*'))
        btn_zero = QPushButton("Заполнить '0'")
        btn_zero.clicked.connect(lambda: self._fill_selection('0'))
        m_btns.addWidget(btn_star)
        m_btns.addWidget(btn_zero)
        l_layout.addLayout(m_btns)

        iso_group = QGroupBox("Анализ")
        iso_layout = QVBoxLayout()

        self.btn_find = QPushButton("Найти изоморфизм")
        self.btn_find.clicked.connect(self.find_isomorphism)
        iso_layout.addWidget(self.btn_find)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(150)
        iso_layout.addWidget(self.log_output)

        iso_group.setLayout(iso_layout)
        l_layout.addWidget(iso_group)

        right_panel = QWidget()
        r_layout = QVBoxLayout(right_panel)

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        r_layout.addWidget(QLabel("Редактор графа (ЛКМ - узел, Shift+ЛКМ - ребро, ПКМ - удалить):"))
        r_layout.addWidget(self.view)

        btn_clear = QPushButton("Очистить граф")
        btn_clear.clicked.connect(self.gm.clear)
        r_layout.addWidget(btn_clear)

        splitter = QSplitter()
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 700])
        main_layout.addWidget(splitter)

    def find_isomorphism(self):
        if not find_isomorphisms_networkx: return

        matrix_data = self.matrix_table.get_matrix_data()
        n = len(matrix_data)
        row_headers = [f"П{i + 1}" for i in range(n)]

        graph_adj = self.gm.get_adj_dict()

        if len(graph_adj) != n:
            self.log_output.setText(f"Ошибка: Граф ({len(graph_adj)}) и Матрица ({n}) имеют разное число вершин.")
            return

        try:
            matcher = find_isomorphisms_networkx(matrix_data, row_headers, graph_adj)

            mapping = next(iter(matcher), None)

            self.log_output.clear()
            if mapping:
                self.current_mapping = mapping
                self.log_output.append("Изоморфизм найден:")
                for k, v in sorted(mapping.items()):
                    self.log_output.append(f"{k} -> {v}")

                nodes = self.gm._get_all_nodes()
                for node in nodes:
                    if node.name in mapping.values():
                        node.set_color_mode('iso')
            else:
                self.log_output.setText("Изоморфизм не найден.")
                self.current_mapping = {}
                for node in self.gm._get_all_nodes(): node.set_color_mode('normal')

        except Exception as e:
            self.log_output.setText(f"Ошибка:\n{traceback.format_exc()}")

    def _fill_selection(self, char):
        for item in self.matrix_table.selectedItems():
            if item.flags() & Qt.ItemIsEnabled:
                item.setText(char)


class InteractiveScene(QGraphicsScene):
    def __init__(self, manager: GraphManager, parent=None):
        super().__init__(parent)
        self.gm = manager
        self.active_node = None

    def mousePressEvent(self, event):
        pos = event.scenePos()
        item = self.itemAt(pos, self.views()[0].transform())

        if event.button() == Qt.LeftButton:
            if event.modifiers() & Qt.ShiftModifier:
                if isinstance(item, NodeItem):
                    if self.active_node and self.active_node != item:
                        self.gm.add_edge(self.active_node, item)
                        self.active_node.set_color_mode('normal')
                        self.active_node = None
                    else:
                        self.active_node = item
                        item.set_color_mode('active')
                else:
                    if self.active_node:
                        self.active_node.set_color_mode('normal')
                        self.active_node = None
            else:
                if not item:
                    self.gm.add_node(pos)

        elif event.button() == Qt.RightButton:
            if item: self.gm.remove_item(item)

        super().mousePressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    w = MainWindow()
    custom_scene = InteractiveScene(w.gm)
    custom_scene.setSceneRect(0, 0, 1000, 800)
    custom_scene.setBackgroundBrush(GraphConfig.COLOR_BG)
    w.scene = custom_scene
    w.gm.scene = custom_scene
    w.view.setScene(custom_scene)

    w.show()
    sys.exit(app.exec())