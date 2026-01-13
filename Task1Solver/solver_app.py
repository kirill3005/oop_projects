import tkinter as tk
import networkx as nx
from tkinter import ttk, messagebox
from typing import List, Dict, Tuple


from auto_solver import find_isomorphisms_networkx


class GraphIsomorphismApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Graph Isomorphism Finder (Tkinter)")
        self.root.geometry("850x650")

        self.matrix_entries: List[List[tk.Entry]] = []
        self.graph_nodes: List[str] = []
        self.graph_edges: List[Tuple[str, str]] = []
        self.graph_nx = nx.Graph()
        self.current_isomorphism: Dict[str, str] = {}

        self._init_ui()

    def _init_ui(self) -> None:
        matrix_frame = ttk.LabelFrame(self.root, text="1. Матрица смежности (Веса)", padding=10)
        matrix_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(matrix_frame, text="Размер (N):").pack(side="left")
        self.matrix_size = tk.StringVar(value="5")
        ttk.Entry(matrix_frame, textvariable=self.matrix_size, width=5).pack(side="left", padx=5)
        ttk.Button(matrix_frame, text="Пересоздать таблицу", command=self.create_matrix_table).pack(side="left", padx=5)

        self.matrix_container = ttk.Frame(self.root)
        self.matrix_container.pack(fill="x", padx=10, pady=5)

        graph_frame = ttk.LabelFrame(self.root, text="2. Топология Графа", padding=10)
        graph_frame.pack(fill="x", padx=10, pady=5)

        v_frame = ttk.Frame(graph_frame)
        v_frame.pack(fill="x", pady=2)
        ttk.Label(v_frame, text="Вершина:").pack(side="left")
        self.node_entry = ttk.Entry(v_frame, width=10)
        self.node_entry.pack(side="left", padx=5)
        ttk.Button(v_frame, text="Добавить", command=self.add_node).pack(side="left")

        e_frame = ttk.Frame(graph_frame)
        e_frame.pack(fill="x", pady=2)
        ttk.Label(e_frame, text="Ребро:").pack(side="left")
        self.edge_from = ttk.Combobox(e_frame, width=8, state="readonly")
        self.edge_from.pack(side="left", padx=2)
        ttk.Label(e_frame, text="->").pack(side="left")
        self.edge_to = ttk.Combobox(e_frame, width=8, state="readonly")
        self.edge_to.pack(side="left", padx=2)
        ttk.Button(e_frame, text="Соединить", command=self.add_edge).pack(side="left", padx=5)

        self.graph_display = tk.Text(graph_frame, height=4, width=80, state="disabled", bg="#f0f0f0")
        self.graph_display.pack(pady=5)

        calc_frame = ttk.LabelFrame(self.root, text="3. Расчеты", padding=10)
        calc_frame.pack(fill="both", expand=True, padx=10, pady=5)

        btn_box = ttk.Frame(calc_frame)
        btn_box.pack(fill="x")
        ttk.Button(btn_box, text="Найти Изоморфизм", command=self.find_isomorphism).pack(side="left", padx=5)
        ttk.Button(btn_box, text="Сброс", command=self.clear_all).pack(side="right", padx=5)

        path_box = ttk.Frame(calc_frame)
        path_box.pack(fill="x", pady=5)
        ttk.Label(path_box, text="Путь от:").pack(side="left")
        self.path_from = ttk.Combobox(path_box, width=8, state="readonly")
        self.path_from.pack(side="left", padx=2)
        ttk.Label(path_box, text="до:").pack(side="left")
        self.path_to = ttk.Combobox(path_box, width=8, state="readonly")
        self.path_to.pack(side="left", padx=2)
        ttk.Button(path_box, text="Рассчитать вес пути", command=self.calc_path_weight).pack(side="left", padx=10)

        self.result_text = tk.Text(calc_frame, height=8, width=80)
        self.result_text.pack(fill="both", expand=True, pady=5)

    def create_matrix_table(self) -> None:
        try:
            n = int(self.matrix_size.get())
            if not (2 <= n <= 12): raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Размер должен быть числом от 2 до 12")
            return

        for w in self.matrix_container.winfo_children(): w.destroy()
        self.matrix_entries = []

        for i in range(n):
            lbl = ttk.Label(self.matrix_container, text=f"П{i + 1}")
            lbl.grid(row=0, column=i + 1)
            lbl = ttk.Label(self.matrix_container, text=f"П{i + 1}")
            lbl.grid(row=i + 1, column=0)

        for i in range(n):
            row_widgets = []
            for j in range(n):
                entry = tk.Entry(self.matrix_container, width=5, justify='center')
                entry.grid(row=i + 1, column=j + 1, padx=1, pady=1)

                if i == j:
                    entry.insert(0, "0")
                    entry.config(state='disabled', disabledbackground='#ddd')
                else:
                    entry.insert(0, "0")
                    if i < j:
                        entry.bind('<KeyRelease>', lambda e, r=i, c=j: self._sync_matrix(r, c))

                row_widgets.append(entry)
            self.matrix_entries.append(row_widgets)

    def _sync_matrix(self, r: int, c: int) -> None:
        val = self.matrix_entries[r][c].get()
        self.matrix_entries[c][r].delete(0, tk.END)
        self.matrix_entries[c][r].insert(0, val)

    def add_node(self) -> None:
        node = self.node_entry.get().strip().upper()
        if node and node not in self.graph_nodes:
            self.graph_nodes.append(node)
            self.graph_nx.add_node(node)
            self.node_entry.delete(0, tk.END)
            self._update_ui_state()
        else:
            messagebox.showwarning("Внимание", "Некорректное имя или вершина уже есть")

    def add_edge(self) -> None:
        u, v = self.edge_from.get(), self.edge_to.get()
        if u and v and u != v:
            if not self.graph_nx.has_edge(u, v):
                self.graph_edges.append((u, v))
                self.graph_nx.add_edge(u, v)
                self._update_ui_state()

    def _update_ui_state(self) -> None:
        nodes_str = ", ".join(sorted(self.graph_nodes))
        edges_str = ", ".join([f"{u}-{v}" for u, v in self.graph_edges])

        self.graph_display.config(state="normal")
        self.graph_display.delete(1.0, tk.END)
        self.graph_display.insert(tk.END, f"V: {{{nodes_str}}}\nE: {{{edges_str}}}")
        self.graph_display.config(state="disabled")

        vals = sorted(self.graph_nodes)
        for cb in [self.edge_from, self.edge_to, self.path_from, self.path_to]:
            cb['values'] = vals

    def find_isomorphism(self) -> None:
        if not self.matrix_entries: return

        n = len(self.matrix_entries)
        matrix = []
        try:
            for r in range(n):
                row_vals = []
                for c in range(n):
                    val_str = self.matrix_entries[r][c].get()
                    val = int(val_str) if val_str.isdigit() else 0
                    row_vals.append(val)
                matrix.append(row_vals)
        except ValueError:
            messagebox.showerror("Ошибка", "Матрица должна содержать целые числа")
            return

        p_nodes = [f"П{i + 1}" for i in range(n)]
        adj_dict = {n: set(self.graph_nx.neighbors(n)) for n in self.graph_nodes}

        try:
            iso_gen = find_isomorphisms_networkx(matrix, p_nodes, adj_dict)
            result = next(iter(iso_gen), None)

            self.result_text.delete(1.0, tk.END)
            if result:
                self.current_isomorphism = result
                self.result_text.insert(tk.END, "Изоморфизм найден!\n\n")
                for k, v in sorted(result.items(), key=lambda x: int(x[0][1:])):
                    self.result_text.insert(tk.END, f"{k} -> {v}\n")
            else:
                self.current_isomorphism = {}
                self.result_text.insert(tk.END, "Изоморфизм не найден.")

        except Exception as e:
            messagebox.showerror("Ошибка алгоритма", str(e))

    def calc_path_weight(self) -> None:
        if not self.current_isomorphism:
            messagebox.showinfo("Инфо", "Сначала найдите изоморфизм")
            return

        start, end = self.path_from.get(), self.path_to.get()
        if not start or not end or start == end: return

        G_weighted = nx.Graph()

        inv_map = {v: k for k, v in self.current_isomorphism.items()}

        for u in self.graph_nodes:
            for v in self.graph_nodes:
                if u == v: continue
                try:
                    idx_u = int(inv_map[u][1:]) - 1
                    idx_v = int(inv_map[v][1:]) - 1
                    weight = int(self.matrix_entries[idx_u][idx_v].get())
                    if weight > 0:
                        G_weighted.add_edge(u, v, weight=weight)
                except (KeyError, ValueError):
                    pass

        try:
            path = nx.shortest_path(G_weighted, start, end, weight='weight')
            w = nx.path_weight(G_weighted, path, weight='weight')
            self.result_text.insert(tk.END, f"\nПуть {start}->{end}: {'->'.join(path)} (Сумма: {w})\n")
        except nx.NetworkXNoPath:
            self.result_text.insert(tk.END, f"\nНет пути между {start} и {end} с учетом весов матрицы.\n")

    def clear_all(self):
        self.graph_nx.clear()
        self.graph_nodes.clear()
        self.graph_edges.clear()
        self.current_isomorphism = {}
        self.result_text.delete(1.0, tk.END)
        self._update_ui_state()
        for row in self.matrix_entries:
            for entry in row:
                if entry['state'] == 'normal':
                    entry.delete(0, tk.END)
                    entry.insert(0, "0")


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphIsomorphismApp(root)
    root.mainloop()