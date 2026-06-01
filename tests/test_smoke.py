from todo_app.main import hello


def test_hello_smoke():
    assert "works" in hello()
