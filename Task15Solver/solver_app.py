import sys
from typing import Dict, Tuple, List, Callable
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QTextEdit, QSpinBox, QComboBox, QTableWidget,
                               QTableWidgetItem, QDoubleSpinBox, QMessageBox)


class SegmentSolver(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Задача 15 ЕГЭ - Отрезки (Refactored)")
        self.resize(700, 600)
        self._init_ui()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        main_layout.addWidget(QLabel("Известные отрезки (имя, начало, конец):"))
        self.table = QTableWidget(5, 3)
        self.table.setHorizontalHeaderLabels(["Имя", "Начало", "Конец"])
        self.table.setMaximumHeight(150)

        self._add_table_item(0, "B", "10", "15")
        self._add_table_item(1, "C", "20", "27")
        main_layout.addWidget(self.table)

        main_layout.addWidget(QLabel("Логическое выражение (используйте B(x), C(x), A(x), impl(A, B), and, or, not):"))
        self.expr_input = QLineEdit("not(impl(B(x) or C(x), A(x)))")
        main_layout.addWidget(self.expr_input)

        params_layout = QHBoxLayout()

        self.a_min = self._create_spinbox(params_layout, "A от:", 0)
        self.a_max = self._create_spinbox(params_layout, "до:", 100)
        self.x_min = self._create_spinbox(params_layout, "x от:", 0)
        self.x_max = self._create_spinbox(params_layout, "до:", 100)

        params_layout.addWidget(QLabel("шаг x:"))
        self.step_spin = QDoubleSpinBox()
        self.step_spin.setRange(0.1, 10.0)
        self.step_spin.setValue(0.5)
        params_layout.addWidget(self.step_spin)

        main_layout.addLayout(params_layout)

        search_layout = QHBoxLayout()

        search_layout.addWidget(QLabel("Искать:"))
        self.search_mode = QComboBox()
        self.search_mode.addItems(["мин. длину A", "макс. длину A", "все подходящие A"])
        search_layout.addWidget(self.search_mode)

        search_layout.addWidget(QLabel("Условие:"))
        self.condition_mode = QComboBox()
        self.condition_mode.addItems(["Истинно (True) при всех x", "Ложно (False) при всех x"])
        search_layout.addWidget(self.condition_mode)

        search_layout.addStretch()
        main_layout.addLayout(search_layout)

        self.solve_btn = QPushButton("РЕШИТЬ")
        self.solve_btn.clicked.connect(self.solve)
        main_layout.addWidget(self.solve_btn)

        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        main_layout.addWidget(self.result_area)

    def _add_table_item(self, row: int, name: str, start: str, end: str):
        self.table.setItem(row, 0, QTableWidgetItem(name))
        self.table.setItem(row, 1, QTableWidgetItem(start))
        self.table.setItem(row, 2, QTableWidgetItem(end))

    def _create_spinbox(self, layout, label_text, default_val):
        layout.addWidget(QLabel(label_text))
        spin = QSpinBox()
        spin.setRange(-1000, 1000)
        spin.setValue(default_val)
        layout.addWidget(spin)
        return spin

    def _get_segments_from_ui(self) -> Dict[str, Tuple[float, float]]:
        segments = {}
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0)
            start_item = self.table.item(row, 1)
            end_item = self.table.item(row, 2)

            if name_item and start_item and end_item:
                name = name_item.text().strip()
                s_txt = start_item.text().strip()
                e_txt = end_item.text().strip()
                if name and s_txt and e_txt:
                    try:
                        segments[name] = (float(s_txt), float(e_txt))
                    except ValueError:
                        continue
        return segments

    def solve(self):
        try:
            segments = self._get_segments_from_ui()
            if not segments:
                QMessageBox.warning(self, "Ошибка", "Не заданы отрезки (B, C и т.д.)")
                return

            expression = self.expr_input.text().strip()
            if not expression:
                QMessageBox.warning(self, "Ошибка", "Введите логическое выражение")
                return

            a_start, a_end = self.a_min.value(), self.a_max.value()
            x_start, x_end = self.x_min.value(), self.x_max.value()
            step = self.step_spin.value()

            search_type = self.search_mode.currentIndex()
            must_be_true = (self.condition_mode.currentIndex() == 0)

            def in_seg(start, end, val):
                return start <= val <= end

            def impl(a, b):
                return (not a) or b

            eval_context = {'impl': impl, '__builtins__': {}}

            for name, (s, e) in segments.items():
                eval_context[name] = lambda x, s=s, e=e: in_seg(s, e, x)

            x_values = []
            curr_x = x_start
            while curr_x <= x_end:
                x_values.append(curr_x)
                curr_x += step

            total_checks = len(x_values)
            valid_segments = []

            best_len = float('inf') if search_type == 0 else float('-inf')
            best_segment = None

            for a in range(a_start, a_end + 1):
                for b in range(a, a_end + 1):

                    eval_context['A'] = lambda x, a=a, b=b: in_seg(a, b, x)

                    is_valid_for_all_x = True
                    for val_x in x_values:
                        eval_context['x'] = val_x
                        try:
                            res = eval(expression, eval_context)

                            if must_be_true and not res:
                                is_valid_for_all_x = False
                                break
                            if not must_be_true and res:
                                is_valid_for_all_x = False
                                break
                        except Exception:
                            is_valid_for_all_x = False
                            break

                    if is_valid_for_all_x:
                        length = b - a
                        valid_segments.append((a, b, length))

                        if search_type == 0:
                            if length < best_len:
                                best_len = length
                                best_segment = (a, b)
                        elif search_type == 1:
                            if length > best_len:
                                best_len = length
                                best_segment = (a, b)

            output = []
            output.append(f"Исходные отрезки: {segments}")
            output.append(f"Выражение: {expression}")
            output.append(f"Проверено точек X: {total_checks} (шаг {step})\n")

            if valid_segments:
                if search_type == 2:
                    output.append(f"Найдено {len(valid_segments)} подходящих отрезков A:")
                    for a, b, l in sorted(valid_segments)[:20]:
                        output.append(f"  A=[{a}; {b}], длина {l}")
                    if len(valid_segments) > 20:
                        output.append("  ... и другие ...")
                else:
                    if best_segment:
                        type_str = "Минимальная" if search_type == 0 else "Максимальная"
                        output.append(f"{type_str} длина: {best_len}")
                        output.append(f"Отрезок A: [{best_segment[0]}; {best_segment[1]}]")
            else:
                output.append("Подходящих отрезков A не найдено в заданном диапазоне.")

            self.result_area.setText("\n".join(output))

        except Exception as e:
            self.result_area.setText(f"Критическая ошибка: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SegmentSolver()
    window.show()
    sys.exit(app.exec())