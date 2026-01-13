import tkinter as tk
from tkinter import ttk


class ColoredCombobox(ttk.Frame):
    def __init__(self, parent, values, colors, width=15, height=10, **kwargs):
        super().__init__(parent, **kwargs)

        self.values = values
        self.colors = colors
        self.height = height

        self.selected_var = tk.StringVar()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.entry = ttk.Entry(self, textvariable=self.selected_var,
                               width=width, state='readonly')
        self.entry.grid(row=0, column=0, sticky='ew')

        self.arrow_btn = ttk.Button(self, text='▼', width=2,
                                    command=self.toggle_listbox)
        self.arrow_btn.grid(row=0, column=1, padx=(1, 0), sticky='ns')

        self.top_popup = None
        self.listbox = None

        self.entry.bind('<Button-1>', self.toggle_listbox)
        self.bind('<Configure>', self._on_configure)

    def toggle_listbox(self, event=None):
        if self.top_popup and self.top_popup.winfo_exists():
            self.hide_listbox()
        else:
            self.show_listbox()

    def show_listbox(self):
        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height()
        w = self.winfo_width()

        self.top_popup = tk.Toplevel(self)
        self.top_popup.wm_overrideredirect(True)
        self.top_popup.configure(bg='white')

        frame = ttk.Frame(self.top_popup, relief='solid', borderwidth=1)
        frame.pack(expand=True, fill='both')

        scrollbar = ttk.Scrollbar(frame, orient='vertical')
        self.listbox = tk.Listbox(frame, height=min(self.height, len(self.values)),
                                  yscrollcommand=scrollbar.set,
                                  exportselection=False,
                                  relief='flat', bd=0, font=self.entry.cget("font"))

        scrollbar.config(command=self.listbox.yview)

        self.listbox.pack(side='left', fill='both', expand=True)
        if len(self.values) > self.height:
            scrollbar.pack(side='right', fill='y')

        for i, (val, col) in enumerate(zip(self.values, self.colors)):
            self.listbox.insert(i, val)
            self.listbox.itemconfig(i, {'fg': col})

        current = self.selected_var.get()
        if current in self.values:
            idx = self.values.index(current)
            self.listbox.selection_set(idx)
            self.listbox.see(idx)

        self.top_popup.update_idletasks()
        req_h = frame.winfo_reqheight()
        self.top_popup.geometry(f"{w}x{req_h}+{x}+{y}")

        self.listbox.bind('<<ListboxSelect>>', self._on_select)
        self.listbox.bind('<Return>', self._on_select)
        self.listbox.bind('<Escape>', self.hide_listbox)
        self.top_popup.bind('<FocusOut>', self._check_focus)

        self.listbox.focus_set()

    def hide_listbox(self, event=None):
        if self.top_popup:
            self.top_popup.destroy()
            self.top_popup = None

    def _on_select(self, event=None):
        if not self.listbox.curselection():
            return
        index = self.listbox.curselection()[0]
        value = self.values[index]
        color = self.colors[index]
        self.set(value, color)
        self.hide_listbox()

    def _check_focus(self, event):
        if self.top_popup:
            focused = self.focus_get()
            if focused is None or focused.winfo_toplevel() != self.top_popup:
                if focused != self.entry and focused != self.arrow_btn:
                    self.hide_listbox()

    def _on_configure(self, event):
        self.hide_listbox()

    def get(self):
        return self.selected_var.get()

    def set(self, value, color=None):
        if value in self.values:
            self.selected_var.set(value)
            if color is None:
                idx = self.values.index(value)
                color = self.colors[idx]
            self.entry.configure(foreground=color)