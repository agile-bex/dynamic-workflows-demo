"""Tests for the UI-free todo_store CRUD + JSON round-trip.

All tests use ``tmp_path`` so the suite never touches a real ``todos.json``.
"""

import json

from todo_app.todo_store import TodoStore


def _store(tmp_path):
    return TodoStore(tmp_path / "todos.json")


# -- create / read ---------------------------------------------------------


def test_create_assigns_id_and_fields(tmp_path):
    store = _store(tmp_path)
    todo = store.create("buy milk")
    assert todo["id"] == 1
    assert todo["title"] == "buy milk"
    assert todo["done"] is False


def test_create_increments_ids(tmp_path):
    store = _store(tmp_path)
    a = store.create("a")
    b = store.create("b")
    assert a["id"] == 1
    assert b["id"] == 2


def test_get_returns_todo_and_none_for_missing(tmp_path):
    store = _store(tmp_path)
    todo = store.create("task")
    assert store.get(todo["id"])["title"] == "task"
    assert store.get(999) is None


def test_list_returns_all(tmp_path):
    store = _store(tmp_path)
    store.create("a")
    store.create("b")
    titles = [t["title"] for t in store.list()]
    assert titles == ["a", "b"]


# -- update ----------------------------------------------------------------


def test_update_title_and_done(tmp_path):
    store = _store(tmp_path)
    todo = store.create("draft")
    updated = store.update(todo["id"], title="final", done=True)
    assert updated["title"] == "final"
    assert updated["done"] is True
    # confirmed via a fresh read
    assert store.get(todo["id"])["done"] is True


def test_update_missing_returns_none(tmp_path):
    store = _store(tmp_path)
    assert store.update(123, title="x") is None


# -- delete ----------------------------------------------------------------


def test_delete_removes_and_returns_true(tmp_path):
    store = _store(tmp_path)
    todo = store.create("temp")
    assert store.delete(todo["id"]) is True
    assert store.get(todo["id"]) is None
    assert store.list() == []


def test_delete_missing_returns_false(tmp_path):
    store = _store(tmp_path)
    assert store.delete(42) is False


# -- persistence / round-trip ---------------------------------------------


def test_save_reload_round_trip(tmp_path):
    path = tmp_path / "todos.json"
    store = TodoStore(path)
    store.create("first", done=True)
    store.create("second")

    # A brand-new store over the same file sees the persisted data.
    reloaded = TodoStore(path)
    items = reloaded.list()
    assert [t["title"] for t in items] == ["first", "second"]
    assert items[0]["done"] is True
    assert items[1]["done"] is False


def test_persisted_file_is_valid_json_list(tmp_path):
    path = tmp_path / "todos.json"
    store = TodoStore(path)
    store.create("only")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert data[0]["title"] == "only"


def test_missing_file_loads_as_empty(tmp_path):
    store = TodoStore(tmp_path / "does-not-exist.json")
    assert store.list() == []


def test_corrupt_file_loads_as_empty(tmp_path):
    path = tmp_path / "todos.json"
    path.write_text("{ this is not valid json", encoding="utf-8")
    store = TodoStore(path)
    assert store.list() == []
    # And it recovers: creating works and overwrites the garbage.
    store.create("recovered")
    reloaded = TodoStore(path)
    assert [t["title"] for t in reloaded.list()] == ["recovered"]


def test_non_list_json_loads_as_empty(tmp_path):
    path = tmp_path / "todos.json"
    path.write_text('{"id": 1, "title": "oops"}', encoding="utf-8")
    store = TodoStore(path)
    assert store.list() == []
