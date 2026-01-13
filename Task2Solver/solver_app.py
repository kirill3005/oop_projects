import tkinter as tk
from tkinter import ttk, messagebox
from typing import List

from custom_ttk import ColoredCombobox
from auto_solver import LogicSolver


class LogicApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Логический решатель (ЕГЭ)")
        self.root.geometry("850x600")

        self.replacements = {
            '→': '<=',
            '≡': '==',
            '∧': ' and ',
            '∨': ' or ',
            '¬': ' not '
        }

        self.table_rows_widgets: List[List[ColoredCombobox]] = []

        self._init_ui()

    def _init_ui(self):
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill=tk.X)

        frame_vars = ttk.LabelFrame(top_frame, text="1. Переменные", padding=5)
        frame_vars.pack(fill=tk.X, pady=5)

        self.entry_vars = ttk.Entry(frame_vars, font=("Arial", 11))
        self.entry_vars.pack(fill=tk.X, padx=5, pady=5)
        self.entry_vars.insert(0, "xyzw")

        frame_expr = ttk.LabelFrame(top_frame, text="2. Логическое выражение", padding=5)
        frame_expr.pack(fill=tk.X, pady=5)

        self.entry_expr = ttk.Entry(frame_expr, font=("Arial", 12))
        self.entry_expr.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        ttk.Button(frame_expr, text="Очистить",
                   command=lambda: self.entry_expr.delete(0, tk.END)).pack(side=tk.LEFT, padx=5)

        frame_kb = ttk.Frame(top_frame)
        frame_kb.pack(fill=tk.X, pady=5)

        symbols = ['→', '¬', '∧', '∨', '≡', '(', ')']
        for sym in symbols:
            ttk.Button(frame_kb, text=sym, width=4,
                       command=lambda s=sym: self._insert_char(s)).pack(side=tk.LEFT, padx=2)

        ttk.Button(frame_kb, text="Обновить кнопки переменных",
                   command=self._create_var_buttons).pack(side=tk.RIGHT, padx=10)

        self.frame_var_btns = ttk.Frame(top_frame)
        self.frame_var_btns.pack(fill=tk.X, pady=2)

        mid_frame = ttk.Frame(self.root, padding=10)
        mid_frame.pack(fill=tk.X)

        ttk.Label(mid_frame, text="Строк во фрагменте:").pack(side=tk.LEFT)
        self.spin_rows = ttk.Spinbox(mid_frame, from_=1, to=16, width=5)
        self.spin_rows.set(3)
        self.spin_rows.pack(side=tk.LEFT, padx=5)

        ttk.Button(mid_frame, text="Создать таблицу",
                   command=self.create_table).pack(side=tk.LEFT, padx=15)

        self.bottom_frame = ttk.Frame(self.root, padding=10)
        self.bottom_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.bottom_frame)
        scrollbar = ttk.Scrollbar(self.bottom_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = ttk.Frame(self.canvas)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        answer_frame = ttk.Frame(self.root, padding=15)
        answer_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.btn_solve = ttk.Button(answer_frame, text="РЕШИТЬ", command=self.solve)
        self.btn_solve.pack(side=tk.LEFT)

        self.lbl_result = ttk.Label(answer_frame, text="...", font=("Arial", 14, "bold"))
        self.lbl_result.pack(side=tk.LEFT, padx=20)

        self._create_var_buttons()

    def _insert_char(self, char):
        idx = self.entry_expr.index(tk.INSERT)
        self.entry_expr.insert(idx, char)

    def _create_var_buttons(self):
        for w in self.frame_var_btns.winfo_children():
            w.destroy()

        vars_str = self.entry_vars.get().replace(" ", "")
        for char in vars_str:
            ttk.Button(self.frame_var_btns, text=char, width=4,
                       command=lambda c=char: self._insert_char(c)).pack(side=tk.LEFT, padx=2)

    def create_table(self):
        for row in self.table_rows_widgets:
            for w in row:
                w.destroy()
        self.table_rows_widgets.clear()

        vars_str = self.entry_vars.get().replace(" ", "")
        try:
            rows_count = int(self.spin_rows.get())
        except ValueError:
            return

        cols_count = len(vars_str)
        if cols_count == 0:
            messagebox.showwarning("Ошибка", "Введите переменные!")
            return

        for _ in range(rows_count):
            row_widgets = []
            row_container = ttk.Frame(self.scroll_frame)
            row_container.pack(fill=tk.X, pady=2)

            for _ in range(cols_count):
                cb = ColoredCombobox(row_container,
                                     values=['0', '1', ' '],
                                     colors=['red', 'green', 'gray'], width=5)
                cb.set(' ')
                cb.pack(side=tk.LEFT, padx=2)
                row_widgets.append(cb)

            ttk.Label(row_container, text="| F = ").pack(side=tk.LEFT, padx=5)

            cb_res = ColoredCombobox(row_container,
                                     values=['0', '1'],
                                     colors=['red', 'green'], width=5)
            cb_res.set('1')
            cb_res.pack(side=tk.LEFT)
            row_widgets.append(cb_res)

            self.table_rows_widgets.append(row_widgets)

    def _get_data(self):
        fragment = []
        results = []

        for row in self.table_rows_widgets:
            var_combos = row[:-1]
            res_combo = row[-1]

            line_vals = []
            for cb in var_combos:
                val = cb.get()
                if val == '1':
                    line_vals.append(True)
                elif val == '0':
                    line_vals.append(False)
                else:
                    line_vals.append(None)

            fragment.append(line_vals)

            res_val = res_combo.get()
            results.append(True if res_val == '1' else False)

        return fragment, results

    def solve(self):
        vars_str = self.entry_vars.get().replace(" ", "")
        raw_expr = self.entry_expr.get().strip()
        variable_names = list(vars_str)

        if not raw_expr or not variable_names:
            messagebox.showerror("Ошибка", "Заполните выражение и переменные")
            return

        py_expr = raw_expr
        for sym, replacement in self.replacements.items():
            py_expr = py_expr.replace(sym, replacement)

        fragment, results = self._get_data()

        try:
            solver = LogicSolver(fragment, results, py_expr, variable_names)
            answer = solver.solve()

            if answer == "Solution not found":
                self.lbl_result.config(text="Решение не найдено", foreground="red")
            else:
                self.lbl_result.config(text=f"Ответ: {answer}", foreground="green")

        except Exception as e:
            self.lbl_result.config(text="Ошибка вычисления", foreground="red")
            print(e)


if __name__ == "__main__":
    root = tk.Tk()
    app = LogicApp(root)
    root.mainloop()