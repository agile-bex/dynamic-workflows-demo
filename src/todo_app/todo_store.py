"""UI-free CRUD store for to-dos, persisted to a single JSON file.

This module is the data + logic layer the app sits on top of. It has no
PySide6 / Qt dependency and knows nothing about a UI. Each :class:`TodoStore`
instance owns one ``todos.json`` file and round-trips the list through it.

A todo is a plain dict with at least ``id`` (int), ``title`` (str), and
``done`` (bool).
"""

from __future__ import annotations

import json
from pathlib import Path

# A todo is a simple mapping; kept as a dict so it serialises straight to JSON.
Todo = dict


class TodoStore:
    """CRUD over a list of todos persisted to a single JSON file.

    The store loads its current state on construction. A missing or corrupt
    file is treated as an empty list rather than an error, so the app never
    crashes on first run or on a damaged file.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._todos: list[Todo] = self._load()

    # -- persistence ------------------------------------------------------

    def _load(self) -> list[Todo]:
        """Load todos from disk, tolerating a missing or corrupt file."""
        try:
            raw = self.path.read_text(encoding="utf-8")
        except (FileNotFoundError, OSError):
            return []
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            return []
        if not isinstance(data, list):
            # Anything that isn't a JSON list is treated as no data.
            return []
        return [t for t in data if isinstance(t, dict)]

    def save(self) -> None:
        """Write the current todos to the JSON file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self._todos, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def reload(self) -> None:
        """Re-read the todos from disk, discarding in-memory state."""
        self._todos = self._load()

    # -- helpers ----------------------------------------------------------

    def _next_id(self) -> int:
        if not self._todos:
            return 1
        return max(int(t["id"]) for t in self._todos) + 1

    def _find(self, todo_id: int) -> Todo | None:
        for t in self._todos:
            if t["id"] == todo_id:
                return t
        return None

    # -- CRUD -------------------------------------------------------------

    def create(self, title: str, done: bool = False) -> Todo:
        """Create a new todo, persist, and return it."""
        todo: Todo = {"id": self._next_id(), "title": title, "done": done}
        self._todos.append(todo)
        self.save()
        return todo

    def get(self, todo_id: int) -> Todo | None:
        """Return the todo with ``todo_id``, or ``None`` if absent."""
        found = self._find(todo_id)
        return dict(found) if found is not None else None

    def list(self) -> list[Todo]:
        """Return a copy of all todos."""
        return [dict(t) for t in self._todos]

    def update(
        self,
        todo_id: int,
        *,
        title: str | None = None,
        done: bool | None = None,
    ) -> Todo | None:
        """Update a todo's title and/or done flag; persist and return it.

        Returns ``None`` if no todo has ``todo_id``.
        """
        todo = self._find(todo_id)
        if todo is None:
            return None
        if title is not None:
            todo["title"] = title
        if done is not None:
            todo["done"] = done
        self.save()
        return dict(todo)

    def delete(self, todo_id: int) -> bool:
        """Delete a todo; persist. Returns ``True`` if one was removed."""
        todo = self._find(todo_id)
        if todo is None:
            return False
        self._todos.remove(todo)
        self.save()
        return True
