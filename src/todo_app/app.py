"""PySide6 desktop UI for managing to-dos.

A thin CRUD front-end over :class:`todo_app.todo_store.TodoStore`. The store
owns all persistence; this module only renders the list and translates user
actions (add / toggle complete / delete) into store calls.

Launch with ``uv run app``. There are no automated tests here by design — see
the task card; the human QAs the behaviour by running it.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from todo_app.todo_store import TodoStore

# The store owns the file; we just decide where it lives. Keeping it in the
# current working directory matches how the human runs `uv run app` from the
# project root.
TODOS_PATH = Path("todos.json")

# Role used to stash each todo's id on its list item.
_ID_ROLE = Qt.ItemDataRole.UserRole


class TodoWindow(QMainWindow):
    """Main window: an add row, the list, and per-selection actions."""

    def __init__(self, store: TodoStore) -> None:
        super().__init__()
        self.store = store

        self.setWindowTitle("Todos")
        self.resize(420, 480)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # -- add row ------------------------------------------------------
        add_row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("What needs doing?")
        self.input.returnPressed.connect(self._on_add)
        add_button = QPushButton("Add")
        add_button.clicked.connect(self._on_add)
        add_row.addWidget(self.input)
        add_row.addWidget(add_button)
        layout.addLayout(add_row)

        # -- list ---------------------------------------------------------
        self.list_widget = QListWidget()
        self.list_widget.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self.list_widget)

        # -- actions ------------------------------------------------------
        action_row = QHBoxLayout()
        self.delete_button = QPushButton("Delete selected")
        self.delete_button.clicked.connect(self._on_delete)
        action_row.addStretch()
        action_row.addWidget(self.delete_button)
        layout.addLayout(action_row)

        self.empty_label = QLabel("No todos yet — add one above.")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.empty_label)

        self._refresh()

    # -- rendering --------------------------------------------------------

    def _refresh(self) -> None:
        """Rebuild the list from the store's current state."""
        # Block signals so rebuilding items doesn't fire itemChanged.
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        todos = self.store.list()
        for todo in todos:
            item = QListWidgetItem(todo["title"])
            item.setData(_ID_ROLE, todo["id"])
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                Qt.CheckState.Checked
                if todo["done"]
                else Qt.CheckState.Unchecked
            )
            self.list_widget.addItem(item)
        self.list_widget.blockSignals(False)
        self.empty_label.setVisible(not todos)

    # -- actions ----------------------------------------------------------

    def _on_add(self) -> None:
        title = self.input.text().strip()
        if not title:
            return
        self.store.create(title)
        self.input.clear()
        self._refresh()

    def _on_item_changed(self, item: QListWidgetItem) -> None:
        """A checkbox toggle marks the todo complete / un-complete."""
        todo_id = item.data(_ID_ROLE)
        done = item.checkState() == Qt.CheckState.Checked
        self.store.update(todo_id, done=done)

    def _on_delete(self) -> None:
        item = self.list_widget.currentItem()
        if item is None:
            QMessageBox.information(
                self, "Delete", "Select a todo to delete first."
            )
            return
        self.store.delete(item.data(_ID_ROLE))
        self._refresh()


def main() -> None:
    """Entry point wired to ``uv run app``."""
    app = QApplication(sys.argv)
    window = TodoWindow(TodoStore(TODOS_PATH))
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
