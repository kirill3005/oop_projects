import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QGroupBox, QLabel, QSpinBox, QComboBox,
                             QPushButton, QListWidget, QListWidgetItem,
                             QTabWidget, QTextEdit, QMessageBox, QFormLayout,
                             QDialog, QDialogButtonBox)

from auto_solver import (
    Game, Analyzer, TerminalCondition,
    AddMove, SubtractMove, MultiplyMove, DivideMove
)


class MoveDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить тип хода")
        self.setModal(True)
        self.move_obj = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.move_type = QComboBox()
        self.move_type.addItems(["Сложить", "Вычесть", "Умножить", "Разделить"])
        self.move_type.currentTextChanged.connect(self.on_move_type_changed)

        self.value_input = QSpinBox()
        self.value_input.setRange(1, 1000)

        form_layout.addRow("Тип хода:", self.move_type)
        form_layout.addRow("Значение:", self.value_input)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.on_move_type_changed(self.move_type.currentText())
        self.setLayout(layout)

    def on_move_type_changed(self, move_type):
        self.value_input.setVisible(True)

    def validate_and_accept(self):
        move_type = self.move_type.currentText()
        val = self.value_input.value()

        if move_type == "Сложить":
            self.move_obj = AddMove(val)
        elif move_type == "Вычесть":
            self.move_obj = SubtractMove(val)
        elif move_type == "Умножить":
            self.move_obj = MultiplyMove(val)
        elif move_type == "Разделить":
            self.move_obj = DivideMove(val)

        self.accept()


class TerminalConditionWidget(QGroupBox):
    def __init__(self):
        super().__init__("Конечное условие")
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        self.comparator = QComboBox()
        self.comparator.addItems(["<=", ">="])

        self.threshold = QSpinBox()
        self.threshold.setRange(0, 10000)
        self.threshold.setValue(30)

        layout.addWidget(QLabel("Окончание игры когда S"))
        layout.addWidget(self.comparator)
        layout.addWidget(self.threshold)
        layout.addStretch()

        self.setLayout(layout)

    def get_condition(self):
        comparator_map = {"<=": "le", ">=": "ge"}
        return TerminalCondition(
            threshold=self.threshold.value(),
            comparator=comparator_map[self.comparator.currentText()]
        )


class MoveListWidget(QGroupBox):
    def __init__(self):
        super().__init__("Ходы")
        self.moves = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.list_widget = QListWidget()

        button_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить ход")
        remove_btn = QPushButton("Удалить выбранный ход")

        add_btn.clicked.connect(self.add_move)
        remove_btn.clicked.connect(self.remove_move)

        button_layout.addWidget(add_btn)
        button_layout.addWidget(remove_btn)
        button_layout.addStretch()

        layout.addWidget(self.list_widget)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def add_move(self):
        dialog = MoveDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            if dialog.move_obj:
                self.moves.append(dialog.move_obj)
                self.update_list()

    def remove_move(self):
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            self.moves.pop(current_row)
            self.update_list()

    def update_list(self):
        self.list_widget.clear()
        for move in self.moves:
            item = QListWidgetItem(move.name)
            self.list_widget.addItem(item)

    def get_moves(self):
        return self.moves.copy()


class AnalysisSettingsWidget(QGroupBox):
    def __init__(self):
        super().__init__("Настройки игры")
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.s_min = QSpinBox()
        self.s_min.setRange(0, 10000)
        self.s_min.setValue(31)

        self.s_max = QSpinBox()
        self.s_max.setRange(1, 10000)
        self.s_max.setValue(600)

        self.monotonic = QComboBox()
        self.monotonic.addItems(["увеличение", "уменьшение"])

        layout.addRow("Мин S:", self.s_min)
        layout.addRow("Макс S:", self.s_max)
        layout.addRow("Изменение S:", self.monotonic)

        self.setLayout(layout)


class ResultsWidget(QGroupBox):
    def __init__(self):
        super().__init__("Результаты")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)
        self.setLayout(layout)

    def update_results(self, results, full_analysis=None):
        text = "<h3>Результаты игры</h3>"
        text += f"<b>Задание 19 (мин L1):</b> {results['19']}<br/>"

        res20 = results['20']
        res20_str = ", ".join(map(str, res20)) if res20 else "Нет решений"
        text += f"<b>Задание 20 (первые 2 W2):</b> {res20_str}<br/>"

        text += f"<b>Задание 21 (мин L2):</b> {results['21']}<br/>"


        self.results_text.setHtml(text)


class GameAnalyzerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Солвер 19-21 задание ЕГЭ")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        self.terminal_widget = TerminalConditionWidget()
        self.moves_widget = MoveListWidget()
        self.settings_widget = AnalysisSettingsWidget()
        self.results_widget = ResultsWidget()

        self.analyze_btn = QPushButton("Проанализировать игру")
        self.analyze_btn.clicked.connect(self.analyze_game)

        tab_widget = QTabWidget()

        config_tab = QWidget()
        config_layout = QVBoxLayout()
        config_layout.addWidget(self.terminal_widget)
        config_layout.addWidget(self.moves_widget)
        config_layout.addWidget(self.settings_widget)
        config_layout.addWidget(self.analyze_btn)
        config_tab.setLayout(config_layout)

        results_tab = QWidget()
        results_layout = QVBoxLayout()
        results_layout.addWidget(self.results_widget)
        results_tab.setLayout(results_layout)

        tab_widget.addTab(config_tab, "Конфигурация")
        tab_widget.addTab(results_tab, "Результаты")

        main_layout.addWidget(tab_widget)
        central_widget.setLayout(main_layout)

    def analyze_game(self):
        try:
            terminal_condition = self.terminal_widget.get_condition()
            moves = self.moves_widget.get_moves()

            if not moves:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, добавьте хотя бы один ход.")
                return

            s_min = self.settings_widget.s_min.value()
            s_max = self.settings_widget.s_max.value()
            monotonic_str = self._get_monotonic()

            game = Game(
                terminal=terminal_condition,
                moves=moves,
                s_min=s_min,
                s_max=s_max,
                monotonic=monotonic_str,
            )

            analyzer = Analyzer(game)
            results = analyzer.solve_19_20_21()

            self.results_widget.update_results(results)

            QMessageBox.information(self, "Готово", "Анализ завершен успешно!")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка анализа", f"Произошла ошибка: {str(e)}")

    def _get_monotonic(self) -> str:
        monotonic = self.settings_widget.monotonic.currentText()
        mon_dict = {'уменьшение': 'decreasing', 'увеличение': 'increasing'}
        return mon_dict.get(monotonic, 'decreasing')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameAnalyzerGUI()
    window.show()
    sys.exit(app.exec_())