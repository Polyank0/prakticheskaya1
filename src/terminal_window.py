"""Окно терминала: ввод и вывод идут в одном текстовом поле."""

import tkinter as tk
from tkinter import scrolledtext
from typing import Optional

from src.session import Session

INPUT_MARK = "input_start"
WINDOW_SIZE = "800x480"
CLOSE_DELAY_MS = 500
SCRIPT_STEP_MS = 350
FONT = ("Courier New", 12)
COLORS = {
    "back": "#fdf6e3",
    "text": "#073642",
    "prompt": "#268bd2",
    "error": "#dc322f",
    "note": "#839496",
}


class TerminalWindow:
    """Графическое окно эмулятора оболочки."""

    def __init__(self, session: Session) -> None:
        """Создаёт окно, текстовое поле и первое приглашение."""
        self.session = session
        self.pending: list[str] = []
        self.root = tk.Tk()
        self.root.title(session.title())
        self.root.geometry(WINDOW_SIZE)
        self.text = scrolledtext.ScrolledText(
            self.root,
            wrap="char",
            font=FONT,
            bg=COLORS["back"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            borderwidth=0,
            padx=10,
            pady=8,
        )
        self.text.pack(fill="both", expand=True)
        for tag in ("prompt", "error", "note"):
            self.text.tag_configure(tag, foreground=COLORS[tag])
        self._bind_keys()
        self.show_prompt()
        self.text.focus_set()

    def _bind_keys(self) -> None:
        """Назначает обработчики клавиш текстового поля."""
        self.text.bind("<Key>", self._on_key)
        self.text.bind("<Return>", self._on_enter)
        self.text.bind("<BackSpace>", self._on_step_back)
        self.text.bind("<Left>", self._on_step_back)
        self.text.bind("<Home>", self._on_home)
        self.text.bind("<Up>", self._ignore_key)
        self.text.bind("<Down>", self._ignore_key)

    def write(self, text: str, tag: str = "") -> None:
        """Дописывает текст в конец поля и прокручивает к нему."""
        self.text.insert("end", text, tag)
        self.text.see("end")

    def show_notes(self, lines: list[str], tag: str = "note") -> None:
        """Печатает служебные строки перед текущим приглашением."""
        self.text.delete("end-1l linestart", "end-1c")
        for line in lines:
            self.write(line + "\n", tag)
        self.show_prompt()

    def play_script(self, lines: list[str]) -> None:
        """Выполняет строки скрипта по очереди, имитируя ввод."""
        self.pending = list(lines)
        self.root.after(SCRIPT_STEP_MS, self._play_next_line)

    def _play_next_line(self) -> None:
        """Печатает и выполняет очередную строку скрипта."""
        if not self.pending or not self.session.running:
            self.pending = []
            return
        line = self.pending.pop(0)
        self.write(line, "note" if line.lstrip().startswith("#") else "")
        self.submit(line)
        self.root.after(SCRIPT_STEP_MS, self._play_next_line)

    def show_prompt(self) -> None:
        """Печатает приглашение и запоминает начало области ввода."""
        self.write(self.session.prompt(), "prompt")
        self.text.mark_set(INPUT_MARK, "end-1c")
        self.text.mark_gravity(INPUT_MARK, "left")
        self.text.mark_set("insert", "end")

    def typed_text(self) -> str:
        """Возвращает текст, набранный после приглашения."""
        return self.text.get(INPUT_MARK, "end-1c")

    def submit(self, line: str) -> None:
        """Выполняет строку, печатает ответ и новое приглашение."""
        self.write("\n")
        reply = self.session.run_line(line)
        if reply.text:
            self.write(reply.text + "\n", "error" if reply.failed else "")
        if not self.session.running:
            self.root.after(CLOSE_DELAY_MS, self.root.destroy)
            return
        self.show_prompt()

    def _keep_cursor_in_input(self) -> None:
        """Возвращает курсор в область ввода и снимает выделение."""
        self.text.tag_remove("sel", "1.0", "end")
        if self.text.compare("insert", "<", INPUT_MARK):
            self.text.mark_set("insert", "end")

    def _on_key(self, _event: tk.Event) -> Optional[str]:
        """Не даёт редактировать уже выведенный текст."""
        if self.pending:
            return "break"
        self._keep_cursor_in_input()
        return None

    def _on_enter(self, _event: tk.Event) -> str:
        """Отправляет набранную строку на выполнение."""
        if not self.pending:
            self.submit(self.typed_text())
        return "break"

    def _on_step_back(self, _event: tk.Event) -> Optional[str]:
        """Запрещает стирать приглашение и уходить левее него."""
        self._keep_cursor_in_input()
        if self.text.compare("insert", "<=", INPUT_MARK):
            return "break"
        return None

    def _on_home(self, _event: tk.Event) -> str:
        """Ставит курсор в начало области ввода."""
        self.text.mark_set("insert", INPUT_MARK)
        return "break"

    def _ignore_key(self, _event: tk.Event) -> str:
        """Отключает клавишу, чтобы курсор не уходил из области ввода."""
        return "break"

    def run(self) -> None:
        """Запускает цикл обработки событий окна."""
        self.root.mainloop()
